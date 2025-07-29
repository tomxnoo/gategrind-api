#!/usr/bin/env python3
"""
Debug the current schema state to understand why the InvalidCachedStatementError persists.
This will help us identify if our schema changes were applied correctly.
"""

import asyncio
import os
from urllib.parse import urlparse

async def debug_schema_state():
    """Debug the current database schema state."""
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
        print("\n" + "="*60)
        print("CURRENT SCHEMA STATE")
        print("="*60)
        
        # 1. Check movement_categories table structure
        print("\n[1] movement_categories table structure:")
        mc_columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories'
            ORDER BY ordinal_position;
        """)
        
        for col in mc_columns:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']}: {col['data_type']}{max_len} {nullable}")
        
        # 2. Check movements table structure (category_id column)
        print("\n[2] movements.category_id column:")
        mov_cat_col = await conn.fetchrow("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'movements' AND column_name = 'category_id';
        """)
        
        if mov_cat_col:
            max_len = f"({mov_cat_col['character_maximum_length']})" if mov_cat_col['character_maximum_length'] else ""
            nullable = "NULL" if mov_cat_col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  category_id: {mov_cat_col['data_type']}{max_len} {nullable}")
        else:
            print("  category_id: COLUMN NOT FOUND")
        
        # 3. Check skill_tree_nodes table structure (category_id column)
        print("\n[3] skill_tree_nodes.category_id column:")
        stn_cat_col = await conn.fetchrow("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        
        if stn_cat_col:
            max_len = f"({stn_cat_col['character_maximum_length']})" if stn_cat_col['character_maximum_length'] else ""
            nullable = "NULL" if stn_cat_col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  category_id: {stn_cat_col['data_type']}{max_len} {nullable}")
        else:
            print("  category_id: COLUMN NOT FOUND")
        
        # 4. Check foreign key constraints
        print("\n[4] Foreign key constraints:")
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
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND (ccu.table_name = 'movement_categories' OR tc.table_name IN ('movements', 'skill_tree_nodes'))
            ORDER BY tc.table_name, tc.constraint_name;
        """)
        
        if fk_constraints:
            for fk in fk_constraints:
                print(f"  {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        else:
            print("  No foreign key constraints found")
        
        # 5. Sample data to verify actual types
        print("\n[5] Sample data with Python types:")
        
        # movement_categories sample
        print("\n  movement_categories sample:")
        mc_sample = await conn.fetch("SELECT id, name FROM movement_categories LIMIT 3;")
        for row in mc_sample:
            print(f"    ID: '{row['id']}' (Python type: {type(row['id']).__name__}) - Name: {row['name']}")
        
        # movements sample
        print("\n  movements sample:")
        mov_sample = await conn.fetch("SELECT id, name, category_id FROM movements LIMIT 3;")
        for row in mov_sample:
            cat_id = row['category_id']
            print(f"    Movement: {row['name']} - Category ID: '{cat_id}' (Python type: {type(cat_id).__name__})")
        
        # skill_tree_nodes sample
        print("\n  skill_tree_nodes sample:")
        stn_sample = await conn.fetch("SELECT node_id, category_id, level FROM skill_tree_nodes LIMIT 3;")
        for row in stn_sample:
            cat_id = row['category_id']
            print(f"    Node: {row['node_id']} - Category ID: '{cat_id}' (Python type: {type(cat_id).__name__})")
        
        # 6. Test the exact query that's failing
        print("\n[6] Testing the failing query:")
        print("Query: SELECT movement_categories.id, movement_categories.name, movement_categories.primary_stat, movement_categories.created_at, movement_categories.updated_at FROM movement_categories ORDER BY movement_categories.id")
        
        try:
            test_result = await conn.fetch("""
                SELECT movement_categories.id, movement_categories.name, movement_categories.primary_stat, movement_categories.created_at, movement_categories.updated_at 
                FROM movement_categories 
                ORDER BY movement_categories.id
            """)
            print(f"  SUCCESS: Query returned {len(test_result)} rows")
            if test_result:
                first_row = test_result[0]
                print(f"  First row ID: '{first_row['id']}' (type: {type(first_row['id']).__name__})")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # 7. Check if there are any problematic sequences or constraints
        print("\n[7] Checking for sequences and indexes on movement_categories.id:")
        sequences = await conn.fetch("""
            SELECT sequence_name, data_type, start_value, increment
            FROM information_schema.sequences 
            WHERE sequence_name LIKE '%movement_categories%';
        """)
        
        if sequences:
            for seq in sequences:
                print(f"  Sequence: {seq['sequence_name']} - Type: {seq['data_type']}")
        else:
            print("  No sequences found for movement_categories")
        
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE tablename = 'movement_categories';
        """)
        
        if indexes:
            for idx in indexes:
                print(f"  Index: {idx['indexname']} - Definition: {idx['indexdef']}")
        else:
            print("  No indexes found for movement_categories")
        
        await conn.close()
        
        print("\n" + "="*60)
        print("DIAGNOSIS COMPLETE")
        print("="*60)
        
        # Analysis
        print("\nANALYSIS:")
        print("1. If movement_categories.id is still 'bigint', our conversion failed")
        print("2. If it's 'character varying', but the query still fails, there might be a sequence issue")
        print("3. If data types are mixed (some bigint, some varchar), we have partial conversion")
        print("4. The InvalidCachedStatementError might indicate PostgreSQL metadata inconsistency")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("SCHEMA STATE DEBUG")
    print("="*80)
    print()
    print("This will analyze the current database schema state")
    print("to understand why the InvalidCachedStatementError persists.")
    print()
    
    try:
        success = asyncio.run(debug_schema_state())
        if success:
            print("\n[SUCCESS] Debug completed successfully!")
        else:
            print("\n[ERROR] Debug failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Debug interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")