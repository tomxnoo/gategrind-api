"""
Quest Generation Service for Awakening System

This service handles the generation of personalized daily awakening quests
based on user progression, unlocked skills, and difficulty preferences.
"""

import logging
import random
from typing import List, Dict, Any, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.movements import Movement
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress
from app.infrastructure.database.models.v2.awakening import AwakeningSession, AwakeningQuest
from sqlalchemy.util import greenlet_spawn

logger = logging.getLogger(__name__)

class QuestGenerationService:
    """Service for generating personalized awakening quests"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
        # Quest generation configuration
        self.QUEST_TYPES = ["movement_reps", "time_based", "endurance_challenge"]
        self.DIFFICULTY_TIERS = {
            "easy": {"multiplier": 0.7, "base_reps": 20, "base_time": 30},
            "normal": {"multiplier": 1.0, "base_reps": 30, "base_time": 60}, 
            "hard": {"multiplier": 1.5, "base_reps": 50, "base_time": 90},
            "extreme": {"multiplier": 2.0, "base_reps": 75, "base_time": 120}
        }
        
        # Default quest counts by readiness level
        self.DEFAULT_QUEST_COUNTS = {
            1: 2,  # Beginner
            2: 2,  # Novice
            3: 3,  # Intermediate
            4: 3,  # Advanced
            5: 4,  # Expert
            6: 4,  # Master
            7: 5,  # Grandmaster
            8: 5,  # Legend
            9: 6,  # Mythic
            10: 6  # Transcendent
        }

    async def generate_daily_quests(
        self, 
        user_id: int, 
        session_date: date,
        tier_level: str = "normal",
        excluded_movements: Optional[List[int]] = None,
        excluded_quest_types: Optional[List[str]] = None,
        readiness_level_override: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized daily quests for a user
        
        Args:
            user_id: The user's ID
            session_date: Date for the quest session
            tier_level: Difficulty tier (easy, normal, hard, extreme)
            excluded_movements: Movement IDs to exclude (for resets)
            excluded_quest_types: Quest types to exclude (for resets)
            readiness_level_override: Override the user's readiness level for quest count
            
        Returns:
            List of quest dictionaries ready for database insertion
        """
        try:
            logger.info(f"Starting quest generation for user {user_id}, tier {tier_level}, readiness override {readiness_level_override}")
            
            # Get user progression data
            user_data = await self._get_user_progression_data(user_id)
            if not user_data:
                logger.error(f"User {user_id} not found in database")
                raise ValueError(f"User {user_id} not found")
            
            logger.info(f"User data retrieved: readiness_level={user_data['readiness_level']}, aura_score={user_data.get('aura_score', 'N/A')}")
            
            # Use override readiness level if provided, otherwise use user's readiness level
            readiness_level = readiness_level_override if readiness_level_override is not None else user_data['readiness_level']
            logger.info(f"Using readiness level: {readiness_level}")
            
            # Get available movements for the user first
            excluded_movement_ids = excluded_movements or []
            logger.info(f"Excluded movements: {excluded_movement_ids}")
            
            available_movements = await self._get_user_available_movements(
                user_id, excluded_movement_ids
            )
            
            # If no movements available after exclusions, allow reuse of excluded movements
            if not available_movements:
                logger.warning(f"No movements available after exclusions, allowing reuse of excluded movements")
                available_movements = await self._get_user_available_movements(user_id, [])
                if not available_movements:
                    logger.error(f"No available movements found for user {user_id}")
                    raise ValueError("No available movements for quest generation")
            
            # Determine quest count based on readiness level, but cap it by available movements
            desired_quest_count = self._get_quest_count_for_readiness(readiness_level)
            quest_count = min(desired_quest_count, len(available_movements))
            
            if quest_count < desired_quest_count:
                logger.warning(f"Reducing quest count from {desired_quest_count} to {quest_count} due to limited available movements")
            
            # Generate quests
            quests = []
            used_movements = set()
            used_quest_types = set(excluded_quest_types or [])
            
            for i in range(quest_count):
                quest = await self._generate_single_quest(
                    user_data=user_data,
                    available_movements=available_movements,
                    tier_level=tier_level,
                    used_movements=used_movements,
                    used_quest_types=used_quest_types,
                    quest_index=i
                )
                
                if quest:
                    quests.append(quest)
                    if quest.get('target_movement_id'):
                        used_movements.add(quest['target_movement_id'])
                    if quest.get('quest_type'):
                        used_quest_types.add(quest['quest_type'])
                else:
                    # Break early if we can't generate more quests
                    break
            
            logger.info(f"Generated {len(quests)} quests for user {user_id} on {session_date}")
            return quests
            
        except Exception as e:
            logger.error(f"Error generating daily quests for user {user_id}: {e}", exc_info=True)
            raise

    async def _get_user_progression_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's progression data for quest personalization"""
        try:
            # Get ascendant data
            ascendant_query = select(Ascendant).where(Ascendant.id == user_id)
            result = await self.db_session.execute(ascendant_query)
            ascendant = await greenlet_spawn(lambda: result.scalar_one_or_none())
            
            if not ascendant:
                return None
            
            # Get skill progress
            skill_query = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == user_id)
            skill_result = await self.db_session.execute(skill_query)
            skills = await greenlet_spawn(lambda: skill_result.scalars().all())
            
            # Ensure readiness_level is an integer
            readiness_level = getattr(ascendant, 'readiness_level', 1)
            if isinstance(readiness_level, str):
                # Convert string readiness levels to integers
                readiness_mapping = {
                    'standard': 1,
                    'beginner': 1,
                    'novice': 2,
                    'intermediate': 3,
                    'advanced': 4,
                    'expert': 5,
                    'master': 6,
                    'grandmaster': 7,
                    'legend': 8,
                    'mythic': 9,
                    'transcendent': 10
                }
                readiness_level = readiness_mapping.get(readiness_level.lower(), 1)
            
            return {
                'user_id': user_id,
                'readiness_level': readiness_level,
                'aura_score': getattr(ascendant, 'aura_score', ascendant.aura),  # Use aura if aura_score not present
                'str_points': getattr(ascendant, 'str_points', ascendant.strength_points),  # Use strength_points
                'end_points': getattr(ascendant, 'end_points', ascendant.endurance_points),  # Use endurance_points
                'tech_points': getattr(ascendant, 'tech_points', ascendant.technique_points),  # Use technique_points
                'awakening_streak': getattr(ascendant, 'awakening_streak', 0),
                'skills': [
                    {
                        'node_id': skill.node_id,
                        'unlocked_at': skill.unlocked_at
                    } for skill in skills
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user progression data for {user_id}: {str(e)}")
            return None

    async def _get_user_available_movements(
        self, 
        user_id: int, 
        excluded_movement_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """Get movements available to the user for quest generation"""
        try:
            logger.info(f"Getting available movements for user {user_id}, excluded: {excluded_movement_ids}")
            
            # Get user's unlocked movements through skill progress
            skill_query = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == user_id)
            skill_result = await self.db_session.execute(skill_query)
            unlocked_skills = await greenlet_spawn(lambda: skill_result.scalars().all())
            
            logger.info(f"Found {len(unlocked_skills)} unlocked skills for user {user_id}")
            
            if not unlocked_skills:
                logger.info("No unlocked skills found, using general movements")
                # Fallback to any available movements if no skills unlocked
                if excluded_movement_ids:
                    movement_query = select(Movement).where(
                        Movement.id.notin_(excluded_movement_ids)
                    ).limit(10)  # Limit to prevent too many results
                else:
                    movement_query = select(Movement).limit(10)
                logger.info("Using fallback movement query")
            else:
                # Get movements from unlocked skill nodes
                node_ids = [skill.node_id for skill in unlocked_skills]
                logger.info(f"Node IDs for filtering: {node_ids}")
                
                if excluded_movement_ids:
                    movement_query = select(Movement).where(
                        and_(
                            Movement.id.notin_(excluded_movement_ids),
                            Movement.node_id.in_(node_ids)
                        )
                    )
                else:
                    movement_query = select(Movement).where(
                        Movement.node_id.in_(node_ids)
                    )
                logger.info("Using skill-based movement query")
            
            result = await self.db_session.execute(movement_query)
            movements = await greenlet_spawn(lambda: result.scalars().all())
            
            logger.info(f"Found {len(movements)} movements from database")
            
            available_movements = [
                {
                    'id': movement.id,
                    'name': movement.name,
                    'node_id': movement.node_id,
                    'difficulty_level': getattr(movement, 'difficulty_level', 1),
                    'movement_type': getattr(movement, 'movement_type', 'strength')
                } for movement in movements
            ]
            
            logger.info(f"Returning {len(available_movements)} available movements")
            return available_movements
            
        except Exception as e:
            logger.error(f"Error getting available movements for user {user_id}: {str(e)}", exc_info=True)
            return []

    async def _generate_single_quest(
        self,
        user_data: Dict[str, Any],
        available_movements: List[Dict[str, Any]],
        tier_level: str,
        used_movements: set,
        used_quest_types: set,
        quest_index: int
    ) -> Optional[Dict[str, Any]]:
        """Generate a single quest based on user data and constraints"""
        try:
            logger.info(f"Generating quest {quest_index + 1}: used_movements={used_movements}, used_quest_types={used_quest_types}")
            
            # Filter available movements
            available_movements = [
                m for m in available_movements 
                if m['id'] not in used_movements
            ]
            
            logger.info(f"Available movements after filtering: {len(available_movements)}")
            
            if not available_movements:
                logger.warning("No available movements left for quest generation")
                return None
            
            # Select quest type
            available_quest_types = [
                qt for qt in self.QUEST_TYPES 
                if qt not in used_quest_types
            ]
            
            logger.info(f"Available quest types before fallback: {available_quest_types}")
            
            if not available_quest_types:
                available_quest_types = self.QUEST_TYPES
                logger.info(f"Using fallback quest types: {available_quest_types}")
            
            quest_type = random.choice(available_quest_types)
            logger.info(f"Selected quest type: {quest_type}")
            
            # Select movement
            movement = self._select_movement_for_quest(
                available_movements, quest_type, user_data
            )
            
            if not movement:
                logger.warning("No suitable movement found for quest")
                return None
            
            logger.info(f"Selected movement: {movement['name']} (ID: {movement['id']})")
            
            # Generate quest parameters
            difficulty_config = self.DIFFICULTY_TIERS[tier_level]
            
            quest_data = {
                'quest_type': quest_type,
                'target_movement_id': movement['id'],
                'target_movement': movement['name'],
                'difficulty_level': tier_level,
                'status': 'active'
            }
            
            # Set quest-specific targets
            if quest_type == "movement_reps":
                base_reps = difficulty_config['base_reps']
                user_modifier = self._get_user_strength_modifier(user_data)
                target_reps = int(base_reps * difficulty_config['multiplier'] * user_modifier)
                quest_data['target_reps'] = max(target_reps, 10)  # Minimum 10 reps
                
            elif quest_type == "time_based":
                base_time = difficulty_config['base_time']
                user_modifier = self._get_user_endurance_modifier(user_data)
                target_time = int(base_time * difficulty_config['multiplier'] * user_modifier)
                quest_data['target_time'] = max(target_time, 15)  # Minimum 15 seconds
                
            elif quest_type == "endurance_challenge":
                # Combination of reps and time
                base_reps = difficulty_config['base_reps'] // 2
                base_time = difficulty_config['base_time'] // 2
                quest_data['target_reps'] = max(int(base_reps * difficulty_config['multiplier']), 5)
                quest_data['target_time'] = max(int(base_time * difficulty_config['multiplier']), 10)
            
            logger.info(f"Generated quest data: {quest_data}")
            return quest_data
            
        except Exception as e:
            logger.error(f"Error generating single quest: {str(e)}")
            return None

    def _select_movement_for_quest(
        self, 
        available_movements: List[Dict[str, Any]], 
        quest_type: str,
        user_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Select appropriate movement for the quest type"""
        
        # Filter movements by quest type compatibility
        if quest_type == "time_based":
            # Prefer isometric/hold movements for time-based quests
            time_movements = [
                m for m in available_movements 
                if any(keyword in m['name'].lower() for keyword in ['hold', 'plank', 'wall sit', 'hang'])
            ]
            if time_movements:
                available_movements = time_movements
        
        elif quest_type == "movement_reps":
            # Prefer dynamic movements for rep-based quests
            rep_movements = [
                m for m in available_movements 
                if not any(keyword in m['name'].lower() for keyword in ['hold', 'static'])
            ]
            if rep_movements:
                available_movements = rep_movements
        
        # Select based on user progression
        readiness_level = user_data['readiness_level']
        
        # Filter by appropriate difficulty
        suitable_movements = [
            m for m in available_movements
            if m.get('difficulty_level', 1) <= readiness_level + 1
        ]
        
        if not suitable_movements:
            suitable_movements = available_movements
        
        return random.choice(suitable_movements) if suitable_movements else None

    def _get_user_strength_modifier(self, user_data: Dict[str, Any]) -> float:
        """Calculate strength-based modifier for rep targets"""
        str_points = user_data.get('str_points', 0)
        readiness = user_data.get('readiness_level', 1)
        
        # Base modifier from strength points
        str_modifier = 1.0 + (str_points * 0.02)  # 2% per strength point
        
        # Readiness level modifier
        readiness_modifier = 1.0 + (readiness * 0.1)  # 10% per readiness level
        
        return min(str_modifier * readiness_modifier, 2.5)  # Cap at 2.5x

    def _get_user_endurance_modifier(self, user_data: Dict[str, Any]) -> float:
        """Calculate endurance-based modifier for time targets"""
        end_points = user_data.get('end_points', 0)
        readiness = user_data.get('readiness_level', 1)
        
        # Base modifier from endurance points
        end_modifier = 1.0 + (end_points * 0.02)  # 2% per endurance point
        
        # Readiness level modifier
        readiness_modifier = 1.0 + (readiness * 0.1)  # 10% per readiness level
        
        return min(end_modifier * readiness_modifier, 2.5)  # Cap at 2.5x

    def _get_quest_count_for_readiness(self, readiness_level: int) -> int:
        """Get the number of quests to generate based on readiness level"""
        return self.DEFAULT_QUEST_COUNTS.get(readiness_level, 3)

    async def get_quest_generation_config(self) -> Dict[str, Any]:
        """Get current quest generation configuration"""
        return {
            'quest_types': self.QUEST_TYPES,
            'difficulty_tiers': self.DIFFICULTY_TIERS,
            'default_quest_counts': self.DEFAULT_QUEST_COUNTS
        }

    async def update_quest_generation_config(
        self, 
        config_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update quest generation configuration (for admin use)"""
        
        if 'quest_counts' in config_updates:
            self.DEFAULT_QUEST_COUNTS.update(config_updates['quest_counts'])
        
        if 'difficulty_tiers' in config_updates:
            for tier, settings in config_updates['difficulty_tiers'].items():
                if tier in self.DIFFICULTY_TIERS:
                    self.DIFFICULTY_TIERS[tier].update(settings)
        
        logger.info("Quest generation configuration updated")
        return await self.get_quest_generation_config()