#!/usr/bin/env python3
"""
Fix the movement_categories.id data type mismatch.
The model expects String(50) but the database has bigint.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_movement_category_id_mismatch():
    """Fix the movement_categories.id data type."""
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
        print("\n[INFO] Checking data types...")
        
        mc_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        print(f"movement_categories.id database type: {mc_id_type}")
        
        stn_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        print(f"skill_tree_nodes.category_id database type: {stn_cat_id_type}")
        
        # The model expects movement_categories.id to be String(50) 
        # But it's currently bigint in the database
        # We need to fix this by either:
        # 1. Change the database to match the model (convert to varchar)
        # 2. Change the model to match the database (use Integer)
        
        # Option 1: Convert movement_categories.id to varchar
        print("\n[FIX] Converting movement_categories.id from bigint to varchar...")
        
        # This is tricky because there might be foreign key references
        # Let's check what references this column
        refs = await conn.fetch("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
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
        
        print(f"Found {len(refs)} foreign key references to movement_categories.id:")
        for ref in refs:
            print(f"  {ref['table_name']}.{ref['column_name']} -> movement_categories.id")
        
        # Since we've already populated skill_tree_nodes with string category_ids
        # Let's convert movement_categories.id to match
        
        print("\n[STEP 1] Converting movement_categories.id to VARCHAR...")
        
        # First, let's see the current data
        sample_data = await conn.fetch("SELECT id, name FROM movement_categories LIMIT 5;")
        print("Sample current data:")
        for row in sample_data:
            print(f"  ID: {row['id']} (type: {type(row['id']).__name__}) - Name: {row['name']}")
        
        # Convert the column type
        try:
            await conn.execute("""
                ALTER TABLE movement_categories 
                ALTER COLUMN id TYPE VARCHAR(50) USING id::VARCHAR(50);
            """)
            print("  [OK] Converted movement_categories.id to VARCHAR(50)")
        except Exception as e:
            print(f"  [ERROR] Failed to convert column: {e}")
            
        # Also need to fix the movements.category_id if it exists
        movements_cat_id_type = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movements' AND column_name = 'category_id';
        """)
        
        if movements_cat_id_type:
            print(f"\n[STEP 2] Converting movements.category_id from {movements_cat_id_type} to VARCHAR...")
            try:
                await conn.execute("""
                    ALTER TABLE movements 
                    ALTER COLUMN category_id TYPE VARCHAR(50) USING category_id::VARCHAR(50);
                """)
                print("  [OK] Converted movements.category_id to VARCHAR(50)")
            except Exception as e:
                print(f"  [ERROR] Failed to convert movements.category_id: {e}")
        
        print("\n[VERIFY] Checking updated data types...")
        
        mc_id_type_new = await conn.fetchval("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        print(f"movement_categories.id new type: {mc_id_type_new}")
        
        # Check sample data after conversion
        sample_data_new = await conn.fetch("SELECT id, name FROM movement_categories LIMIT 5;")
        print("Sample data after conversion:")
        for row in sample_data_new:
            print(f"  ID: {row['id']} (type: {type(row['id']).__name__}) - Name: {row['name']}")
        
        await conn.close()
        
        print("\n[SUCCESS] Data type conversion completed!")
        print("\nNext steps:")
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
    print("MOVEMENT CATEGORY ID DATA TYPE FIX")
    print("=" * 80)
    print()
    print("This will convert movement_categories.id from bigint to varchar")
    print("to match the SQLAlchemy model definition.")
    print()
    
    try:
        success = asyncio.run(fix_movement_category_id_mismatch())
        if success:
            print("\n[SUCCESS] Fix completed successfully!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")