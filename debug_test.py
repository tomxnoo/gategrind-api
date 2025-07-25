import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database.models.v2.movements import Movement
from app.infrastructure.database.models.v2.skill_tree_nodes import SkillTreeNode
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress
from app.infrastructure.database.models.v2.ascendants import Ascendant

async def debug_test_data(db_session: AsyncSession, test_user, test_movements):
    """Debug function to check test data setup"""
    print("\n=== DEBUG TEST DATA ===")
    
    # Check user
    print(f"Test user ID: {test_user.id}")
    
    # Check movements
    movement_query = select(Movement)
    movement_result = await db_session.execute(movement_query)
    movements = movement_result.scalars().all()
    print(f"Total movements: {len(movements)}")
    for movement in movements:
        print(f"  Movement: {movement.name}, node_id: {movement.node_id}")
    
    # Check skill tree nodes
    node_query = select(SkillTreeNode)
    node_result = await db_session.execute(node_query)
    nodes = node_result.scalars().all()
    print(f"Total nodes: {len(nodes)}")
    for node in nodes:
        print(f"  Node: {node.node_id} (id: {node.id}), name: {node.name}")
    
    # Check user skill progress
    skill_query = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == test_user.id)
    skill_result = await db_session.execute(skill_query)
    skills = skill_result.scalars().all()
    print(f"User skill progress entries: {len(skills)}")
    for skill in skills:
        print(f"  Skill: ascendant_id={skill.ascendant_id}, node_id={skill.node_id}")
    
    # Check movements for unlocked nodes
    if skills:
        node_ids = [skill.node_id for skill in skills]
        movement_query = select(Movement).where(Movement.node_id.in_(node_ids))
        movement_result = await db_session.execute(movement_query)
        available_movements = movement_result.scalars().all()
        print(f"Available movements for unlocked nodes: {len(available_movements)}")
        for movement in available_movements:
            print(f"  Available: {movement.name}, node_id: {movement.node_id}")
    
    print("=== END DEBUG ===\n")

if __name__ == "__main__":
    print("This is a debug script to be imported and used in tests")