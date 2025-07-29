#!/usr/bin/env python3
"""
Debug script to check UserSkillProgress table structure and data.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_skill_progress_table():
    """Debug the user_skill_progress table structure and data."""
    
    # Get database connection details
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/ros_db')
    
    try:
        print("Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        print("\n" + "="*80)
        print("USER_SKILL_PROGRESS TABLE STRUCTURE")
        print("="*80)
        
        # Check table structure
        table_info = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'user_skill_progress'
            ORDER BY ordinal_position;
        """)
        
        print("Columns:")
        for row in table_info:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']}, default: {row['column_default']})")
        
        print("\n" + "="*80)
        print("SKILL_TREE_NODES TABLE STRUCTURE")
        print("="*80)
        
        # Check skill_tree_nodes structure
        nodes_info = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position
            LIMIT 10;
        """)
        
        print("Columns:")
        for row in nodes_info:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']}, default: {row['column_default']})")
        
        print("\n" + "="*80)
        print("SAMPLE DATA FROM SKILL_TREE_NODES")
        print("="*80)
        
        # Check some sample skill tree nodes
        sample_nodes = await conn.fetch("""
            SELECT id, node_id, category_id, level, name
            FROM skill_tree_nodes 
            WHERE node_id LIKE 'push_%'
            ORDER BY id
            LIMIT 5;
        """)
        
        print("Sample nodes:")
        for row in sample_nodes:
            print(f"  ID: {row['id']} | node_id: '{row['node_id']}' | category: {row['category_id']} | level: {row['level']} | name: {row['name']}")
        
        print("\n" + "="*80)
        print("SAMPLE DATA FROM USER_SKILL_PROGRESS")
        print("="*80)
        
        # Check existing progress data
        progress_data = await conn.fetch("""
            SELECT ascendant_id, node_id, unlocked_at
            FROM user_skill_progress 
            ORDER BY unlocked_at DESC
            LIMIT 10;
        """)
        
        print("Recent progress entries:")
        if progress_data:
            for row in progress_data:
                print(f"  User: {row['ascendant_id']} | Node ID: {row['node_id']} | Unlocked: {row['unlocked_at']}")
        else:
            print("  No progress entries found")
        
        print("\n" + "="*80)
        print("TESTING SPECIFIC QUERY")
        print("="*80)
        
        # Test the specific failing query
        print("Looking for push_1 node...")
        push_node = await conn.fetchrow("""
            SELECT id, node_id, category_id, level 
            FROM skill_tree_nodes 
            WHERE node_id = 'push_1';
        """)
        
        if push_node:
            print(f"Found push_1: ID={push_node['id']}, node_id='{push_node['node_id']}', category={push_node['category_id']}, level={push_node['level']}")
            
            # Test the problematic query with correct types
            print(f"\nTesting progress query with user_id=1, node_db_id={push_node['id']}...")
            existing_progress = await conn.fetchrow("""
                SELECT ascendant_id, node_id, unlocked_at
                FROM user_skill_progress 
                WHERE ascendant_id = $1 AND node_id = $2;
            """, 1, push_node['id'])
            
            if existing_progress:
                print(f"Found existing progress: {existing_progress}")
            else:
                print("No existing progress found (this is expected for new unlock)")
        else:
            print("❌ push_1 node not found in database!")
        
        await conn.close()
        print("\nDatabase check completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_skill_progress_table())