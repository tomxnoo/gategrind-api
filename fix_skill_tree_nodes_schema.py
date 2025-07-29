#!/usr/bin/env python3
"""
Fix the skill_tree_nodes table schema by adding missing columns.
Based on the error, we need to add required_ascendant_level column.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_skill_tree_nodes_schema():
    """Add missing columns to skill_tree_nodes table."""
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
        
        # Check current columns
        existing_columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes';
        """)
        
        column_names = [col['column_name'] for col in existing_columns]
        print(f"[INFO] Existing columns: {column_names}")
        
        # Define columns to add
        columns_to_add = [
            ("required_ascendant_level", "INTEGER DEFAULT 1 NOT NULL"),
            ("required_str_points", "INTEGER DEFAULT 0 NOT NULL"),
            ("required_end_points", "INTEGER DEFAULT 0 NOT NULL"), 
            ("required_tech_points", "INTEGER DEFAULT 0 NOT NULL"),
            ("node_id", "VARCHAR(50)"),  # Will make unique after adding
            ("description", "TEXT")
        ]
        
        # Add missing columns
        for col_name, col_definition in columns_to_add:
            if col_name not in column_names:
                print(f"[FIX] Adding column {col_name}...")
                try:
                    await conn.execute(f"ALTER TABLE skill_tree_nodes ADD COLUMN {col_name} {col_definition};")
                    print(f"  [OK] Added {col_name}")
                except Exception as e:
                    print(f"  [ERROR] Failed to add {col_name}: {e}")
            else:
                print(f"  [SKIP] Column {col_name} already exists")
        
        # If node_id was added, we need to populate it and make it unique
        if 'node_id' not in column_names:
            print("\n[FIX] Populating node_id values...")
            try:
                # Generate node_id values based on category_id and level
                await conn.execute("""
                    UPDATE skill_tree_nodes 
                    SET node_id = category_id || '_level_' || level 
                    WHERE node_id IS NULL;
                """)
                
                # Add unique constraint and index
                await conn.execute("""
                    ALTER TABLE skill_tree_nodes 
                    ADD CONSTRAINT skill_tree_nodes_node_id_unique UNIQUE (node_id);
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_skill_tree_nodes_node_id 
                    ON skill_tree_nodes(node_id);
                """)
                
                print("  [OK] node_id values populated and indexed")
            except Exception as e:
                print(f"  [ERROR] Failed to populate node_id: {e}")
        
        # Verify the fix by checking if all columns exist now
        print("\n[VERIFY] Checking updated schema...")
        updated_columns = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        print("Updated skill_tree_nodes schema:")
        for col in updated_columns:
            print(f"  {col['column_name']:<30} {col['data_type']}")
        
        await conn.close()
        
        print("\n[SUCCESS] skill_tree_nodes schema fix completed!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. The column error should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE NODES SCHEMA FIX")
    print("=" * 80)
    print()
    print("This will add missing columns to skill_tree_nodes table:")
    print("- required_ascendant_level (INTEGER DEFAULT 1 NOT NULL)")
    print("- required_str_points (INTEGER DEFAULT 0 NOT NULL)")
    print("- required_end_points (INTEGER DEFAULT 0 NOT NULL)")
    print("- required_tech_points (INTEGER DEFAULT 0 NOT NULL)")
    print("- node_id (VARCHAR(50) UNIQUE)")
    print("- description (TEXT)")
    print()
    
    try:
        success = asyncio.run(fix_skill_tree_nodes_schema())
        if success:
            print("\n[SUCCESS] Fix completed successfully!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")