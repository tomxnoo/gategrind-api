#!/usr/bin/env python3
"""
Check the actual column names in the skill_tree_nodes table.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_actual_schema():
    """Check the real column names in skill_tree_nodes table."""
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
        
        # Get all columns in skill_tree_nodes table
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        print(f"\n[INFO] skill_tree_nodes table schema ({len(columns)} columns):")
        print("-" * 80)
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<35} {col['data_type']:<20} {nullable:<10} {default}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("SKILL TREE NODES ACTUAL SCHEMA CHECK")
    print("=" * 80)
    print()
    
    try:
        success = asyncio.run(check_actual_schema())
        if success:
            print("\n[SUCCESS] Schema check completed!")
        else:
            print("\n[ERROR] Schema check failed")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Check interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")