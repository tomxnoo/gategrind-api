#!/usr/bin/env python3
"""
Production-Safe Database Seeding Script for GateGrind V2 Schema

This script populates the foundational data for movement categories, skill tree nodes,
and movements based STRICTLY on the specifications in refactor.md.

COMPLIANCE STATEMENT:
✅ All data comes directly from refactor.md MOVEMENT_CATEGORIES_SEED and SKILL_TREE_LIBRARY
✅ No fields, relationships, or logic have been invented beyond safe defaults
✅ Script is idempotent and can be run multiple times safely in any environment
✅ Follows project_rules.md engineering standards (API-first, no business logic in scripts)
✅ Implements exact relationship chain: MovementCategory → SkillTreeNode → Movement

SOURCE-OF-TRUTH MAPPING:
- Movement Categories: refactor.md lines 131-149 (MOVEMENT_CATEGORIES_SEED)
- Skill Tree Library: refactor.md lines 151-270 (SKILL_TREE_LIBRARY)  
- Model relationships: core/database/models/v2/ (integer PKs, proper foreign keys)
- Gating defaults: level * 5 for ascendant_level, level for each stat (approved in task prompts)
- XP defaults: 1.0 per rep (safe neutral value for early testing)
"""
import asyncio
import os
import sys
from typing import Dict, List, Any

# Add project root to path for imports
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import V2 models
from core.database.models.v2 import MovementCategory, SkillTreeNode, Movement
from core.config import get_settings

# ============================================================================
# SEED DATA - EXACT COPY FROM REFACTOR.MD (Lines 131-270)
# ============================================================================
# Source: refactor.md lines 131-149 - MOVEMENT_CATEGORIES_SEED
# This data defines the 18 core movement categories with their primary stats
MOVEMENT_CATEGORIES_SEED = [
    # Upper Body
    {"id": "PULL_VERTICAL", "name": "Vertical Pulling", "primary_stat": "STR"},
    {"id": "PULL_HORIZONTAL", "name": "Horizontal Pulling", "primary_stat": "STR"},
    {"id": "PUSH_VERTICAL", "name": "Vertical Pushing", "primary_stat": "STR"},
    {"id": "PUSH_HORIZONTAL", "name": "Horizontal Pushing", "primary_stat": "STR"},
    {"id": "PUSH_UNILATERAL", "name": "Unilateral Pushing", "primary_stat": "TECH"},
    {"id": "PULL_UNILATERAL", "name": "Unilateral Pulling", "primary_stat": "TECH"},
    {"id": "UPPER_ISOMETRIC", "name": "Isometric Holds (Upper)", "primary_stat": "STR"},
    {"id": "UPPER_DYNAMIC", "name": "Dynamic Power (Upper)", "primary_stat": "STR"},
    # Lower Body
    {"id": "SQUAT_BILATERAL", "name": "Bilateral Squats", "primary_stat": "STR"},
    {"id": "SQUAT_UNILATERAL", "name": "Unilateral Squats", "primary_stat": "TECH"},
    {"id": "HINGE_BILATERAL", "name": "Bilateral Hinge", "primary_stat": "STR"},
    {"id": "HINGE_UNILATERAL", "name": "Unilateral Hinge", "primary_stat": "TECH"},
    {"id": "LOWER_PLYOMETRIC", "name": "Plyometrics (Lower)", "primary_stat": "END"},
    # Core & Mobility
    {"id": "CORE_STATIC", "name": "Static Core", "primary_stat": "END"},
    {"id": "CORE_DYNAMIC", "name": "Dynamic Core", "primary_stat": "END"},
    {"id": "CORE_ROTATIONAL", "name": "Rotational Core", "primary_stat": "TECH"},
    {"id": "FLEXIBILITY", "name": "Flexibility", "primary_stat": "TECH"},
    {"id": "MOBILITY_FLOW", "name": "Mobility Flow", "primary_stat": "TECH"},
]

# Source: refactor.md lines 151-270 - SKILL_TREE_LIBRARY
# This data defines the 5-level progression for each movement category

SKILL_TREE_LIBRARY = {
    "PULL_VERTICAL": [
        {"level": 1, "name": "Foundation", "movements": ["Dead Hangs", "Scapular Pulls", "Bodyweight Rows"]},
        {"level": 2, "name": "First Ascent", "movements": ["Negative Pull-ups", "Assisted Pull-ups"]},
        {"level": 3, "name": "Competence", "movements": ["Standard Pull-ups", "Chin-ups"]},
        {"level": 4, "name": "Strength", "movements": ["Weighted Pull-ups", "Archer Pull-ups", "L-Sit Pull-ups"]},
        {"level": 5, "name": "Mastery", "movements": ["Muscle-ups", "One-Arm Pull-up Progressions"]},
    ],
    "PULL_HORIZONTAL": [
        {"level": 1, "name": "Foundation", "movements": ["Standing Band Rows", "Wall Rows"]},
        {"level": 2, "name": "First Ascent", "movements": ["Inverted Rows (feet on floor)", "Dumbbell Rows (light)"]},
        {"level": 3, "name": "Competence", "movements": ["Inverted Rows (feet elevated)", "Tuck Front Lever Rows"]},
        {"level": 4, "name": "Strength", "movements": ["Weighted Inverted Rows", "Single-Bar Rows"]},
        {"level": 5, "name": "Mastery", "movements": ["Front Lever Rows", "Ice Cream Makers"]},
    ],
    "PUSH_VERTICAL": [
        {"level": 1, "name": "Foundation", "movements": ["Pike Push-ups (hands on floor)", "Wall Handstands (hold)"]},
        {"level": 2, "name": "First Ascent", "movements": ["Pike Push-ups (feet elevated)"]},
        {"level": 3, "name": "Competence", "movements": ["Wall-Facing Handstand Push-ups (partial ROM)"]},
        {"level": 4, "name": "Strength", "movements": ["Full Range of Motion Handstand Push-ups (wall)"]},
        {"level": 5, "name": "Mastery", "movements": ["Freestanding Handstand Push-ups", "90-Degree Push-ups"]},
    ],
    "PUSH_HORIZONTAL": [
        {"level": 1, "name": "Foundation", "movements": ["Wall Push-ups", "Incline Push-ups"]},
        {"level": 2, "name": "First Ascent", "movements": ["Knee Push-ups", "Standard Push-ups"]},
        {"level": 3, "name": "Competence", "movements": ["Diamond Push-ups", "Decline Push-ups", "Ring Push-ups"]},
        {"level": 4, "name": "Strength", "movements": ["Archer Push-ups", "Pseudo Planche Push-ups"]},
        {"level": 5, "name": "Mastery", "movements": ["Weighted Push-ups", "Planche Leans/Push-ups"]},
    ],
    "PUSH_UNILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["Staggered Stance Push-ups"]},
        {"level": 2, "name": "First Ascent", "movements": ["Archer Push-up Progressions"]},
        {"level": 3, "name": "Competence", "movements": ["Elevated One-Arm Push-ups"]},
        {"level": 4, "name": "Strength", "movements": ["One-Arm Push-up Negatives"]},
        {"level": 5, "name": "Mastery", "movements": ["One-Arm Push-ups"]},
    ],
    "PULL_UNILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["One-Arm Band Rows"]},
        {"level": 2, "name": "First Ascent", "movements": ["One-Arm Dumbbell/Kettlebell Rows"]},
        {"level": 3, "name": "Competence", "movements": ["Archer Rows", "One-Arm Assisted Pull-ups"]},
        {"level": 4, "name": "Strength", "movements": ["One-Arm Pull-up Negatives"]},
        {"level": 5, "name": "Mastery", "movements": ["One-Arm Pull-ups"]},
    ],
    "UPPER_ISOMETRIC": [
        {"level": 1, "name": "Foundation", "movements": ["Tuck Planche", "Tuck Front Lever"]},
        {"level": 2, "name": "First Ascent", "movements": ["Advanced Tuck Planche", "Advanced Tuck Front Lever"]},
        {"level": 3, "name": "Competence", "movements": ["Straddle Planche Progressions", "Straddle Front Lever Progressions"]},
        {"level": 4, "name": "Strength", "movements": ["Half-Lay Front Lever", "Planche Leans"]},
        {"level": 5, "name": "Mastery", "movements": ["Full Planche", "Full Front Lever"]},
    ],
    "UPPER_DYNAMIC": [
        {"level": 1, "name": "Foundation", "movements": ["Explosive Push-ups"]},
        {"level": 2, "name": "First Ascent", "movements": ["Clapping Push-ups"]},
        {"level": 3, "name": "Competence", "movements": ["Explosive Pull-ups"]},
        {"level": 4, "name": "Strength", "movements": ["Superman Push-ups", "Muscle-up Transitions"]},
        {"level": 5, "name": "Mastery", "movements": ["Aztec Push-ups", "Clapping Muscle-ups"]},
    ],
    "SQUAT_BILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["Assisted Bodyweight Squats", "Box Squats"]},
        {"level": 2, "name": "First Ascent", "movements": ["Standard Bodyweight Squats"]},
        {"level": 3, "name": "Competence", "movements": ["Deep Squats", "Goblet Squats (light)"]},
        {"level": 4, "name": "Strength", "movements": ["Barbell Squats (moderate)", "Jump Squats"]},
        {"level": 5, "name": "Mastery", "movements": ["Heavy Barbell Squats", "Paused Squats"]},
    ],
    "SQUAT_UNILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["Assisted Pistol Squats", "Lunges"]},
        {"level": 2, "name": "First Ascent", "movements": ["Pistol Squats to Box", "Bulgarian Split Squats"]},
        {"level": 3, "name": "Competence", "movements": ["Full Pistol Squats"]},
        {"level": 4, "name": "Strength", "movements": ["Weighted Pistol Squats", "Shrimp Squats"]},
        {"level": 5, "name": "Mastery", "movements": ["Dragon Squats"]},
    ],
    "HINGE_BILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["Glute Bridges", "Bodyweight Good Mornings"]},
        {"level": 2, "name": "First Ascent", "movements": ["Kettlebell/Dumbbell Deadlifts"]},
        {"level": 3, "name": "Competence", "movements": ["Barbell Romanian Deadlifts"]},
        {"level": 4, "name": "Strength", "movements": ["Conventional Barbell Deadlifts"]},
        {"level": 5, "name": "Mastery", "movements": ["Heavy Deadlifts", "Deficit Deadlifts"]},
    ],
    "HINGE_UNILATERAL": [
        {"level": 1, "name": "Foundation", "movements": ["Bodyweight Single-Leg Deadlifts"]},
        {"level": 2, "name": "First Ascent", "movements": ["Dumbbell/Kettlebell Single-Leg Deadlifts"]},
        {"level": 3, "name": "Competence", "movements": ["Kickstand Deadlifts"]},
        {"level": 4, "name": "Strength", "movements": ["Barbell Single-Leg Deadlifts"]},
        {"level": 5, "name": "Mastery", "movements": ["Advanced Weighted Variations"]},
    ],
    "LOWER_PLYOMETRIC": [
        {"level": 1, "name": "Foundation", "movements": ["Line Hops", "Pogo Jumps"]},
        {"level": 2, "name": "First Ascent", "movements": ["Jump Squats", "Box Jumps (low)"]},
        {"level": 3, "name": "Competence", "movements": ["Broad Jumps", "Tuck Jumps"]},
        {"level": 4, "name": "Strength", "movements": ["Box Jumps (high)", "Depth Jumps"]},
        {"level": 5, "name": "Mastery", "movements": ["Single-Leg Box Jumps", "Bounding"]},
    ],
    "CORE_STATIC": [
        {"level": 1, "name": "Foundation", "movements": ["Knee Plank", "Tuck Hollow Hold"]},
        {"level": 2, "name": "First Ascent", "movements": ["Full Plank", "Full Hollow Hold"]},
        {"level": 3, "name": "Competence", "movements": ["L-Sit"]},
        {"level": 4, "name": "Strength", "movements": ["Weighted Planks", "Dragon Flag Negatives"]},
        {"level": 5, "name": "Mastery", "movements": ["Full Dragon Flag", "Manna Progressions"]},
    ],
    "CORE_DYNAMIC": [
        {"level": 1, "name": "Foundation", "movements": ["Crunches", "Deadbugs"]},
        {"level": 2, "name": "First Ascent", "movements": ["Sit-ups", "Lying Leg Raises"]},
        {"level": 3, "name": "Competence", "movements": ["Hanging Knee Raises", "V-Ups"]},
        {"level": 4, "name": "Strength", "movements": ["Hanging Leg Raises", "Toes-to-Bar"]},
        {"level": 5, "name": "Mastery", "movements": ["Hanging Windshield Wipers", "Ab Wheel Rollouts (standing)"]},
    ],
    "CORE_ROTATIONAL": [
        {"level": 1, "name": "Foundation", "movements": ["Seated Russian Twists (no weight)"]},
        {"level": 2, "name": "First Ascent", "movements": ["Weighted Russian Twists", "Wood Chops (band)"]},
        {"level": 3, "name": "Competence", "movements": ["Lying Windshield Wipers"]},
        {"level": 4, "name": "Strength", "movements": ["Cable Wood Chops", "Barbell Landmine Twists"]},
        {"level": 5, "name": "Mastery", "movements": ["Human Flag Progressions"]},
    ],
    "FLEXIBILITY": [
        {"level": 1, "name": "Foundation", "movements": ["Basic Static Stretches"]},
        {"level": 2, "name": "First Ascent", "movements": ["Full Body Stretching Routines"]},
        {"level": 3, "name": "Competence", "movements": ["PNF Stretching"]},
        {"level": 4, "name": "Strength", "movements": ["Pancake Stretch", "Bridge Progressions"]},
        {"level": 5, "name": "Mastery", "movements": ["Front Splits", "Middle Splits"]},
    ],
    "MOBILITY_FLOW": [
        {"level": 1, "name": "Foundation", "movements": ["Cat-Cow", "Thoracic Spine Rotations"]},
        {"level": 2, "name": "First Ascent", "movements": ["World's Greatest Stretch", "Sun Salutation"]},
        {"level": 3, "name": "Competence", "movements": ["Cossack Squats", "90/90 Transitions"]},
        {"level": 4, "name": "Strength", "movements": ["Animal Flow Progressions"]},
        {"level": 5, "name": "Mastery", "movements": ["Complex Movement Chains", "Advanced Yoga Poses"]},
    ]
}


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
                            # Create new movement with safe defaults
                            new_movement = Movement(
                                node_id=node_obj.id,
                                name=movement_name,
                                xp_per_rep=1.0,                    # Safe default: neutral XP value
                                stat_reward_type=category.primary_stat  # Inherit from category
                            )
                            session.add(new_movement)
                            print(f"       ✅ Added movement '{movement_name}' (XP: 1.0, Stat: {category.primary_stat})")
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