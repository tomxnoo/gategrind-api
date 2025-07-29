#!/usr/bin/env python3
"""
Fix UserSkillProgress table schema to match new string-based node IDs.

The issue is that user_skill_progress.node_id column needs to reference
skill_tree_nodes.node_id (VARCHAR) instead of skill_tree_nodes.id (INTEGER).
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_user_skill_progress_schema():
    """Fix the user_skill_progress table to use string node_id references."""
    
    # Get database connection details
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/ros_db')
    
    try:
        print("Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        print("\n" + "="*80)
        print("CHECKING CURRENT SCHEMA")
        print("="*80)
        
        # Check current table structure
        progress_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'user_skill_progress'
            ORDER BY ordinal_position;
        """)
        
        print("Current user_skill_progress columns:")
        for row in progress_columns:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        # Check if we need to fix the schema
        node_id_column = next((col for col in progress_columns if col['column_name'] == 'node_id'), None)
        
        if not node_id_column:
            print("❌ node_id column not found!")
            return False
        
        if node_id_column['data_type'] == 'character varying':
            print("✅ Schema already correct - node_id is VARCHAR")
            return True
        
        print(f"❌ Schema needs fixing - node_id is {node_id_column['data_type']}, should be VARCHAR")
        
        print("\n" + "="*80)
        print("BACKING UP AND UPDATING SCHEMA")
        print("="*80)
        
        # Start transaction
        async with conn.transaction():
            print("1. Backing up existing data...")
            
            # Create backup table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_skill_progress_backup AS 
                SELECT * FROM user_skill_progress;
            """)
            
            print("2. Dropping existing constraints...")
            
            # Drop foreign key constraint
            await conn.execute("""
                ALTER TABLE user_skill_progress 
                DROP CONSTRAINT IF EXISTS user_skill_progress_node_id_fkey;
            """)
            
            # Drop unique constraint
            await conn.execute("""
                ALTER TABLE user_skill_progress 
                DROP CONSTRAINT IF EXISTS uq_user_skill_progress_ascendant_node;
            """)
            
            print("3. Converting node_id column to VARCHAR...")
            
            # Change column type to VARCHAR and update references
            await conn.execute("""
                ALTER TABLE user_skill_progress 
                ALTER COLUMN node_id TYPE VARCHAR(50);
            """)
            
            print("4. Updating node_id values to string format...")
            
            # Update existing data to use string node_id instead of numeric id
            # This requires joining with skill_tree_nodes to map id -> node_id
            update_result = await conn.execute("""
                UPDATE user_skill_progress 
                SET node_id = stn.node_id
                FROM skill_tree_nodes stn 
                WHERE user_skill_progress.node_id::INTEGER = stn.id;
            """)
            
            print(f"   Updated {update_result.split()[-1]} rows")
            
            print("5. Adding new foreign key constraint...")
            
            # Add foreign key constraint to skill_tree_nodes.node_id
            await conn.execute("""
                ALTER TABLE user_skill_progress 
                ADD CONSTRAINT user_skill_progress_node_id_fkey 
                FOREIGN KEY (node_id) REFERENCES skill_tree_nodes (node_id);
            """)
            
            print("6. Adding unique constraint...")
            
            # Add back unique constraint
            await conn.execute("""
                ALTER TABLE user_skill_progress 
                ADD CONSTRAINT uq_user_skill_progress_ascendant_node 
                UNIQUE (ascendant_id, node_id);
            """)
            
            print("7. Updating indexes...")
            
            # Recreate indexes
            await conn.execute("""
                DROP INDEX IF EXISTS idx_user_skill_progress_node_id;
                CREATE INDEX idx_user_skill_progress_node_id ON user_skill_progress (node_id);
            """)
        
        print("\n" + "="*80)
        print("VERIFYING UPDATED SCHEMA")
        print("="*80)
        
        # Verify the fix
        updated_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'user_skill_progress'
            ORDER BY ordinal_position;
        """)
        
        print("Updated user_skill_progress columns:")
        for row in updated_columns:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        # Test the query that was failing
        print("\nTesting the previously failing query...")
        test_result = await conn.fetchrow("""
            SELECT ascendant_id, node_id, unlocked_at
            FROM user_skill_progress 
            WHERE ascendant_id = $1 AND node_id = $2
            LIMIT 1;
        """, 1, 'push_1')
        
        print("Query executed successfully!")
        if test_result:
            print(f"Found existing progress: {test_result}")
        else:
            print("No existing progress found (expected for new unlock)")
        
        await conn.close()
        print("\n✅ Schema fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("USER SKILL PROGRESS SCHEMA FIX")
    print("="*80)
    print("This script fixes the user_skill_progress table to use string node_id")
    print("references instead of numeric id references.")
    print()
    
    result = asyncio.run(fix_user_skill_progress_schema())
    
    if result:
        print("\n🎉 Schema fix completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Discord bot")
        print("2. Try unlocking skill nodes - they should work now!")
    else:
        print("\n❌ Schema fix failed - check output above")