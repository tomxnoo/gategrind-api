#!/usr/bin/env python3
"""
Check the actual schema of the skill_tree_nodes table to see what columns are missing.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_skill_tree_nodes_schema():
    """Check the current schema of skill_tree_nodes table."""
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
        
        # Check if skill_tree_nodes table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'skill_tree_nodes'
            );
        """)
        
        if not table_exists:
            print("[ERROR] skill_tree_nodes table does not exist!")
            await conn.close()
            return False
        
        print("[OK] skill_tree_nodes table exists")
        
        # Get all columns in the table
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        print(f"\n[INFO] Current skill_tree_nodes table schema ({len(columns)} columns):")
        print("-" * 80)
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<30} {col['data_type']:<15} {nullable:<8} {default}")
        
        # Check for expected columns based on the model
        expected_columns = [
            'id', 'created_at', 'updated_at',  # BaseModel columns
            'node_id', 'category_id', 'level', 'name', 'description',  # Core columns
            'required_ascendant_level', 'required_str_points', 'required_end_points', 'required_tech_points'  # Requirements
        ]
        
        existing_columns = [col['column_name'] for col in columns]
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"\n[ERROR] Missing columns: {missing_columns}")
            print("\nSQL to add missing columns:")
            for col in missing_columns:
                if col == 'required_ascendant_level':
                    print(f"ALTER TABLE skill_tree_nodes ADD COLUMN {col} INTEGER DEFAULT 1 NOT NULL;")
                elif col in ['required_str_points', 'required_end_points', 'required_tech_points']:
                    print(f"ALTER TABLE skill_tree_nodes ADD COLUMN {col} INTEGER DEFAULT 0 NOT NULL;")
                elif col == 'node_id':
                    print(f"ALTER TABLE skill_tree_nodes ADD COLUMN {col} VARCHAR(50) NOT NULL;")
                elif col == 'description':
                    print(f"ALTER TABLE skill_tree_nodes ADD COLUMN {col} TEXT;")
        else:
            print("\n[OK] All expected columns exist!")
        
        # Check if there's any data in the table
        row_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        print(f"\n[INFO] skill_tree_nodes table has {row_count} rows")
        
        await conn.close()
        return len(missing_columns) == 0
        
    except Exception as e:
        print(f"\n[ERROR] Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE NODES SCHEMA CHECK")
    print("=" * 80)
    print()
    
    try:
        success = asyncio.run(check_skill_tree_nodes_schema())
        if success:
            print("\n[SUCCESS] Schema check completed - all columns exist!")
        else:
            print("\n[ERROR] Schema check failed - missing columns detected")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Check interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")