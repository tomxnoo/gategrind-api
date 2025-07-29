#!/usr/bin/env python3
"""
Fix skill tree node IDs to match the configuration.

The database currently has node_ids like 'cat_10_level_1' but the 
skill tree configuration expects IDs like 'upper_dynamic_1'.

This script updates the database node_ids to match the configuration.
"""

import asyncio
import os
from urllib.parse import urlparse

# Map database category IDs to configuration node ID prefixes
# Based on the debug output, we need to map numeric category IDs to proper names
CATEGORY_TO_CONFIG_MAP = {
    # The 3 categories already in skill_tree_config.py
    "23": "upper_dynamic",       # Dynamic Power (Upper) -> UPPER_DYNAMIC  
    "34": "mobility_flow",       # Mobility Flow -> MOBILITY_FLOW
    "18": "pull_vertical",       # Vertical Pulling -> PULL_VERTICAL
    
    # Additional categories that would need to be added to config
    "10": "push",                # Push
    "11": "pull",                # Pull  
    "12": "squat",               # Squat
    "13": "hinge",               # Hinge
    "14": "carry",               # Carry
    "15": "core",                # Core
    "16": "cardio",              # Cardio
    "17": "flexibility",         # Flexibility
    "19": "pull_horizontal",     # Horizontal Pulling
    "20": "pull_unilateral",     # Unilateral Pulling
    "21": "push_horizontal",     # Horizontal Pushing
    "22": "push_unilateral",     # Unilateral Pushing
    "24": "push_vertical",       # Vertical Pushing
    "25": "upper_isometric",     # Isometric Holds (Upper)
    "26": "squat_bilateral",     # Bilateral Squats
    "27": "squat_unilateral",    # Unilateral Squats
    "28": "hinge_bilateral",     # Bilateral Hinge
    "29": "hinge_unilateral",    # Unilateral Hinge
    "30": "lower_plyometric",    # Plyometrics (Lower)
    "31": "core_static",         # Static Core
    "32": "core_dynamic",        # Dynamic Core
    "33": "core_rotational",     # Rotational Core
    "35": "accessory_shoulders", # Shoulder Stability
    "36": "locomotion",          # Locomotion
    "37": "balance",             # Balance
    "38": "coordination",        # Coordination
    "39": "upper_plyometric",    # Plyometrics (Upper)
    "40": "power_endurance",     # Power Endurance
    "42": "grip",                # Grip Strength
    "43": "posterior",           # Posterior Chain
    "44": "recovery",            # Recovery
    "45": "cardio_steady",       # Steady State Cardio
    "46": "cardio_interval",     # Interval Training
    "47": "handstand",           # Handstand Skills
    "48": "bridge",              # Bridge Skills
    "49": "flow_movement",       # Flow Movement
}

async def fix_skill_tree_node_ids():
    """Update skill tree node IDs to match configuration."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        print("Please install it with: pip install asyncpg")
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
        
        # First, check what categories and nodes we have
        print("\n📊 Checking current skill tree nodes...")
        
        nodes = await conn.fetch("""
            SELECT id, node_id, category_id, level, name
            FROM skill_tree_nodes
            ORDER BY category_id, level;
        """)
        
        print(f"Found {len(nodes)} skill tree nodes")
        
        # Group nodes by category for analysis
        categories = {}
        for node in nodes:
            cat_id = node['category_id']
            if cat_id not in categories:
                categories[cat_id] = []
            categories[cat_id].append(node)
        
        print("\nCategories found:")
        for cat_id, cat_nodes in categories.items():
            print(f"  {cat_id}: {len(cat_nodes)} nodes")
        
        # Start a transaction to handle foreign key constraints properly
        async with conn.transaction():
            # Step 1: Backup movement references 
            print("\n🔒 Backing up movement references...")
            movement_backup = await conn.fetch("""
                SELECT m.id, m.node_id, m.name
                FROM movements m
                WHERE m.node_id IS NOT NULL;
            """)
            print(f"Found {len(movement_backup)} movements with skill tree references")
            
            # Step 2: Temporarily clear movement references to avoid foreign key issues
            await conn.execute("""
                UPDATE movements 
                SET node_id = NULL 
                WHERE node_id IS NOT NULL;
            """)
            print("✅ Temporarily cleared movement references")
            
            # Step 3: Update node_ids based on configuration mapping
            print("\n🔧 Updating node IDs to match configuration...")
            
            update_count = 0
            node_id_mapping = {}  # old_node_id -> new_node_id
            
            for cat_id, cat_nodes in categories.items():
                if cat_id in CATEGORY_TO_CONFIG_MAP:
                    config_prefix = CATEGORY_TO_CONFIG_MAP[cat_id]
                    
                    for node in cat_nodes:
                        old_node_id = node['node_id']
                        new_node_id = f"{config_prefix}_{node['level']}"
                        node_id_mapping[old_node_id] = new_node_id
                        
                        if old_node_id != new_node_id:
                            print(f"  Updating: {old_node_id} → {new_node_id}")
                            
                            try:
                                # Update the node_id
                                await conn.execute("""
                                    UPDATE skill_tree_nodes 
                                    SET node_id = $1 
                                    WHERE id = $2;
                                """, new_node_id, node['id'])
                                
                                update_count += 1
                            except Exception as e:
                                print(f"    ❌ Failed to update: {e}")
                        else:
                            print(f"  ✅ Already correct: {old_node_id}")
                            node_id_mapping[old_node_id] = old_node_id  # Keep mapping for movements
                else:
                    print(f"\n⚠️  WARNING: No mapping for category '{cat_id}'")
                    print(f"    This category's nodes will not be accessible through the skill tree config!")
                    # Keep original node_id for unmapped categories
                    for node in cat_nodes:
                        node_id_mapping[node['node_id']] = node['node_id']
            
            # Step 4: Restore movement references with new node_ids
            print(f"\n🔗 Restoring movement references...")
            restored_count = 0
            failed_count = 0
            
            for movement in movement_backup:
                old_node_id = movement['node_id']
                if old_node_id in node_id_mapping:
                    new_node_id = node_id_mapping[old_node_id]
                    try:
                        await conn.execute("""
                            UPDATE movements 
                            SET node_id = $1 
                            WHERE id = $2;
                        """, new_node_id, movement['id'])
                        restored_count += 1
                    except Exception as e:
                        print(f"  ⚠️ Failed to restore {movement['name']}: {e}")
                        failed_count += 1
                else:
                    print(f"  ⚠️ No mapping found for movement {movement['name']} -> {old_node_id}")
                    failed_count += 1
            
            print(f"✅ Restored {restored_count} movement references")
            if failed_count > 0:
                print(f"⚠️ Failed to restore {failed_count} movement references")
        
        print(f"\n✅ Updated {update_count} node IDs")
        
        # Verify the critical expected nodes exist
        print("\n🔍 Verifying critical expected nodes...")
        expected_nodes = [
            'upper_dynamic_1', 'upper_dynamic_2', 'upper_dynamic_3',
            'mobility_flow_1', 'mobility_flow_2', 'mobility_flow_3', 
            'pull_vertical_1', 'pull_vertical_2', 'pull_vertical_3'
        ]
        
        print("Checking expected nodes:")
        all_found = True
        for expected in expected_nodes:
            found = await conn.fetch("""
                SELECT id, category_id, level, name
                FROM skill_tree_nodes 
                WHERE node_id = $1;
            """, expected)
            
            if found:
                node = found[0]
                print(f"  ✅ {expected:<20} -> Found (Cat: {node['category_id']}, Level: {node['level']})")
            else:
                print(f"  ❌ {expected:<20} -> NOT FOUND")
                all_found = False
        
        # Show sample of updated nodes
        print("\n📊 Sample of updated nodes:")
        
        updated_nodes = await conn.fetch("""
            SELECT node_id, category_id, level, name
            FROM skill_tree_nodes
            WHERE category_id IN ('23', '34', '18')  -- Upper Dynamic, Mobility Flow, Pull Vertical
            ORDER BY category_id::integer, level
            LIMIT 15;
        """)
        
        for node in updated_nodes:
            print(f"  {node['node_id']:<20} - {node['name']} (Cat: {node['category_id']}, Lvl: {node['level']})")
        
        if all_found:
            print("\n🎉 SUCCESS: All expected nodes are now available!")
        else:
            print("\n⚠️ Some expected nodes are still missing - there may be an issue with the mapping")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: Skill tree node IDs have been fixed!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel - unlocking should now work")
        print("3. If you have categories not in the configuration, add them to skill_tree_config.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE NODE ID FIX")
    print("=" * 80)
    print()
    print("This script will update skill tree node IDs to match the configuration.")
    print("Current database uses IDs like 'cat_10_level_1'")
    print("Configuration expects IDs like 'upper_dynamic_1'")
    print()
    
    response = input("Do you want to proceed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        exit(0)
    
    try:
        success = asyncio.run(fix_skill_tree_node_ids())
        if success:
            print("\n✅ Fix completed successfully!")
        else:
            print("\n❌ Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")