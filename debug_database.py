#!/usr/bin/env python3
"""
Database debugging script for Replit environment.
This script will fetch all relevant information about the skill tree system
to help diagnose the "Skill tree node '3' not found" error.
"""

import asyncio
import os
import sys
from urllib.parse import urlparse

async def debug_database():
    """Debug the database to understand the skill tree node structure."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        print("Run: pip install asyncpg")
        return False
    
    try:
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
        
        print("🔍 Connecting to database...")
        
        # Handle different URL formats
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
        
        print("✅ Connected successfully!")
        
        # =================================================================
        # 1. Check skill_tree_nodes table structure and data
        # =================================================================
        print("\n" + "="*60)
        print("1. SKILL TREE NODES TABLE")
        print("="*60)
        
        # Table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        print("\nTable structure:")
        for col in columns:
            print(f"  {col['column_name']:<25} {col['data_type']:<15} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        # All skill tree nodes
        nodes = await conn.fetch("""
            SELECT id, node_id, category_id, level, name, 
                   required_ascendant_level, required_str_points, 
                   required_end_points, required_tech_points
            FROM skill_tree_nodes
            ORDER BY category_id::integer, level;
        """)
        
        print(f"\nTotal nodes in database: {len(nodes)}")
        print("\nAll skill tree nodes:")
        print(f"{'DB_ID':<5} {'NODE_ID':<20} {'CAT_ID':<6} {'LVL':<3} {'NAME':<25} {'ASC_LVL':<7} {'STR':<5} {'END':<5} {'TECH':<5}")
        print("-" * 90)
        
        for node in nodes:
            print(f"{node['id']:<5} {node['node_id']:<20} {node['category_id']:<6} {node['level']:<3} {node['name']:<25} {node['required_ascendant_level']:<7} {node['required_str_points']:<5} {node['required_end_points']:<5} {node['required_tech_points']:<5}")
        
        # =================================================================
        # 2. Check movement_categories table
        # =================================================================
        print("\n" + "="*60)
        print("2. MOVEMENT CATEGORIES")
        print("="*60)
        
        categories = await conn.fetch("""
            SELECT id, name, primary_stat
            FROM movement_categories
            ORDER BY id::integer;
        """)
        
        print(f"\nTotal categories: {len(categories)}")
        print("\nMovement categories:")
        print(f"{'ID':<5} {'NAME':<30} {'PRIMARY_STAT':<12}")
        print("-" * 50)
        
        for cat in categories:
            print(f"{cat['id']:<5} {cat['name']:<30} {cat['primary_stat']:<12}")
        
        # =================================================================
        # 3. Check specific problem cases
        # =================================================================
        print("\n" + "="*60)
        print("3. PROBLEM ANALYSIS")
        print("="*60)
        
        # Check for node_id '3' specifically
        node_3 = await conn.fetch("""
            SELECT * FROM skill_tree_nodes WHERE node_id = '3';
        """)
        
        print(f"\nNodes with node_id = '3': {len(node_3)}")
        if node_3:
            for node in node_3:
                print(f"  Found: {dict(node)}")
        else:
            print("  No nodes found with node_id = '3'")
        
        # Check for nodes that might be interpreted as '3'
        numeric_like = await conn.fetch("""
            SELECT node_id, category_id, level, name
            FROM skill_tree_nodes 
            WHERE node_id ~ '^[0-9]+$' OR node_id LIKE '%_3' OR node_id LIKE '%3%'
            ORDER BY node_id;
        """)
        
        print(f"\nNodes with numeric or '3'-containing node_ids: {len(numeric_like)}")
        for node in numeric_like:
            print(f"  {node['node_id']:<20} -> Category {node['category_id']}, Level {node['level']}, {node['name']}")
        
        # Check expected configuration nodes
        expected_nodes = ['upper_dynamic_1', 'upper_dynamic_2', 'upper_dynamic_3', 
                         'mobility_flow_1', 'mobility_flow_2', 'mobility_flow_3',
                         'pull_vertical_1', 'pull_vertical_2', 'pull_vertical_3']
        
        print(f"\nChecking expected configuration nodes:")
        for expected in expected_nodes:
            found = await conn.fetch("""
                SELECT id, category_id, level, name
                FROM skill_tree_nodes 
                WHERE node_id = $1;
            """, expected)
            
            if found:
                node = found[0]
                print(f"  ✅ {expected:<20} -> Found (DB ID: {node['id']}, Cat: {node['category_id']}, Level: {node['level']})")
            else:
                print(f"  ❌ {expected:<20} -> NOT FOUND")
        
        # =================================================================
        # 4. Check user skill progress table
        # =================================================================
        print("\n" + "="*60)
        print("4. USER SKILL PROGRESS")
        print("="*60)
        
        # Table structure
        progress_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'user_skill_progress'
            ORDER BY ordinal_position;
        """)
        
        print("\nuser_skill_progress table structure:")
        for col in progress_columns:
            print(f"  {col['column_name']:<25} {col['data_type']:<15} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        # Sample data
        progress_data = await conn.fetch("""
            SELECT usp.id, usp.ascendant_id, usp.node_id, stn.node_id as skill_node_id
            FROM user_skill_progress usp
            LEFT JOIN skill_tree_nodes stn ON stn.id = usp.node_id
            LIMIT 10;
        """)
        
        print(f"\nSample user skill progress data: {len(progress_data)} records")
        if progress_data:
            print(f"{'PROG_ID':<8} {'USER_ID':<8} {'NODE_DB_ID':<10} {'SKILL_NODE_ID':<20}")
            print("-" * 50)
            for prog in progress_data:
                print(f"{prog['id']:<8} {prog['ascendant_id']:<8} {prog['node_id']:<10} {prog['skill_node_id'] or 'NULL':<20}")
        
        # =================================================================
        # 5. Check movements table relationship
        # =================================================================
        print("\n" + "="*60)
        print("5. MOVEMENTS TABLE RELATIONSHIP")
        print("="*60)
        
        # Check movements that reference skill tree nodes
        movements_with_nodes = await conn.fetch("""
            SELECT m.id, m.name, m.node_id, stn.node_id as skill_node_id, stn.name as skill_node_name
            FROM movements m
            LEFT JOIN skill_tree_nodes stn ON stn.node_id = m.node_id
            WHERE m.node_id IS NOT NULL
            LIMIT 15;
        """)
        
        print(f"\nMovements linked to skill nodes: {len(movements_with_nodes)} total (showing first 15)")
        if movements_with_nodes:
            print(f"{'MOV_ID':<6} {'MOVEMENT_NAME':<25} {'REF_NODE_ID':<15} {'SKILL_NODE_ID':<15} {'SKILL_NAME':<20}")
            print("-" * 90)
            for mov in movements_with_nodes:
                print(f"{mov['id']:<6} {mov['name'][:24]:<25} {mov['node_id']:<15} {mov['skill_node_id'] or 'NULL':<15} {(mov['skill_node_name'] or 'NULL')[:19]:<20}")
        
        # =================================================================
        # 6. Database integrity check
        # =================================================================
        print("\n" + "="*60)
        print("6. DATABASE INTEGRITY CHECK")
        print("="*60)
        
        # Check for orphaned movements
        orphaned_movements = await conn.fetch("""
            SELECT COUNT(*) as count
            FROM movements m
            WHERE m.node_id IS NOT NULL 
            AND NOT EXISTS (
                SELECT 1 FROM skill_tree_nodes stn 
                WHERE stn.node_id = m.node_id
            );
        """)
        
        print(f"\nOrphaned movements (reference non-existent skill nodes): {orphaned_movements[0]['count']}")
        
        # Check for missing prerequisite nodes
        missing_prereqs = await conn.fetch("""
            SELECT COUNT(*) as count
            FROM user_skill_progress usp
            WHERE NOT EXISTS (
                SELECT 1 FROM skill_tree_nodes stn 
                WHERE stn.id = usp.node_id
            );
        """)
        
        print(f"User progress records with missing skill nodes: {missing_prereqs[0]['count']}")
        
        await conn.close()
        
        # =================================================================
        # 7. Analysis summary
        # =================================================================
        print("\n" + "="*60)
        print("7. ANALYSIS SUMMARY")
        print("="*60)
        
        print("\n🔍 Key Findings:")
        print("1. The error 'Skill tree node \"3\" not found' suggests the system is looking")
        print("   for a node with node_id='3', but this doesn't exist in the expected format.")
        
        print("\n2. Expected node_id format: 'category_level' (e.g., 'upper_dynamic_3')")
        print("   But the system might be receiving just '3' instead.")
        
        print("\n3. This could be caused by:")
        print("   - Frontend sending wrong node_id format")
        print("   - Database having wrong node_id values")
        print("   - Mismatch between skill_tree_config.py and database")
        
        print("\n4. Check the above data to see:")
        print("   - Are node_ids in correct format?")
        print("   - Do expected nodes exist?")
        print("   - Are there any '3' or numeric-only node_ids?")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Database debugging failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE DATABASE DEBUGGING SCRIPT")
    print("=" * 80)
    print()
    print("This script will examine the database to understand the")
    print("'Skill tree node not found' error.")
    print()
    
    try:
        success = asyncio.run(debug_database())
        if success:
            print("\n✅ Database debugging completed!")
        else:
            print("\n❌ Database debugging failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Debugging interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")