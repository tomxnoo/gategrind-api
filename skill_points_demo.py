#!/usr/bin/env python3
"""
Test script to verify skill points deduction functionality.

This script tests the skill point system to ensure:
1. Skill points are properly deducted when unlocking nodes
2. Requirements are properly validated
3. The system works end-to-end
"""

import asyncio
import sys
import os

# Enable development mode to allow database access
os.environ["DEVELOPMENT_MODE"] = "true"

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application.services.progression_service import ProgressionService
from app.infrastructure.database.models.v2 import Ascendant, AscendantStats
from app.infrastructure.database.session import get_async_session
from app.application.game_data.skill_tree_config import get_node_by_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_test_user(session: AsyncSession) -> Ascendant:
    """Create a test user with sufficient skill points."""
    # Check if test user exists
    stmt = select(Ascendant).where(Ascendant.discord_id == "test_user_123456789")
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print(f"Using existing test user: {existing_user.username} (ID: {existing_user.id})")
        return existing_user
    
    # Create new test user
    test_user = Ascendant(
        discord_id="test_user_123456789",  # 20 characters max
        username="TestSkillPointsUser",
        level=10,  # High level to meet requirements
        global_xp=5000,
        strength_points=20,  # Plenty of skill points
        endurance_points=20,
        technique_points=20,
        aura=500
    )
    
    # Create stats for the user
    test_stats = AscendantStats(
        ascendant_id=test_user.id,
        str_level=5,
        end_level=5,
        tech_level=5,
        str_xp=2000,
        end_xp=2000,
        tech_xp=2000,
        str_value=1500,  # High enough to meet stat requirements
        end_value=1500,
        tech_value=1500
    )
    
    session.add(test_user)
    await session.flush()  # Get the user ID
    
    test_stats.ascendant_id = test_user.id
    session.add(test_stats)
    
    await session.commit()
    print(f"Created test user: {test_user.username} (ID: {test_user.id})")
    return test_user


async def test_skill_point_deduction():
    """Test the skill point deduction system."""
    print("=== Testing Skill Point Deduction System ===\n")
    
    # Get database session
    session_gen = get_async_session()
    session = await session_gen.__anext__()
    
    try:
        # Create test user
        user = await create_test_user(session)
        
        # Get progression service
        progression_service = ProgressionService(session=session)
        
        # Get user's current skill points
        print(f"Initial skill points:")
        print(f"  Strength: {user.strength_points}")
        print(f"  Endurance: {user.endurance_points}")
        print(f"  Technique: {user.technique_points}")
        print()
        
        # Test with upper_dynamic_2 node (has skill point costs)
        node_id = "upper_dynamic_2"
        node_config = get_node_by_id(node_id)
        
        if not node_config:
            print(f"[ERROR] Node '{node_id}' not found in configuration")
            return
        
        print(f"Testing with node: {node_config.name}")
        print(f"Required skill points:")
        print(f"  Strength: {node_config.requirements.strength_skill_points}")
        print(f"  Endurance: {node_config.requirements.endurance_skill_points}")
        print(f"  Technique: {node_config.requirements.technique_skill_points}")
        print()
        
        # Check if user already has this node unlocked
        from app.infrastructure.database.models.v2 import UserSkillProgress
        existing_stmt = select(UserSkillProgress).where(
            UserSkillProgress.ascendant_id == user.id,
            UserSkillProgress.node_id == node_id
        )
        existing_result = await session.execute(existing_stmt)
        existing_progress = existing_result.scalar_one_or_none()
        
        if existing_progress:
            print(f"[WARNING] Node '{node_id}' is already unlocked. Deleting for test...")
            await session.delete(existing_progress)
            await session.commit()
        
        # Make sure user has prerequisite node (upper_dynamic_1)
        prereq_id = "upper_dynamic_1"
        prereq_stmt = select(UserSkillProgress).where(
            UserSkillProgress.ascendant_id == user.id,
            UserSkillProgress.node_id == prereq_id
        )
        prereq_result = await session.execute(prereq_stmt)
        prereq_progress = prereq_result.scalar_one_or_none()
        
        if not prereq_progress:
            print(f"Adding prerequisite node: {prereq_id}")
            prereq_progress = UserSkillProgress(
                ascendant_id=user.id,
                node_id=prereq_id
            )
            session.add(prereq_progress)
            await session.commit()
        
        # Refresh user data
        await session.refresh(user)
        
        # Attempt to unlock the skill
        try:
            print(f"Attempting to unlock '{node_id}'...")
            result = await progression_service.unlock_skill(user.id, node_id)
            
            print("[SUCCESS] Skill unlock successful!")
            print(f"Unlock message: {result.unlock_message}")
            
            if result.skill_points_deducted:
                print(f"Skill points deducted:")
                for point_type, amount in result.skill_points_deducted.items():
                    if amount > 0:
                        print(f"  {point_type}: {amount}")
            
            print(f"Aura change: {result.new_aura - result.previous_aura}")
            
            # Check user's skill points after unlock
            await session.refresh(user)
            print(f"\nFinal skill points:")
            print(f"  Strength: {user.strength_points}")
            print(f"  Endurance: {user.endurance_points}")
            print(f"  Technique: {user.technique_points}")
            
        except Exception as e:
            print(f"[ERROR] Skill unlock failed: {e}")
            
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(test_skill_point_deduction())