#!/usr/bin/env python3
"""
Check the actual structure of the movement_categories and movements tables.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_table_structure():
    """Check the structure of relevant tables."""
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
        
        # Check movement_categories table structure
        print("\n=== MOVEMENT_CATEGORIES TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'movement_categories'
            ORDER BY ordinal_position;
        """)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check movements table structure
        print("\n=== MOVEMENTS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'movements'
            ORDER BY ordinal_position;
        """)
        
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check if there are any foreign key constraints
        print("\n=== FOREIGN KEY CONSTRAINTS ===")
        constraints = await conn.fetch("""
            SELECT 
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
            AND (tc.table_name = 'movement_categories' OR tc.table_name = 'movements');
        """)
        
        for constraint in constraints:
            print(f"  {constraint['table_name']}.{constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to check structure: {e}")
        return False

if __name__ == "__main__":
    print("CHECKING DATABASE TABLE STRUCTURE")
    print("=" * 50)
    
    try:
        asyncio.run(check_table_structure())
    except Exception as e:
        print(f"Unexpected error: {e}")