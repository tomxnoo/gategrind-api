#!/usr/bin/env python3
"""
Quick fix for skill unlock error.

The database has been updated correctly, but skill_tree_config.py only defines 3 categories.
This script adds basic configurations for the missing categories.
"""

import os

def add_missing_categories_to_config():
    """Add missing skill tree categories to the configuration."""
    
    config_path = os.path.join(os.getcwd(), "app/application/game_data/skill_tree_config.py")
    
    if not os.path.exists(config_path):
        print(f"[ERROR] Could not find skill_tree_config.py at {config_path}")
        return False
    
    print("[INFO] Reading skill_tree_config.py...")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if PUSH category already exists
    if 'SKILL_TREE_CONFIG["PUSH"]' in content:
        print("[SUCCESS] Additional categories already added!")
        return True
    
    # Find the end of the existing configuration
    insertion_point = content.rfind('# =========================================================================')
    if insertion_point == -1:
        insertion_point = content.rfind(']')
    
    # Add basic configurations for the missing categories that are being accessed
    additional_config = '''

# =========================================================================
# PUSH - Basic Pushing (5 nodes) - BASIC CONFIG
# =========================================================================
SKILL_TREE_CONFIG["PUSH"] = [
    SkillTreeNode(
        id="push_1",
        category_id="PUSH",
        level=1,
        name="Push Foundation",
        description="Master the fundamentals of pushing movements",
        lore_text="Every great strength begins with a simple push.",
        node_type=SkillNodeType.FOUNDATION,
        requirements=SkillNodeRequirements(
            str_points=0,
            end_points=0,
            tech_points=0,
            skill_points=0,
            strength_skill_points=0,
            endurance_skill_points=0,
            technique_skill_points=0,
            prerequisite_nodes=[],
            min_ascendant_level=1
        ),
        rewards={"str_points": 1, "xp": 50},
        unlock_message="You have mastered Push Foundation!"
    ),
    SkillTreeNode(
        id="push_2",
        category_id="PUSH",
        level=2,
        name="Push Development",
        description="Develop intermediate pushing strength",
        lore_text="Progress demands consistent effort and dedication.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=500,
            end_points=250,
            tech_points=250,
            skill_points=3,
            strength_skill_points=2,
            endurance_skill_points=0,
            technique_skill_points=1,
            prerequisite_nodes=["push_1"],
            min_ascendant_level=4
        ),
        rewards={"str_points": 2, "xp": 75},
        unlock_message="You have achieved Push Development!"
    ),
    SkillTreeNode(
        id="push_3",
        category_id="PUSH",
        level=3,
        name="Push Proficiency",
        description="Reach proficiency in pushing movements",
        lore_text="Proficiency is the bridge between effort and mastery.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1000,
            end_points=500,
            tech_points=500,
            skill_points=8,
            strength_skill_points=5,
            endurance_skill_points=1,
            technique_skill_points=2,
            prerequisite_nodes=["push_2"],
            min_ascendant_level=7
        ),
        rewards={"str_points": 3, "end_points": 1, "xp": 100},
        unlock_message="You have reached Push Proficiency!"
    ),
    SkillTreeNode(
        id="push_4",
        category_id="PUSH",
        level=4,
        name="Push Mastery",
        description="Master advanced pushing techniques",
        lore_text="Mastery requires both strength and wisdom.",
        node_type=SkillNodeType.PROGRESSION,
        requirements=SkillNodeRequirements(
            str_points=1500,
            end_points=750,
            tech_points=750,
            skill_points=15,
            strength_skill_points=10,
            endurance_skill_points=2,
            technique_skill_points=3,
            prerequisite_nodes=["push_3"],
            min_ascendant_level=10
        ),
        rewards={"str_points": 4, "end_points": 2, "xp": 125},
        unlock_message="You have achieved Push Mastery!"
    ),
    SkillTreeNode(
        id="push_5",
        category_id="PUSH",
        level=5,
        name="Push Transcendence",
        description="Transcend the limits of pushing power",
        lore_text="To transcend is to become one with the force itself.",
        node_type=SkillNodeType.MASTERY,
        requirements=SkillNodeRequirements(
            str_points=2000,
            end_points=1000,
            tech_points=1000,
            skill_points=25,
            strength_skill_points=18,
            endurance_skill_points=3, 
            technique_skill_points=4,
            prerequisite_nodes=["push_4"],
            min_ascendant_level=13
        ),
        rewards={"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200},
        unlock_message="You have achieved Push Transcendence!"
    )
]'''

    # Insert the additional configuration
    new_content = content[:insertion_point] + additional_config + content[insertion_point:]
    
    print("[INFO] Adding PUSH category configuration...")
    
    # Write the updated content
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("[SUCCESS] Successfully added PUSH category to skill_tree_config.py")
    print("\nThe skill tree should now be able to unlock 'push_1' and related nodes.")
    print("Restart your application to apply the changes.")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL UNLOCK ERROR FIX")
    print("=" * 80)
    print()
    print("This script adds the missing PUSH category to skill_tree_config.py")
    print("to fix the 'Skill tree node not found' error.")
    print()
    
    # Auto-proceed for automated execution
    print("Auto-proceeding with fix...")
    
    try:
        success = add_missing_categories_to_config()
        if success:
            print("\n[SUCCESS] Fix completed successfully!")
            print("\nNext steps:")
            print("1. Restart your Discord bot")
            print("2. Try unlocking skill nodes - they should work now!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()