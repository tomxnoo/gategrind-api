"""
Progression service for handling user advancement and XP management.

This service manages all business logic related to user progression including:
- XP addition and distribution across global and stat-specific categories
- Level-up calculations using the formula: 100 * (current_level ^ 1.5)
- Stat point rewards upon leveling up
- Milestone progression rewards for stat achievements
- Aura calculation and updates
"""
import math
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.infrastructure.database.models.v2 import Ascendant, AscendantStats, UserSkillProgress, SkillTreeNode
from app.application.game_data.skill_tree_config import get_node_by_id
from core.config import get_settings


class ProgressionResult:
    """
    Result object for progression operations.
    
    Contains all the information about what changed during a progression update.
    """
    
    def __init__(self):
        self.user_id: Optional[int] = None
        self.xp_added: int = 0
        self.category: str = ""
        self.level_changes: Dict[str, Dict[str, int]] = {}
        self.stat_points_awarded: Dict[str, int] = {}
        self.milestone_rewards: Dict[str, List[int]] = {}  # New field for milestone achievements
        self.stat_rewards_awarded: Dict[str, int] = {}  # NEW: Direct stat rewards (Approach A)
        self.new_aura: int = 0
        self.previous_aura: int = 0
        self.aura_change_reason: str = ""  # NEW: Track why aura changed
        # New fields for skill unlocking
        self.skill_points_deducted: Optional[Dict[str, int]] = None
        self.unlock_message: Optional[str] = None
        self.node_name: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        result = {
            "user_id": self.user_id,
            "xp_added": self.xp_added,
            "category": self.category,
            "level_changes": self.level_changes,
            "stat_points_awarded": self.stat_points_awarded,
            "milestone_rewards": self.milestone_rewards,
            "stat_rewards_awarded": self.stat_rewards_awarded,  # NEW: Direct stat rewards
            "aura_update": {  # Updated to match Story 4.2 format
                "previous_aura": self.previous_aura,
                "new_aura": self.new_aura,
                "change": self.new_aura - self.previous_aura,
                "reason": self.aura_change_reason
            }
        }
        
        # Add skill unlocking fields if present
        if self.skill_points_deducted is not None:
            result["skill_points_deducted"] = self.skill_points_deducted
        if self.unlock_message is not None:
            result["unlock_message"] = self.unlock_message
        if self.node_name is not None:
            result["node_name"] = self.node_name
            
        return result


class ProgressionService(BaseService):
    """
    Service for managing user progression and advancement.
    
    This service handles:
    - XP addition across different categories (global, strength, endurance, technique)
    - Level-up calculations and stat point rewards
    - Milestone progression rewards for stat achievements
    - Aura calculation and updates
    - Transaction management for progression changes
    """
    
    # Valid XP categories
    VALID_CATEGORIES = {'global', 'strength', 'endurance', 'technique'}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = get_settings()
        self.milestone_interval = self.settings.STAT_MILESTONE_INTERVAL
    
    async def add_stat_rewards(self, user_id: int, str_reward: int = 0, end_reward: int = 0, tech_reward: int = 0) -> ProgressionResult:
        """
        Add direct stat rewards to user (Approach A).
        
        This method awards direct stat values that are displayed to users (STR: 245).
        Used when completing quests, workouts, or other activities.
        
        Args:
            user_id: User ID to award stats to
            str_reward: Direct strength points to award
            end_reward: Direct endurance points to award  
            tech_reward: Direct technique points to award
            
        Returns:
            ProgressionResult with stat changes and any level-ups/milestones
            
        Raises:
            Exception: If user not found or database error occurs
        """
        if str_reward < 0 or end_reward < 0 or tech_reward < 0:
            raise ValueError("Stat rewards must be non-negative")
            
        if str_reward == 0 and end_reward == 0 and tech_reward == 0:
            raise ValueError("At least one stat reward must be greater than 0")
        
        result = ProgressionResult()
        result.user_id = user_id
        result.stat_rewards_awarded = {
            'str_reward': str_reward,
            'end_reward': end_reward,
            'tech_reward': tech_reward
        }
        result.aura_change_reason = "Stat rewards"  # Set aura change reason
        
        try:
            # Execute all progression logic in a single transaction
            async def progression_transaction(session: AsyncSession):
                # Fetch user with stats
                user = await self._get_user_with_stats(session, user_id)
                if not user:
                    raise Exception(f"User with ID {user_id} not found")
                
                # Ensure user has stats record
                if not user.stats:
                    user.stats = AscendantStats(ascendant_id=user.id)
                    session.add(user.stats)
                
                stats = user.stats
                
                # Store original aura for comparison
                result.previous_aura = user.aura
                
                # Award direct stat values
                if str_reward > 0:
                    current_str = stats.str_value or 10
                    stats.str_value = current_str + str_reward
                    
                if end_reward > 0:
                    current_end = stats.end_value or 10
                    stats.end_value = current_end + end_reward
                    
                if tech_reward > 0:
                    current_tech = stats.tech_value or 10
                    stats.tech_value = current_tech + tech_reward
                
                # Check for stat value milestones (every 150 points awards 1 skill point)
                await self._check_stat_value_milestones(session, user, result)
                
                # Calculate and update aura
                new_aura = await self._calculate_and_update_aura(session, user)
                result.new_aura = new_aura
                
                return result
            
            return await self.execute_in_transaction(progression_transaction)
            
        except Exception as e:
            self.handle_service_error(e, f"add_stat_rewards(user_id={user_id}, str={str_reward}, end={end_reward}, tech={tech_reward})")
            raise

    async def _check_stat_value_milestones(self, session: AsyncSession, user: Ascendant, result: ProgressionResult) -> None:
        """Check if stat values have crossed milestone thresholds and award skill points."""
        if not user.stats:
            return
            
        stats = user.stats
        milestone_threshold = 150  # Every 150 stat points = 1 skill point
        
        # Check each stat for milestone crossings
        stat_configs = [
            ('str_value', 'strength_points', 'strength'),
            ('end_value', 'endurance_points', 'endurance'), 
            ('tech_value', 'technique_points', 'technique')
        ]
        
        for value_field, points_field, category in stat_configs:
            current_value = getattr(stats, value_field) or 10
            
            # Calculate how many milestones this stat has reached
            milestones_reached = current_value // milestone_threshold
            
            # Get current skill points for this stat
            current_skill_points = getattr(user, points_field) or 0
            
            # Calculate expected skill points based on milestones
            expected_skill_points = milestones_reached
            
            # Award any missing skill points
            if expected_skill_points > current_skill_points:
                points_to_award = expected_skill_points - current_skill_points
                setattr(user, points_field, current_skill_points + points_to_award)
                
                # Record in result
                if not result.stat_points_awarded:
                    result.stat_points_awarded = {}
                    
                if points_field not in result.stat_points_awarded:
                    result.stat_points_awarded[points_field] = 0
                result.stat_points_awarded[points_field] += points_to_award
                
                # Record milestone achievements
                if not result.milestone_rewards:
                    result.milestone_rewards = {}
                    
                milestones = []
                for i in range(current_skill_points + 1, expected_skill_points + 1):
                    milestone_value = i * milestone_threshold
                    milestones.append(milestone_value)
                    
                if milestones:
                    result.milestone_rewards[category] = milestones
                
                self.logger.info(f"User {user.id} {category} stat value milestones: awarded {points_to_award} skill points for reaching {current_value} stat value")

    async def add_xp(self, user_id: int, amount: int, category: str) -> ProgressionResult:
        """
        Add XP to a user in the specified category and handle all progression logic.
        
        Args:
            user_id: The user's database ID (not discord_id)
            amount: Amount of XP to add (must be positive)
            category: XP category ('global', 'strength', 'endurance', 'technique')
            
        Returns:
            ProgressionResult: Complete progression update information
            
        Raises:
            ValueError: If category is invalid or amount is not positive
            Exception: If user not found or database error occurs
        """
        # Validate inputs
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.VALID_CATEGORIES}")
        
        if amount <= 0:
            raise ValueError(f"XP amount must be positive, got: {amount}")
        
        result = ProgressionResult()
        result.user_id = user_id
        result.xp_added = amount
        result.category = category
        result.aura_change_reason = f"{category.title()} progression"  # Set aura change reason
        
        try:
            # Execute all progression logic in a single transaction
            async def progression_transaction(session: AsyncSession):
                # Fetch user with stats
                user = await self._get_user_with_stats(session, user_id)
                if not user:
                    raise Exception(f"User with ID {user_id} not found")
                
                # Store original aura for comparison
                result.previous_aura = user.aura
                
                # Add XP and check for level-ups
                await self._add_xp_to_category(session, user, amount, category, result)
                
                # Calculate and update aura
                new_aura = await self._calculate_and_update_aura(session, user)
                result.new_aura = new_aura
                
                return result
            
            return await self.execute_in_transaction(progression_transaction)
            
        except Exception as e:
            self.handle_service_error(e, f"add_xp(user_id={user_id}, amount={amount}, category={category})")
            raise
    
    async def _get_user_with_stats(self, session: AsyncSession, user_id: int) -> Optional[Ascendant]:
        """Fetch user with their stats relationship loaded."""
        stmt = (
            select(Ascendant)
            .options(selectinload(Ascendant.stats))
            .where(Ascendant.id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _add_xp_to_category(self, session: AsyncSession, user: Ascendant, amount: int, 
                                category: str, result: ProgressionResult) -> None:
        """Add XP to the specified category and handle level-ups."""
        if category == 'global':
            await self._add_global_xp(session, user, amount, result)
        else:
            await self._add_stat_xp(session, user, amount, category, result)
    
    async def _add_global_xp(self, session: AsyncSession, user: Ascendant, amount: int, 
                           result: ProgressionResult) -> None:
        """Add XP to global progression and handle main level-ups."""
        # Add XP to global total (handle None values)
        current_xp = user.global_xp or 0
        new_global_xp = current_xp + amount
        
        # Check for level-ups
        current_level = user.level or 1
        new_level = self._calculate_level_from_xp(new_global_xp)
        
        if new_level > current_level:
            levels_gained = new_level - current_level
            
            # Award stat points for each level gained
            stat_points_per_level = 1
            total_points_awarded = levels_gained * stat_points_per_level
            
            # Update user data
            user.level = new_level
            user.global_xp = new_global_xp
            user.strength_points += total_points_awarded
            user.endurance_points += total_points_awarded
            user.technique_points += total_points_awarded
            
            # Record changes in result
            result.level_changes['global'] = {
                'previous': current_level,
                'new': new_level,
                'gained': levels_gained
            }
            result.stat_points_awarded = {
                'strength_points': total_points_awarded,
                'endurance_points': total_points_awarded,
                'technique_points': total_points_awarded
            }
            
            self.logger.info(f"User {user.id} leveled up from {current_level} to {new_level}, "
                           f"awarded {total_points_awarded} points to each stat")
        else:
            # Just update XP
            user.global_xp = new_global_xp
    
    async def _add_stat_xp(self, session: AsyncSession, user: Ascendant, amount: int, 
                         category: str, result: ProgressionResult) -> None:
        """Add XP to a specific stat category and handle stat level-ups."""
        # Ensure user has stats record
        if not user.stats:
            # Create stats record if it doesn't exist
            user.stats = AscendantStats(ascendant_id=user.id)
            session.add(user.stats)
        
        stats = user.stats
        
        # Map stat categories to their corresponding fields
        stat_mapping = {
            'strength': {
                'xp_field': 'str_xp',
                'level_field': 'str_level',
                'points_field': 'strength_points',
                'value_field': 'str_value'  # NEW: Direct stat value field
            },
            'endurance': {
                'xp_field': 'end_xp',
                'level_field': 'end_level',
                'points_field': 'endurance_points',
                'value_field': 'end_value'  # NEW: Direct stat value field
            },
            'technique': {
                'xp_field': 'tech_xp',
                'level_field': 'tech_level',
                'points_field': 'technique_points',
                'value_field': 'tech_value'  # NEW: Direct stat value field
            }
        }
        
        mapping = stat_mapping[category]
        xp_field = mapping['xp_field']
        level_field = mapping['level_field']
        points_field = mapping['points_field']
        value_field = mapping['value_field']  # NEW: Direct stat value field
        
        # Get current values (handle None values)
        current_level = getattr(stats, level_field) or 1
        current_xp = getattr(stats, xp_field) or 0
        
        # Check for milestone achievements before adding XP
        milestones_achieved = self._check_stat_milestones(current_xp, current_xp + amount)
        
        # Add XP
        new_xp = current_xp + amount
        
        # Check for level-ups
        current_level = getattr(stats, level_field) or 1
        new_level = self._calculate_level_from_xp(new_xp)
        
        if new_level > current_level:
            levels_gained = new_level - current_level
            
            # Update stat values
            setattr(stats, level_field, new_level)
            setattr(stats, xp_field, new_xp)
            
            # Award stat points for level-ups
            current_points = getattr(user, points_field) or 0
            setattr(user, points_field, current_points + levels_gained)
            
            # Record stat points awarded for level-ups
            if not result.stat_points_awarded:
                result.stat_points_awarded = {}
            
            if points_field not in result.stat_points_awarded:
                result.stat_points_awarded[points_field] = 0
            result.stat_points_awarded[points_field] += levels_gained
            
            # Record changes in result
            result.level_changes[category] = {
                'previous': current_level,
                'new': new_level,
                'gained': levels_gained
            }
            
            self.logger.info(f"User {user.id} {category} stat leveled up from {current_level} to {new_level}, awarded {levels_gained} stat points")
        else:
            # Just update XP
            setattr(stats, xp_field, new_xp)
        
        # Process milestone rewards
        if milestones_achieved:
            # Award stat points for milestones to the user model
            milestone_points = len(milestones_achieved)
            
            current_points = getattr(user, points_field) or 0
            setattr(user, points_field, current_points + milestone_points)
            
            # Record milestone achievements in result
            result.milestone_rewards[category] = milestones_achieved
            
            # Update stat_points_awarded to include milestone rewards
            if not result.stat_points_awarded:
                result.stat_points_awarded = {}
            
            # Add milestone points to the appropriate stat category
            if points_field not in result.stat_points_awarded:
                result.stat_points_awarded[points_field] = 0
            result.stat_points_awarded[points_field] += milestone_points
            
            self.logger.info(f"User {user.id} achieved {len(milestones_achieved)} {category} milestones: {milestones_achieved}, awarded {milestone_points} stat points")
    
    def _check_stat_milestones(self, old_xp: int, new_xp: int) -> List[int]:
        """
        Check for milestone achievements between old and new XP values.
        
        Args:
            old_xp: Previous XP amount
            new_xp: New XP amount after addition
            
        Returns:
            List[int]: List of milestone thresholds that were crossed
        """
        milestones_achieved = []
        
        # Calculate the first milestone after old_xp
        first_milestone = ((old_xp // self.milestone_interval) + 1) * self.milestone_interval
        
        # Find all milestones between old_xp and new_xp
        current_milestone = first_milestone
        while current_milestone <= new_xp:
            milestones_achieved.append(current_milestone)
            current_milestone += self.milestone_interval
        
        return milestones_achieved
    
    def _calculate_level_from_xp(self, total_xp: float) -> int:
        """
        Calculate level based on total XP using the formula: 100 * (level ^ 1.5).
        
        This function finds the highest level where the required XP is <= total_xp.
        
        Args:
            total_xp: Total experience points
            
        Returns:
            int: The level corresponding to the XP amount
        """
        if total_xp < 0:
            return 1
        
        # Start from level 1 and find the highest achievable level
        level = 1
        while True:
            required_xp = self._calculate_xp_for_level(level + 1)
            if total_xp < required_xp:
                break
            level += 1
            
            # Safety check to prevent infinite loops
            if level > 1000:  # Reasonable max level
                break
        
        return level
    
    def _calculate_xp_for_level(self, level: int) -> float:
        """
        Calculate the total XP required to reach a specific level.
        
        Uses the formula: 100 * (level ^ 1.5) for each level and sums them up.
        
        Args:
            level: Target level
            
        Returns:
            float: Total XP required to reach that level
        """
        if level <= 1:
            return 0
        
        total_xp = 0
        for l in range(2, level + 1):
            total_xp += 100 * (l ** 1.5)
        
        return total_xp
    
    async def _calculate_and_update_aura(self, session: AsyncSession, user: Ascendant) -> int:
        """
        Calculate and update the user's Aura score.
        
        Aura calculation formula (Story 4.1):
        (Level * 100) + (STR*10 + END*10 + TECH*5) + (Nodes Unlocked * 25)
        
        Args:
            session: Database session
            user: User object with stats loaded
            
        Returns:
            int: New aura value
        """
        # Base aura from main level: Level * 100
        base_aura = (user.level or 1) * 100
        
        # Stat bonus: STR*10 + END*10 + TECH*5
        stat_bonus = 0
        if user.stats:
            stat_bonus = (
                (user.stats.str_level or 1) * 10 +  # STR * 10
                (user.stats.end_level or 1) * 10 +  # END * 10
                (user.stats.tech_level or 1) * 5    # TECH * 5
            )
        else:
            # Default stat levels are 1 if no stats record exists
            stat_bonus = 1 * 10 + 1 * 10 + 1 * 5  # 25
        
        # Skill bonus from unlocked skill tree nodes: Nodes Unlocked * 25
        skill_bonus = await self._calculate_skill_bonus(session, user.id)
        
        # Calculate total aura using the exact formula from Story 4.1
        new_aura = base_aura + stat_bonus + skill_bonus
        
        # Update user's aura
        user.aura = new_aura
        
        self.logger.info(f"Updated aura for user {user.id}: base={base_aura}, "
                        f"stat={stat_bonus}, skill={skill_bonus}, total={new_aura}")
        
        return new_aura
    
    async def _calculate_skill_bonus(self, session: AsyncSession, user_id: int) -> int:
        """Calculate aura bonus from unlocked skills: Nodes Unlocked * 25."""
        try:
            # Count unlocked skill tree nodes
            stmt = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == user_id)
            result = await session.execute(stmt)
            unlocked_skills = result.scalars().all()
            
            # Story 4.1 formula: Nodes Unlocked * 25
            return len(unlocked_skills) * 25
            
        except Exception as e:
            self.logger.warning(f"Error calculating skill bonus for user {user_id}: {e}")
            return 0
    
    async def calculate_level_progress(self, user_id: int, category: str = 'global') -> Dict[str, Any]:
        """
        Calculate level progress information for a user in a specific category.
        
        Args:
            user_id: User's database ID
            category: Category to check ('global', 'strength', 'endurance', 'technique')
            
        Returns:
            Dict containing current level, XP, next level XP requirement, and progress percentage
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.VALID_CATEGORIES}")
        
        try:
            session = await self.get_session()
            user = await self._get_user_with_stats(session, user_id)
            
            if not user:
                raise Exception(f"User with ID {user_id} not found")
            
            if category == 'global':
                current_level = user.level or 1
                current_xp = user.global_xp or 0
            else:
                if not user.stats:
                    # Return default values if no stats exist
                    return {
                        'current_level': 1,
                        'current_xp': 0,
                        'next_level_xp_required': 100 * (2 ** 1.5),
                        'progress_percentage': 0.0,
                        'xp_to_next_level': 100 * (2 ** 1.5)
                    }
                
                stat_mapping = {
                    'strength': ('str_level', 'str_xp'),
                    'endurance': ('end_level', 'end_xp'),
                    'technique': ('tech_level', 'tech_xp')
                }
                
                level_field, xp_field = stat_mapping[category]
                current_level = getattr(user.stats, level_field) or 1
                current_xp = getattr(user.stats, xp_field) or 0
            
            # Calculate next level requirements
            next_level_total_xp = self._calculate_xp_for_level(current_level + 1)
            current_level_total_xp = self._calculate_xp_for_level(current_level)
            xp_needed_for_next = next_level_total_xp - current_level_total_xp
            xp_progress_in_level = current_xp - current_level_total_xp
            
            progress_percentage = (xp_progress_in_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 100
            xp_to_next_level = max(0, xp_needed_for_next - xp_progress_in_level)
            
            return {
                'current_level': current_level,
                'current_xp': current_xp,
                'next_level_xp_required': xp_needed_for_next,
                'progress_percentage': round(progress_percentage, 2),
                'xp_to_next_level': round(xp_to_next_level, 2)
            }
            
        except Exception as e:
            self.handle_service_error(e, f"calculate_level_progress(user_id={user_id}, category={category})")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the ProgressionService.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            session = await self.get_session()
            
            # Test basic database connectivity by counting users
            stmt = select(Ascendant)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            return {
                "service": "ProgressionService",
                "status": "healthy",
                "database_connection": "ok",
                "users_count": len(users),
                "timestamp": None  # Will be set by the API layer
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "service": "ProgressionService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": None
            }

    async def unlock_skill(self, user_id: int, node_id: str) -> ProgressionResult:
        """
        Unlock a skill tree node for a user.
        
        This method:
        1. Validates the node exists and user meets requirements
        2. Deducts the required skill points
        3. Creates the UserSkillProgress record
        4. Updates user's aura
        
        Args:
            user_id: User's database ID
            node_id: ID of the skill tree node to unlock
            
        Returns:
            ProgressionResult with unlock information
            
        Raises:
            ValueError: If node doesn't exist or requirements not met
            Exception: If user not found or database error occurs
        """
        # Get node configuration
        node_config = get_node_by_id(node_id)
        if not node_config:
            raise ValueError(f"Skill tree node '{node_id}' not found")
        
        result = ProgressionResult()
        result.user_id = user_id
        result.category = "skill_unlock"
        result.aura_change_reason = "Skill tree progression"  # Set aura change reason
        
        try:
            async def unlock_transaction(session: AsyncSession):
                # Fetch user with stats and skill progress
                user = await self._get_user_with_skill_progress(session, user_id)
                if not user:
                    raise Exception(f"User with ID {user_id} not found")
                
                # Check if already unlocked
                existing_progress = await self._check_existing_skill_progress(session, user_id, node_id)
                if existing_progress:
                    raise ValueError(f"Skill tree node '{node_id}' is already unlocked")
                
                # Validate requirements
                await self._validate_skill_requirements(session, user, node_config)
                
                # Store original aura for comparison
                result.previous_aura = user.aura
                
                # Deduct skill points
                self._deduct_skill_points(user, node_config, result)
                
                # Create skill progress record
                await self._create_skill_progress(session, user_id, node_id)
                
                # Calculate and update aura
                new_aura = await self._calculate_and_update_aura(session, user)
                result.new_aura = new_aura
                
                # Set success message
                result.unlock_message = node_config.unlock_message
                result.node_name = node_config.name
                
                return result
            
            return await self.execute_in_transaction(unlock_transaction)
            
        except Exception as e:
            self.handle_service_error(e, f"unlock_skill(user_id={user_id}, node_id={node_id})")
            raise

    async def _get_user_with_skill_progress(self, session: AsyncSession, user_id: int) -> Optional[Ascendant]:
        """Fetch user with their stats and skill progress relationships loaded."""
        stmt = (
            select(Ascendant)
            .options(
                selectinload(Ascendant.stats),
                selectinload(Ascendant.skill_progress)
            )
            .where(Ascendant.id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _check_existing_skill_progress(self, session: AsyncSession, user_id: int, node_id: str) -> Optional[UserSkillProgress]:
        """Check if user has already unlocked this skill node."""
        # First get the SkillTreeNode database record
        node_stmt = select(SkillTreeNode).where(SkillTreeNode.node_id == node_id)
        node_result = await session.execute(node_stmt)
        node_record = node_result.scalar_one_or_none()
        
        if not node_record:
            return None
            
        # Check for existing progress
        progress_stmt = (
            select(UserSkillProgress)
            .where(
                UserSkillProgress.ascendant_id == user_id,
                UserSkillProgress.node_id == node_record.id
            )
        )
        progress_result = await session.execute(progress_stmt)
        return progress_result.scalar_one_or_none()

    async def _validate_skill_requirements(self, session: AsyncSession, user: Ascendant, node_config) -> None:
        """Validate that user meets all requirements for unlocking the skill node."""
        requirements = node_config.requirements
        
        # Check ascendant level requirement
        if user.level < requirements.min_ascendant_level:
            raise ValueError(
                f"Ascendant level {requirements.min_ascendant_level} required, "
                f"current level: {user.level}"
            )
        
        # Check stat requirements (these are checked but not deducted)
        if user.stats:
            current_str = user.stats.str_value or 10
            current_end = user.stats.end_value or 10
            current_tech = user.stats.tech_value or 10
            
            if current_str < requirements.str_points:
                raise ValueError(
                    f"Strength stat {requirements.str_points} required, "
                    f"current: {current_str}"
                )
            if current_end < requirements.end_points:
                raise ValueError(
                    f"Endurance stat {requirements.end_points} required, "
                    f"current: {current_end}"
                )
            if current_tech < requirements.tech_points:
                raise ValueError(
                    f"Technique stat {requirements.tech_points} required, "
                    f"current: {current_tech}"
                )
        else:
            # No stats record means default values (10 each)
            if requirements.str_points > 10 or requirements.end_points > 10 or requirements.tech_points > 10:
                raise ValueError("Insufficient stat values to unlock this skill")
        
        # Check skill point requirements (these will be deducted)
        if user.strength_points < requirements.strength_skill_points:
            raise ValueError(
                f"Strength skill points {requirements.strength_skill_points} required, "
                f"available: {user.strength_points}"
            )
        if user.endurance_points < requirements.endurance_skill_points:
            raise ValueError(
                f"Endurance skill points {requirements.endurance_skill_points} required, "
                f"available: {user.endurance_points}"
            )
        if user.technique_points < requirements.technique_skill_points:
            raise ValueError(
                f"Technique skill points {requirements.technique_skill_points} required, "
                f"available: {user.technique_points}"
            )
        
        # Check prerequisite nodes
        if requirements.prerequisite_nodes:
            await self._validate_prerequisite_nodes(session, user.id, requirements.prerequisite_nodes)

    async def _validate_prerequisite_nodes(self, session: AsyncSession, user_id: int, prerequisite_node_ids: List[str]) -> None:
        """Validate that all prerequisite nodes are unlocked."""
        for prereq_node_id in prerequisite_node_ids:
            # Get the database record for the prerequisite node
            node_stmt = select(SkillTreeNode).where(SkillTreeNode.node_id == prereq_node_id)
            node_result = await session.execute(node_stmt)
            node_record = node_result.scalar_one_or_none()
            
            if not node_record:
                raise ValueError(f"Prerequisite node '{prereq_node_id}' not found in database")
            
            # Check if user has unlocked this prerequisite
            progress_stmt = (
                select(UserSkillProgress)
                .where(
                    UserSkillProgress.ascendant_id == user_id,
                    UserSkillProgress.node_id == node_record.id
                )
            )
            progress_result = await session.execute(progress_stmt)
            progress_record = progress_result.scalar_one_or_none()
            
            if not progress_record:
                raise ValueError(f"Prerequisite skill '{prereq_node_id}' must be unlocked first")

    def _deduct_skill_points(self, user: Ascendant, node_config, result: ProgressionResult) -> None:
        """Deduct the required skill points from the user."""
        requirements = node_config.requirements
        
        # Deduct skill points
        user.strength_points -= requirements.strength_skill_points
        user.endurance_points -= requirements.endurance_skill_points
        user.technique_points -= requirements.technique_skill_points
        
        # Record the deductions in the result
        result.skill_points_deducted = {
            'strength_skill_points': requirements.strength_skill_points,
            'endurance_skill_points': requirements.endurance_skill_points,
            'technique_skill_points': requirements.technique_skill_points,
            'total': (requirements.strength_skill_points + 
                     requirements.endurance_skill_points + 
                     requirements.technique_skill_points)
        }

    async def _create_skill_progress(self, session: AsyncSession, user_id: int, node_id: str) -> None:
        """Create a UserSkillProgress record for the unlocked skill."""
        # Get the SkillTreeNode database record
        node_stmt = select(SkillTreeNode).where(SkillTreeNode.node_id == node_id)
        node_result = await session.execute(node_stmt)
        node_record = node_result.scalar_one_or_none()
        
        if not node_record:
            raise ValueError(f"Skill tree node '{node_id}' not found in database")
        
        # Create the progress record
        skill_progress = UserSkillProgress(
            ascendant_id=user_id,
            node_id=node_record.id
        )
        session.add(skill_progress)

    def _check_stat_milestones(self, old_xp: int, new_xp: int) -> List[int]:
        """
        Check for milestone achievements between old and new XP values.
        
        Args:
            old_xp: Previous XP amount
            new_xp: New XP amount after addition
            
        Returns:
            List[int]: List of milestone thresholds that were crossed
        """
        milestones_achieved = []
        
        # Calculate the first milestone after old_xp
        first_milestone = ((old_xp // self.milestone_interval) + 1) * self.milestone_interval
        
        # Find all milestones between old_xp and new_xp
        current_milestone = first_milestone
        while current_milestone <= new_xp:
            milestones_achieved.append(current_milestone)
            current_milestone += self.milestone_interval
        
        return milestones_achieved
    
    def _calculate_level_from_xp(self, total_xp: float) -> int:
        """
        Calculate level based on total XP using the formula: 100 * (level ^ 1.5).
        
        This function finds the highest level where the required XP is <= total_xp.
        
        Args:
            total_xp: Total experience points
            
        Returns:
            int: The level corresponding to the XP amount
        """
        if total_xp < 0:
            return 1
        
        # Start from level 1 and find the highest achievable level
        level = 1
        while True:
            required_xp = self._calculate_xp_for_level(level + 1)
            if total_xp < required_xp:
                break
            level += 1
            
            # Safety check to prevent infinite loops
            if level > 1000:  # Reasonable max level
                break
        
        return level
    
    def _calculate_xp_for_level(self, level: int) -> float:
        """
        Calculate the total XP required to reach a specific level.
        
        Uses the formula: 100 * (level ^ 1.5) for each level and sums them up.
        
        Args:
            level: Target level
            
        Returns:
            float: Total XP required to reach that level
        """
        if level <= 1:
            return 0
        
        total_xp = 0
        for l in range(2, level + 1):
            total_xp += 100 * (l ** 1.5)
        
        return total_xp
    
    async def _calculate_skill_bonus(self, session: AsyncSession, user_id: int) -> int:
        """Calculate aura bonus from unlocked skills: Nodes Unlocked * 25."""
        try:
            # Count unlocked skill tree nodes
            stmt = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == user_id)
            result = await session.execute(stmt)
            unlocked_skills = result.scalars().all()
            
            return len(unlocked_skills) * 25
            
        except Exception as e:
            self.logger.warning(f"Error calculating skill bonus for user {user_id}: {e}")
            return 0
    
    async def calculate_level_progress(self, user_id: int, category: str = 'global') -> Dict[str, Any]:
        """
        Calculate level progress information for a user in a specific category.
        
        Args:
            user_id: User's database ID
            category: Category to check ('global', 'strength', 'endurance', 'technique')
            
        Returns:
            Dict containing current level, XP, next level XP requirement, and progress percentage
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.VALID_CATEGORIES}")
        
        try:
            session = await self.get_session()
            user = await self._get_user_with_stats(session, user_id)
            
            if not user:
                raise Exception(f"User with ID {user_id} not found")
            
            if category == 'global':
                current_level = user.level or 1
                current_xp = user.global_xp or 0
            else:
                if not user.stats:
                    # Return default values if no stats exist
                    return {
                        'current_level': 1,
                        'current_xp': 0,
                        'next_level_xp_required': 100 * (2 ** 1.5),
                        'progress_percentage': 0.0,
                        'xp_to_next_level': 100 * (2 ** 1.5)
                    }
                
                stat_mapping = {
                    'strength': ('str_level', 'str_xp'),
                    'endurance': ('end_level', 'end_xp'),
                    'technique': ('tech_level', 'tech_xp')
                }
                
                level_field, xp_field = stat_mapping[category]
                current_level = getattr(user.stats, level_field) or 1
                current_xp = getattr(user.stats, xp_field) or 0
            
            # Calculate next level requirements
            next_level_total_xp = self._calculate_xp_for_level(current_level + 1)
            current_level_total_xp = self._calculate_xp_for_level(current_level)
            xp_needed_for_next = next_level_total_xp - current_level_total_xp
            xp_progress_in_level = current_xp - current_level_total_xp
            
            progress_percentage = (xp_progress_in_level / xp_needed_for_next) * 100 if xp_needed_for_next > 0 else 100
            xp_to_next_level = max(0, xp_needed_for_next - xp_progress_in_level)
            
            return {
                'current_level': current_level,
                'current_xp': current_xp,
                'next_level_xp_required': xp_needed_for_next,
                'progress_percentage': round(progress_percentage, 2),
                'xp_to_next_level': round(xp_to_next_level, 2)
            }
            
        except Exception as e:
            self.handle_service_error(e, f"calculate_level_progress(user_id={user_id}, category={category})")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the ProgressionService.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            session = await self.get_session()
            
            # Test basic database connectivity by counting users
            stmt = select(Ascendant)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            return {
                "service": "ProgressionService",
                "status": "healthy",
                "database_connection": "ok",
                "users_count": len(users),
                "timestamp": None  # Will be set by the API layer
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "service": "ProgressionService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": None
            }