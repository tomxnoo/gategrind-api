"""Awakening Service for Daily Challenge System

This service handles the core business logic for the daily awakening system,
including session management, quest generation, completion tracking, and rewards.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.util import greenlet_spawn

from app.infrastructure.database.models.v2.awakening import (
    AwakeningSession, AwakeningQuest, AwakeningReward, UserAwakeningProgress
)
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.movements import Movement
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress
from app.application.services.progression_service import ProgressionService
from app.application.services.quest_generation_service import QuestGenerationService
from app.application.services.cache_service import cache_service

# Standard Python exceptions
class ValidationError(ValueError):
    """Raised when validation fails"""
    pass

class NotFoundError(Exception):
    """Raised when a resource is not found"""
    pass

logger = logging.getLogger(__name__)


class AwakeningService:
    """Service for managing daily awakening challenges and progression"""
    
    def __init__(self, db_session: AsyncSession, progression_service: ProgressionService):
        self.db_session = db_session
        self.progression_service = progression_service
        self.quest_generation_service = QuestGenerationService(db_session)
        self.cache_service = cache_service
        
        # Reward configuration
        self.BASE_XP_REWARD = 50
        self.BASE_AURA_REWARD = 10
        self.SHADOW_KEY_THRESHOLD = 3  # Complete 3 quests for Shadow Key
        self.STREAK_BONUS_MULTIPLIER = 0.1  # 10% bonus per streak day

    async def get_daily_session(self, user_id: int, session_date: date) -> Optional[AwakeningSession]:
        """
        Get the daily awakening session for a user on a specific date
        
        Args:
            user_id: The user's ID
            session_date: The date to get the session for
            
        Returns:
            AwakeningSession if exists, None otherwise
        """
        try:
            query = select(AwakeningSession).options(
                selectinload(AwakeningSession.quests),
                selectinload(AwakeningSession.rewards)
            ).where(
                and_(
                    AwakeningSession.user_id == user_id,
                    AwakeningSession.session_date == session_date
                )
            )
            
            result = await self.db_session.execute(query)
            
            session = await greenlet_spawn(lambda: result.scalar_one_or_none())
            
            logger.debug(f"Retrieved daily session for user {user_id} on {session_date}: {session is not None}")
            return session
            
        except Exception as e:
            logger.error(f"Error getting daily session for user {user_id}: {str(e)}")
            raise

    async def get_or_create_daily_session(self, user_id: int, readiness_level: int) -> Dict[str, Any]:
        """
        Get or create today's awakening session for a user with caching
        
        Args:
            user_id: The user's ID
            readiness_level: User's current readiness level
            
        Returns:
            Dict containing session data and quests
        """
        # Try to get from cache first
        cached_session = await self.cache_service.get_daily_session(user_id)
        if cached_session:
            logger.info(f"Retrieved daily session from cache for user {user_id}")
            return cached_session
        
        today = date.today()
        
        # Check if session already exists
        existing_session = await self.get_daily_session(user_id, today)
        
        if existing_session:
            session_data = self._format_session_for_api(existing_session)
        else:
            # Create new session
            session_data = await self.create_daily_session(user_id, readiness_level, today)
        
        # Cache the session data
        await self.cache_service.cache_daily_session(user_id, session_data)
        
        return session_data

    async def create_daily_session(
        self, 
        user_id: int, 
        readiness_level: int, 
        session_date: date,
        tier_level: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new daily awakening session with generated quests and caching
        
        Args:
            user_id: The user's ID
            readiness_level: User's current readiness level
            session_date: Date for the session
            tier_level: Difficulty tier for quest generation
            
        Returns:
            Dict containing the new session and quest data
            
        Raises:
            ValidationError: If session already exists for today
        """
        try:
            # Check if session already exists
            existing_session = await self.get_daily_session(user_id, session_date)
            if existing_session:
                session_data = self._format_session_for_api(existing_session)
                await self.cache_service.cache_daily_session(user_id, session_data)
                return session_data
            
            # Get cached user progression or calculate from database
            progression_data = await self.cache_service.get_user_progression(user_id)
            if not progression_data:
                # Calculate progression data dynamically from existing data
                progression_data = await self._calculate_user_progression(user_id)
                await self.cache_service.cache_user_progression(user_id, progression_data)
            
            # Create new session
            new_session = AwakeningSession(
                user_id=user_id,
                session_date=session_date,
                tier_level=tier_level,
                reset_used=False,
                created_at=datetime.now(timezone.utc)
            )
            self.db_session.add(new_session)

            # Just flush to make the session available, let the caller handle commit
            await self.db_session.flush()

            # Generate quests using QuestGenerationService
            logger.info(f"Generating daily quests for user {user_id}, tier {tier_level}, readiness {readiness_level}")
            try:
                quest_data_list = await self.quest_generation_service.generate_daily_quests(
                    user_id=user_id,
                    session_date=session_date,
                    tier_level=tier_level,
                    readiness_level_override=readiness_level
                )
                logger.info(f"Successfully generated {len(quest_data_list)} quests")
            except Exception as e:
                logger.error(f"Failed to generate daily quests: {e}")
                raise

            # Create AwakeningQuest objects linked to the new_session.
            quests = []
            for quest_data in quest_data_list:
                quest = AwakeningQuest(
                    session_id=new_session.id,  # Explicitly set session_id
                    quest_type=quest_data.get('quest_type'),
                    target_movement_id=quest_data.get('target_movement_id'),
                    target_movement=quest_data.get('target_movement'),
                    target_reps=quest_data.get('target_reps'),
                    target_time=quest_data.get('target_time'),
                    target_distance=quest_data.get('target_distance'),
                    difficulty_level=quest_data.get('difficulty_level'),
                    parameters=quest_data.get('parameters'),
                    status='active',
                    created_at=datetime.now(timezone.utc)
                )
                quests.append(quest)
                self.db_session.add(quest)  # Add each quest to the session

            # Flush to get the quest IDs assigned
            await self.db_session.flush()
            
            # Set the quests on the session for proper relationship
            new_session.quests = quests
            
            # Format response and cache
            session_data = self._format_session_for_api(new_session)
            await self.cache_service.cache_daily_session(user_id, session_data)
            
            logger.info(f"Created daily session for user {user_id} with {len(quests)} quests")
            return session_data
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating daily session for user {user_id}: {str(e)}")
            raise

    async def complete_quest(self, user_id: int, quest_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a specific quest and calculate rewards
        
        Args:
            user_id: The user's ID
            quest_id: The quest to complete
            progress_data: Progress information (reps, time, etc.)
            
        Returns:
            Dict containing completion status and rewards
            
        Raises:
            NotFoundError: If quest not found or not owned by user
            ValidationError: If quest already completed or invalid progress
        """
        try:
            # Get quest with session
            quest_query = select(AwakeningQuest).options(
                selectinload(AwakeningQuest.session)
            ).where(AwakeningQuest.id == quest_id)
            
            result = await self.db_session.execute(quest_query)
            quest = await greenlet_spawn(lambda: result.scalar_one_or_none())
            
            if not quest or quest.session.user_id != user_id:
                raise NotFoundError("Quest not found or not accessible")
            
            if quest.status == 'completed':
                raise ValidationError("Quest already completed")
            
            # Validate quest completion
            if not self._validate_quest_completion(quest, progress_data):
                raise ValidationError("Progress does not meet quest requirements")
            
            # Mark quest as completed
            quest.status = 'completed'
            quest.completed_at = datetime.now(timezone.utc)
            quest.progress_reps = progress_data.get('reps', 0)
            quest.progress_time = progress_data.get('time', 0)
            
            # Calculate and apply rewards
            rewards = await self._calculate_quest_rewards(quest, user_id)
            await self._apply_quest_rewards(user_id, quest, rewards)
            
            # Check if session is complete
            session_complete = await self._check_session_completion(quest.session_id)
            if session_complete:
                await self._complete_session(quest.session_id, user_id)
            
            # Just flush to make changes available, let the caller handle commit
            await self.db_session.flush()
            
            # Invalidate user cache after successful completion
            await self.cache_service.invalidate_user_cache(user_id)
            
            logger.info(f"Quest {quest_id} completed by user {user_id}")
            return {
                'success': True,
                'quest_id': quest_id,
                'rewards': rewards,
                'session_complete': session_complete
            }
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error completing quest {quest_id} for user {user_id}: {str(e)}")
            raise

    async def reset_daily_session(self, user_id: int) -> Dict[str, Any]:
        """
        Reset today's awakening session with reduced difficulty
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dict containing reset status and new quests
            
        Raises:
            ValidationError: If reset already used or no session exists
        """
        try:
            today = date.today()
            session = await self.get_daily_session(user_id, today)
            
            if not session:
                raise ValidationError("No awakening session found for today")
            
            if session.reset_used:
                raise ValidationError("Reset already used for today")
            
            # Mark reset as used
            session.reset_used = True
            session.reset_at = datetime.now(timezone.utc)
            
            # Get completed quest types and movements to exclude
            completed_quests = [q for q in session.quests if q.status == 'completed']
            excluded_movements = [q.target_movement_id for q in completed_quests if q.target_movement_id]
            excluded_quest_types = [q.quest_type for q in completed_quests]
            
            # Determine reduced tier level
            tier_mapping = {
                "extreme": "hard",
                "hard": "normal", 
                "normal": "easy",
                "easy": "easy"  # Can't go lower
            }
            new_tier = tier_mapping.get(session.tier_level, "easy")
            session.tier_level = new_tier
            
            # Remove incomplete quests
            incomplete_quests = [q for q in session.quests if q.status != 'completed']
            for quest in incomplete_quests:
                await self.db_session.delete(quest)
            
            # Generate new quests with exclusions
            quest_data_list = await self.quest_generation_service.generate_daily_quests(
                user_id=user_id,
                session_date=today,
                tier_level=new_tier,
                excluded_movements=excluded_movements,
                excluded_quest_types=excluded_quest_types
            )
            
            # Create new quest objects
            new_quests = []
            for quest_data in quest_data_list:
                quest = AwakeningQuest(
                    session_id=session.id,
                    quest_type=quest_data['quest_type'],
                    target_movement_id=quest_data['target_movement_id'],
                    target_movement=quest_data.get('target_movement'),
                    target_reps=quest_data.get('target_reps'),
                    target_time=quest_data.get('target_time'),
                    difficulty_level=quest_data['difficulty_level'],
                    status='active',
                    created_at=datetime.now(timezone.utc)
                )
                new_quests.append(quest)
                self.db_session.add(quest)
            
            # Just flush to make changes available, let the caller handle commit
            await self.db_session.flush()
            
            # Invalidate user cache after reset
            await self.cache_service.invalidate_user_cache(user_id)
            
            logger.info(f"Reset daily session for user {user_id} to tier {new_tier}")
            return self._format_session_for_api(session)
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error resetting daily session for user {user_id}: {str(e)}")
            raise

    async def get_awakening_history(self, user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Get user's awakening session history
        
        Args:
            user_id: The user's ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of session history data
        """
        try:
            # Query sessions with quests
            query = select(AwakeningSession).options(
                selectinload(AwakeningSession.quests)
            ).where(
                AwakeningSession.user_id == user_id
            ).order_by(
                AwakeningSession.session_date.desc()
            ).limit(limit)
            
            result = await self.db_session.execute(query)
            sessions = await greenlet_spawn(lambda: result.scalars().all())
            
            # For each session, explicitly query for rewards
            formatted_sessions = []
            for session in sessions:
                # Explicitly query for rewards
                rewards_query = select(AwakeningReward).where(AwakeningReward.session_id == session.id)
                rewards_result = await self.db_session.execute(rewards_query)
                rewards = rewards_result.scalars().all()
                
                # Manually attach rewards to session for formatting
                session.rewards = rewards
                
                formatted_sessions.append(self._format_session_for_api(session))
            
            return formatted_sessions
            
        except Exception as e:
            logger.error(f"Error getting awakening history for user {user_id}: {str(e)}")
            raise

    # Helper methods continue...

    def _format_session_for_api(self, session: AwakeningSession) -> Dict[str, Any]:
        """Format session data for API response"""
        return {
            'session_id': session.id,
            'user_id': session.user_id,
            'session_date': session.session_date.isoformat(),
            'status': session.status,
            'tier_level': session.tier_level,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'reset_used': session.reset_used,
            'quests': [self._format_quest_for_api(q) for q in session.quests],
            'rewards': [self._format_reward_for_api(r) for r in session.rewards] if hasattr(session, 'rewards') and session.rewards else []
        }

    def _format_quest_for_api(self, quest: AwakeningQuest) -> Dict[str, Any]:
        """Format quest data for API response"""
        return {
            'id': quest.id,
            'quest_type': quest.quest_type,
            'target_movement': quest.target_movement,
            'target_reps': quest.target_reps,
            'target_time': quest.target_time,
            'target_distance': quest.target_distance,
            'difficulty_level': quest.difficulty_level,
            'status': quest.status,
            'completed_at': quest.completed_at.isoformat() if quest.completed_at else None,
            'parameters': quest.parameters
        }

    def _format_reward_for_api(self, reward: 'AwakeningReward') -> Dict[str, Any]:
        """Format reward data for API response"""
        return {
            'id': reward.id,
            'xp_gained': reward.xp_gained,
            'aura_change': reward.aura_change,
            'shadow_keys': reward.shadow_keys,
            'created_at': reward.created_at.isoformat() if reward.created_at else None
        }

    def _validate_quest_completion(self, quest: AwakeningQuest, progress_data: Dict[str, Any]) -> bool:
        """Validate that progress meets quest requirements."""
        if quest.quest_type == "movement_reps":
            provided = progress_data.get("reps", 0)
            target = quest.target_reps
            return provided >= target
        elif quest.quest_type == "time_based":
            provided = progress_data.get("time", 0)
            target = quest.target_time
            return provided >= target
        elif quest.quest_type == "distance":
            provided = progress_data.get("distance", 0)
            target = quest.target_distance
            return provided >= target
        elif quest.quest_type == "endurance_challenge":
            # Endurance challenge requires both reps and time targets to be met
            provided_reps = progress_data.get("reps", 0)
            provided_time = progress_data.get("time", 0)
            target_reps = quest.target_reps
            target_time = quest.target_time
            reps_valid = provided_reps >= target_reps
            time_valid = provided_time >= target_time
            return reps_valid and time_valid
        
        logger.warning(f"Unknown quest type: {quest.quest_type}")
        return False

    async def _calculate_quest_rewards(self, quest: AwakeningQuest, user_id: int) -> Dict[str, Any]:
        """
        Calculate rewards for completing a quest
        
        Args:
            quest: The completed quest
            user_id: The user's ID
            
        Returns:
            Dict containing reward amounts
        """
        # Base rewards
        base_xp = self.BASE_XP_REWARD
        base_aura = self.BASE_AURA_REWARD
        
        # Difficulty multipliers
        difficulty_multipliers = {
            'easy': 0.8,
            'normal': 1.0,
            'hard': 1.3,
            'extreme': 1.6
        }
        
        multiplier = difficulty_multipliers.get(quest.difficulty_level, 1.0)
        
        # Calculate final rewards
        xp_reward = int(base_xp * multiplier)
        aura_reward = int(base_aura * multiplier)
        
        # Check for Shadow Key reward (based on session completion)
        shadow_keys = 0
        session_quests_completed = await self._count_completed_quests(quest.session_id)
        if session_quests_completed >= self.SHADOW_KEY_THRESHOLD:
            shadow_keys = 1
        
        return {
            'xp': xp_reward,
            'aura': aura_reward,
            'shadow_keys': shadow_keys
        }

    async def _apply_quest_rewards(self, user_id: int, quest: AwakeningQuest, rewards: Dict[str, Any]) -> None:
        """
        Apply calculated rewards to the user's account
        
        Args:
            user_id: The user's ID
            quest: The completed quest
            rewards: Calculated rewards
        """
        # Create reward record
        reward_record = AwakeningReward(
            session_id=quest.session_id,
            xp_gained=rewards['xp'],
            aura_change=rewards['aura'],
            shadow_keys=rewards['shadow_keys'],
            created_at=datetime.now(timezone.utc)
        )
        
        self.db_session.add(reward_record)
        
        # Apply XP rewards via ProgressionService (this will also update aura automatically)
        await self.progression_service.add_xp(user_id, rewards['xp'], 'global')
        
        # Handle shadow keys directly (since progression service doesn't have add_shadow_keys method)
        if rewards['shadow_keys'] > 0:
            await self._add_shadow_keys_to_user(user_id, rewards['shadow_keys'])

    async def _add_shadow_keys_to_user(self, user_id: int, shadow_keys: int) -> None:
        """
        Add shadow keys to user's account
        
        Args:
            user_id: The user's ID
            shadow_keys: Number of shadow keys to add
        """
        # Update user's shadow keys
        stmt = (
            update(Ascendant)
            .where(Ascendant.id == user_id)
            .values(shadow_keys=Ascendant.shadow_keys + shadow_keys)
        )
        
        await self.db_session.execute(stmt)

    async def _check_session_completion(self, session_id: int) -> bool:
        """
        Check if all quests in a session are completed
        
        Args:
            session_id: The session ID to check
            
        Returns:
            True if all quests are completed, False otherwise
        """
        query = select(AwakeningQuest).where(AwakeningQuest.session_id == session_id)
        result = await self.db_session.execute(query)
        quests = result.scalars().all()
        
        if not quests:
            return False
        
        return all(quest.status == 'completed' for quest in quests)

    async def _complete_session(self, session_id: int, user_id: int) -> None:
        """
        Mark a session as completed and apply streak bonuses
        
        Args:
            session_id: The session ID to complete
            user_id: The user's ID
        """
        # Update session status
        session_query = select(AwakeningSession).where(AwakeningSession.id == session_id)
        result = await self.db_session.execute(session_query)
        session = result.scalar_one_or_none()
        
        if session:
            session.completed_at = datetime.now(timezone.utc)
            session.status = 'completed'
            
            # Update user's awakening streak
            await self._update_awakening_streak(user_id)



    async def _count_completed_quests(self, session_id: int) -> int:
        """
        Count completed quests in a session
        
        Args:
            session_id: The session ID
            
        Returns:
            Number of completed quests
        """
        query = select(func.count(AwakeningQuest.id)).where(
            and_(
                AwakeningQuest.session_id == session_id,
                AwakeningQuest.status == 'completed'
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar() or 0

    def _get_quest_count_for_readiness(self, readiness_level: int) -> int:
        """
        Get the number of quests to generate based on readiness level
        
        Args:
            readiness_level: User's readiness level (1-10)
            
        Returns:
            Number of quests to generate
        """
        if readiness_level <= 3:
            return 3  # Low energy - minimum 3 quests
        elif readiness_level <= 7:
            return 3  # Normal energy
        else:
            return 4  # High energy

    def _get_difficulty_for_readiness(self, readiness_level: int) -> str:
        """
        Get difficulty tier based on readiness level
        
        Args:
            readiness_level: User's readiness level (1-10)
            
        Returns:
            Difficulty tier string
        """
        if readiness_level <= 3:
            return 'easy'
        elif readiness_level <= 5:
            return 'normal'
        elif readiness_level <= 8:
            return 'hard'
        else:
            return 'extreme'

    # Private helper methods

    async def _get_user_progression_data(self, user_id: int) -> Dict[str, Any]:
        """Get user's progression data for quest personalization."""
        stmt = (
            select(Ascendant)
            .options(
                selectinload(Ascendant.stats),
                selectinload(Ascendant.skill_progress)
            )
            .where(Ascendant.id == user_id)
        )
        
        result = await self.db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        return {
            "level": user.level,
            "stats": {
                "strength": user.stats.strength if user.stats else 1,
                "endurance": user.stats.endurance if user.stats else 1,
                "technique": user.stats.technique if user.stats else 1
            },
            "skill_progress": [
                {
                    "skill_name": sp.skill_name,
                    "current_level": sp.current_level,
                    "unlocked": sp.unlocked
                }
                for sp in user.skill_progress
            ] if user.skill_progress else []
        }

    async def _generate_personalized_quests(
        self, session_id: int, user_data: Dict[str, Any], readiness_level: str
    ) -> List[AwakeningQuest]:
        """Generate personalized quests based on user progression and readiness."""
        quest_count = self._get_quest_count_for_readiness(readiness_level)
        difficulty = self._get_difficulty_for_readiness(readiness_level)
        
        quests = []
        
        # Generate movement-based quests
        movement_quests = await self._generate_movement_quests(
            session_id, user_data, difficulty, quest_count - 1
        )
        quests.extend(movement_quests)
        
        # Generate one time-based quest
        time_quest = await self._generate_time_quest(session_id, user_data, difficulty)
        quests.append(time_quest)
        
        return quests

    async def _generate_reduced_tier_quests(
        self, session_id: int, user_data: Dict[str, Any], completed_quests: List[AwakeningQuest]
    ) -> List[AwakeningQuest]:
        """Generate reduced-tier quests excluding completed quest types."""
        # Get movements from completed quests to exclude
        excluded_movements = {q.target_movement for q in completed_quests if q.target_movement}
        
        # Generate easier quests
        quest_count = max(2, 4 - len(completed_quests))  # Ensure minimum viable quest count
        difficulty = "easy"
        
        quests = []
        
        # Generate movement quests excluding completed ones
        movement_quests = await self._generate_movement_quests(
            session_id, user_data, difficulty, quest_count - 1, excluded_movements
        )
        quests.extend(movement_quests)
        
        # Add time quest if not already completed
        if not any(q.quest_type == "time_based" for q in completed_quests):
            time_quest = await self._generate_time_quest(session_id, user_data, difficulty)
            quests.append(time_quest)
        
        return quests

    async def _generate_movement_quests(
        self, session_id: int, user_data: Dict[str, Any], difficulty: str, 
        count: int, excluded_movements: set = None
    ) -> List[AwakeningQuest]:
        """Generate movement-based quests."""
        if excluded_movements is None:
            excluded_movements = set()
        
        # Basic movement pool (would be expanded with actual movement data)
        movements = [
            {"name": "Standard Pushup", "base_reps": 20, "stat_focus": "strength"},
            {"name": "Bodyweight Squat", "base_reps": 30, "stat_focus": "endurance"},
            {"name": "Mountain Climber", "base_reps": 40, "stat_focus": "endurance"},
            {"name": "Burpee", "base_reps": 15, "stat_focus": "technique"},
            {"name": "Jumping Jack", "base_reps": 50, "stat_focus": "endurance"},
        ]
        
        # Filter out excluded movements
        available_movements = [m for m in movements if m["name"] not in excluded_movements]
        
        if len(available_movements) < count:
            # If not enough movements, allow repeats with different rep counts
            available_movements = movements
        
        quests = []
        user_level = user_data["level"]
        
        for i in range(min(count, len(available_movements))):
            movement = available_movements[i]
            
            # Calculate target reps based on difficulty and user level
            base_reps = movement["base_reps"]
            level_modifier = 1 + (user_level - 1) * 0.1  # 10% increase per level
            difficulty_modifier = {"easy": 0.7, "moderate": 1.0, "hard": 1.3}[difficulty]
            
            target_reps = int(base_reps * level_modifier * difficulty_modifier)
            
            quest = AwakeningQuest(
                session_id=session_id,
                quest_type="movement_reps",
                target_movement=movement["name"],
                target_reps=target_reps,
                difficulty_level=difficulty,
                parameters={"stat_focus": movement["stat_focus"]}
            )
            
            quests.append(quest)
        
        return quests

    async def _generate_time_quest(
        self, session_id: int, user_data: Dict[str, Any], difficulty: str
    ) -> AwakeningQuest:
        """Generate a time-based quest."""
        # Time-based exercises
        time_exercises = [
            {"name": "Plank Hold", "base_time": 60},
            {"name": "Wall Sit", "base_time": 45},
            {"name": "Dead Hang", "base_time": 30},
        ]
        
        exercise = time_exercises[0]  # Default to plank
        user_level = user_data["level"]
        
        # Calculate target time
        base_time = exercise["base_time"]
        level_modifier = 1 + (user_level - 1) * 0.05  # 5% increase per level
        difficulty_modifier = {"easy": 0.7, "moderate": 1.0, "hard": 1.3}[difficulty]
        
        target_time = int(base_time * level_modifier * difficulty_modifier)
        
        return AwakeningQuest(
            session_id=session_id,
            quest_type="time_based",
            target_movement=exercise["name"],
            target_time=target_time,
            difficulty_level=difficulty
        )

    def _get_quest_count_for_readiness(self, readiness_level: str) -> int:
        """Determine quest count based on readiness level."""
        return {
            "low": 3,
            "standard": 3,
            "high": 4
        }.get(readiness_level, 3)

    def _get_difficulty_for_readiness(self, readiness_level: str) -> str:
        """Determine difficulty based on readiness level."""
        return {
            "low": "easy",
            "standard": "moderate", 
            "high": "hard"
        }.get(readiness_level, "moderate")

    async def _get_user_quest(self, user_id: int, quest_id: int) -> Optional[AwakeningQuest]:
        """Get a quest and validate user ownership."""
        stmt = (
            select(AwakeningQuest)
            .join(AwakeningSession)
            .where(
                and_(
                    AwakeningQuest.id == quest_id,
                    AwakeningSession.user_id == user_id
                )
            )
        )
        
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    def _validate_quest_completion(self, quest: AwakeningQuest, progress_data: Dict[str, Any]) -> bool:
        """Validate that progress meets quest requirements."""
        if quest.quest_type == "movement_reps":
            return progress_data.get("reps", 0) >= quest.target_reps
        elif quest.quest_type == "time_based":
            return progress_data.get("time", 0) >= quest.target_time
        elif quest.quest_type == "distance":
            return progress_data.get("distance", 0) >= quest.target_distance
        elif quest.quest_type == "endurance_challenge":
            # Endurance challenge requires both reps and time targets to be met
            provided_reps = progress_data.get("reps", 0)
            provided_time = progress_data.get("time", 0)
            target_reps = quest.target_reps
            target_time = quest.target_time
            reps_valid = provided_reps >= target_reps
            time_valid = provided_time >= target_time
            return reps_valid and time_valid
        
        return False

    async def _calculate_user_progression(self, user_id: int) -> Dict[str, Any]:
        """Calculate user's overall awakening progression dynamically from session and quest data."""
        # Get user's current streak from Ascendant model
        user_stmt = select(Ascendant).where(Ascendant.id == user_id)
        user_result = await self.db_session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            # For testing purposes, let's check if there are any users at all
            all_users_stmt = select(Ascendant)
            all_users_result = await self.db_session.execute(all_users_stmt)
            all_users = all_users_result.scalars().all()
            logger.warning(f"User {user_id} not found. Available users: {[u.id for u in all_users]}")
            
            # Return default progression data instead of raising an error
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_sessions_completed': 0,
                'total_quests_completed': 0,
                'total_xp_earned': 0,
                'total_aura_earned': 0,
                'total_shadow_keys_earned': 0
            }
        
        current_streak = user.awakening_streak
        
        # Calculate total sessions completed
        completed_sessions_stmt = (
            select(func.count(AwakeningSession.id))
            .where(
                and_(
                    AwakeningSession.user_id == user_id,
                    AwakeningSession.status == "completed"
                )
            )
        )
        sessions_result = await self.db_session.execute(completed_sessions_stmt)
        total_sessions_completed = sessions_result.scalar() or 0
        
        # Calculate total quests completed
        completed_quests_stmt = (
            select(func.count(AwakeningQuest.id))
            .where(
                and_(
                    AwakeningQuest.session_id.in_(
                        select(AwakeningSession.id).where(AwakeningSession.user_id == user_id)
                    ),
                    AwakeningQuest.status == "completed"
                )
            )
        )
        quests_result = await self.db_session.execute(completed_quests_stmt)
        total_quests_completed = quests_result.scalar() or 0
        
        # Calculate total rewards earned (sum from AwakeningReward table)
        rewards_stmt = (
            select(
                func.coalesce(func.sum(AwakeningReward.xp_gained), 0).label('total_xp'),
                func.coalesce(func.sum(AwakeningReward.aura_change), 0).label('total_aura'),
                func.coalesce(func.sum(AwakeningReward.shadow_keys), 0).label('total_shadow_keys')
            )
            .where(
                AwakeningReward.session_id.in_(
                    select(AwakeningSession.id).where(AwakeningSession.user_id == user_id)
                )
            )
        )
        rewards_result = await self.db_session.execute(rewards_stmt)
        rewards_data = rewards_result.first()
        
        # Calculate longest streak (would need historical data - for now use current streak)
        # TODO: Implement proper longest streak calculation with historical session data
        longest_streak = current_streak
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_sessions_completed': total_sessions_completed,
            'total_quests_completed': total_quests_completed,
            'total_xp_earned': rewards_data.total_xp if rewards_data else 0,
            'total_aura_earned': rewards_data.total_aura if rewards_data else 0,
            'total_shadow_keys_earned': rewards_data.total_shadow_keys if rewards_data else 0
        }









    async def _update_awakening_streak(self, user_id: int):
        """Update user's awakening completion streak."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Check if user completed awakening yesterday
        yesterday_session_stmt = (
            select(AwakeningSession)
            .where(
                and_(
                    AwakeningSession.user_id == user_id,
                    AwakeningSession.session_date == yesterday,
                    AwakeningSession.status == "completed"
                )
            )
        )
        
        result = await self.db_session.execute(yesterday_session_stmt)
        yesterday_session = result.scalar_one_or_none()
        
        if yesterday_session:
            # Continue streak
            stmt = (
                update(Ascendant)
                .where(Ascendant.id == user_id)
                .values(awakening_streak=Ascendant.awakening_streak + 1)
            )
        else:
            # Reset streak to 1
            stmt = (
                update(Ascendant)
                .where(Ascendant.id == user_id)
                .values(awakening_streak=1)
            )
        
        await self.db_session.execute(stmt)
