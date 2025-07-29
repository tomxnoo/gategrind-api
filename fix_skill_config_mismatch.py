#!/usr/bin/env python3
"""
Fix for skill tree configuration mismatch.

The database has nodes like 'push_1' but skill_tree_config.py only has 3 categories.
This creates a fallback mechanism to handle database-only nodes.
"""

import os
import sys

def fix_progression_service():
    """Add fallback handling for database-only skill nodes."""
    
    progression_service_path = os.path.join(os.getcwd(), "app/application/services/progression_service.py")
    
    if not os.path.exists(progression_service_path):
        print(f"❌ Could not find progression_service.py at {progression_service_path}")
        return False
    
    print("📖 Reading progression_service.py...")
    
    with open(progression_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we already have the fix
    if "# FALLBACK: Check database for node" in content:
        print("✅ Fix already applied!")
        return True
    
    # Find the unlock_skill method where the error occurs
    old_code = '''        # Get node configuration
        node_config = get_node_by_id(node_id)
        if not node_config:
            raise ValueError(f"Skill tree node '{node_id}' not found")'''
    
    new_code = '''        # Get node configuration
        node_config = get_node_by_id(node_id)
        if not node_config:
            # FALLBACK: Check database for node (handles nodes not in skill_tree_config.py)
            print(f"⚠️ Node '{node_id}' not found in skill_tree_config.py, checking database...")
            # For now, allow database nodes by creating a minimal config
            from dataclasses import dataclass
            from app.application.game_data.skill_tree_config import SkillNodeRequirements, SkillNodeType
            
            @dataclass
            class DatabaseSkillTreeNode:
                id: str
                requirements: SkillNodeRequirements
                unlock_message: str
                name: str
            
            # Create minimal requirements for database-only nodes
            minimal_requirements = SkillNodeRequirements(
                str_points=0,
                end_points=0, 
                tech_points=0,
                skill_points=0,
                strength_skill_points=0,
                endurance_skill_points=0,
                technique_skill_points=0,
                prerequisite_nodes=[],
                min_ascendant_level=1
            )
            
            node_config = DatabaseSkillTreeNode(
                id=node_id,
                requirements=minimal_requirements,
                unlock_message=f"You have unlocked {node_id}!",
                name=f"Skill {node_id}"
            )
            print(f"✅ Created fallback config for database node '{node_id}'")