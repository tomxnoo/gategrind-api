#!/usr/bin/env python3
"""
Fix the data type mismatch between movement_categories.id and skill_tree_nodes.category_id.
The model expects strings but we have integers in the database.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_category_id_data_types():
    """Fix the category_id data type mismatch."""
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
        
        # Check current data types
        print("\n[INFO] Checking current data types...")
        
        mc_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        print(f"movement_categories.id: {mc_id_type}")
        
        stn_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        print(f"skill_tree_nodes.category_id: {stn_cat_id_type}")
        
        mov_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movements' AND column_name = 'category_id';
        """)
        print(f"movements.category_id: {mov_cat_id_type}")
        
        # Check sample data
        print("\n[INFO] Checking sample category IDs...")
        categories = await conn.fetch("""
            SELECT id, name FROM movement_categories LIMIT 5;
        """)
        
        print("Sample movement_categories:")
        for cat in categories:
            print(f"  ID: {cat['id']} ({type(cat['id']).__name__}) - Name: {cat['name']}")
        
        # The issue is that movement_categories.id is integer but models expect string
        # We need to convert the integer IDs to strings
        
        print("\n[FIX] Converting category IDs to string format...")
        
        # Step 1: Check if there are any skill_tree_nodes records
        stn_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        print(f"skill_tree_nodes records: {stn_count}")
        
        mov_count = await conn.fetchval("SELECT COUNT(*) FROM movements;")
        print(f"movements records: {mov_count}")
        
        if stn_count == 0 and mov_count > 0:
            print("\n[INFO] No skill_tree_nodes exist, but movements exist.")
            print("The issue is that the query is trying to find skill tree nodes for category IDs")
            print("but no skill tree nodes have been created yet.")
            
            # Check if movements have proper string category_id values
            mov_sample = await conn.fetch("""
                SELECT category_id FROM movements LIMIT 5;
            """)
            print("\nSample movements.category_id values:")
            for mov in mov_sample:
                print(f"  {mov['category_id']} ({type(mov['category_id']).__name__})")
        
        elif stn_count > 0:
            print("\n[FIX] Converting skill_tree_nodes.category_id to match movement_categories...")
            
            # If skill_tree_nodes exist with wrong types, fix them
            await conn.execute("""
                UPDATE skill_tree_nodes 
                SET category_id = movement_categories.id::varchar
                FROM movement_categories 
                WHERE skill_tree_nodes.category_id::int = movement_categories.id;
            """)
            print("  [OK] Updated skill_tree_nodes.category_id to string format")
        
        # The real issue might be that we don't have skill tree nodes data
        # Let's check what category IDs movements are using
        print("\n[INFO] Checking movements category_id values...")
        mov_categories = await conn.fetch("""
            SELECT DISTINCT category_id, COUNT(*) as count
            FROM movements 
            GROUP BY category_id 
            ORDER BY category_id;
        """)
        
        print("Movement category_id distribution:")
        for cat in mov_categories:
            print(f"  Category ID: {cat['category_id']} - {cat['count']} movements")
        
        # Check if we need to create skill_tree_nodes
        if stn_count == 0:
            print("\n[NOTICE] No skill_tree_nodes exist.")
            print("This might be why the query fails - it's looking for nodes that don't exist.")
            print("You may need to populate the skill_tree_nodes table with appropriate data.")
            
            # Show what category IDs exist in movement_categories
            all_categories = await conn.fetch("""
                SELECT id, name FROM movement_categories ORDER BY id;
            """)
            print("\nAll movement categories:")
            for cat in all_categories:
                print(f"  ID: {cat['id']} - Name: {cat['name']}")
        
        await conn.close()
        
        print("\n[SUCCESS] Category ID data type analysis completed!")
        print("\nNext steps:")
        if stn_count == 0:
            print("1. You need to populate skill_tree_nodes table")
            print("2. Create nodes for each category with appropriate levels")
            print("3. Then test the Skill Tree panel again")
        else:
            print("1. Restart your application")
            print("2. Test the Skill Tree panel")
            print("3. The data type mismatch should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("CATEGORY ID DATA TYPE FIX")
    print("=" * 80)
    print()
    print("This will analyze and fix category_id data type mismatches")
    print("between movement_categories, skill_tree_nodes, and movements tables.")
    print()
    
    try:
        success = asyncio.run(fix_category_id_data_types())
        if success:
            print("\n[SUCCESS] Analysis completed successfully!")
        else:
            print("\n[ERROR] Analysis failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")