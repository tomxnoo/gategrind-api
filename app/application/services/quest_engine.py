"""
Quest Generation Engine
Unified quest generation system that integrates with the exercise library
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import random
from datetime import datetime, date
import asyncio

from ..game_data.exercise_library import (
    EXERCISE_LIBRARY, MovementCategory, QuestTier, CoreStat,
    get_exercise_by_difficulty, get_user_appropriate_exercise,
    calculate_quest_reps, calculate_quest_duration, get_stat_rewards,
    get_vtaper_movement_weights, get_quest_layout_template,
    get_tier_probabilities, ExerciseProgression, MovementPath
)


class ReadinessLevel(Enum):
    """User readiness levels for autoregulation"""
    LOW = "low"
    STANDARD = "standard" 
    HIGH = "high"


class QuestType(Enum):
    """Types of quests that can be generated"""
    AWAKENING = "awakening"
    DAILY = "daily"
    WEEKLY = "weekly"
    CHALLENGE = "challenge"
    RECOVERY = "recovery"


@dataclass
class QuestParameters:
    """Parameters for quest generation"""
    user_level: int
    readiness_level: ReadinessLevel
    quest_type: QuestType
    preferred_stats: List[CoreStat] = field(default_factory=list)
    excluded_categories: List[MovementCategory] = field(default_factory=list)
    time_constraint_minutes: Optional[int] = None
    intensity_modifier: float = 1.0
    focus_category: Optional[MovementCategory] = None


@dataclass
class GeneratedQuest:
    """A generated quest with all necessary data"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    movement_name: str = ""
    movement_category: MovementCategory = MovementCategory.PULL
    exercise_progression: ExerciseProgression = None
    target_reps: int = 0
    target_sets: int = 1
    rest_seconds: int = 60
    xp_reward: int = 0
    stat_rewards: Dict[str, int] = field(default_factory=dict)
    tier: QuestTier = QuestTier.PRACTICE
    difficulty_level: int = 1
    estimated_duration_minutes: int = 5
    quest_flavor: str = ""
    special_modifiers: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QuestSession:
    """A collection of quests for a session (awakening, daily, etc.)"""
    session_id: Optional[int] = None
    user_id: int = 0
    quest_type: QuestType = QuestType.AWAKENING
    readiness_level: ReadinessLevel = ReadinessLevel.STANDARD
    quests: List[GeneratedQuest] = field(default_factory=list)
    total_estimated_duration: int = 0
    total_xp_potential: int = 0
    session_theme: str = ""
    session_description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


class QuestGenerationEngine:
    """
    Advanced quest generation engine that creates personalized quests
    based on user data, readiness levels, and V-taper training principles
    """
    
    def __init__(self):
        self.exercise_library = EXERCISE_LIBRARY
        self.random = random.Random()
        
    def generate_awakening_session(
        self,
        user_id: int,
        user_level: int,
        readiness_level: ReadinessLevel,
        user_preferences: Optional[Dict] = None
    ) -> QuestSession:
        """Generate a complete awakening session"""
        
        # Determine quest count based on readiness and level
        quest_count = self._calculate_awakening_quest_count(user_level, readiness_level)
        
        # Create quest parameters
        params = QuestParameters(
            user_level=user_level,
            readiness_level=readiness_level,
            quest_type=QuestType.AWAKENING,
            time_constraint_minutes=self._get_awakening_time_limit(readiness_level),
            intensity_modifier=self._get_readiness_intensity_modifier(readiness_level)
        )
        
        # Apply user preferences
        if user_preferences:
            params = self._apply_user_preferences(params, user_preferences)
        
        # Generate individual quests
        quests = []
        movement_weights = get_vtaper_movement_weights()
        used_categories = set()
        
        for i in range(quest_count):
            # Select movement category with V-taper weighting
            available_categories = [
                cat for cat in MovementCategory 
                if cat not in used_categories or len(used_categories) >= len(MovementCategory) // 2
            ]
            
            category = self._weighted_category_selection(available_categories, movement_weights)
            used_categories.add(category)
            
            # Generate quest for this category
            quest = self._generate_single_quest(category, params, i)
            if quest:
                quests.append(quest)
        
        # Create session
        session = QuestSession(
            user_id=user_id,
            quest_type=QuestType.AWAKENING,
            readiness_level=readiness_level,
            quests=quests,
            total_estimated_duration=sum(q.estimated_duration_minutes for q in quests),
            total_xp_potential=sum(q.xp_reward for q in quests),
            session_theme=self._generate_session_theme(readiness_level, quests),
            session_description=self._generate_session_description(readiness_level, quest_count)
        )
        
        return session
    
    def generate_daily_quest(
        self,
        user_id: int,
        user_level: int,
        preferred_category: Optional[MovementCategory] = None
    ) -> GeneratedQuest:
        """Generate a single daily quest"""
        
        params = QuestParameters(
            user_level=user_level,
            readiness_level=ReadinessLevel.STANDARD,
            quest_type=QuestType.DAILY,
            focus_category=preferred_category
        )
        
        # Select category
        if preferred_category:
            category = preferred_category
        else:
            weights = get_vtaper_movement_weights()
            category = self._weighted_category_selection(list(MovementCategory), weights)
        
        return self._generate_single_quest(category, params, 0)
    
    def generate_weekly_challenge(
        self,
        user_id: int,
        user_level: int,
        challenge_theme: Optional[str] = None
    ) -> QuestSession:
        """Generate a weekly challenge session"""
        
        params = QuestParameters(
            user_level=user_level,
            readiness_level=ReadinessLevel.HIGH,
            quest_type=QuestType.WEEKLY,
            intensity_modifier=1.5
        )
        
        # Generate 3-5 challenging quests
        quest_count = min(5, max(3, user_level // 5 + 2))
        quests = []
        
        for i in range(quest_count):
            category = list(MovementCategory)[i % len(MovementCategory)]
            quest = self._generate_single_quest(category, params, i)
            if quest:
                quest.xp_reward = int(quest.xp_reward * 1.5)  # Bonus XP for weekly
                quests.append(quest)
        
        session = QuestSession(
            user_id=user_id,
            quest_type=QuestType.WEEKLY,
            readiness_level=ReadinessLevel.HIGH,
            quests=quests,
            total_estimated_duration=sum(q.estimated_duration_minutes for q in quests),
            total_xp_potential=sum(q.xp_reward for q in quests),
            session_theme="Weekly Shadow Challenge",
            session_description="Push your limits with this week's ultimate test"
        )
        
        return session
    
    def _generate_single_quest(
        self,
        category: MovementCategory,
        params: QuestParameters,
        quest_index: int
    ) -> Optional[GeneratedQuest]:
        """Generate a single quest for the given category and parameters"""
        
        # Get appropriate exercise
        exercise = get_user_appropriate_exercise(
            category, 
            params.user_level
        )
        
        if not exercise:
            return None
        
        # Get the movement path for additional data
        movement_path = EXERCISE_LIBRARY[category]
        
        # Determine quest tier based on readiness level
        tier_probabilities = get_tier_probabilities(
            3 if params.readiness_level == ReadinessLevel.STANDARD 
            else 2 if params.readiness_level == ReadinessLevel.LOW 
            else 4
        )
        tier = self.random.choices(
            list(tier_probabilities.keys()), 
            weights=list(tier_probabilities.values())
        )[0]
        
        # Calculate quest parameters
        base_reps = calculate_quest_reps(exercise, params.user_level, tier)
        
        # Apply intensity modifier
        target_reps = max(1, int(base_reps * params.intensity_modifier))
        
        # Determine sets based on quest type and tier
        target_sets = self._calculate_sets(params.quest_type, tier, target_reps)
        
        # Calculate duration and XP
        duration = calculate_quest_duration(exercise, params.user_level, tier)
        if params.time_constraint_minutes:
            duration = min(duration, params.time_constraint_minutes // len(params.preferred_stats) if params.preferred_stats else params.time_constraint_minutes)
        
        stat_rewards = get_stat_rewards(category, tier)
        xp_reward = stat_rewards.get_total_reward() * 10  # Convert to XP scale
        
        # Apply readiness modifiers
        xp_reward = int(xp_reward * self._get_readiness_xp_modifier(params.readiness_level))
        
        # Generate quest flavor
        quest_flavor = self._select_quest_flavor(movement_path, params.readiness_level, tier)
        
        # Create quest
        quest = GeneratedQuest(
            title=self._generate_quest_title(movement_path, params.readiness_level),
            description=self._generate_quest_description(exercise, target_reps, target_sets, quest_flavor),
            movement_name=exercise.name,
            movement_category=category,
            exercise_progression=exercise,
            target_reps=target_reps,
            target_sets=target_sets,
            rest_seconds=self._calculate_rest_time(tier, params.readiness_level),
            xp_reward=xp_reward,
            stat_rewards={
                "strength": stat_rewards.str_reward,
                "endurance": stat_rewards.end_reward,
                "technique": stat_rewards.tech_reward
            },
            tier=tier,
            difficulty_level=exercise.difficulty_level,
            estimated_duration_minutes=duration,
            quest_flavor=quest_flavor,
            special_modifiers=self._generate_special_modifiers(params, quest_index)
        )
        
        return quest
    
    def _calculate_awakening_quest_count(self, user_level: int, readiness: ReadinessLevel) -> int:
        """Calculate number of quests for awakening based on level and readiness"""
        base_count = min(6, max(2, user_level // 3 + 1))
        
        readiness_modifiers = {
            ReadinessLevel.LOW: 0.7,
            ReadinessLevel.STANDARD: 1.0,
            ReadinessLevel.HIGH: 1.3
        }
        
        return max(1, int(base_count * readiness_modifiers[readiness]))
    
    def _get_awakening_time_limit(self, readiness: ReadinessLevel) -> int:
        """Get time limit for awakening session in minutes"""
        time_limits = {
            ReadinessLevel.LOW: 15,
            ReadinessLevel.STANDARD: 25,
            ReadinessLevel.HIGH: 35
        }
        return time_limits[readiness]
    
    def _get_readiness_intensity_modifier(self, readiness: ReadinessLevel) -> float:
        """Get intensity modifier based on readiness"""
        modifiers = {
            ReadinessLevel.LOW: 0.7,
            ReadinessLevel.STANDARD: 1.0,
            ReadinessLevel.HIGH: 1.3
        }
        return modifiers[readiness]
    
    def _get_readiness_xp_modifier(self, readiness: ReadinessLevel) -> float:
        """Get XP modifier based on readiness"""
        modifiers = {
            ReadinessLevel.LOW: 0.8,
            ReadinessLevel.STANDARD: 1.0,
            ReadinessLevel.HIGH: 1.2
        }
        return modifiers[readiness]
    
    def _weighted_category_selection(
        self, 
        categories: List[MovementCategory], 
        weights: Dict[MovementCategory, float]
    ) -> MovementCategory:
        """Select a movement category using weighted random selection"""
        
        category_weights = [weights.get(cat, 1.0) for cat in categories]
        return self.random.choices(categories, weights=category_weights)[0]
    
    def _calculate_sets(self, quest_type: QuestType, tier: QuestTier, reps: int) -> int:
        """Calculate number of sets based on quest type and parameters"""
        
        base_sets = {
            QuestType.AWAKENING: 2,
            QuestType.DAILY: 3,
            QuestType.WEEKLY: 4,
            QuestType.CHALLENGE: 5,
            QuestType.RECOVERY: 1
        }
        
        tier_modifiers = {
            QuestTier.PRACTICE: 1.0,
            QuestTier.TRIAL: 1.2,
            QuestTier.CHALLENGE: 1.5
        }
        
        sets = base_sets.get(quest_type, 2)
        sets = int(sets * tier_modifiers.get(tier, 1.0))
        
        # Adjust for very high rep counts
        if reps > 20:
            sets = max(1, sets - 1)
        
        return max(1, sets)
    
    def _calculate_rest_time(self, tier: QuestTier, readiness: ReadinessLevel) -> int:
        """Calculate rest time between sets"""
        
        base_rest = {
            QuestTier.PRACTICE: 45,
            QuestTier.TRIAL: 60,
            QuestTier.CHALLENGE: 90
        }
        
        readiness_modifiers = {
            ReadinessLevel.LOW: 1.3,
            ReadinessLevel.STANDARD: 1.0,
            ReadinessLevel.HIGH: 0.8
        }
        
        rest = base_rest.get(tier, 60)
        return int(rest * readiness_modifiers[readiness])
    
    def _select_quest_flavor(self, movement_path: MovementPath, readiness: ReadinessLevel, tier: QuestTier) -> str:
        """Select appropriate quest flavor text"""
        
        flavors = movement_path.quest_flavors.get(tier, [])
        
        if not flavors:
            return "Execute with precision and purpose."
        
        return self.random.choice(flavors)
    
    def _generate_quest_title(self, movement_path: MovementPath, readiness: ReadinessLevel) -> str:
        """Generate a thematic quest title"""
        
        readiness_prefixes = {
            ReadinessLevel.LOW: ["Recovery", "Gentle", "Mindful"],
            ReadinessLevel.STANDARD: ["Shadow", "Warrior's", "Focused"],
            ReadinessLevel.HIGH: ["Ascendant", "Elite", "Ultimate"]
        }
        
        prefix = self.random.choice(readiness_prefixes[readiness])
        return f"{prefix} {movement_path.thematic_title}"
    
    def _generate_quest_description(
        self, 
        exercise: ExerciseProgression, 
        reps: int, 
        sets: int, 
        flavor: str
    ) -> str:
        """Generate a complete quest description"""
        
        return f"{exercise.description}\n\n**Objective:** {sets} sets × {reps} reps\n\n*{flavor}*"
    
    def _generate_special_modifiers(self, params: QuestParameters, quest_index: int) -> Dict[str, Any]:
        """Generate special modifiers for quests"""
        
        modifiers = {}
        
        # Add time pressure for high readiness
        if params.readiness_level == ReadinessLevel.HIGH and quest_index == 0:
            modifiers["time_challenge"] = True
            modifiers["bonus_xp_multiplier"] = 1.2
        
        # Add form focus for low readiness
        if params.readiness_level == ReadinessLevel.LOW:
            modifiers["form_focus"] = True
            modifiers["tempo_requirement"] = "slow_controlled"
        
        # Add intensity boost for weekly challenges
        if params.quest_type == QuestType.WEEKLY:
            modifiers["weekly_challenge"] = True
            modifiers["completion_bonus"] = 50
        
        return modifiers
    
    def _generate_session_theme(self, readiness: ReadinessLevel, quests: List[GeneratedQuest]) -> str:
        """Generate a thematic name for the session"""
        
        themes = {
            ReadinessLevel.LOW: [
                "Path of Recovery", "Gentle Awakening", "Mindful Movement",
                "Shadow's Rest", "Restoration Ritual"
            ],
            ReadinessLevel.STANDARD: [
                "Warrior's Dawn", "Shadow Training", "Balanced Awakening",
                "Daily Discipline", "Focused Practice"
            ],
            ReadinessLevel.HIGH: [
                "Ascendant's Trial", "Elite Awakening", "Peak Performance",
                "Ultimate Challenge", "Mastery Session"
            ]
        }
        
        return self.random.choice(themes[readiness])
    
    def _generate_session_description(self, readiness: ReadinessLevel, quest_count: int) -> str:
        """Generate a description for the session"""
        
        descriptions = {
            ReadinessLevel.LOW: f"A gentle {quest_count}-quest awakening focused on recovery and mindful movement. Listen to your body and prioritize form over intensity.",
            ReadinessLevel.STANDARD: f"A balanced {quest_count}-quest awakening designed for steady progress. Execute each movement with precision and purpose.",
            ReadinessLevel.HIGH: f"An intense {quest_count}-quest awakening that will push your limits. Channel your energy and embrace the challenge ahead."
        }
        
        return descriptions[readiness]
    
    def _apply_user_preferences(self, params: QuestParameters, preferences: Dict) -> QuestParameters:
        """Apply user preferences to quest parameters"""
        
        if "preferred_stats" in preferences:
            params.preferred_stats = [CoreStat(stat) for stat in preferences["preferred_stats"]]
        
        if "excluded_categories" in preferences:
            params.excluded_categories = [MovementCategory(cat) for cat in preferences["excluded_categories"]]
        
        if "time_limit" in preferences:
            params.time_constraint_minutes = preferences["time_limit"]
        
        if "intensity_preference" in preferences:
            intensity_map = {"low": 0.8, "normal": 1.0, "high": 1.2}
            params.intensity_modifier *= intensity_map.get(preferences["intensity_preference"], 1.0)
        
        return params


# Convenience functions for easy integration
def create_quest_engine() -> QuestGenerationEngine:
    """Create a new quest generation engine instance"""
    return QuestGenerationEngine()


def generate_awakening_for_user(
    user_id: int,
    user_level: int,
    readiness_level: str,
    preferences: Optional[Dict] = None
) -> QuestSession:
    """Quick function to generate awakening session"""
    engine = create_quest_engine()
    readiness = ReadinessLevel(readiness_level)
    return engine.generate_awakening_session(user_id, user_level, readiness, preferences)


def generate_daily_for_user(
    user_id: int,
    user_level: int,
    category: Optional[str] = None
) -> GeneratedQuest:
    """Quick function to generate daily quest"""
    engine = create_quest_engine()
    cat = MovementCategory(category) if category else None
    return engine.generate_daily_quest(user_id, user_level, cat)