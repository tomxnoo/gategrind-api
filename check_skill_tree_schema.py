#!/usr/bin/env python3
"""
Check the actual schema of skill_tree_nodes table to understand the column types.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_skill_tree_schema():
    """Check the skill_tree_nodes table schema."""
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
        
        # Check skill_tree_nodes table structure
        print("\n=== SKILL_TREE_NODES TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'skill_tree_nodes'
            ORDER BY ordinal_position;
        """)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check if there's any foreign key constraint
        print("\n=== FOREIGN KEY CONSTRAINTS ===")
        constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
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
            AND tc.table_name = 'skill_tree_nodes';
        """)
        
        for constraint in constraints:
            print(f"  {constraint['constraint_name']}: {constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
        
        # Check movement_categories for reference
        print("\n=== MOVEMENT_CATEGORIES ID TYPE ===")
        cat_id_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        print(f"  movement_categories.id type: {cat_id_type}")
        
        # Check skill_tree_nodes category_id type
        node_cat_id_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'skill_tree_nodes' AND column_name = 'category_id';
        """)
        print(f"  skill_tree_nodes.category_id type: {node_cat_id_type}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to check structure: {e}")
        return False

if __name__ == "__main__":
    print("CHECKING SKILL TREE NODES TABLE STRUCTURE")
    print("=" * 50)
    
    try:
        asyncio.run(check_skill_tree_schema())
    except Exception as e:
        print(f"Unexpected error: {e}")