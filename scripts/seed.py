#!/usr/bin/env python3
"""
Database Seeding Script for V2 Schema

This script populates the movement_categories, skill_tree_nodes, and movements tables
with foundational data from the Game Design Document (refactor.md).

The script is idempotent - it can be run safely multiple times without creating duplicates.
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

# Seed data from refactor.md
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


async def create_database_engine():
    """Create async database engine using settings"""
    settings = get_settings()
    
    # Convert PostgreSQL URL to async version
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(database_url, echo=False)
    return engine


async def seed_data():
    """Main seeding function"""
    print("🌱 Starting Database Seeding")
    print("=" * 50)
    
    # Create database engine and session
    engine = await create_database_engine()
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # Seed Movement Categories
            print("\n📂 Seeding Movement Categories...")
            categories_added = 0
            
            for category_data in MOVEMENT_CATEGORIES_SEED:
                # Check if category already exists
                result = await session.execute(
                    select(MovementCategory).where(MovementCategory.id == category_data["id"])
                )
                existing_category = result.scalar_one_or_none()
                
                if existing_category:
                    print(f"   ⏭️  Skipping existing category: {category_data['id']}")
                else:
                    # Create new category
                    new_category = MovementCategory(
                        id=category_data["id"],
                        name=category_data["name"],
                        primary_stat=category_data["primary_stat"]
                    )
                    session.add(new_category)
                    categories_added += 1
                    print(f"   ✅ Added category: {category_data['id']} - {category_data['name']}")
            
            # Commit categories before proceeding
            await session.commit()
            print(f"\n📊 Movement Categories Summary: {categories_added} new categories added")
            
            # Seed Skill Tree Nodes and Movements
            print("\n🌳 Seeding Skill Tree Nodes and Movements...")
            nodes_added = 0
            movements_added = 0
            
            for category_id, nodes_list in SKILL_TREE_LIBRARY.items():
                # Get the primary stat for this category
                result = await session.execute(
                    select(MovementCategory).where(MovementCategory.id == category_id)
                )
                category = result.scalar_one_or_none()
                
                if not category:
                    print(f"   ⚠️  Warning: Category {category_id} not found, skipping nodes")
                    continue
                
                primary_stat = category.primary_stat
                print(f"\n   📁 Processing category: {category_id} (Primary Stat: {primary_stat})")
                
                for node_data in nodes_list:
                    # Check if node already exists
                    result = await session.execute(
                        select(SkillTreeNode).where(
                            SkillTreeNode.category_id == category_id,
                            SkillTreeNode.level == node_data["level"]
                        )
                    )
                    existing_node = result.scalar_one_or_none()
                    
                    if existing_node:
                        print(f"      ⏭️  Skipping existing node: {node_data['name']} (Level {node_data['level']})")
                        node_id = existing_node.id
                    else:
                        # Create new skill tree node
                        new_node = SkillTreeNode(
                            category_id=category_id,
                            level=node_data["level"],
                            name=node_data["name"],
                            description=f"Unlock this node to master {node_data['name']}.",
                            required_ascendant_level=node_data["level"] * 5,
                            required_str_points=node_data["level"],
                            required_end_points=node_data["level"],
                            required_tech_points=node_data["level"]
                        )
                        session.add(new_node)
                        await session.flush()  # Flush to get the ID
                        node_id = new_node.id
                        nodes_added += 1
                        print(f"      ✅ Added node: {node_data['name']} (Level {node_data['level']})")
                    
                    # Seed movements for this node
                    for movement_name in node_data["movements"]:
                        # Check if movement already exists for this node
                        result = await session.execute(
                            select(Movement).where(
                                Movement.node_id == node_id,
                                Movement.name == movement_name
                            )
                        )
                        existing_movement = result.scalar_one_or_none()
                        
                        if existing_movement:
                            print(f"         ⏭️  Skipping existing movement: {movement_name}")
                        else:
                            # Create new movement
                            new_movement = Movement(
                                node_id=node_id,
                                name=movement_name,
                                xp_per_rep=1.0,
                                stat_reward_type=primary_stat
                            )
                            session.add(new_movement)
                            movements_added += 1
                            print(f"         ✅ Added movement: {movement_name}")
            
            # Final commit
            await session.commit()
            
            print(f"\n📊 Skill Tree Summary:")
            print(f"   🌳 Skill Tree Nodes: {nodes_added} new nodes added")
            print(f"   🏃 Movements: {movements_added} new movements added")
            
            print(f"\n🎉 Database seeding completed successfully!")
            print("=" * 50)
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            await session.close()
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())