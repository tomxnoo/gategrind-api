#!/usr/bin/env python3
"""
Complete fix for skill tree node IDs with foreign key handling.

This script will:
1. Temporarily update movements.node_id to handle foreign key constraints
2. Update skill tree node IDs to match configuration pattern
3. Update movements back to reference the new node IDs
4. Show what needs to be added to skill_tree_config.py
"""

import asyncio
import os
from urllib.parse import urlparse

# Based on the console output, here are the actual categories
CATEGORY_MAPPING = {
    "10": "push",
    "11": "pull", 
    "12": "squat",
    "13": "hinge",
    "14": "carry",
    "15": "core",
    "16": "cardio",
    "17": "flexibility",
    "18": "pull_vertical",
    "19": "pull_horizontal",
    "20": "pull_unilateral",
    "21": "push_horizontal",
    "22": "push_unilateral",
    "23": "upper_dynamic",
    "24": "push_vertical",
    "25": "upper_isometric",
    "26": "bilateral_squats",
    "27": "unilateral_squats",
    "28": "bilateral_hinge",
    "29": "unilateral_hinge",
    "30": "lower_plyometric",
    "31": "static_core",
    "32": "dynamic_core",
    "33": "rotational",
    "34": "mobility_flow",
    "35": "shoulder_stability",
    "36": "locomotion",
    "37": "balance",
    "38": "coordination",
    "39": "upper_plyometric",
    "40": "power_endurance",
    "42": "grip_strength",
    "43": "posterior_chain",
    "44": "recovery",
    "45": "steady_state_cardio",
    "46": "interval_training",
    "47": "handstand_skills",
    "48": "bridge_skills",
    "49": "flow_movement"
}

async def fix_skill_tree_complete():
    """Fix skill tree node IDs handling foreign key constraints."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        return False
    
    try:
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
        
        print("Connecting to database...")
        
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:] if parsed.path else 'postgres'
        )
        
        print("Connected successfully!")
        
        # Start a transaction
        async with conn.transaction():
            print("\n🔧 Step 1: Temporarily set movements.node_id to NULL...")
            
            # Store movement to node mappings
            movements_mapping = await conn.fetch("""
                SELECT m.id, m.node_id, m.name
                FROM movements m
                WHERE m.node_id IS NOT NULL;
            """)
            
            print(f"Found {len(movements_mapping)} movements linked to skill tree nodes")
            
            # Temporarily set node_id to NULL to avoid foreign key constraint
            await conn.execute("""
                UPDATE movements 
                SET node_id = NULL 
                WHERE node_id IS NOT NULL;
            """)
            print("✅ Movements temporarily unlinked")
            
            # Step 2: Update skill tree node IDs
            print("\n🔧 Step 2: Updating skill tree node IDs...")
            
            update_count = 0
            node_id_mapping = {}  # Old ID -> New ID mapping
            
            nodes = await conn.fetch("""
                SELECT id, node_id, category_id, level 
                FROM skill_tree_nodes
                ORDER BY category_id::integer, level;
            """)
            
            for node in nodes:
                cat_id_str = str(node['category_id'])
                if cat_id_str in CATEGORY_MAPPING:
                    old_node_id = node['node_id']
                    new_node_id = f"{CATEGORY_MAPPING[cat_id_str]}_{node['level']}"
                    node_id_mapping[old_node_id] = new_node_id
                    
                    if old_node_id != new_node_id:
                        await conn.execute("""
                            UPDATE skill_tree_nodes 
                            SET node_id = $1 
                            WHERE id = $2;
                        """, new_node_id, node['id'])
                        update_count += 1
            
            print(f"✅ Updated {update_count} skill tree node IDs")
            
            # Step 3: Update movements to use new node IDs
            print("\n🔧 Step 3: Re-linking movements to new node IDs...")
            
            relink_count = 0
            for movement in movements_mapping:
                old_node_id = movement['node_id']
                if old_node_id in node_id_mapping:
                    new_node_id = node_id_mapping[old_node_id]
                    await conn.execute("""
                        UPDATE movements 
                        SET node_id = $1 
                        WHERE id = $2;
                    """, new_node_id, movement['id'])
                    relink_count += 1
            
            print(f"✅ Re-linked {relink_count} movements")
        
        # Verify the changes
        print("\n📊 Verifying changes...")
        
        sample_nodes = await conn.fetch("""
            SELECT stn.node_id, stn.category_id, stn.level, stn.name,
                   mc.name as category_name
            FROM skill_tree_nodes stn
            JOIN movement_categories mc ON mc.id::text = stn.category_id
            ORDER BY stn.category_id::integer, stn.level
            LIMIT 15;
        """)
        
        print("\nSample of updated skill tree nodes:")
        for node in sample_nodes:
            print(f"  {node['node_id']:<20} - {node['name']:<25} (Category: {node['category_name']})")
        
        # Check which categories need to be added to config
        print("\n" + "=" * 80)
        print("SKILL TREE CONFIG UPDATES NEEDED:")
        print("=" * 80)
        
        # Check which categories already exist in config
        existing_in_config = ['upper_dynamic', 'mobility_flow', 'pull_vertical']
        
        print("\nAdd these to app/application/game_data/skill_tree_config.py:\n")
        
        categories = await conn.fetch("""
            SELECT DISTINCT mc.id, mc.name, mc.primary_stat
            FROM movement_categories mc
            JOIN skill_tree_nodes stn ON stn.category_id = mc.id::text
            ORDER BY mc.id::integer;
        """)
        
        for cat in categories:
            cat_id = str(cat['id'])
            if cat_id in CATEGORY_MAPPING:
                config_key = CATEGORY_MAPPING[cat_id]
                if config_key not in existing_in_config:
                    config_key_upper = config_key.upper()
                    print(f'# {cat["name"]} ({cat["primary_stat"]})')
                    print(f'SKILL_TREE_CONFIG["{config_key_upper}"] = [')
                    for level in range(1, 6):
                        level_names = ["Foundation", "Development", "Proficiency", "Mastery", "Transcendence"]
                        print(f'    SkillTreeNode(')
                        print(f'        id="{config_key}_{level}",')
                        print(f'        category_id="{config_key_upper}",')
                        print(f'        level={level},')
                        print(f'        name="{level_names[level-1]}",')
                        print(f'        description="Level {level} of {cat["name"]} progression",')
                        print(f'        # Add appropriate requirements and rewards')
                        print(f'    ),')
                    print(']')
                    print()
        
        await conn.close()
        
        print("\n🎉 SUCCESS: Skill tree node IDs have been fixed!")
        print("\nNext steps:")
        print("1. Update skill_tree_config.py with the missing categories shown above")
        print("2. Restart your application")
        print("3. Test the Skill Tree panel - unlocking should now work!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("COMPLETE SKILL TREE NODE ID FIX")
    print("=" * 80)
    print()
    print("This script will:")
    print("1. Handle foreign key constraints properly")
    print("2. Update skill tree node IDs to match configuration pattern")
    print("3. Re-link movements to the new node IDs")
    print("4. Show what needs to be added to skill_tree_config.py")
    print()
    
    response = input("Do you want to proceed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        exit(0)
    
    try:
        success = asyncio.run(fix_skill_tree_complete())
        if success:
            print("\n✅ Fix completed successfully!")
        else:
            print("\n❌ Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")