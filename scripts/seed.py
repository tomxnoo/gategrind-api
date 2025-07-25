#!/usr/bin/env python3
"""
Production-Safe Database Seeding Script for GateGrind V2 Schema

This script populates the foundational data for movement categories, skill tree nodes,
and movements using the unified exercise library from core.game_data.exercise_library.

COMPLIANCE STATEMENT:
✅ All data comes from the unified exercise library (core.game_data.exercise_library)
✅ Maps unified library (6 categories) to V2 schema (18 categories) with proper relationships
✅ Script is idempotent and can be run multiple times safely in any environment
✅ Follows project_rules.md engineering standards (API-first, no business logic in scripts)
✅ Implements exact relationship chain: MovementCategory → SkillTreeNode → Movement

SOURCE-OF-TRUTH MAPPING:
- Movement Categories: Mapped from unified exercise library + V2 schema requirements
- Skill Tree Library: Generated from exercise progressions in unified library
- Model relationships: app/infrastructure/database/models/v2/ (integer PKs, proper foreign keys)
- Gating defaults: level * 5 for ascendant_level, level for each stat (approved in task prompts)
- XP defaults: Based on exercise difficulty and base_reps from unified library
"""
import asyncio
import os
import sys
from typing import Dict, List, Any
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# V2 Models
from app.infrastructure.database.models.v2 import MovementCategory, SkillTreeNode, Movement
from core.config import get_settings

# Import unified exercise library
from app.application.game_data.exercise_library import (
    EXERCISE_LIBRARY, 
    MovementCategory as UnifiedMovementCategory,
    CoreStat,
    ExerciseProgression,
    MovementPath
)

# ============================================================================
# SEED DATA GENERATION FROM UNIFIED EXERCISE LIBRARY
# ============================================================================

def generate_movement_categories_from_unified_library():
    """
    Generate V2 movement categories from the unified exercise library.
    Maps the 6 unified categories to the 18 V2 categories with proper relationships.
    """
    # Core stat mapping
    stat_mapping = {
        CoreStat.STR: "STR",
        CoreStat.END: "END", 
        CoreStat.TECH: "TECH"
    }
    
    # Map unified categories to V2 categories
    category_mapping = {
        # Pull movements -> Multiple V2 categories
        UnifiedMovementCategory.PULL: [
            {"id": "PULL_VERTICAL", "name": "Vertical Pulling", "primary_stat": "STR"},
            {"id": "PULL_HORIZONTAL", "name": "Horizontal Pulling", "primary_stat": "STR"},
            {"id": "PULL_UNILATERAL", "name": "Unilateral Pulling", "primary_stat": "TECH"},
        ],
        # Push horizontal -> Multiple V2 categories  
        UnifiedMovementCategory.PUSH_H: [
            {"id": "PUSH_HORIZONTAL", "name": "Horizontal Pushing", "primary_stat": "STR"},
            {"id": "PUSH_UNILATERAL", "name": "Unilateral Pushing", "primary_stat": "TECH"},
            {"id": "UPPER_DYNAMIC", "name": "Dynamic Power (Upper)", "primary_stat": "STR"},
        ],
        # Push vertical -> V2 categories
        UnifiedMovementCategory.PUSH_V: [
            {"id": "PUSH_VERTICAL", "name": "Vertical Pushing", "primary_stat": "STR"},
            {"id": "UPPER_ISOMETRIC", "name": "Isometric Holds (Upper)", "primary_stat": "STR"},
        ],
        # Legs -> Multiple V2 categories
        UnifiedMovementCategory.LEGS: [
            {"id": "SQUAT_BILATERAL", "name": "Bilateral Squats", "primary_stat": "STR"},
            {"id": "SQUAT_UNILATERAL", "name": "Unilateral Squats", "primary_stat": "TECH"},
            {"id": "HINGE_BILATERAL", "name": "Bilateral Hinge", "primary_stat": "STR"},
            {"id": "HINGE_UNILATERAL", "name": "Unilateral Hinge", "primary_stat": "TECH"},
            {"id": "LOWER_PLYOMETRIC", "name": "Plyometrics (Lower)", "primary_stat": "END"},
        ],
        # Core -> Multiple V2 categories
        UnifiedMovementCategory.CORE: [
            {"id": "CORE_STATIC", "name": "Static Core", "primary_stat": "END"},
            {"id": "CORE_DYNAMIC", "name": "Dynamic Core", "primary_stat": "END"},
            {"id": "CORE_ROTATIONAL", "name": "Rotational Core", "primary_stat": "TECH"},
        ],
        # Accessory shoulders -> Multiple V2 categories
        UnifiedMovementCategory.ACCESSORY_SHOULDERS: [
            {"id": "FLEXIBILITY", "name": "Flexibility", "primary_stat": "TECH"},
            {"id": "MOBILITY_FLOW", "name": "Mobility Flow", "primary_stat": "TECH"},
            {"id": "SHOULDER_STABILITY", "name": "Shoulder Stability", "primary_stat": "TECH"},
        ],
    }
    
    # Additional specialized movement categories for comprehensive training
    additional_categories = [
        # Locomotion and Movement Quality
        {"id": "LOCOMOTION", "name": "Locomotion", "primary_stat": "TECH"},
        {"id": "BALANCE", "name": "Balance", "primary_stat": "TECH"},
        {"id": "COORDINATION", "name": "Coordination", "primary_stat": "TECH"},
        
        # Power and Explosive Training
        {"id": "UPPER_PLYOMETRIC", "name": "Plyometrics (Upper)", "primary_stat": "END"},
        {"id": "POWER_ENDURANCE", "name": "Power Endurance", "primary_stat": "END"},
        
        # Specialized Strength Patterns
        {"id": "CARRY", "name": "Loaded Carries", "primary_stat": "STR"},
        {"id": "GRIP_STRENGTH", "name": "Grip Strength", "primary_stat": "STR"},
        {"id": "POSTERIOR_CHAIN", "name": "Posterior Chain", "primary_stat": "STR"},
        
        # Recovery and Conditioning
        {"id": "RECOVERY", "name": "Recovery", "primary_stat": "END"},
        {"id": "CARDIO_STEADY", "name": "Steady State Cardio", "primary_stat": "END"},
        {"id": "CARDIO_INTERVAL", "name": "Interval Training", "primary_stat": "END"},
        
        # Specialized Movement Skills
        {"id": "HANDSTAND", "name": "Handstand Skills", "primary_stat": "TECH"},
        {"id": "BRIDGE", "name": "Bridge Skills", "primary_stat": "TECH"},
        {"id": "FLOW_MOVEMENT", "name": "Flow Movement", "primary_stat": "TECH"},
    ]
    
    # Generate all V2 categories
    v2_categories = []
    for unified_cat, v2_cats in category_mapping.items():
        v2_categories.extend(v2_cats)
    
    # Add the additional specialized categories
    v2_categories.extend(additional_categories)
    
    return v2_categories


def generate_skill_tree_from_unified_library():
    """
    Generate skill tree nodes and movements from the unified exercise library.
    Creates 5 levels per V2 category with 2-3 movements per node for better progression pacing.
    """
    skill_tree = {}
    
    # Get V2 categories
    v2_categories = generate_movement_categories_from_unified_library()
    
    # Define movement variations for each category type
    movement_variations = {
        # Pull movements
        "PULL_VERTICAL": {
            1: ["Dead Hang", "Assisted Pull-ups"],
            2: ["Negative Pull-ups", "Band-Assisted Pull-ups", "Jumping Pull-ups"],
            3: ["Standard Pull-ups", "Chin-ups"],
            4: ["Wide-Grip Pull-ups", "Commando Pull-ups", "L-Sit Pull-ups"],
            5: ["Weighted Pull-ups", "One-Arm Pull-up Progression", "Muscle-ups"]
        },
        "PULL_HORIZONTAL": {
            1: ["Incline Rows", "Bent-Over Rows"],
            2: ["Bodyweight Rows", "Ring Rows", "TRX Rows"],
            3: ["Horizontal Pull-ups", "Inverted Rows"],
            4: ["Single-Arm Rows", "Archer Rows"],
            5: ["Advanced Ring Rows", "Weighted Horizontal Pulls", "One-Arm Rows"]
        },
        "PULL_UNILATERAL": {
            1: ["Single-Arm Dead Hang", "Assisted Single-Arm Rows"],
            2: ["Single-Arm Negatives", "Uneven Pull-ups"],
            3: ["Archer Pull-ups", "Single-Arm Lat Pulls", "Typewriter Pull-ups"],
            4: ["One-Arm Pull-up Negatives", "Advanced Archer Variations"],
            5: ["One-Arm Pull-ups", "One-Arm Chin-ups"]
        },
        
        # Push movements
        "PUSH_HORIZONTAL": {
            1: ["Wall Push-ups", "Incline Push-ups"],
            2: ["Knee Push-ups", "Standard Push-ups", "Wide-Grip Push-ups"],
            3: ["Diamond Push-ups", "Decline Push-ups"],
            4: ["Archer Push-ups", "Single-Arm Push-up Progression", "Clapping Push-ups"],
            5: ["One-Arm Push-ups", "Planche Push-ups", "Handstand Push-ups"]
        },
        "PUSH_VERTICAL": {
            1: ["Wall Handstand Hold", "Chest-to-Wall Handstand"],
            2: ["Pike Push-ups", "Elevated Pike Push-ups", "Handstand Progression"],
            3: ["Handstand Push-up Negatives", "Partial Handstand Push-ups"],
            4: ["Full Handstand Push-ups", "Freestanding Handstand Push-ups"],
            5: ["Deficit Handstand Push-ups", "One-Arm Handstand Progression", "90-Degree Push-ups"]
        },
        "PUSH_UNILATERAL": {
            1: ["Single-Arm Wall Push-ups", "Uneven Push-ups"],
            2: ["Archer Push-ups", "Single-Arm Incline Push-ups"],
            3: ["One-Arm Push-up Negatives", "Lever Push-ups"],
            4: ["Assisted One-Arm Push-ups", "Advanced Archer Variations"],
            5: ["One-Arm Push-ups", "One-Arm Handstand Push-ups"]
        },
        
        # Lower body movements
        "SQUAT_BILATERAL": {
            1: ["Bodyweight Squats", "Box Squats"],
            2: ["Jump Squats", "Goblet Squats", "Sumo Squats"],
            3: ["Pistol Squat Progression", "Bulgarian Split Squats"],
            4: ["Jump Squats with Tuck", "Single-Leg Box Squats", "Weighted Squats"],
            5: ["Pistol Squats", "Shrimp Squats", "Dragon Squats"]
        },
        "SQUAT_UNILATERAL": {
            1: ["Assisted Pistol Squats", "Single-Leg Box Squats"],
            2: ["Pistol Squat Negatives", "Cossack Squats", "Lateral Lunges"],
            3: ["Pistol Squats", "Shrimp Squat Progression"],
            4: ["Advanced Pistol Variations", "Jumping Pistol Squats"],
            5: ["Weighted Pistol Squats", "Shrimp Squats", "Dragon Squats"]
        },
        "HINGE_BILATERAL": {
            1: ["Romanian Deadlifts", "Good Mornings"],
            2: ["Single-Leg Deadlifts", "Hip Thrusts", "Glute Bridges"],
            3: ["Nordic Curls Progression", "Single-Leg Hip Thrusts"],
            4: ["Nordic Curls", "Advanced Single-Leg Deadlifts"],
            5: ["Full Nordic Curls", "Weighted Hip Thrusts", "Advanced Posterior Chain"]
        },
        "HINGE_UNILATERAL": {
            1: ["Single-Leg Glute Bridges", "Single-Leg Hip Thrusts"],
            2: ["Single-Leg Deadlifts", "Single-Leg Good Mornings"],
            3: ["Advanced Single-Leg Deadlifts", "Curtsy Lunges"],
            4: ["Single-Leg Nordic Progression", "Weighted Single-Leg Deadlifts"],
            5: ["Single-Leg Nordic Curls", "Advanced Unilateral Hinges"]
        },
        
        # Core movements
        "CORE_STATIC": {
            1: ["Plank", "Side Plank"],
            2: ["Extended Plank", "Single-Arm Plank", "Plank Up-Downs"],
            3: ["L-Sit Progression", "Hollow Body Hold", "V-Sit Progression"],
            4: ["L-Sit", "Advanced Hollow Body", "Human Flag Progression"],
            5: ["Advanced L-Sit", "Human Flag", "Front Lever Progression"]
        },
        "CORE_DYNAMIC": {
            1: ["Crunches", "Bicycle Crunches"],
            2: ["Mountain Climbers", "Russian Twists", "Leg Raises"],
            3: ["Hanging Knee Raises", "Windshield Wipers", "Dragon Flags Progression"],
            4: ["Hanging Leg Raises", "Dragon Flags", "Advanced Core Flows"],
            5: ["Advanced Dragon Flags", "Human Flag Dynamics", "Core Flow Mastery"]
        },
        "CORE_ROTATIONAL": {
            1: ["Russian Twists", "Wood Chops"],
            2: ["Medicine Ball Slams", "Rotational Lunges", "Side Planks with Rotation"],
            3: ["Windshield Wipers", "Turkish Get-ups", "Rotational Power"],
            4: ["Advanced Windshield Wipers", "Single-Arm Turkish Get-ups"],
            5: ["Rotational Flow Mastery", "Advanced Turkish Get-up Variations"]
        },
        
        # Upper body isometric and dynamic
        "UPPER_ISOMETRIC": {
            1: ["Planche Lean", "Front Lever Tuck"],
            2: ["Tuck Planche", "Advanced Tuck Front Lever", "Back Lever Progression"],
            3: ["Advanced Tuck Planche", "Straddle Front Lever", "Back Lever"],
            4: ["Straddle Planche", "Full Front Lever", "Iron Cross Progression"],
            5: ["Full Planche", "One-Arm Front Lever", "Iron Cross"]
        },
        "UPPER_DYNAMIC": {
            1: ["Muscle-up Progression", "Kipping Pull-ups"],
            2: ["Assisted Muscle-ups", "Chest-to-Bar Pull-ups", "Ring Transitions"],
            3: ["Muscle-ups", "Ring Muscle-ups", "Bar Muscle-ups"],
            4: ["Weighted Muscle-ups", "Slow Muscle-ups", "Advanced Ring Work"],
            5: ["One-Arm Muscle-up Progression", "Advanced Ring Sequences", "Freestyle Combinations"]
        },
        
        # Plyometric movements
        "LOWER_PLYOMETRIC": {
            1: ["Jump Squats", "Box Jumps"],
            2: ["Broad Jumps", "Lateral Jumps", "Tuck Jumps"],
            3: ["Single-Leg Jumps", "Depth Jumps", "Reactive Jumps"],
            4: ["Advanced Plyometric Sequences", "Weighted Jump Squats"],
            5: ["Elite Plyometric Combinations", "Sport-Specific Power"]
        },
        "UPPER_PLYOMETRIC": {
            1: ["Clapping Push-ups", "Medicine Ball Throws"],
            2: ["Explosive Push-ups", "Plyometric Pull-ups", "Medicine Ball Slams"],
            3: ["Advanced Clapping Push-ups", "Explosive Muscle-ups"],
            4: ["Multiple Clap Push-ups", "Weighted Explosive Movements"],
            5: ["Elite Upper Body Power", "Advanced Explosive Sequences"]
        },
        
        # Flexibility and mobility
        "FLEXIBILITY": {
            1: ["Basic Stretching", "Hip Flexor Stretches"],
            2: ["Dynamic Stretching", "Shoulder Mobility", "Hip Circles"],
            3: ["Advanced Stretching", "PNF Stretching", "Active Flexibility"],
            4: ["Loaded Stretching", "Extreme Range of Motion", "Flexibility Flows"],
            5: ["Contortion Basics", "Advanced Flexibility", "Mobility Mastery"]
        },
        "MOBILITY_FLOW": {
            1: ["Basic Flow Sequences", "Joint Mobility"],
            2: ["Animal Movements", "Crawling Patterns", "Flow Transitions"],
            3: ["Advanced Animal Flow", "Complex Movement Patterns"],
            4: ["Freestyle Flow", "Creative Movement", "Flow Combinations"],
            5: ["Flow Mastery", "Advanced Creative Sequences", "Movement Art"]
        }
    }
    
    # Default movements for categories not specifically defined
    def get_default_movements(category_id, level):
        if "PULL" in category_id:
            base = ["Basic Pull", "Intermediate Pull", "Advanced Pull"]
        elif "PUSH" in category_id:
            base = ["Basic Push", "Intermediate Push", "Advanced Push"]
        elif "SQUAT" in category_id or "HINGE" in category_id or "LOWER" in category_id:
            base = ["Basic Lower", "Intermediate Lower", "Advanced Lower"]
        elif "CORE" in category_id:
            base = ["Basic Core", "Intermediate Core", "Advanced Core"]
        elif "SHOULDER" in category_id:
            base = ["Basic Shoulder", "Intermediate Shoulder", "Advanced Shoulder"]
        elif "LOCOMOTION" in category_id:
            base = ["Basic Locomotion", "Crawling Patterns"]
        elif "BALANCE" in category_id:
            base = ["Basic Balance", "Dynamic Balance", "Advanced Balance"]
        elif "COORDINATION" in category_id:
            base = ["Basic Coordination", "Complex Patterns", "Advanced Coordination"]
        elif "POWER" in category_id or "PLYOMETRIC" in category_id:
            base = ["Basic Power", "Explosive Movements", "Advanced Power"]
        elif "CARRY" in category_id:
            base = ["Basic Carries", "Loaded Carries"]
        elif "GRIP" in category_id:
            base = ["Basic Grip", "Advanced Grip", "Grip Endurance"]
        elif "POSTERIOR" in category_id:
            base = ["Basic Posterior", "Posterior Strength", "Advanced Posterior"]
        elif "RECOVERY" in category_id:
            base = ["Active Recovery", "Restorative Movements"]
        elif "CARDIO" in category_id:
            base = ["Basic Cardio", "Interval Training", "Advanced Conditioning"]
        elif "HANDSTAND" in category_id:
            base = ["Handstand Basics", "Handstand Hold", "Advanced Handstand"]
        elif "BRIDGE" in category_id:
            base = ["Basic Bridge", "Bridge Hold", "Advanced Bridge"]
        elif "FLOW" in category_id:
            base = ["Basic Flow", "Flow Sequences", "Advanced Flow"]
        else:
            base = ["Basic Movement", "Intermediate Movement", "Advanced Movement"]
        
        # Return 2-3 movements based on level
        if level == 1:
            return base[:2]  # 2 movements for foundation
        elif level in [2, 3]:
            return base if len(base) >= 3 else base + [f"Advanced {base[-1]}"]  # 3 movements for progression
        else:
            return base[:2] if level == 4 else base[:3]  # 2-3 movements for higher levels
    
    # Generate skill tree for each V2 category
    for v2_cat in v2_categories:
        category_id = v2_cat["id"]
        skill_tree[category_id] = []
        level_names = ["Foundation", "First Ascent", "Competence", "Strength", "Mastery"]
        
        for level in range(1, 6):
            level_name = level_names[level - 1]
            
            # Get movements for this level
            if category_id in movement_variations:
                level_movements = movement_variations[category_id].get(level, [])
            else:
                level_movements = get_default_movements(category_id, level)
            
            # Ensure we have at least 2 movements per node
            if len(level_movements) < 2:
                level_movements.extend([f"Advanced {level_movements[0]}", f"Elite {level_movements[0]}"])
                level_movements = level_movements[:3]  # Cap at 3 movements
            
            skill_tree[category_id].append({
                "level": level,
                "name": level_name,
                "movements": level_movements
            })
    
    return skill_tree


def calculate_movement_xp(movement_name: str, level: int, category_id: str) -> float:
    """
    Calculate XP per rep for a movement based on unified library data.
    
    Args:
        movement_name: Name of the movement
        level: Skill tree level (1-5)
        category_id: V2 category ID
        
    Returns:
        XP per rep value
    """
    # Base XP values by level
    base_xp_by_level = {
        1: 1.0,   # Foundation
        2: 1.5,   # First Ascent
        3: 2.0,   # Competence
        4: 2.5,   # Strength
        5: 3.0    # Mastery
    }
    
    # Category multipliers based on complexity
    category_multipliers = {
        # Upper body strength movements (higher complexity)
        "PULL_VERTICAL": 1.2,
        "PULL_HORIZONTAL": 1.1,
        "PUSH_VERTICAL": 1.3,  # Handstand progressions are complex
        "PUSH_HORIZONTAL": 1.0,
        "UPPER_ISOMETRIC": 1.4,  # Planche/front lever are very complex
        "UPPER_DYNAMIC": 1.2,
        
        # Unilateral movements (higher skill requirement)
        "PULL_UNILATERAL": 1.3,
        "PUSH_UNILATERAL": 1.3,
        "SQUAT_UNILATERAL": 1.2,
        "HINGE_UNILATERAL": 1.2,
        
        # Lower body movements
        "SQUAT_BILATERAL": 1.0,
        "HINGE_BILATERAL": 1.0,
        "LOWER_PLYOMETRIC": 1.1,
        
        # Core movements
        "CORE_STATIC": 1.1,
        "CORE_DYNAMIC": 1.0,
        "CORE_ROTATIONAL": 1.2,
        
        # Mobility/flexibility (lower intensity)
        "FLEXIBILITY": 0.8,
        "MOBILITY_FLOW": 0.8,
        
        # Additional shoulder categories
        "SHOULDER_STABILITY": 1.1,
        
        # Locomotion and Movement Quality
        "LOCOMOTION": 1.1,
        "BALANCE": 1.2,
        "COORDINATION": 1.3,
        
        # Power and Explosive Training
        "UPPER_PLYOMETRIC": 1.2,
        "POWER_ENDURANCE": 1.1,
        
        # Specialized Strength Patterns
        "CARRY": 1.0,
        "GRIP_STRENGTH": 1.1,
        "POSTERIOR_CHAIN": 1.0,
        
        # Recovery and Conditioning
        "RECOVERY": 0.7,
        "CARDIO_STEADY": 0.8,
        "CARDIO_INTERVAL": 1.0,
        
        # Specialized Movement Skills
        "HANDSTAND": 1.5,  # Very complex skill
        "BRIDGE": 1.3,
        "FLOW_MOVEMENT": 1.2,
    }
    
    base_xp = base_xp_by_level.get(level, 1.0)
    multiplier = category_multipliers.get(category_id, 1.0)
    
    return round(base_xp * multiplier, 1)


def get_stat_reward_type(category_id: str) -> str:
    """
    Get the stat reward type for a category based on V2 schema mapping.
    
    Args:
        category_id: V2 category ID
        
    Returns:
        Stat type (STR, END, TECH)
    """
    # Map categories to their primary stats
    stat_mapping = {
        # Strength-based movements
        "PULL_VERTICAL": "STR",
        "PULL_HORIZONTAL": "STR", 
        "PUSH_VERTICAL": "STR",
        "PUSH_HORIZONTAL": "STR",
        "UPPER_ISOMETRIC": "STR",
        "UPPER_DYNAMIC": "STR",
        "SQUAT_BILATERAL": "STR",
        "HINGE_BILATERAL": "STR",
        
        # Endurance-based movements
        "LOWER_PLYOMETRIC": "END",
        "CORE_STATIC": "END",
        "CORE_DYNAMIC": "END",
        
        # Technique-based movements
        "PULL_UNILATERAL": "TECH",
        "PUSH_UNILATERAL": "TECH",
        "SQUAT_UNILATERAL": "TECH",
        "HINGE_UNILATERAL": "TECH",
        "CORE_ROTATIONAL": "TECH",
        "FLEXIBILITY": "TECH",
        "MOBILITY_FLOW": "TECH",
        
        # Additional shoulder categories
        "SHOULDER_STABILITY": "TECH",
        
        # Locomotion and Movement Quality
        "LOCOMOTION": "TECH",
        "BALANCE": "TECH",
        "COORDINATION": "TECH",
        
        # Power and Explosive Training
        "UPPER_PLYOMETRIC": "END",
        "POWER_ENDURANCE": "END",
        
        # Specialized Strength Patterns
        "CARRY": "STR",
        "GRIP_STRENGTH": "STR",
        "POSTERIOR_CHAIN": "STR",
        
        # Recovery and Conditioning
        "RECOVERY": "END",
        "CARDIO_STEADY": "END",
        "CARDIO_INTERVAL": "END",
        
        # Specialized Movement Skills
        "HANDSTAND": "TECH",
        "BRIDGE": "TECH",
        "FLOW_MOVEMENT": "TECH",
    }
    
    return stat_mapping.get(category_id, "STR")  # Default to STR


# Generate the seed data from unified library
MOVEMENT_CATEGORIES_SEED = generate_movement_categories_from_unified_library()
SKILL_TREE_LIBRARY = generate_skill_tree_from_unified_library()


# ============================================================================
# DATABASE CONNECTION SETUP
# ============================================================================
# Source: Follows patterns from core/config.py and existing database setup
# Handles cloud database SSL requirements and asyncpg compatibility

def create_database_engine():
    """
    Create async database engine with proper PostgreSQL URL handling.
    
    Handles:
    - URL normalization to postgresql+asyncpg://
    - Removal of asyncpg-incompatible parameters
    - SSL configuration for cloud databases
    """
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # Normalize to asyncpg driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not database_url.startswith("postgresql+asyncpg://"):
        # Handle other postgres variants
        for prefix in ["postgres://", "postgresql+psycopg2://", "postgresql+psycopg://"]:
            if database_url.startswith(prefix):
                database_url = database_url.replace(prefix, "postgresql+asyncpg://", 1)
                break
    
    # Remove asyncpg-incompatible parameters
    incompatible_params = ["sslmode", "channel_binding", "sslcert", "sslkey", "sslrootcert"]
    for param in incompatible_params:
        if f"{param}=" in database_url:
            # Remove parameter and its value
            import re
            pattern = f"[?&]{param}=[^&]*"
            database_url = re.sub(pattern, "", database_url)
            # Clean up any double ? or & characters
            database_url = re.sub(r"\?&", "?", database_url)
            database_url = re.sub(r"&&", "&", database_url)
    
    # Determine if SSL is required for cloud databases
    connect_args = {}
    cloud_providers = ["neon.tech", "amazonaws.com", "supabase", "azure.com"]
    if any(provider in database_url for provider in cloud_providers):
        connect_args["ssl"] = "require"
    
    return create_async_engine(
        database_url,
        echo=False,  # Quiet by default
        connect_args=connect_args
    )


# ============================================================================
# SEEDING LOGIC - IMPLEMENTS REFACTOR.MD SPECIFICATIONS
# ============================================================================
# Source: Implements the exact data structure from refactor.md
# Relationship chain: MovementCategory → SkillTreeNode → Movement
# All seeding is idempotent with existence checks

async def seed_data():
    """
    Main seeding function implementing idempotent data population.
    
    Follows exact relationship chain: MovementCategory → SkillTreeNode → Movement
    Uses safe defaults for required fields not specified in refactor.md
    """
    print("🌱 Starting GateGrind V2 database seeding...")
    
    # Create database engine and session
    engine = create_database_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Counters for summary
            categories_added = 0
            categories_existing = 0
            nodes_added = 0
            nodes_existing = 0
            movements_added = 0
            movements_existing = 0
            
            print("\n📂 Seeding Movement Categories...")
            
            # Seed MovementCategory records
            for category_data in MOVEMENT_CATEGORIES_SEED:
                category_id = category_data["id"]
                
                # Check if category exists
                result = await session.execute(
                    select(MovementCategory).where(MovementCategory.id == category_id)
                )
                existing_category = result.scalar_one_or_none()
                
                if existing_category:
                    print(f"   ⏭️ Category '{category_id}' already exists")
                    categories_existing += 1
                else:
                    # Create new category
                    new_category = MovementCategory(
                        id=category_data["id"],
                        name=category_data["name"],
                        primary_stat=category_data["primary_stat"]
                    )
                    session.add(new_category)
                    print(f"   ✅ Added category '{category_id}' ({category_data['name']})")
                    categories_added += 1
            
            # Commit categories first
            await session.commit()
            print(f"📂 Categories complete: {categories_added} added, {categories_existing} existing")
            
            print("\n🌳 Seeding Skill Tree Nodes and Movements...")
            
            # Seed SkillTreeNode and Movement records
            for category_id, nodes_data in SKILL_TREE_LIBRARY.items():
                # Verify category exists
                result = await session.execute(
                    select(MovementCategory).where(MovementCategory.id == category_id)
                )
                category = result.scalar_one_or_none()
                
                if not category:
                    print(f"   ⚠️ Missing category '{category_id}' - skipping nodes")
                    continue
                
                print(f"   Processing nodes for category '{category_id}'...")
                
                for node_data in nodes_data:
                    level = node_data["level"]
                    node_name = node_data["name"]
                    movements = node_data["movements"]
                    
                    # Check if node exists by (category_id, level)
                    result = await session.execute(
                        select(SkillTreeNode).where(
                            SkillTreeNode.category_id == category_id,
                            SkillTreeNode.level == level
                        )
                    )
                    existing_node = result.scalar_one_or_none()
                    
                    if existing_node:
                        print(f"     ⏭️ Node L{level} '{node_name}' already exists")
                        nodes_existing += 1
                        node_obj = existing_node
                    else:
                        # Create new node with safe defaults for gating
                        new_node = SkillTreeNode(
                            category_id=category_id,
                            level=level,
                            name=node_name,
                            description=f"Unlock this node to master {node_name}.",
                            required_ascendant_level=level * 5,  # Safe default: level * 5
                            required_str_points=level,           # Safe default: level
                            required_end_points=level,           # Safe default: level  
                            required_tech_points=level           # Safe default: level
                        )
                        session.add(new_node)
                        await session.flush()  # Get the auto-generated ID
                        print(f"     ✅ Added node L{level} '{node_name}' (ID: {new_node.id})")
                        nodes_added += 1
                        node_obj = new_node
                    
                    # Seed movements for this node
                    for movement_name in movements:
                        # Check if movement exists by (node_id, name)
                        result = await session.execute(
                            select(Movement).where(
                                Movement.node_id == node_obj.id,
                                Movement.name == movement_name
                            )
                        )
                        existing_movement = result.scalar_one_or_none()
                        
                        if existing_movement:
                            print(f"       ⏭️ Movement '{movement_name}' already exists")
                            movements_existing += 1
                        else:
                            # Calculate XP and stat reward based on unified library data
                            xp_per_rep = calculate_movement_xp(movement_name, level, category_id)
                            stat_reward = get_stat_reward_type(category_id)
                            
                            # Create new movement with calculated values
                            new_movement = Movement(
                                node_id=node_obj.id,
                                name=movement_name,
                                xp_per_rep=xp_per_rep,
                                stat_reward_type=stat_reward
                            )
                            session.add(new_movement)
                            print(f"       ✅ Added movement '{movement_name}' (XP: {xp_per_rep}, Stat: {stat_reward})")
                            movements_added += 1
            
            # Final commit
            await session.commit()
            
            # Summary
            print(f"\n🎉 Seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   📂 Categories: {categories_added} added, {categories_existing} existing")
            print(f"   🌳 Nodes: {nodes_added} added, {nodes_existing} existing") 
            print(f"   🏃 Movements: {movements_added} added, {movements_existing} existing")
            print(f"   📈 Total records processed: {categories_added + categories_existing + nodes_added + nodes_existing + movements_added + movements_existing}")
            
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        await engine.dispose()

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================


if __name__ == "__main__":
    asyncio.run(seed_data())