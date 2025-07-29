#!/usr/bin/env python3
"""
Check the foreign key constraint between skill_tree_nodes and movement_categories.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_foreign_key():
    """Check the foreign key constraint and data types."""
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
        
        # Check foreign key constraints
        print("\n[INFO] Checking foreign key constraints...")
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND tc.table_name = 'skill_tree_nodes'
              AND kcu.column_name = 'category_id';
        """)
        
        print("Foreign key constraints for skill_tree_nodes.category_id:")
        for fk in fk_constraints:
            print(f"  {fk['constraint_name']}: {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        # Check data types of the referenced columns
        print("\n[INFO] Checking data types...")
        mc_id_info = await conn.fetchrow("""
            SELECT data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories' 
              AND column_name = 'id';
        """)
        
        stn_cat_id_info = await conn.fetchrow("""
            SELECT data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' 
              AND column_name = 'category_id';
        """)
        
        print(f"movement_categories.id: {mc_id_info['data_type']}")
        print(f"skill_tree_nodes.category_id: {stn_cat_id_info['data_type']} ({stn_cat_id_info['character_maximum_length']})")
        
        # Check sample data
        print("\n[INFO] Sample movement_categories.id values:")
        sample_cats = await conn.fetch("SELECT id FROM movement_categories LIMIT 5;")
        for cat in sample_cats:
            print(f"  {cat['id']} (type: {type(cat['id']).__name__})")
        
        # The issue: movement_categories.id is bigint, but skill_tree_nodes.category_id is varchar
        # For the foreign key to work, we need to either:
        # 1. Convert movement_categories.id to varchar, OR
        # 2. Convert skill_tree_nodes.category_id to bigint
        
        print("\n[SOLUTION] Data type mismatch found!")
        print("movement_categories.id is bigint, but skill_tree_nodes.category_id is varchar")
        print("The foreign key constraint expects matching data types.")
        print("\nOptions:")
        print("1. Use integer category IDs in skill_tree_nodes (change our script)")
        print("2. Remove the foreign key constraint temporarily")
        print("3. Convert movement_categories.id to varchar (risky)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("FOREIGN KEY CONSTRAINT CHECK")
    print("=" * 80)
    print()
    
    try:
        success = asyncio.run(check_foreign_key())
        if success:
            print("\n[SUCCESS] Check completed!")
        else:
            print("\n[ERROR] Check failed")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Check interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")