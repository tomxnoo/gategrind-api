#!/usr/bin/env python3
"""
Comprehensive fix for all skill tree categories.

This script adds ALL 39 missing categories to skill_tree_config.py based on 
the database structure, replacing the incomplete 3-category configuration.
"""

import os

# All 39 categories from the database
ALL_CATEGORIES = [
    "UPPER_DYNAMIC", "MOBILITY_FLOW", "PULL_VERTICAL", "PUSH", "PULL", "SQUAT", 
    "HINGE", "LUNGE", "ROTATION", "GAIT", "LOADED_CARRY", "GROUND_MOVEMENT", 
    "BALLISTIC", "PLYOMETRIC", "GRIP", "CORE", "FLEXIBILITY", "BALANCE", 
    "COORDINATION", "REACTION", "AGILITY", "POWER", "SPEED", "STRENGTH", 
    "ENDURANCE", "TECHNIQUE", "TACTICAL", "DEFENSIVE", "OFFENSIVE", 
    "RECOVERY", "INJURY_PREVENTION", "MENTAL", "STRATEGIC", "COMPETITIVE", 
    "FUNCTIONAL", "SPORT_SPECIFIC", "REHABILITATION", "CORRECTIVE", "ADVANCED"
]

def create_skill_node_config(category_id):
    """Create a complete 5-level skill node configuration for a category."""
    category_name = category_id.replace("_", " ").title()
    
    return f'''
# =========================================================================
# {category_id} - {category_name} (5 nodes)
# =========================================================================
SKILL_TREE_CONFIG["{category_id}"] = [
    SkillTreeNode(
        id="{category_id.lower()}_1",
        category_id="{category_id}",
        level=1,
        name="{category_name} Foundation",
        description="Master the fundamentals of {category_name.lower()} movements",
        lore_text="Every great strength begins with a solid foundation.",
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
        rewards={{"str_points": 1, "xp": 50}},
        unlock_message="You have mastered {category_name} Foundation!"
    ),
    SkillTreeNode(
        id="{category_id.lower()}_2",
        category_id="{category_id}",
        level=2,
        name="{category_name} Development",
        description="Develop intermediate {category_name.lower()} strength",
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
            prerequisite_nodes=["{category_id.lower()}_1"],
            min_ascendant_level=4
        ),
        rewards={{"str_points": 2, "xp": 75}},
        unlock_message="You have achieved {category_name} Development!"
    ),
    SkillTreeNode(
        id="{category_id.lower()}_3",
        category_id="{category_id}",
        level=3,
        name="{category_name} Proficiency",
        description="Reach proficiency in {category_name.lower()} movements",
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
            prerequisite_nodes=["{category_id.lower()}_2"],
            min_ascendant_level=7
        ),
        rewards={{"str_points": 3, "end_points": 1, "xp": 100}},
        unlock_message="You have reached {category_name} Proficiency!"
    ),
    SkillTreeNode(
        id="{category_id.lower()}_4",
        category_id="{category_id}",
        level=4,
        name="{category_name} Mastery",
        description="Master advanced {category_name.lower()} techniques",
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
            prerequisite_nodes=["{category_id.lower()}_3"],
            min_ascendant_level=10
        ),
        rewards={{"str_points": 4, "end_points": 2, "xp": 125}},
        unlock_message="You have achieved {category_name} Mastery!"
    ),
    SkillTreeNode(
        id="{category_id.lower()}_5",
        category_id="{category_id}",
        level=5,
        name="{category_name} Transcendence",
        description="Transcend the limits of {category_name.lower()} power",
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
            prerequisite_nodes=["{category_id.lower()}_4"],
            min_ascendant_level=13
        ),
        rewards={{"str_points": 6, "end_points": 3, "tech_points": 2, "xp": 200}},
        unlock_message="You have achieved {category_name} Transcendence!"
    )
]'''

def replace_skill_tree_config():
    """Replace the entire skill_tree_config.py with all 39 categories."""
    
    config_path = os.path.join(os.getcwd(), "app/application/game_data/skill_tree_config.py")
    
    if not os.path.exists(config_path):
        print(f"[ERROR] Could not find skill_tree_config.py at {config_path}")
        return False
    
    print("[INFO] Reading current skill_tree_config.py...")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the header (imports and class definitions)
    header_end = content.find('# =========================================================================')
    if header_end == -1:
        print("[ERROR] Could not find configuration start marker")
        return False
    
    header = content[:header_end]
    
    print(f"[INFO] Generating configurations for all {len(ALL_CATEGORIES)} categories...")
    
    # Generate all category configurations
    all_configs = ""
    for category in ALL_CATEGORIES:
        all_configs += create_skill_node_config(category)
    
    # Create the new complete file
    new_content = header + all_configs
    
    print("[INFO] Writing complete skill_tree_config.py...")
    
    # Write the updated content
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[SUCCESS] Successfully replaced skill_tree_config.py with all {len(ALL_CATEGORIES)} categories!")
    print(f"[INFO] Generated {len(ALL_CATEGORIES) * 5} skill nodes total")
    print("\nThe skill tree should now support ALL database skill nodes.")
    print("Restart your application to apply the changes.")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("COMPLETE SKILL TREE CONFIG FIX")
    print("=" * 80)
    print()
    print(f"This script replaces skill_tree_config.py with all {len(ALL_CATEGORIES)} categories")
    print("from the database, creating a complete 195-node skill tree.")
    print()
    
    # Auto-proceed for automated execution
    print("Auto-proceeding with complete fix...")
    
    try:
        success = replace_skill_tree_config()
        if success:
            print("\n[SUCCESS] Complete fix applied successfully!")
            print("\nNext steps:")
            print("1. Restart your Discord bot")
            print("2. All skill nodes should now be unlockable!")
            print("3. No more 'Skill tree node not found' errors")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()