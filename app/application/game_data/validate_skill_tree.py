#!/usr/bin/env python3
"""
Skill Tree Configuration Validator
Validates the complete skill tree structure for Rise of Strength
"""

from .skill_tree_config import SKILL_TREE_CONFIG, SkillNodeType

def validate_skill_tree():
    """Validate the complete skill tree configuration"""
    
    print("🔍 Validating Skill Tree Configuration...")
    print("=" * 60)
    
    total_nodes = 0
    categories_validated = 0
    
    # Expected structure: 18 categories × 5 nodes = 90 total nodes
    expected_categories = 18
    expected_nodes_per_category = 5
    expected_total_nodes = 90
    
    for category_id, nodes in SKILL_TREE_CONFIG.items():
        print(f"\n📂 Category: {category_id}")
        print(f"   Nodes: {len(nodes)}")
        
        # Validate node count per category
        if len(nodes) != expected_nodes_per_category:
            print(f"   ❌ ERROR: Expected {expected_nodes_per_category} nodes, found {len(nodes)}")
            continue
        
        # Validate node structure
        node_types = {
            SkillNodeType.FOUNDATION: 0,
            SkillNodeType.PROGRESSION: 0,
            SkillNodeType.MASTERY: 0
        }
        
        for i, node in enumerate(nodes, 1):
            # Check level progression
            if node.level != i:
                print(f"   ❌ ERROR: Node {node.id} has level {node.level}, expected {i}")
                continue
            
            # Count node types
            node_types[node.node_type] += 1
            
            # Validate node structure
            if not all([node.id, node.name, node.description, node.lore_text]):
                print(f"   ❌ ERROR: Node {node.id} missing required fields")
                continue
        
        # Validate node type distribution (1 foundation, 3 progression, 1 mastery)
        if (node_types[SkillNodeType.FOUNDATION] != 1 or 
            node_types[SkillNodeType.PROGRESSION] != 3 or 
            node_types[SkillNodeType.MASTERY] != 1):
            print(f"   ❌ ERROR: Invalid node type distribution")
            print(f"      Foundation: {node_types[SkillNodeType.FOUNDATION]} (expected 1)")
            print(f"      Progression: {node_types[SkillNodeType.PROGRESSION]} (expected 3)")
            print(f"      Mastery: {node_types[SkillNodeType.MASTERY]} (expected 1)")
            continue
        
        print(f"   ✅ Category validated successfully")
        categories_validated += 1
        total_nodes += len(nodes)
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Categories: {len(SKILL_TREE_CONFIG)}/{expected_categories}")
    print(f"Categories Validated: {categories_validated}/{expected_categories}")
    print(f"Total Nodes: {total_nodes}/{expected_total_nodes}")
    
    if (len(SKILL_TREE_CONFIG) == expected_categories and 
        categories_validated == expected_categories and 
        total_nodes == expected_total_nodes):
        print("\n🎉 SKILL TREE VALIDATION SUCCESSFUL!")
        print("All 90 nodes across 18 categories are properly configured.")
        return True
    else:
        print("\n❌ SKILL TREE VALIDATION FAILED!")
        return False

def print_skill_tree_overview():
    """Print a comprehensive overview of the skill tree"""
    
    print("\n🌟 RISE OF STRENGTH - SKILL TREE OVERVIEW")
    print("=" * 80)
    
    categories = [
        ("PULL_VERTICAL", "Mountain's Call"),
        ("PULL_HORIZONTAL", "River's Flow"),
        ("PUSH_VERTICAL", "Sky Piercer"),
        ("PUSH_HORIZONTAL", "Earth Mover"),
        ("SQUAT_BILATERAL", "Foundation's Might"),
        ("CORE_STATIC", "Pillar's Strength"),
        ("PULL_UNILATERAL", "Shadow's Balance"),
        ("PUSH_UNILATERAL", "Lone Warrior's Path"),
        ("SQUAT_UNILATERAL", "Dancer's Grace"),
        ("HINGE_BILATERAL", "Titan's Hinge"),
        ("HINGE_UNILATERAL", "Crane's Poise"),
        ("CORE_DYNAMIC", "Storm's Fury"),
        ("CORE_ROTATIONAL", "Spiral's Wisdom"),
        ("UPPER_ISOMETRIC", "Stone Guardian"),
        ("LOWER_PLYOMETRIC", "Lightning's Speed"),
        ("FLEXIBILITY", "Sculptor's Art"),
        ("ACCESSORY_SHOULDERS", "Sentinel's Watch")
    ]
    
    for category_id, theme_name in categories:
        if category_id in SKILL_TREE_CONFIG:
            nodes = SKILL_TREE_CONFIG[category_id]
            print(f"\n🏛️  {theme_name} ({category_id})")
            print(f"    └── {len(nodes)} nodes: {nodes[0].name} → {nodes[-1].name}")
        else:
            print(f"\n❌ {theme_name} ({category_id}) - NOT FOUND")

if __name__ == "__main__":
    # Run validation
    success = validate_skill_tree()
    
    # Print overview
    print_skill_tree_overview()
    
    if success:
        print("\n🚀 Ready to implement in the game!")
    else:
        print("\n🔧 Please fix validation errors before proceeding.")