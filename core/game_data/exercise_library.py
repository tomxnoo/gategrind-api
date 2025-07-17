"""
Unified Exercise Library for Realm of Shadows
============================================

This module contains the foundational exercise data structure that powers the quest generation engine.
It consolidates movement data from legacy files and implements the new tiered quest system.

Based on Gemini 2.5 Pro's design recommendations for V-taper focused training.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class MovementCategory(Enum):
    """Movement categories aligned with V-taper physique goals"""
    PULL = "pull"                    # Path of Ascension - Back & Biceps
    PUSH_H = "push_horizontal"       # Earthbreaker's Might - Chest, Shoulders, Triceps  
    PUSH_V = "push_vertical"         # Titan's Shoulders - Shoulders & Upper Chest
    LEGS = "legs"                    # Root of Power - Legs & Glutes
    CORE = "core"                    # Iron Will - Abs & Core
    ACCESSORY_SHOULDERS = "accessory_shoulders"  # Sculptor's Art - Lateral Delts


class QuestTier(Enum):
    """Quest difficulty tiers for autoregulation"""
    PRACTICE = 1      # Shadow's Practice - Volume/GtG (60% chance)
    TRIAL = 2         # Warrior's Trial - Technique (30% chance)  
    CHALLENGE = 3     # Ascendant's Challenge - Intensity (10% chance)


class CoreStat(Enum):
    """Core stats that exercises can reward"""
    STR = "strength"     # Strength - progression to harder variations
    END = "endurance"    # Endurance - volume accumulation
    TECH = "technique"   # Technique - form focus and control


@dataclass
class ExerciseProgression:
    """Represents a single exercise in a progression chain"""
    name: str
    display_name: str
    description: str
    difficulty_level: int  # 1-5, where 1 is easiest
    base_reps: int        # Base rep count for level 1 user
    base_duration: Optional[int] = None  # For time-based exercises (seconds)
    equipment_needed: List[str] = None
    form_cues: List[str] = None
    
    def __post_init__(self):
        if self.equipment_needed is None:
            self.equipment_needed = []
        if self.form_cues is None:
            self.form_cues = []


@dataclass
class MovementPath:
    """Represents a complete progression path for a movement category"""
    category: MovementCategory
    path_name: str
    thematic_title: str
    description: str
    primary_stat: CoreStat
    progressions: List[ExerciseProgression]
    quest_flavors: Dict[QuestTier, List[str]]


@dataclass
class CoreStats:
    """Core stats reward system"""
    str_reward: int = 0
    end_reward: int = 0
    tech_reward: int = 0
    
    def get_total_reward(self) -> int:
        return self.str_reward + self.end_reward + self.tech_reward


# =============================================================================
# EXERCISE LIBRARY - The Foundation of All Quests
# =============================================================================

EXERCISE_LIBRARY: Dict[MovementCategory, MovementPath] = {
    
    # =========================================================================
    # PULL - Path of Ascension (Back & Biceps)
    # =========================================================================
    MovementCategory.PULL: MovementPath(
        category=MovementCategory.PULL,
        path_name="Path of Ascension",
        thematic_title="🌙 The Ascendant's Climb",
        description="The cornerstone of the V-taper. A wide back creates the most dramatic illusion of width.",
        primary_stat=CoreStat.STR,
        progressions=[
            ExerciseProgression(
                name="dead_hang",
                display_name="Dead Hang",
                description="Simply hanging from the bar to build foundational grip strength",
                difficulty_level=1,
                base_reps=0,
                base_duration=30,
                equipment_needed=["pull_up_bar"],
                form_cues=[
                    "Shoulders engaged, not hanging loose",
                    "Straight arms, active grip",
                    "Breathe normally, don't hold breath"
                ]
            ),
            ExerciseProgression(
                name="scapular_pull",
                display_name="Scapular Pull",
                description="Hanging and pulling shoulder blades down without bending arms",
                difficulty_level=2,
                base_reps=8,
                equipment_needed=["pull_up_bar"],
                form_cues=[
                    "Initiate movement with shoulder blades",
                    "Keep arms straight throughout",
                    "Feel the squeeze between shoulder blades"
                ]
            ),
            ExerciseProgression(
                name="inverted_row",
                display_name="Inverted Row",
                description="Pulling body up at an angle using a low bar or table",
                difficulty_level=2,
                base_reps=12,
                equipment_needed=["low_bar", "table"],
                form_cues=[
                    "Body in straight line from head to heels",
                    "Pull chest to bar/table edge",
                    "Squeeze shoulder blades at top"
                ]
            ),
            ExerciseProgression(
                name="negative_pullup",
                display_name="Negative Pull-up",
                description="Jumping to top position and lowering slowly",
                difficulty_level=3,
                base_reps=5,
                equipment_needed=["pull_up_bar"],
                form_cues=[
                    "3-5 second controlled descent",
                    "Full range of motion to dead hang",
                    "Reset between each rep"
                ]
            ),
            ExerciseProgression(
                name="assisted_pullup",
                display_name="Assisted Pull-up",
                description="Pull-ups with band or partner assistance",
                difficulty_level=4,
                base_reps=6,
                equipment_needed=["pull_up_bar", "resistance_band"],
                form_cues=[
                    "Use minimal assistance needed",
                    "Focus on pulling with back muscles",
                    "Full range of motion"
                ]
            ),
            ExerciseProgression(
                name="full_pullup",
                display_name="Pull-up",
                description="The classic unassisted pull-up",
                difficulty_level=5,
                base_reps=3,
                equipment_needed=["pull_up_bar"],
                form_cues=[
                    "Dead hang to chin over bar",
                    "No kipping or swinging",
                    "Controlled descent"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "The shadows whisper of warriors who can climb the very air. Practice your grip.",
                "Accumulate time in the void. Let gravity teach you patience.",
                "The bar knows no mercy, but neither do you. Hang with purpose.",
                "Each second suspended builds the foundation of ascension."
            ],
            QuestTier.TRIAL: [
                "Feel the pull of the abyss. Control your descent into power.",
                "The warrior's trial: rise not with speed, but with intention.",
                "Master the space between earth and sky. Perfect your form.",
                "Technique is the bridge between effort and achievement."
            ],
            QuestTier.CHALLENGE: [
                "Today you challenge the very laws of gravity. Rise, Ascendant.",
                "The realm demands proof of your vertical might. Show your strength.",
                "Push beyond the whispers of doubt. Claim your place among the climbers.",
                "This is your test of ascension. The shadows watch and judge."
            ]
        }
    ),
    
    # =========================================================================
    # PUSH_H - Earthbreaker's Might (Chest, Shoulders, Triceps)
    # =========================================================================
    MovementCategory.PUSH_H: MovementPath(
        category=MovementCategory.PUSH_H,
        path_name="Earthbreaker's Might",
        thematic_title="⚡ The Unyielding Chestplate",
        description="A well-developed chest provides the foundation that enhances the V-taper.",
        primary_stat=CoreStat.STR,
        progressions=[
            ExerciseProgression(
                name="incline_pushup",
                display_name="Incline Push-up",
                description="Hands elevated on desk, chair, or wall",
                difficulty_level=1,
                base_reps=15,
                equipment_needed=["elevated_surface"],
                form_cues=[
                    "Straight line from head to heels",
                    "Lower chest to surface",
                    "Push through palms, not fingertips"
                ]
            ),
            ExerciseProgression(
                name="knee_pushup",
                display_name="Knee Push-up",
                description="Push-up performed from knees",
                difficulty_level=2,
                base_reps=12,
                form_cues=[
                    "Straight line from head to knees",
                    "Lower chest to floor",
                    "Keep core engaged"
                ]
            ),
            ExerciseProgression(
                name="standard_pushup",
                display_name="Push-up",
                description="The classic push-up from toes",
                difficulty_level=3,
                base_reps=8,
                form_cues=[
                    "Plank position, straight body line",
                    "Lower until chest nearly touches floor",
                    "Push up explosively, control the descent"
                ]
            ),
            ExerciseProgression(
                name="diamond_pushup",
                display_name="Diamond Push-up",
                description="Hands close together forming diamond shape",
                difficulty_level=4,
                base_reps=5,
                form_cues=[
                    "Thumbs and index fingers touching",
                    "Elbows track close to body",
                    "Emphasizes triceps and inner chest"
                ]
            ),
            ExerciseProgression(
                name="archer_pushup",
                display_name="Archer Push-up",
                description="Shifting weight to one arm during push-up",
                difficulty_level=5,
                base_reps=3,
                form_cues=[
                    "Shift weight to working arm",
                    "Non-working arm stays straight",
                    "Alternate sides each rep"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "The earth itself will be your anvil. Forge strength with repetition.",
                "A warrior's armor is built rep by rep. Practice your craft.",
                "Let the ground know your power. Press away the weight of doubt.",
                "Each push builds the foundation of an unbreakable chest."
            ],
            QuestTier.TRIAL: [
                "Control the descent, command the ascent. Master the earthbreaker's form.",
                "Feel the burn of forging. Your chest becomes an unyielding shield.",
                "Technique transforms effort into art. Perfect your pressing ritual.",
                "The trial of the horizontal plane. Show your controlled might."
            ],
            QuestTier.CHALLENGE: [
                "Today the earth trembles beneath your power. Push with fury.",
                "Challenge the limits of your pressing strength. Break new ground.",
                "The realm demands a demonstration of raw horizontal might.",
                "Push beyond comfort, beyond doubt. Claim your earthbreaker title."
            ]
        }
    ),
    
    # =========================================================================
    # PUSH_V - Titan's Shoulders (Shoulders & Upper Chest)
    # =========================================================================
    MovementCategory.PUSH_V: MovementPath(
        category=MovementCategory.PUSH_V,
        path_name="Titan's Shoulders",
        thematic_title="🏔️ The Abyssal Press",
        description="The secret weapon for anime physique. Pike push-ups build crucial shoulder width.",
        primary_stat=CoreStat.STR,
        progressions=[
            ExerciseProgression(
                name="pike_pushup",
                display_name="Pike Push-up",
                description="Downward-dog position, lower head towards floor",
                difficulty_level=2,
                base_reps=8,
                form_cues=[
                    "Form inverted V with body",
                    "Lower head between hands",
                    "Push through shoulders, not arms"
                ]
            ),
            ExerciseProgression(
                name="elevated_pike_pushup",
                display_name="Feet-Elevated Pike Push-up",
                description="Pike push-up with feet on chair or box",
                difficulty_level=3,
                base_reps=6,
                equipment_needed=["elevated_surface"],
                form_cues=[
                    "More weight on shoulders",
                    "Maintain pike position",
                    "Control the descent"
                ]
            ),
            ExerciseProgression(
                name="deficit_pike_pushup",
                display_name="Deficit Pike Push-up",
                description="Hands on elevated surfaces for increased range",
                difficulty_level=4,
                base_reps=4,
                equipment_needed=["yoga_blocks", "books"],
                form_cues=[
                    "Hands on elevated platforms",
                    "Deeper range of motion",
                    "Feel the stretch at bottom"
                ]
            ),
            ExerciseProgression(
                name="wall_handstand_pushup",
                display_name="Wall Handstand Push-up",
                description="Handstand against wall with push-up motion",
                difficulty_level=5,
                base_reps=2,
                equipment_needed=["wall"],
                form_cues=[
                    "Heels against wall for support",
                    "Lower head to floor",
                    "Press back to full extension"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "To see the world as titans do, you must first look down upon it.",
                "Invert your perspective. Build shoulders that touch the sky.",
                "The abyssal press teaches humility and builds godlike shoulders.",
                "Practice the inverted path. Each rep elevates your presence."
            ],
            QuestTier.TRIAL: [
                "Master the vertical press. Let technique guide your ascension.",
                "The trial of inverted might. Control your descent into power.",
                "Feel the shoulders forge themselves in the fires of the abyss.",
                "Perfect form in the inverted realm. Technique conquers all."
            ],
            QuestTier.CHALLENGE: [
                "Today you press against the very heavens. Show titanic strength.",
                "Challenge gravity itself. Your shoulders shall know no limits.",
                "The abyssal challenge: press with the fury of the titans.",
                "Defy the natural order. Press your way to shoulder supremacy."
            ]
        }
    ),
    
    # =========================================================================
    # LEGS - Root of Power (Legs & Glutes)
    # =========================================================================
    MovementCategory.LEGS: MovementPath(
        category=MovementCategory.LEGS,
        path_name="Root of Power",
        thematic_title="🌳 Earthshaker's Ritual",
        description="Strong legs provide metabolic demand and balanced aesthetics.",
        primary_stat=CoreStat.END,
        progressions=[
            ExerciseProgression(
                name="bodyweight_squat",
                display_name="Bodyweight Squat",
                description="Basic squat mastering fundamental movement pattern",
                difficulty_level=1,
                base_reps=20,
                form_cues=[
                    "Feet shoulder-width apart",
                    "Lower until thighs parallel to floor",
                    "Drive through heels to stand"
                ]
            ),
            ExerciseProgression(
                name="lunge",
                display_name="Lunge",
                description="Forward or reverse lunges working each leg independently",
                difficulty_level=2,
                base_reps=12,
                form_cues=[
                    "Step forward into lunge position",
                    "Lower back knee toward floor",
                    "Push through front heel to return"
                ]
            ),
            ExerciseProgression(
                name="jump_squat",
                display_name="Jump Squat",
                description="Explosive squat with jump at the top",
                difficulty_level=3,
                base_reps=10,
                form_cues=[
                    "Squat down, then explode upward",
                    "Land softly, absorb impact",
                    "Immediate transition to next rep"
                ]
            ),
            ExerciseProgression(
                name="pistol_negative",
                display_name="Pistol Squat Negative",
                description="Single-leg squat lowering phase only",
                difficulty_level=4,
                base_reps=5,
                equipment_needed=["chair", "support"],
                form_cues=[
                    "Lower on one leg as slowly as possible",
                    "Non-working leg extended forward",
                    "Use support to return to standing"
                ]
            ),
            ExerciseProgression(
                name="assisted_pistol",
                display_name="Assisted Pistol Squat",
                description="Single-leg squat with minimal assistance",
                difficulty_level=5,
                base_reps=3,
                equipment_needed=["doorframe", "band"],
                form_cues=[
                    "Minimal assistance for balance only",
                    "Full range single-leg squat",
                    "Control both up and down phases"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "Power does not float in the air; it is drawn from the ground.",
                "Root yourself to the realm. Build a foundation that cannot be moved.",
                "Each squat connects you deeper to the earth's endless strength.",
                "The ritual of grounding. Let the earth teach you stability."
            ],
            QuestTier.TRIAL: [
                "The earthshaker's trial: balance power with precision.",
                "Master the single-leg path. Show your unilateral might.",
                "Control the descent into the earth's embrace. Rise with purpose.",
                "Technique in the foundational realm. Perfect your rooting ritual."
            ],
            QuestTier.CHALLENGE: [
                "Today the earth shall tremble beneath your explosive power.",
                "Challenge the very foundations. Show your earthshaking might.",
                "The realm demands proof of your lower body supremacy.",
                "Explode from the earth like a force of nature unleashed."
            ]
        }
    ),
    
    # =========================================================================
    # CORE - Iron Will (Abs & Core)
    # =========================================================================
    MovementCategory.CORE: MovementPath(
        category=MovementCategory.CORE,
        path_name="Iron Will",
        thematic_title="⚔️ The Unmoving Center",
        description="The cinch for your V-taper. A strong core makes the waist appear narrower.",
        primary_stat=CoreStat.TECH,
        progressions=[
            ExerciseProgression(
                name="plank",
                display_name="Plank",
                description="Holding the top of push-up position",
                difficulty_level=1,
                base_reps=0,
                base_duration=45,
                form_cues=[
                    "Straight line from head to heels",
                    "Engage core, don't sag hips",
                    "Breathe normally throughout hold"
                ]
            ),
            ExerciseProgression(
                name="hollow_hold",
                display_name="Hollow Body Hold",
                description="Creating dish shape lying on back",
                difficulty_level=2,
                base_reps=0,
                base_duration=30,
                form_cues=[
                    "Lower back pressed to floor",
                    "Shoulders and legs off ground",
                    "Create banana/dish shape"
                ]
            ),
            ExerciseProgression(
                name="lying_leg_raise",
                display_name="Lying Leg Raise",
                description="Raising legs toward ceiling from lying position",
                difficulty_level=3,
                base_reps=10,
                form_cues=[
                    "Lower back stays on floor",
                    "Raise legs to 90 degrees",
                    "Control the lowering phase"
                ]
            ),
            ExerciseProgression(
                name="hanging_knee_raise",
                display_name="Hanging Knee Raise",
                description="Bringing knees to chest while hanging",
                difficulty_level=4,
                base_reps=8,
                equipment_needed=["pull_up_bar"],
                form_cues=[
                    "Hang with straight arms",
                    "Bring knees to chest",
                    "Control the lowering"
                ]
            ),
            ExerciseProgression(
                name="l_sit",
                display_name="L-Sit",
                description="Holding L-shape position with legs extended",
                difficulty_level=5,
                base_reps=0,
                base_duration=15,
                equipment_needed=["parallettes", "dip_bars"],
                form_cues=[
                    "Legs parallel to floor",
                    "Shoulders over hands",
                    "Press down through arms"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "The storm of battle rages, but the master is calm at its center.",
                "Forge a core of unyielding shadow iron. Be unmovable.",
                "Stillness in motion, strength in stability. Practice the center.",
                "Each second of hold builds the foundation of unshakeable will."
            ],
            QuestTier.TRIAL: [
                "The trial of the unmoving center. Master stillness within motion.",
                "Control the chaos within. Let technique guide your stability.",
                "Feel the iron will forge itself in the fires of sustained effort.",
                "Perfect the art of controlled tension. Technique over time."
            ],
            QuestTier.CHALLENGE: [
                "Today your core faces the ultimate test of iron will.",
                "Challenge the limits of your central stability. Show your steel.",
                "The realm demands proof of your unbreakable center.",
                "Forge an iron will that bends to nothing and no one."
            ]
        }
    ),
    
    # =========================================================================
    # ACCESSORY_SHOULDERS - Sculptor's Art (Lateral Delts)
    # =========================================================================
    MovementCategory.ACCESSORY_SHOULDERS: MovementPath(
        category=MovementCategory.ACCESSORY_SHOULDERS,
        path_name="Sculptor's Art",
        thematic_title="🎨 The Widening Ritual",
        description="Specialized shoulder work for maximum V-taper width.",
        primary_stat=CoreStat.TECH,
        progressions=[
            ExerciseProgression(
                name="wall_lateral_raise",
                display_name="Wall Lateral Raise",
                description="Lateral raise against wall for resistance",
                difficulty_level=1,
                base_reps=15,
                equipment_needed=["wall"],
                form_cues=[
                    "Stand sideways to wall",
                    "Press arm against wall, slide up",
                    "Feel lateral delt engagement"
                ]
            ),
            ExerciseProgression(
                name="prone_lateral_raise",
                display_name="Prone Lateral Raise",
                description="Lateral raise lying face down",
                difficulty_level=2,
                base_reps=12,
                form_cues=[
                    "Lie face down on bench/floor",
                    "Raise arms out to sides",
                    "Squeeze shoulder blades"
                ]
            ),
            ExerciseProgression(
                name="water_bottle_lateral",
                display_name="Water Bottle Lateral Raise",
                description="Lateral raise with water bottles for resistance",
                difficulty_level=3,
                base_reps=10,
                equipment_needed=["water_bottles"],
                form_cues=[
                    "Arms slightly bent",
                    "Raise to shoulder height",
                    "Control the descent"
                ]
            ),
            ExerciseProgression(
                name="single_arm_lateral",
                display_name="Single-Arm Lateral Raise",
                description="Unilateral lateral raise for focus",
                difficulty_level=4,
                base_reps=8,
                equipment_needed=["weight", "resistance"],
                form_cues=[
                    "Focus on one side at a time",
                    "Perfect form over speed",
                    "Feel the lateral delt isolation"
                ]
            )
        ],
        quest_flavors={
            QuestTier.PRACTICE: [
                "The sculptor's art: each rep carves wider shoulders from stone.",
                "Practice the widening ritual. Let your silhouette expand.",
                "Small movements, profound changes. Sculpt your V-taper.",
                "The artist's patience: width is built one careful rep at a time."
            ],
            QuestTier.TRIAL: [
                "The sculptor's trial: precision over power, art over aggression.",
                "Master the lateral path. Feel each fiber respond to your will.",
                "Technique in the realm of aesthetics. Perfect your sculpting form.",
                "Control the weight of transformation. Sculpt with intention."
            ],
            QuestTier.CHALLENGE: [
                "Today you sculpt with the fury of a master artist.",
                "Challenge the limits of your shoulder width. Carve new dimensions.",
                "The realm demands a masterpiece. Show your sculpting prowess.",
                "Push the boundaries of your V-taper. Art through intensity."
            ]
        }
    )
}


# =============================================================================
# QUEST GENERATION HELPERS
# =============================================================================

def get_exercise_by_difficulty(category: MovementCategory, difficulty: int) -> Optional[ExerciseProgression]:
    """Get exercise of specific difficulty from a category"""
    movement_path = EXERCISE_LIBRARY.get(category)
    if not movement_path:
        return None
    
    for exercise in movement_path.progressions:
        if exercise.difficulty_level == difficulty:
            return exercise
    return None


def get_user_appropriate_exercise(category: MovementCategory, user_level: int) -> ExerciseProgression:
    """Get appropriate exercise based on user level"""
    movement_path = EXERCISE_LIBRARY[category]
    
    # Map user level to exercise difficulty (1-5 user level -> 1-5 exercise difficulty)
    target_difficulty = min(max(1, (user_level // 5) + 1), 5)
    
    # Find exercise at target difficulty, or closest available
    for difficulty in range(target_difficulty, 0, -1):
        exercise = get_exercise_by_difficulty(category, difficulty)
        if exercise:
            return exercise
    
    # Fallback to easiest exercise
    return movement_path.progressions[0]


def calculate_quest_reps(exercise: ExerciseProgression, user_level: int, tier: QuestTier) -> int:
    """Calculate appropriate rep count based on exercise, user level, and quest tier"""
    base_reps = exercise.base_reps
    
    # Level scaling (1.0x to 2.5x based on user level)
    level_multiplier = 1 + (user_level - 1) * 0.1
    level_multiplier = min(level_multiplier, 2.5)
    
    # Tier scaling
    tier_multipliers = {
        QuestTier.PRACTICE: 1.5,    # Higher volume for practice
        QuestTier.TRIAL: 1.0,       # Moderate volume for technique
        QuestTier.CHALLENGE: 0.7    # Lower volume for intensity
    }
    
    tier_multiplier = tier_multipliers[tier]
    final_reps = int(base_reps * level_multiplier * tier_multiplier)
    
    return max(1, final_reps)  # Ensure at least 1 rep


def calculate_quest_duration(exercise: ExerciseProgression, user_level: int, tier: QuestTier) -> int:
    """Calculate appropriate duration for time-based exercises"""
    if not exercise.base_duration:
        return 0
    
    base_duration = exercise.base_duration
    
    # Level scaling
    level_multiplier = 1 + (user_level - 1) * 0.05
    level_multiplier = min(level_multiplier, 2.0)
    
    # Tier scaling for duration
    tier_multipliers = {
        QuestTier.PRACTICE: 1.2,    # Longer holds for practice
        QuestTier.TRIAL: 1.0,       # Standard duration for technique
        QuestTier.CHALLENGE: 1.5    # Longer holds for challenge
    }
    
    tier_multiplier = tier_multipliers[tier]
    final_duration = int(base_duration * level_multiplier * tier_multiplier)
    
    return max(5, final_duration)  # Minimum 5 seconds


def get_stat_rewards(category: MovementCategory, tier: QuestTier) -> CoreStats:
    """Calculate stat rewards based on movement category and quest tier"""
    movement_path = EXERCISE_LIBRARY[category]
    primary_stat = movement_path.primary_stat
    
    # Base rewards by tier
    base_rewards = {
        QuestTier.PRACTICE: 2,
        QuestTier.TRIAL: 4,
        QuestTier.CHALLENGE: 6
    }
    
    base_reward = base_rewards[tier]
    
    # Create reward distribution
    rewards = CoreStats()
    
    if primary_stat == CoreStat.STR:
        rewards.str_reward = base_reward
        rewards.end_reward = base_reward // 2
        rewards.tech_reward = base_reward // 3
    elif primary_stat == CoreStat.END:
        rewards.end_reward = base_reward
        rewards.str_reward = base_reward // 2
        rewards.tech_reward = base_reward // 3
    elif primary_stat == CoreStat.TECH:
        rewards.tech_reward = base_reward
        rewards.str_reward = base_reward // 3
        rewards.end_reward = base_reward // 3
    
    return rewards


# =============================================================================
# V-TAPER FOCUSED MOVEMENT SELECTION
# =============================================================================

def get_vtaper_movement_weights() -> Dict[MovementCategory, float]:
    """Get movement category weights optimized for V-taper physique"""
    return {
        MovementCategory.PULL: 0.25,              # 25% - Critical for back width
        MovementCategory.PUSH_V: 0.15,            # 15% - Essential for shoulder width
        MovementCategory.PUSH_H: 0.20,            # 20% - Chest development
        MovementCategory.LEGS: 0.15,              # 15% - Metabolic and balance
        MovementCategory.CORE: 0.15,              # 15% - Waist definition
        MovementCategory.ACCESSORY_SHOULDERS: 0.10  # 10% - Specialized width work
    }


def get_quest_layout_template() -> List[Tuple[MovementCategory, float]]:
    """Get the optimal quest layout for daily quest generation"""
    return [
        # Quest 1: Main Upper Body (40% chance PULL/PUSH_V, 30% PUSH_H)
        (MovementCategory.PULL, 0.4),
        (MovementCategory.PUSH_V, 0.4), 
        (MovementCategory.PUSH_H, 0.2),
        
        # Quest 2: Foundation (60% LEGS, 40% CORE)
        (MovementCategory.LEGS, 0.6),
        (MovementCategory.CORE, 0.4),
        
        # Quest 3: Wildcard/Technique (balanced selection)
        (MovementCategory.PULL, 0.2),
        (MovementCategory.PUSH_H, 0.2),
        (MovementCategory.PUSH_V, 0.2),
        (MovementCategory.CORE, 0.2),
        (MovementCategory.ACCESSORY_SHOULDERS, 0.2),
    ]


# =============================================================================
# AUTOREGULATION LOGIC
# =============================================================================

def get_tier_probabilities(readiness_level: int) -> Dict[QuestTier, float]:
    """Get quest tier probabilities based on user's readiness level (1-5)"""
    if readiness_level <= 2:  # Low energy
        return {
            QuestTier.PRACTICE: 0.8,   # 80% practice
            QuestTier.TRIAL: 0.2,      # 20% trial
            QuestTier.CHALLENGE: 0.0   # 0% challenge
        }
    elif readiness_level == 3:  # Moderate energy
        return {
            QuestTier.PRACTICE: 0.6,   # 60% practice
            QuestTier.TRIAL: 0.3,      # 30% trial
            QuestTier.CHALLENGE: 0.1   # 10% challenge
        }
    else:  # High energy (4-5)
        return {
            QuestTier.PRACTICE: 0.4,   # 40% practice
            QuestTier.TRIAL: 0.4,      # 40% trial
            QuestTier.CHALLENGE: 0.2   # 20% challenge
        }


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

def get_legacy_movement_mapping() -> Dict[str, Tuple[MovementCategory, str]]:
    """Map legacy movement names to new exercise system"""
    return {
        # Legacy -> (Category, Exercise Name)
        "Pull Ups": (MovementCategory.PULL, "full_pullup"),
        "Push Ups": (MovementCategory.PUSH_H, "standard_pushup"),
        "Pike Push Ups": (MovementCategory.PUSH_V, "pike_pushup"),
        "Squats": (MovementCategory.LEGS, "bodyweight_squat"),
        "Plank": (MovementCategory.CORE, "plank"),
        "Hollow Body Hold": (MovementCategory.CORE, "hollow_hold"),
        "Passive Hang": (MovementCategory.PULL, "dead_hang"),
        "Row": (MovementCategory.PULL, "inverted_row"),
        "Dips": (MovementCategory.PUSH_H, "standard_pushup"),  # Approximate
        "L-Sit": (MovementCategory.CORE, "l_sit"),
        "Pistol Squats": (MovementCategory.LEGS, "assisted_pistol"),
        "Diamond Push Ups": (MovementCategory.PUSH_H, "diamond_pushup"),
        "Lunges": (MovementCategory.LEGS, "lunge"),
    }


if __name__ == "__main__":
    # Quick test of the library
    print("🎯 Unified Exercise Library Loaded Successfully!")
    print(f"📚 Categories: {len(EXERCISE_LIBRARY)}")
    
    total_exercises = sum(len(path.progressions) for path in EXERCISE_LIBRARY.values())
    print(f"🏋️ Total Exercises: {total_exercises}")
    
    for category, path in EXERCISE_LIBRARY.items():
        print(f"  {path.thematic_title}: {len(path.progressions)} progressions")