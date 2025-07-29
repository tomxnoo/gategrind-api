#!/usr/bin/env python3
"""
Comprehensive fix for movement categories and skill tree nodes.

The database has numeric category IDs (10, 11, 12, etc.) but should have
string IDs (PULL_VERTICAL, UPPER_DYNAMIC, etc.).

This script will:
1. Show what categories exist in the database
2. Create a proper mapping based on category names
3. Fix the skill tree node IDs to match the configuration
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_categories_comprehensive():
    """Fix category IDs and skill tree node IDs comprehensively."""
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
        
        # First, let's see what movement categories we have
        print("\n📊 Checking movement categories...")
        
        categories = await conn.fetch("""
            SELECT id, name, primary_stat
            FROM movement_categories
            ORDER BY id;
        """)
        
        print(f"\nFound {len(categories)} movement categories:")
        print("-" * 60)
        
        # Build mapping based on category names
        category_mapping = {}
        
        for cat in categories:
            cat_id = cat['id']
            cat_name = cat['name']
            cat_stat = cat['primary_stat']
            
            print(f"ID: {cat_id:>3} | Name: {cat_name:<30} | Stat: {cat_stat}")
            
            # Try to determine the proper string ID from the name
            name_lower = cat_name.lower()
            
            # Map based on known patterns
            if 'vertical pulling' in name_lower or 'pull-up' in name_lower:
                mapped_id = "PULL_VERTICAL"
            elif 'horizontal pulling' in name_lower:
                mapped_id = "PULL_HORIZONTAL"
            elif 'unilateral pulling' in name_lower:
                mapped_id = "PULL_UNILATERAL"
            elif 'dynamic power' in name_lower and 'upper' in name_lower:
                mapped_id = "UPPER_DYNAMIC"
            elif 'horizontal pushing' in name_lower:
                mapped_id = "PUSH_HORIZONTAL"
            elif 'unilateral pushing' in name_lower:
                mapped_id = "PUSH_UNILATERAL"
            elif 'overhead' in name_lower or 'vertical pushing' in name_lower:
                mapped_id = "PUSH_VERTICAL"
            elif 'squat' in name_lower:
                mapped_id = "SQUAT"
            elif 'lunge' in name_lower:
                mapped_id = "LUNGE"
            elif 'hip hinge' in name_lower:
                mapped_id = "HINGE"
            elif 'core stability' in name_lower:
                mapped_id = "CORE_STABILITY"
            elif 'rotational' in name_lower:
                mapped_id = "ROTATIONAL"
            elif 'isometric' in name_lower and 'upper' in name_lower:
                mapped_id = "UPPER_ISOMETRIC"
            elif 'plyometric' in name_lower and 'lower' in name_lower:
                mapped_id = "LOWER_PLYOMETRIC"
            elif 'plyometric' in name_lower and 'upper' in name_lower:
                mapped_id = "UPPER_PLYOMETRIC"
            elif 'flexibility' in name_lower:
                mapped_id = "FLEXIBILITY"
            elif 'mobility' in name_lower or 'flow' in name_lower:
                mapped_id = "MOBILITY_FLOW"
            else:
                # Generate a reasonable ID from the name
                mapped_id = name_lower.replace(' ', '_').replace('(', '').replace(')', '').upper()
            
            category_mapping[str(cat_id)] = {
                'new_id': mapped_id,
                'name': cat_name,
                'config_prefix': mapped_id.lower()
            }
        
        print("\n" + "=" * 60)
        print("PROPOSED CATEGORY MAPPING:")
        print("=" * 60)
        
        for old_id, mapping in category_mapping.items():
            print(f"{old_id:>3} → {mapping['new_id']:<20} ({mapping['name']})")
        
        # Now check skill tree nodes
        print("\n📊 Checking skill tree nodes...")
        
        nodes = await conn.fetch("""
            SELECT id, node_id, category_id, level, name
            FROM skill_tree_nodes
            ORDER BY category_id::integer, level
            LIMIT 20;
        """)
        
        print(f"\nSample of skill tree nodes:")
        for node in nodes:
            print(f"  Cat {node['category_id']} Level {node['level']}: {node['node_id']} - {node['name']}")
        
        # Ask for confirmation
        print("\n" + "=" * 60)
        print("FIX PLAN:")
        print("=" * 60)
        print("1. Update skill tree node IDs to match configuration pattern")
        print("2. Based on the category mapping above")
        print("3. This will make nodes accessible through the skill tree config")
        print("\nNOTE: You'll need to update skill_tree_config.py to include")
        print("      definitions for all these categories!")
        
        response = input("\nDo you want to proceed with the fix? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return False
        
        # Apply the fix
        print("\n🔧 Updating skill tree node IDs...")
        
        update_count = 0
        for node in await conn.fetch("SELECT id, node_id, category_id, level FROM skill_tree_nodes"):
            cat_id_str = str(node['category_id'])
            if cat_id_str in category_mapping:
                old_node_id = node['node_id']
                new_node_id = f"{category_mapping[cat_id_str]['config_prefix']}_{node['level']}"
                
                if old_node_id != new_node_id:
                    await conn.execute("""
                        UPDATE skill_tree_nodes 
                        SET node_id = $1 
                        WHERE id = $2;
                    """, new_node_id, node['id'])
                    update_count += 1
        
        print(f"✅ Updated {update_count} node IDs")
        
        # Verify the changes
        print("\n📊 Verifying changes...")
        
        sample_nodes = await conn.fetch("""
            SELECT node_id, category_id, level, name
            FROM skill_tree_nodes
            ORDER BY category_id::integer, level
            LIMIT 15;
        """)
        
        print("\nSample of updated nodes:")
        for node in sample_nodes:
            cat_name = category_mapping.get(str(node['category_id']), {}).get('name', 'Unknown')
            print(f"  {node['node_id']} - {node['name']} (Cat: {cat_name})")
        
        # Generate skill tree config entries
        print("\n" + "=" * 60)
        print("SKILL TREE CONFIG ENTRIES NEEDED:")
        print("=" * 60)
        print("\nAdd these to skill_tree_config.py:\n")
        
        for cat_id, mapping in sorted(category_mapping.items(), key=lambda x: int(x[0])):
            if mapping['new_id'] not in ['UPPER_DYNAMIC', 'MOBILITY_FLOW', 'PULL_VERTICAL']:
                print(f'SKILL_TREE_CONFIG["{mapping["new_id"]}"] = [')
                print(f'    # Add 5 skill tree nodes for {mapping["name"]}')
                for level in range(1, 6):
                    print(f'    SkillTreeNode(id="{mapping["config_prefix"]}_{level}", ...),')
                print(']')
                print()
        
        await conn.close()
        
        print("\n🎉 SUCCESS: Database fixes applied!")
        print("\nNext steps:")
        print("1. Update skill_tree_config.py with the missing category definitions")
        print("2. Restart your application")
        print("3. Test the Skill Tree panel")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE CATEGORY AND NODE ID FIX")
    print("=" * 80)
    print()
    print("This script will:")
    print("1. Analyze your movement categories")
    print("2. Create proper mappings to string IDs")
    print("3. Fix skill tree node IDs")
    print("4. Show what needs to be added to skill_tree_config.py")
    print()
    
    try:
        success = asyncio.run(fix_categories_comprehensive())
        if success:
            print("\n✅ Fix completed successfully!")
        else:
            print("\n❌ Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")