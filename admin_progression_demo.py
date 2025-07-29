#!/usr/bin/env python3
"""
Test script for admin progression commands.

This script demonstrates how to use the new admin endpoints to:
1. Grant skill points for testing
2. Level up users
3. Grant stats to meet skill node requirements
4. Test skill unlocking with proper progression
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


async def test_admin_progression():
    """Test the admin progression commands."""
    print("=== Testing Admin Progression Commands ===\n")
    
    # Get database session
    session_gen = get_async_session()
    session = await session_gen.__anext__()
    
    try:
        # Create or get test user
        user = await create_test_user(session)
        
        print(f"Starting test with user: {user.username} (ID: {user.id})")
        print(f"Initial state:")
        print(f"  Level: {user.level}")
        print(f"  Skill Points - STR: {user.strength_points}, END: {user.endurance_points}, TECH: {user.technique_points}")
        print(f"  Stats - STR: {user.stats.str_value if user.stats else 10}, END: {user.stats.end_value if user.stats else 10}, TECH: {user.stats.tech_value if user.stats else 10}")
        print()
        
        # Create progression service without session for transaction management
        progression_service = ProgressionService()
        
        # Test 1: Grant XP to level up (this should give skill points)
        print("--- Test 1: Granting XP to level up ---")
        result = await progression_service.add_xp(user.id, 2000, "global")
        await session.refresh(user)
        
        print(f"After granting 2000 global XP:")
        print(f"  Level: {user.level} (was {result.level_changes.get('global', {}).get('previous', 1) if result.level_changes else 1})")
        print(f"  Skill Points - STR: {user.strength_points}, END: {user.endurance_points}, TECH: {user.technique_points}")
        print(f"  Aura: {user.aura}")
        print()
        
        # Test 2: Grant additional skill points directly
        print("--- Test 2: Granting skill points directly ---")
        original_str = user.strength_points
        original_end = user.endurance_points
        original_tech = user.technique_points
        
        user.strength_points += 10
        user.endurance_points += 5
        user.technique_points += 5
        await session.commit()
        await session.refresh(user)
        
        print(f"After granting additional skill points:")
        print(f"  Skill Points - STR: {user.strength_points} (+{user.strength_points - original_str})")
        print(f"  Skill Points - END: {user.endurance_points} (+{user.endurance_points - original_end})")
        print(f"  Skill Points - TECH: {user.technique_points} (+{user.technique_points - original_tech})")
        print()
        
        # Test 3: Grant stats to meet skill node requirements
        print("--- Test 3: Granting stats to meet node requirements ---")
        result = await progression_service.add_stat_rewards(user.id, 1500, 1000, 1000)
        await session.refresh(user)
        
        print(f"After granting stats:")
        print(f"  Stats - STR: {user.stats.str_value}, END: {user.stats.end_value}, TECH: {user.stats.tech_value}")
        if result.stat_points_awarded:
            total_milestone_points = sum(result.stat_points_awarded.values())
            print(f"  Milestone rewards: {total_milestone_points} skill points")
        print()
        
        # Test 4: Now try to unlock a skill node that requires skill points
        print("--- Test 4: Testing skill node unlocking ---")
        test_node_id = "upper_dynamic_2"
        node_config = get_node_by_id(test_node_id)
        
        if node_config:
            print(f"Testing unlock for: {node_config.name}")
            print(f"Requirements:")
            print(f"  Min Level: {node_config.requirements.min_ascendant_level}")
            print(f"  Stat Requirements - STR: {node_config.requirements.str_points}, END: {node_config.requirements.end_points}, TECH: {node_config.requirements.tech_points}")
            print(f"  Skill Point Costs - STR: {node_config.requirements.strength_skill_points}, END: {node_config.requirements.endurance_skill_points}, TECH: {node_config.requirements.technique_skill_points}")
            print()
            
            print(f"Current user state:")
            print(f"  Level: {user.level} (req: {node_config.requirements.min_ascendant_level})")
            print(f"  Stats - STR: {user.stats.str_value} (req: {node_config.requirements.str_points}), END: {user.stats.end_value} (req: {node_config.requirements.end_points}), TECH: {user.stats.tech_value} (req: {node_config.requirements.tech_points})")
            print(f"  Skill Points - STR: {user.strength_points} (cost: {node_config.requirements.strength_skill_points}), END: {user.endurance_points} (cost: {node_config.requirements.endurance_skill_points}), TECH: {user.technique_points} (cost: {node_config.requirements.technique_skill_points})")
            print()
            
            # Check if user meets all requirements
            can_unlock = (
                user.level >= node_config.requirements.min_ascendant_level and
                user.stats.str_value >= node_config.requirements.str_points and
                user.stats.end_value >= node_config.requirements.end_points and
                user.stats.tech_value >= node_config.requirements.tech_points and
                user.strength_points >= node_config.requirements.strength_skill_points and
                user.endurance_points >= node_config.requirements.endurance_skill_points and
                user.technique_points >= node_config.requirements.technique_skill_points
            )
            
            if can_unlock:
                print("[SUCCESS] User meets all requirements! Attempting unlock...")
                
                # Make sure prerequisite is unlocked first
                await ensure_prerequisite(session, user.id, "upper_dynamic_1")
                
                try:
                    result = await progression_service.unlock_skill(user.id, test_node_id)
                    print(f"[SUCCESS] Skill unlocked: {result.node_name}")
                    
                    if result.skill_points_deducted:
                        print("Skill points deducted:")
                        for point_type, amount in result.skill_points_deducted.items():
                            if amount > 0:
                                print(f"  {point_type}: {amount}")
                    
                    print(f"Aura change: +{result.new_aura - result.previous_aura}")
                    
                    # Show final state
                    await session.refresh(user)
                    print(f"\nFinal user state:")
                    print(f"  Skill Points - STR: {user.strength_points}, END: {user.endurance_points}, TECH: {user.technique_points}")
                    print(f"  Aura: {user.aura}")
                    
                except Exception as e:
                    print(f"[ERROR] Skill unlock failed: {e}")
            else:
                print("[INFO] User does not meet all requirements yet")
                missing = []
                if user.level < node_config.requirements.min_ascendant_level:
                    missing.append(f"Level {node_config.requirements.min_ascendant_level} (current: {user.level})")
                if user.stats.str_value < node_config.requirements.str_points:
                    missing.append(f"STR stat {node_config.requirements.str_points} (current: {user.stats.str_value})")
                if user.strength_points < node_config.requirements.strength_skill_points:
                    missing.append(f"STR skill points {node_config.requirements.strength_skill_points} (current: {user.strength_points})")
                print(f"Missing: {', '.join(missing)}")
        else:
            print(f"[ERROR] Node '{test_node_id}' not found")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await session.close()


async def create_test_user(session: AsyncSession) -> Ascendant:
    """Create or get a test user."""
    stmt = select(Ascendant).where(Ascendant.discord_id == "admin_test_123456")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        print(f"Using existing test user: {user.username}")
        return user
    
    # Create new test user
    user = Ascendant(
        discord_id="admin_test_123456",
        username="AdminTestUser",
        level=1,
        global_xp=0,
        strength_points=0,
        endurance_points=0,
        technique_points=0,
        aura=100
    )
    
    session.add(user)
    await session.flush()
    
    # Create stats
    stats = AscendantStats(
        ascendant_id=user.id,
        str_level=1,
        end_level=1,
        tech_level=1,
        str_xp=0,
        end_xp=0,
        tech_xp=0,
        str_value=10,
        end_value=10,
        tech_value=10
    )
    
    session.add(stats)
    await session.commit()
    
    print(f"Created test user: {user.username}")
    return user


async def ensure_prerequisite(session: AsyncSession, user_id: int, node_id: str):
    """Ensure a prerequisite node is unlocked."""
    from app.infrastructure.database.models.v2 import UserSkillProgress
    
    stmt = select(UserSkillProgress).where(
        UserSkillProgress.ascendant_id == user_id,
        UserSkillProgress.node_id == node_id
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if not existing:
        progress = UserSkillProgress(
            ascendant_id=user_id,
            node_id=node_id
        )
        session.add(progress)
        await session.commit()
        print(f"Added prerequisite: {node_id}")


if __name__ == "__main__":
    asyncio.run(test_admin_progression())