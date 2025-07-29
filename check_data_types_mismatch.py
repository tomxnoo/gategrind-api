#!/usr/bin/env python3
"""
Check the data type mismatch between movements.node_id and skill_tree_nodes.id
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_data_types_mismatch():
    """Check the data types and sample data to understand the mismatch."""
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
        
        print("\n" + "="*60)
        print("DATA TYPE MISMATCH ANALYSIS")
        print("="*60)
        
        # 1. Check skill_tree_nodes table structure and sample data
        print("\n[1] skill_tree_nodes table:")
        
        stn_columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        print("  Columns:")
        for col in stn_columns:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"    {col['column_name']}: {col['data_type']}{max_len}")
        
        print("\n  Sample data:")
        stn_sample = await conn.fetch("SELECT id, node_id, category_id, level FROM skill_tree_nodes LIMIT 5;")
        for row in stn_sample:
            print(f"    ID: {row['id']} (type: {type(row['id']).__name__}) | Node ID: '{row['node_id']}' | Category: '{row['category_id']}' | Level: {row['level']}")
        
        # 2. Check movements table structure and sample data
        print("\n[2] movements table:")
        
        mov_columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'movements'
            ORDER BY ordinal_position;
        """)
        
        print("  Columns:")
        for col in mov_columns:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"    {col['column_name']}: {col['data_type']}{max_len}")
        
        print("\n  Sample data:")
        mov_sample = await conn.fetch("SELECT id, name, node_id, category_id FROM movements LIMIT 5;")
        for row in mov_sample:
            node_id = row['node_id']
            cat_id = row['category_id']
            print(f"    Movement: {row['name']} | Node ID: '{node_id}' ({type(node_id).__name__}) | Category: '{cat_id}' ({type(cat_id).__name__})")
        
        # 3. Check the foreign key relationship
        print("\n[3] Foreign key relationships:")
        
        # Check if there's a foreign key between movements.node_id and skill_tree_nodes
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
              AND (tc.table_name = 'movements' OR ccu.table_name = 'skill_tree_nodes')
            ORDER BY tc.table_name, tc.constraint_name;
        """)
        
        if fk_constraints:
            for fk in fk_constraints:
                print(f"    {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        else:
            print("    No foreign key constraints found")
        
        # 4. Try to understand the mismatch
        print("\n[4] Data Mismatch Analysis:")
        
        # Check if skill_tree_nodes.id is integer but node_id is string
        try:
            stn_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
            print(f"    skill_tree_nodes records: {stn_count}")
            
            mov_count = await conn.fetchval("SELECT COUNT(*) FROM movements;")
            print(f"    movements records: {mov_count}")
            
            # Check if movements.node_id values exist in skill_tree_nodes.node_id
            orphan_count = await conn.fetchval("""
                SELECT COUNT(*) FROM movements m
                WHERE m.node_id IS NOT NULL 
                AND NOT EXISTS (
                    SELECT 1 FROM skill_tree_nodes s 
                    WHERE s.node_id = m.node_id
                );
            """)
            print(f"    Orphaned movements (node_id not in skill_tree_nodes): {orphan_count}")
            
            # Check if movements.node_id values exist in skill_tree_nodes.id (integer comparison)
            try:
                orphan_count_id = await conn.fetchval("""
                    SELECT COUNT(*) FROM movements m
                    WHERE m.node_id IS NOT NULL 
                    AND NOT EXISTS (
                        SELECT 1 FROM skill_tree_nodes s 
                        WHERE s.id::text = m.node_id
                    );
                """)
                print(f"    Movements with node_id not matching skill_tree_nodes.id: {orphan_count_id}")
            except Exception as e:
                print(f"    Could not check skill_tree_nodes.id match: {e}")
                
        except Exception as e:
            print(f"    Error in mismatch analysis: {e}")
        
        # 5. Show what SQLAlchemy is trying to do
        print("\n[5] SQLAlchemy Query Issue:")
        print("    SQLAlchemy is trying to run:")
        print("      SELECT * FROM movements WHERE node_id IN (3, 4, 5, 6, 7, ...)")
        print("    But movements.node_id is varchar, expecting strings like:")
        print("      'cat_10_level_1', 'cat_10_level_2', etc.")
        print("    While skill_tree_nodes.id are integers: 3, 4, 5, 6, 7, ...")
        print("    And skill_tree_nodes.node_id are strings: 'cat_10_level_1', 'cat_10_level_2', ...")
        
        await conn.close()
        
        print("\n" + "="*60)
        print("DIAGNOSIS")
        print("="*60)
        
        print("\nThe issue is:")
        print("1. movements.node_id is VARCHAR and contains string values")
        print("2. skill_tree_nodes.id is INTEGER (3, 4, 5, 6, 7...)")
        print("3. skill_tree_nodes.node_id is VARCHAR ('cat_10_level_1', 'cat_10_level_2'...)")
        print("4. SQLAlchemy is trying to match movements.node_id with skill_tree_nodes.id")
        print("5. But it should match movements.node_id with skill_tree_nodes.node_id")
        print("\nSolution:")
        print("- Update the foreign key relationship to use the correct columns")
        print("- OR fix the data types to be consistent")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("DATA TYPE MISMATCH CHECKER")
    print("="*80)
    print()
    print("This will analyze the data type mismatch between")
    print("movements.node_id and skill_tree_nodes tables.")
    print()
    
    try:
        success = asyncio.run(check_data_types_mismatch())
        if success:
            print("\n[SUCCESS] Analysis completed successfully!")
        else:
            print("\n[ERROR] Analysis failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")