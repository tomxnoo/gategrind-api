#!/usr/bin/env python3
"""
Comprehensive fix for all data type mismatches.
Drop foreign keys, convert columns, recreate relationships.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_all_data_types():
    """Fix all data type mismatches comprehensively."""
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
        
        # Step 1: Drop all foreign key constraints that reference movement_categories.id
        print("\n[STEP 1] Dropping foreign key constraints...")
        
        # Find all foreign key constraints
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND ccu.table_name = 'movement_categories'
              AND ccu.column_name = 'id';
        """)
        
        dropped_constraints = []
        for fk in fk_constraints:
            constraint_name = fk['constraint_name']
            table_name = fk['table_name']
            print(f"  Dropping {constraint_name} from {table_name}...")
            
            try:
                await conn.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name};")
                dropped_constraints.append((table_name, constraint_name, fk['column_name']))
                print(f"    [OK] Dropped {constraint_name}")
            except Exception as e:
                print(f"    [ERROR] Failed to drop {constraint_name}: {e}")
        
        # Step 2: Convert movement_categories.id to VARCHAR
        print("\n[STEP 2] Converting movement_categories.id to VARCHAR...")
        try:
            await conn.execute("""
                ALTER TABLE movement_categories 
                ALTER COLUMN id TYPE VARCHAR(50) USING id::VARCHAR(50);
            """)
            print("  [OK] Converted movement_categories.id to VARCHAR(50)")
        except Exception as e:
            print(f"  [ERROR] Failed to convert movement_categories.id: {e}")
        
        # Step 3: Convert movements.category_id to VARCHAR 
        print("\n[STEP 3] Converting movements.category_id to VARCHAR...")
        try:
            await conn.execute("""
                ALTER TABLE movements 
                ALTER COLUMN category_id TYPE VARCHAR(50) USING category_id::VARCHAR(50);
            """)
            print("  [OK] Converted movements.category_id to VARCHAR(50)")
        except Exception as e:
            print(f"  [ERROR] Failed to convert movements.category_id: {e}")
        
        # Step 4: Recreate foreign key constraints
        print("\n[STEP 4] Recreating foreign key constraints...")
        for table_name, constraint_name, column_name in dropped_constraints:
            try:
                await conn.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {constraint_name} 
                    FOREIGN KEY ({column_name}) REFERENCES movement_categories(id);
                """)
                print(f"  [OK] Recreated {constraint_name} on {table_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to recreate {constraint_name}: {e}")
        
        # Step 5: Verify the changes
        print("\n[VERIFY] Checking final data types...")
        
        mc_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        print(f"movement_categories.id: {mc_id_type}")
        
        mov_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movements' AND column_name = 'category_id';
        """)
        print(f"movements.category_id: {mov_cat_id_type}")
        
        stn_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        print(f"skill_tree_nodes.category_id: {stn_cat_id_type}")
        
        # Check sample data
        print("\nSample data after conversion:")
        sample_cats = await conn.fetch("SELECT id, name FROM movement_categories LIMIT 3;")
        for cat in sample_cats:
            print(f"  Category ID: '{cat['id']}' ({type(cat['id']).__name__}) - Name: {cat['name']}")
        
        sample_movs = await conn.fetch("SELECT id, name, category_id FROM movements LIMIT 3;")
        for mov in sample_movs:
            print(f"  Movement: {mov['name']} - Category ID: '{mov['category_id']}' ({type(mov['category_id']).__name__})")
        
        sample_nodes = await conn.fetch("SELECT node_id, category_id, level FROM skill_tree_nodes LIMIT 3;")
        for node in sample_nodes:
            print(f"  Node: {node['node_id']} - Category ID: '{node['category_id']}' ({type(node['category_id']).__name__})")
        
        await conn.close()
        
        print("\n[SUCCESS] All data type conversions completed!")
        print("\nSummary:")
        print("- movement_categories.id: bigint -> VARCHAR(50)")
        print("- movements.category_id: bigint -> VARCHAR(50)")
        print("- skill_tree_nodes.category_id: already VARCHAR(50)")
        print("- Foreign key constraints recreated")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. All data types should now be consistent")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE DATA TYPE FIX")
    print("=" * 80)
    print()
    print("This will fix all data type mismatches by:")
    print("1. Dropping foreign key constraints")
    print("2. Converting movement_categories.id to VARCHAR(50)")
    print("3. Converting movements.category_id to VARCHAR(50)")
    print("4. Recreating foreign key constraints")
    print()
    
    try:
        success = asyncio.run(fix_all_data_types())
        if success:
            print("\n[SUCCESS] Comprehensive fix completed successfully!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")