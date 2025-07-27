"""
DungeonService - Core business logic for managing dungeon system

This service handles:
- Dungeon entry validation and session creation
- Trial generation and completion tracking
- Reward calculation and distribution
- Level progression and unlock management
- Integration with progression system
- Performance optimization with caching
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.application.services.base_service import BaseService
from app.application.services.quest_generation_service import QuestGenerationService
from app.application.services.dungeon_cache_service import DungeonCacheService
from app.infrastructure.database.models.v2.dungeon_sessions import DungeonSession
from app.infrastructure.database.models.v2.dungeon_trials import DungeonTrial
from app.infrastructure.database.models.v2.dungeon_rewards import DungeonReward
from app.infrastructure.database.models.v2.dungeon_level_unlocks import DungeonLevelUnlock
from app.infrastructure.database.models.v2.daily_modifiers import DailyModifier
from app.infrastructure.database.models.v2.dungeon_keys import DungeonKey
from app.infrastructure.database.models.v2.dungeon_progress import DungeonProgress
from app.infrastructure.database.models.v2.ascendants import Ascendant


class DungeonLevelLockedError(Exception):
    """Raised when trying to enter a locked dungeon level"""
    pass


class InsufficientRequirementsError(Exception):
    """Raised when user doesn't meet entry requirements"""
    pass


class ActiveSessionExistsError(Exception):
    """Raised when trying to enter dungeon with an active session"""
    pass


class DungeonService(BaseService):
    """
    Service for managing dungeon entry, progression, and completion.
    
    Follows hexagonal architecture pattern and integrates with the existing
    BaseService infrastructure for transaction management and error handling.
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize the DungeonService with optional session and caching."""
        super().__init__(session)
        self.quest_generation_service = None  # Will be initialized when needed
        self.cache_service = None  # Will be initialized when needed
    
    async def get_quest_generation_service(self) -> QuestGenerationService:
        """Get or create quest generation service instance."""
        if self.quest_generation_service is None:
            session = await self.get_session()
            self.quest_generation_service = QuestGenerationService(session)
        return self.quest_generation_service
    
    async def get_cache_service(self) -> DungeonCacheService:
        """Get or create cache service instance."""
        if self.cache_service is None:
            session = await self.get_session()
            self.cache_service = DungeonCacheService(session)
        return self.cache_service
    
    async def enter_dungeon(self, ascendant_id: int, dungeon_level: int) -> Dict[str, Any]:
        """
        Enter a dungeon level with validation and trial generation.
        
        Args:
            ascendant_id: The ascendant entering the dungeon
            dungeon_level: The dungeon level to enter
            
        Returns:
            Dict containing session info, trials, and expiration
            
        Raises:
            DungeonLevelLockedError: If level is locked
            InsufficientRequirementsError: If requirements not met
            ActiveSessionExistsError: If user already has an active session
        """
        try:
            # Always costs 1 Shadow Key regardless of level
            shadow_key_cost = 1
            
            # Check for existing active session
            active_session = await self.get_active_session(ascendant_id)
            if active_session:
                raise ActiveSessionExistsError(
                    f"Active dungeon session already exists (ID: {active_session.id}). "
                    f"Complete or abandon it before entering a new dungeon."
                )
            
            # Validate entry requirements
            await self.validate_entry_requirements(ascendant_id, dungeon_level)
            
            # Deduct Shadow Keys
            await self.deduct_shadow_keys(ascendant_id, shadow_key_cost)
            
            # Get daily modifier from cache
            cache_service = await self.get_cache_service()
            daily_modifier = await cache_service.get_cached_daily_modifier()
            
            # Generate trials for the level
            trials = await self.generate_trials(dungeon_level, daily_modifier)
            
            # Create session
            session = await self.create_session(ascendant_id, dungeon_level, trials, shadow_key_cost)
            
            self.logger.info(f"Ascendant {ascendant_id} entered dungeon level {dungeon_level}")
            
            return {
                "session_id": session.id,
                "level": dungeon_level,
                "trials": trials,
                "daily_modifier": daily_modifier.to_dict() if daily_modifier else None,
                "expires_at": session.expires_at
            }
            
        except Exception as e:
            self.handle_service_error(e, f"enter_dungeon(ascendant_id={ascendant_id}, level={dungeon_level})")
            raise
    
    async def validate_entry_requirements(self, ascendant_id: int, dungeon_level: int) -> bool:
        """
        Validate Aura, Shadow Keys, and skill tree requirements with infinite scaling.
        
        Args:
            ascendant_id: The ascendant to validate
            dungeon_level: The level to validate for
            
        Returns:
            bool: True if requirements are met
            
        Raises:
            DungeonLevelLockedError: If level is locked
            InsufficientRequirementsError: If requirements not met
        """
        try:
            session = await self.get_session()
            cache_service = await self.get_cache_service()
            
            # Get ascendant data with optimized query (eager loading)
            ascendant_result = await session.execute(
                select(Ascendant)
                .options(joinedload(Ascendant.dungeon_progress))
                .where(Ascendant.id == ascendant_id)
            )
            ascendant = ascendant_result.scalar_one_or_none()
            if not ascendant:
                raise InsufficientRequirementsError(f"Ascendant {ascendant_id} not found")
            
            # Get dungeon progress (may be loaded via eager loading above)
            dungeon_progress = ascendant.dungeon_progress if hasattr(ascendant, 'dungeon_progress') else await self.get_dungeon_progress(ascendant_id)
            
            # Check level requirements using cache
            level_requirements = await cache_service.get_cached_level_requirements(dungeon_level)
            if level_requirements and level_requirements.get('is_enabled', True):
                # Use cached unlock requirements for validation
                unlock_req = DungeonLevelUnlock(**level_requirements)
                is_unlocked, missing_reqs = unlock_req.check_unlock_requirements(ascendant, dungeon_progress)
                if not is_unlocked:
                    raise DungeonLevelLockedError(f"Level {dungeon_level} requirements not met: {', '.join(missing_reqs)}")
            
            # Use cached aura requirement calculation
            required_aura = cache_service.get_cached_aura_requirement(dungeon_level)
            
            # Check Shadow Keys (optimized query)
            shadow_keys = await self.get_shadow_keys_optimized(ascendant_id)
            if shadow_keys < 1:
                raise InsufficientRequirementsError("Requires 1 Shadow Key to enter dungeon")
            
            # Validate aura requirement
            if ascendant.aura < required_aura:
                raise InsufficientRequirementsError(f"Requires {required_aura} aura (you have {ascendant.aura})")
            
            return True
            
        except Exception as e:
            if isinstance(e, (DungeonLevelLockedError, InsufficientRequirementsError)):
                raise
            self.handle_service_error(e, f"validate_entry_requirements(ascendant_id={ascendant_id}, level={dungeon_level})")
            raise
    
    def calculate_aura_requirement(self, level: int) -> int:
        """Calculate aura requirement with exponential scaling."""
        # Base aura requirement of 100, scaling by 1.5x per level
        return int(100 * (1.5 ** (level - 1)))
    
    def calculate_stat_requirements(self, level: int) -> dict:
        """Calculate STR/END/TECH requirements with progressive scaling."""
        # Base requirement of 10 for each stat, scaling by 1.5x per level
        base_req = int(10 * (1.5 ** (level - 1)))
        
        return {
            'strength': base_req,
            'endurance': base_req,
            'technique': base_req
        }
    
    def calculate_skill_tree_requirements(self, level: int) -> int:
        """Calculate required Movement skill tree nodes."""
        # No requirement for level 1
        if level <= 1:
            return 0
        elif level <= 4:
            # Early levels: level - 1
            return level - 1
        elif level <= 10:
            # Mid levels: 5 + (level - 5) * 2
            return 5 + (level - 5) * 2
        else:
            # High levels: 15 + (level - 10) * 3
            return 15 + (level - 10) * 3
    
    async def get_shadow_keys(self, ascendant_id: int) -> int:
        """Get the number of shadow keys for an ascendant."""
        try:
            session = await self.get_session()
            
            result = await session.execute(
                select(DungeonKey.quantity).where(
                    and_(
                        DungeonKey.ascendant_id == ascendant_id,
                        DungeonKey.key_type == 'shadow_key'
                    )
                )
            )
            quantity = result.scalar_one_or_none()
            return quantity or 0
            
        except Exception as e:
            self.handle_service_error(e, f"get_shadow_keys(ascendant_id={ascendant_id})")
            raise
    
    async def get_shadow_keys_optimized(self, ascendant_id: int) -> int:
        """
        Optimized version of get_shadow_keys with better query performance.
        Uses index hints and minimal data transfer.
        """
        try:
            session = await self.get_session()
            
            # Optimized query with explicit column selection
            result = await session.execute(
                select(DungeonKey.quantity)
                .where(
                    and_(
                        DungeonKey.ascendant_id == ascendant_id,
                        DungeonKey.key_type == 'shadow_key'
                    )
                )
                .limit(1)  # Ensure only one result
            )
            quantity = result.scalar_one_or_none()
            return quantity or 0
            
        except Exception as e:
            self.logger.warning(f"Optimized shadow keys query failed, falling back to standard method: {e}")
            # Fallback to standard method
            return await self.get_shadow_keys(ascendant_id)
    
    async def deduct_shadow_keys(self, ascendant_id: int, amount: int = 1) -> bool:
        """
        Deduct Shadow Keys with transaction safety (always 1 for dungeons).
        
        Args:
            ascendant_id: The ascendant to deduct keys from
            amount: Number of keys to deduct (default 1)
            
        Returns:
            bool: True if successful
            
        Raises:
            InsufficientRequirementsError: If not enough keys
        """
        try:
            session = await self.get_session()
            
            # Get current keys
            current_keys = await self.get_shadow_keys(ascendant_id)
            if current_keys < amount:
                raise InsufficientRequirementsError(f"Insufficient Shadow Keys: need {amount}, have {current_keys}")
            
            # Update keys
            await session.execute(
                update(DungeonKey)
                .where(
                    and_(
                        DungeonKey.ascendant_id == ascendant_id,
                        DungeonKey.key_type == 'shadow_key'
                    )
                )
                .values(quantity=DungeonKey.quantity - amount)
            )
            
            await session.commit()
            self.logger.info(f"Deducted {amount} Shadow Keys from ascendant {ascendant_id}")
            return True
            
        except Exception as e:
            if isinstance(e, InsufficientRequirementsError):
                raise
            self.handle_service_error(e, f"deduct_shadow_keys(ascendant_id={ascendant_id}, amount={amount})")
            raise
    
    async def get_active_daily_modifier(self) -> Optional[DailyModifier]:
        """Get the currently active daily modifier."""
        try:
            session = await self.get_session()
            
            result = await session.execute(
                select(DailyModifier).where(
                    DailyModifier.is_active == True
                )
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.handle_service_error(e, "get_active_daily_modifier")
            raise
    
    async def generate_trials(self, dungeon_level: int, daily_modifier: Optional[DailyModifier] = None) -> List[Dict[str, Any]]:
        """
        Generate movement trials with difficulty scaling for infinite levels.
        
        Args:
            dungeon_level: The dungeon level
            daily_modifier: Optional daily modifier to apply
            
        Returns:
            List of trial dictionaries
        """
        try:
            session = await self.get_session()
            
            # Base number of trials with scaling
            base_trials = 3
            additional_trials = min(2, dungeon_level // 5)  # +1 trial every 5 levels, max 5 total
            total_trials = base_trials + additional_trials
            
            # Generate trials with increasing difficulty
            trials = []
            
            # Import models for querying
            from app.infrastructure.database.models.v2.movements import Movement
            from app.infrastructure.database.models.v2.skill_tree_nodes import SkillTreeNode
            
            for i in range(total_trials):
                trial_difficulty = self.calculate_trial_difficulty(dungeon_level, i)
                movement_category = self._get_movement_category_for_trial(i)
                
                # Get a random movement from the category
                movement_query = await session.execute(
                    select(Movement)
                    .join(SkillTreeNode, Movement.node_id == SkillTreeNode.id)
                    .where(SkillTreeNode.category_id == movement_category)
                    .order_by(func.random())
                    .limit(1)
                )
                movement = movement_query.scalar_one_or_none()
                
                if not movement:
                    # Fallback to any movement if category not found
                    movement_query = await session.execute(
                        select(Movement)
                        .order_by(func.random())
                        .limit(1)
                    )
                    movement = movement_query.scalar_one_or_none()
                
                # Calculate target value based on movement type and difficulty
                target_type = 'reps'  # Default
                base_value = 20  # Base reps
                
                if movement:
                    # Scale based on dungeon level and trial difficulty
                    # Higher levels require more reps
                    level_scaling = 1 + (dungeon_level - 1) * 0.1  # 10% more per level
                    base_value = int(base_value * level_scaling * trial_difficulty)
                
                # Apply difficulty scaling
                target_value = self._calculate_target_value_enhanced(
                    dungeon_level, trial_difficulty, base_value, daily_modifier
                )
                
                # Create trial data structure
                trial = {
                    'trial_number': i + 1,
                    'trial_type': 'movement',
                    'movement_id': movement.id if movement else None,
                    'movement_name': movement.name if movement else f'{movement_category} Movement',
                    'movement_category': movement_category,
                    'target_type': target_type,
                    'target_value': target_value,
                    'difficulty_multiplier': trial_difficulty,
                    'daily_modifier_applied': daily_modifier.modifier_type if daily_modifier else None
                }
                
                trials.append(trial)
            
            return trials
            
        except Exception as e:
            self.handle_service_error(e, f"generate_trials(level={dungeon_level})")
            raise
    
    def calculate_trial_difficulty(self, level: int, trial_index: int) -> float:
        """Calculate trial difficulty based on level and position."""
        base_difficulty = 0.5 + (level * 0.1)  # Increases with level
        trial_modifier = trial_index * 0.1  # Later trials are harder
        return min(1.0, base_difficulty + trial_modifier)
    
    def _get_movement_category_for_trial(self, trial_index: int) -> str:
        """Get movement category based on trial index."""
        categories = ['Push', 'Pull', 'Legs', 'Core', 'Cardio']
        return categories[trial_index % len(categories)]
    
    def _calculate_target_value(self, level: int, difficulty: float) -> int:
        """Calculate target reps based on level and difficulty."""
        base_reps = 10
        level_multiplier = 1 + (level * 0.2)
        difficulty_multiplier = 1 + difficulty
        return int(base_reps * level_multiplier * difficulty_multiplier)
    
    def _calculate_target_value_enhanced(self, level: int, difficulty: float, base_value: int, 
                                       daily_modifier: Optional[DailyModifier] = None) -> int:
        """
        Enhanced target value calculation with daily modifier support.
        
        Args:
            level: Dungeon level
            difficulty: Trial difficulty multiplier
            base_value: Base target value for the movement
            daily_modifier: Optional daily modifier
            
        Returns:
            int: Calculated target value
        """
        # Apply exponential scaling for infinite progression
        level_multiplier = 1.2 ** (level - 1)  # 1.2x per level
        
        # Apply difficulty multiplier
        total_multiplier = level_multiplier * (1 + difficulty)
        
        # Apply daily modifier if present
        if daily_modifier and daily_modifier.difficulty_multiplier:
            total_multiplier *= float(daily_modifier.difficulty_multiplier)
        
        # Calculate final value
        target_value = int(base_value * total_multiplier)
        
        # Ensure reasonable bounds
        return max(5, min(target_value, 1000))  # Min 5, max 1000
    
    async def create_session(self, ascendant_id: int, dungeon_level: int, trials: List[Dict[str, Any]], shadow_keys_spent: int) -> DungeonSession:
        """
        Create a new dungeon session.
        
        Args:
            ascendant_id: The ascendant entering
            dungeon_level: The level being entered
            trials: List of trial data
            shadow_keys_spent: Number of keys spent
            
        Returns:
            DungeonSession: The created session
        """
        try:
            session = await self.get_session()
            
            # Calculate expiration (24 hours from now)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            # Create session
            dungeon_session = DungeonSession(
                ascendant_id=ascendant_id,
                dungeon_level=dungeon_level,
                status='active',
                shadow_keys_spent=shadow_keys_spent,
                expires_at=expires_at,
                trial_data={'trials': trials}  # Store trials data as JSON
            )
            
            session.add(dungeon_session)
            await session.commit()
            await session.refresh(dungeon_session)
            
            # Create trial records
            for trial_data in trials:
                trial = DungeonTrial(
                    session_id=dungeon_session.id,
                    trial_number=trial_data['trial_number'],
                    trial_type=trial_data.get('trial_type', 'movement'),
                    movement_id=trial_data.get('movement_id'),
                    required_reps=trial_data['target_value'],
                    completed_reps=0,
                    trial_status='pending'
                )
                session.add(trial)
            
            await session.commit()
            
            return dungeon_session
            
        except Exception as e:
            self.handle_service_error(e, f"create_session(ascendant_id={ascendant_id}, level={dungeon_level})")
            raise
    
    async def get_dungeon_progress(self, ascendant_id: int) -> Optional[DungeonProgress]:
        """Get dungeon progress for an ascendant."""
        try:
            session = await self.get_session()
            
            result = await session.execute(
                select(DungeonProgress).where(DungeonProgress.ascendant_id == ascendant_id)
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.handle_service_error(e, f"get_dungeon_progress(ascendant_id={ascendant_id})")
            raise

    async def get_active_session(self, ascendant_id: int) -> Optional[DungeonSession]:
        """Get the active dungeon session for an ascendant."""
        try:
            session = await self.get_session()
            
            result = await session.execute(
                select(DungeonSession).where(
                    and_(
                        DungeonSession.ascendant_id == ascendant_id,
                        DungeonSession.status == 'active',
                        DungeonSession.expires_at > datetime.now(timezone.utc)
                    )
                )
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            self.handle_service_error(e, f"get_active_session(ascendant_id={ascendant_id})")
            raise
    
    async def complete_trial(self, trial_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a trial and check session completion.
        
        Args:
            trial_id: The trial being completed
            progress_data: Movement progress data
            
        Returns:
            Dict containing completion status and rewards
        """
        try:
            session = await self.get_session()
            
            # Get trial
            trial = await session.get(DungeonTrial, trial_id)
            if not trial:
                raise ValueError(f"Trial {trial_id} not found")
            
            # Update trial with progress
            completed_reps = progress_data.get('reps', 0)
            trial.completed_reps = completed_reps
            trial.trial_status = 'completed' if completed_reps >= trial.required_reps else 'failed'
            trial.completed_at = datetime.now(timezone.utc)
            trial.is_completed = completed_reps >= trial.required_reps
            
            # Get session
            dungeon_session = await session.get(DungeonSession, trial.session_id)
            if not dungeon_session:
                raise ValueError(f"Session {trial.session_id} not found")
            
            # Check if session is complete by counting completed trials
            # Load all trials for this session to check completion status
            from sqlalchemy.orm import selectinload
            session_with_trials = await session.get(
                DungeonSession, 
                trial.session_id,
                options=[selectinload(DungeonSession.trials)]
            )
            
            if session_with_trials:
                completed_trials = [t for t in session_with_trials.trials if t.is_completed]
                total_trials = len(session_with_trials.trials)
                session_completed = len(completed_trials) == total_trials and total_trials > 0
            else:
                session_completed = False
            
            if session_completed:
                dungeon_session.status = 'completed'
                dungeon_session.completed_at = datetime.now(timezone.utc)
                
                # Calculate completion time
                completion_time_seconds = None
                if dungeon_session.created_at:
                    time_delta = dungeon_session.completed_at - dungeon_session.created_at
                    completion_time_seconds = int(time_delta.total_seconds())
                
                # Calculate and distribute rewards
                rewards = await self.calculate_rewards(dungeon_session)
                await self.distribute_rewards(dungeon_session.ascendant_id, rewards, dungeon_session.id)
                
                # Update dungeon progress with completion time
                await self.update_dungeon_progress(
                    dungeon_session.ascendant_id, 
                    dungeon_session.dungeon_level,
                    completion_time_seconds
                )
            else:
                rewards = []
            
            await session.commit()
            
            return {
                'trial_completed': trial.is_completed,
                'session_completed': session_completed,
                'rewards_earned': rewards,
                'next_trial_available': not session_completed
            }
            
        except Exception as e:
            self.handle_service_error(e, f"complete_trial(trial_id={trial_id})")
            raise
    
    async def calculate_rewards(self, session: DungeonSession) -> List[Dict[str, Any]]:
        """
        Calculate and distribute rewards with exponential scaling.
        
        Args:
            session: The completed dungeon session
            
        Returns:
            List of reward dictionaries
        """
        try:
            level = session.dungeon_level
            base_aura = 50
            
            # Exponential reward scaling
            aura_reward = int(base_aura * (1.3 ** (level - 1)))
            
            rewards = [
                {
                    'type': 'aura',
                    'amount': aura_reward,
                    'description': f'Dungeon Level {level} Completion Bonus'
                },
                {
                    'type': 'shadow_essence',
                    'amount': level * 5,
                    'description': f'Shadow Essence from Level {level}'
                }
            ]
            
            # Milestone rewards
            if level % 10 == 0:  # Every 10 levels
                rewards.append({
                    'type': 'special_item',
                    'item_id': f'dungeon_milestone_{level}',
                    'description': f'Level {level} Milestone Achievement'
                })
            
            return rewards
            
        except Exception as e:
            self.handle_service_error(e, f"calculate_rewards(session_id={session.id})")
            raise
    
    async def distribute_rewards(self, ascendant_id: int, rewards: List[Dict[str, Any]], session_id: int = None) -> None:
        """Distribute rewards to the ascendant."""
        try:
            session = await self.get_session()
            
            shadow_essence_total = 0
            
            for reward in rewards:
                reward_record = DungeonReward(
                    session_id=session_id,
                    ascendant_id=ascendant_id,
                    reward_type=reward['type'],
                    amount=reward.get('amount', 0),
                    applied_at=datetime.now(timezone.utc)
                )
                session.add(reward_record)
                
                # Track shadow essence for progress update
                if reward['type'] == 'shadow_essence':
                    shadow_essence_total += reward.get('amount', 0)
            
            # Update progress with shadow essence earned
            if shadow_essence_total > 0:
                progress = await self.get_dungeon_progress(ascendant_id)
                if progress:
                    progress.total_shadow_essence_earned = (progress.total_shadow_essence_earned or 0) + shadow_essence_total
            
            await session.commit()
            self.logger.info(f"Distributed {len(rewards)} rewards to ascendant {ascendant_id}")
            
        except Exception as e:
            self.handle_service_error(e, f"distribute_rewards(ascendant_id={ascendant_id})")
            raise
    
    async def update_dungeon_progress(self, ascendant_id: int, completed_level: int, 
                                    completion_time_seconds: Optional[int] = None) -> None:
        """
        Update dungeon progress for an ascendant.
        
        Args:
            ascendant_id: The ascendant ID
            completed_level: The level that was completed
            completion_time_seconds: Time taken to complete in seconds
        """
        try:
            session = await self.get_session()
            
            # Get or create progress record
            progress = await self.get_dungeon_progress(ascendant_id)
            if not progress:
                progress = DungeonProgress(
                    ascendant_id=ascendant_id,
                    highest_level_completed=completed_level,
                    total_completions=1,
                    total_shadow_keys_spent=1,
                    last_completion_date=datetime.now(timezone.utc)
                )
                if completion_time_seconds:
                    progress.best_completion_time = completion_time_seconds
                session.add(progress)
            else:
                # Update highest level
                if completed_level > progress.highest_level_completed:
                    progress.highest_level_completed = completed_level
                
                # Update counters
                progress.total_completions = (progress.total_completions or 0) + 1
                progress.total_shadow_keys_spent = (progress.total_shadow_keys_spent or 0) + 1
                progress.last_completion_date = datetime.now(timezone.utc)
                
                # Update best time if better
                if completion_time_seconds:
                    if progress.best_completion_time is None or completion_time_seconds < progress.best_completion_time:
                        progress.best_completion_time = completion_time_seconds
            
            await session.commit()
            self.logger.info(f"Updated dungeon progress for ascendant {ascendant_id} to level {completed_level}")
            
        except Exception as e:
            self.handle_service_error(e, f"update_dungeon_progress(ascendant_id={ascendant_id}, level={completed_level})")
            raise
    
    async def cleanup_expired_sessions(self) -> Dict[str, Any]:
        """
        Clean up expired dungeon sessions.
        
        Returns:
            Dict containing cleanup statistics
        """
        try:
            session = await self.get_session()
            current_time = datetime.now(timezone.utc)
            
            # Find expired sessions
            expired_sessions_query = select(DungeonSession).where(
                and_(
                    DungeonSession.expires_at < current_time,
                    DungeonSession.status.in_(['active', 'in_progress'])
                )
            )
            
            result = await session.execute(expired_sessions_query)
            expired_sessions = result.scalars().all()
            
            cleanup_count = 0
            for expired_session in expired_sessions:
                # Mark session as expired
                expired_session.status = 'expired'
                expired_session.completed_at = current_time
                cleanup_count += 1
                
                self.logger.info(f"Cleaned up expired session {expired_session.id} for ascendant {expired_session.ascendant_id}")
            
            await session.commit()
            
            return {
                "cleaned_sessions": cleanup_count,
                "cleanup_time": current_time.isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            self.handle_service_error(e, "cleanup_expired_sessions")
            return {
                "cleaned_sessions": 0,
                "error": str(e),
                "status": "failed"
            }

    async def recover_session(self, ascendant_id: int) -> Optional[Dict[str, Any]]:
        """
        Recover an active dungeon session for session recovery.
        
        Args:
            ascendant_id: The ascendant to recover session for
            
        Returns:
            Dict containing session info if found, None otherwise
        """
        try:
            active_session = await self.get_active_session(ascendant_id)
            if not active_session:
                return None
            
            # Get trials for the session
            session = await self.get_session()
            trials_result = await session.execute(
                select(DungeonTrial)
                .where(DungeonTrial.session_id == active_session.id)
                .order_by(DungeonTrial.trial_number)
            )
            trials = trials_result.scalars().all()
            
            # Convert trials to dict format
            trials_data = []
            for trial in trials:
                trials_data.append({
                    'trial_id': trial.id,
                    'trial_number': trial.trial_number,
                    'trial_type': trial.trial_type,
                    'movement_id': trial.movement_id,
                    'movement_name': f"Movement {trial.trial_number}",  # Would need to join with movements table
                    'target_type': 'reps',
                    'target_value': trial.required_reps,
                    'current_progress': trial.completed_reps,
                    'is_completed': trial.is_completed,
                    'trial_status': trial.trial_status
                })
            
            return {
                'session_id': active_session.id,
                'level': active_session.dungeon_level,
                'trials': trials_data,
                'status': active_session.status,
                'expires_at': active_session.expires_at,
                'created_at': active_session.created_at,
                'progress_percentage': active_session.progress_percentage
            }
            
        except Exception as e:
            self.handle_service_error(e, f"recover_session(ascendant_id={ascendant_id})")
            raise
    
    async def abandon_session(self, session_id: int, ascendant_id: int) -> Dict[str, Any]:
        """
        Abandon an active dungeon session.
        
        Args:
            session_id: The session to abandon
            ascendant_id: The ascendant abandoning (for verification)
            
        Returns:
            Dict with abandonment confirmation
        """
        try:
            session = await self.get_session()
            
            # Get and verify session ownership
            dungeon_session = await session.get(DungeonSession, session_id)
            if not dungeon_session:
                raise ValueError(f"Session {session_id} not found")
            
            if dungeon_session.ascendant_id != ascendant_id:
                raise ValueError("Unauthorized: Session does not belong to this user")
            
            if dungeon_session.status != 'active':
                raise ValueError(f"Cannot abandon session with status: {dungeon_session.status}")
            
            # Update session status
            dungeon_session.status = 'abandoned'
            dungeon_session.completed_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            self.logger.info(f"Session {session_id} abandoned by ascendant {ascendant_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'message': 'Dungeon session abandoned successfully',
                'shadow_keys_refunded': 0  # No refund per business rules
            }
            
        except Exception as e:
            self.handle_service_error(e, f"abandon_session(session_id={session_id}, ascendant_id={ascendant_id})")
            raise
    
    async def get_session_details(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a dungeon session.
        
        Args:
            session_id: The session to get details for
            
        Returns:
            Dict containing session details or None if not found
        """
        try:
            session = await self.get_session()
            
            # Get session with trials
            result = await session.execute(
                select(DungeonSession)
                .options(selectinload(DungeonSession.trials))
                .where(DungeonSession.id == session_id)
            )
            dungeon_session = result.scalar_one_or_none()
            
            if not dungeon_session:
                return None
            
            # Build response
            trials_data = []
            for trial in dungeon_session.trials:
                trials_data.append({
                    'trial_id': trial.id,
                    'trial_number': trial.trial_number,
                    'trial_type': trial.trial_type,
                    'required_reps': trial.required_reps,
                    'completed_reps': trial.completed_reps,
                    'is_completed': trial.is_completed,
                    'trial_status': trial.trial_status,
                    'completed_at': trial.completed_at.isoformat() if trial.completed_at else None
                })
            
            return {
                'session_id': dungeon_session.id,
                'ascendant_id': dungeon_session.ascendant_id,
                'dungeon_level': dungeon_session.dungeon_level,
                'status': dungeon_session.status,
                'shadow_keys_spent': dungeon_session.shadow_keys_spent,
                'trials': trials_data,
                'created_at': dungeon_session.created_at.isoformat(),
                'expires_at': dungeon_session.expires_at.isoformat(),
                'completed_at': dungeon_session.completed_at.isoformat() if dungeon_session.completed_at else None,
                'progress_percentage': dungeon_session.progress_percentage
            }
            
        except Exception as e:
            self.handle_service_error(e, f"get_session_details(session_id={session_id})")
            raise
    
    async def get_daily_modifier(self) -> Optional[Dict[str, Any]]:
        """
        Get the current daily modifier.
        
        Returns:
            Dict containing daily modifier info or None if not active
        """
        try:
            # Try cache first
            cache_service = await self.get_cache_service()
            daily_modifier = await cache_service.get_cached_daily_modifier()
            
            if daily_modifier:
                return daily_modifier.to_dict()
            
            # Fallback to direct query if cache miss
            modifier = await self.get_active_daily_modifier()
            return modifier.to_dict() if modifier else None
            
        except Exception as e:
            self.handle_service_error(e, "get_daily_modifier")
            raise

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get dungeon leaderboard based on highest level completed and best completion times.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of leaderboard entries
        """
        try:
            session = await self.get_session()
            
            # Query for top performers based on highest level and best time
            result = await session.execute(
                select(
                    DungeonProgress.ascendant_id,
                    DungeonProgress.highest_level_completed,
                    DungeonProgress.best_completion_time,
                    DungeonProgress.total_completions,
                    Ascendant.username
                )
                .join(Ascendant, DungeonProgress.ascendant_id == Ascendant.id)
                .order_by(
                    DungeonProgress.highest_level_completed.desc(),
                    DungeonProgress.best_completion_time.asc()
                )
                .limit(limit)
            )
            
            leaderboard = []
            for rank, row in enumerate(result.all(), 1):
                leaderboard.append({
                    'rank': rank,
                    'ascendant_id': row.ascendant_id,
                    'username': row.username,
                    'highest_level': row.highest_level_completed,
                    'best_time_seconds': row.best_completion_time,
                    'total_completions': row.total_completions
                })
            
            return leaderboard
            
        except Exception as e:
            self.handle_service_error(e, f"get_leaderboard(limit={limit})")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check for the dungeon service."""
        try:
            session = await self.get_session()
            
            # Check database connectivity
            result = await session.execute(select(func.count(DungeonSession.id)))
            session_count = result.scalar()
            
            return {
                "service": "DungeonService",
                "status": "healthy",
                "database_connected": True,
                "total_sessions": session_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "service": "DungeonService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }