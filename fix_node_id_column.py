#!/usr/bin/env python3
"""
Fix the movements.node_id column to allow null values temporarily.
This allows us to seed basic movements linked to categories without requiring skill tree nodes.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_node_id_column():
    """Make node_id column nullable in movements table."""
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
        
        # Check current node_id column constraint
        print("\n🔧 Checking movements.node_id column constraint...")
        
        constraint_info = await conn.fetch("""
            SELECT column_name, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_name = 'movements' AND column_name = 'node_id';
        """)
        
        if constraint_info:
            col_info = constraint_info[0]
            print(f"Current node_id: {col_info['data_type']}, nullable: {col_info['is_nullable']}")
            
            if col_info['is_nullable'] == 'NO':
                print("Making node_id column nullable...")
                
                try:
                    # Make node_id nullable
                    await conn.execute("""
                        ALTER TABLE movements 
                        ALTER COLUMN node_id DROP NOT NULL;
                    """)
                    print("✓ node_id column is now nullable")
                    
                except Exception as e:
                    print(f"❌ Failed to make node_id nullable: {e}")
                    return False
            else:
                print("✓ node_id column is already nullable")
        else:
            print("! node_id column not found")
            return False
        
        # Also check if we need to create some basic skill tree nodes for the future
        print("\n🌳 Checking for skill tree nodes...")
        
        node_count = await conn.fetchval("SELECT COUNT(*) FROM skill_tree_nodes;")
        print(f"Current skill tree nodes: {node_count}")
        
        if node_count == 0:
            print("No skill tree nodes found - movements will have null node_id for now")
            print("This is fine for basic movement logging, skill tree functionality can be added later")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: node_id column fix completed!")
        print("\nNext steps:")
        print("1. Run the skill tree seeding script again: python fix.py")
        print("2. Movements should now be created successfully")
        print("3. Test the Skill Tree panel")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MOVEMENTS NODE_ID COLUMN FIX")
    print("=" * 70)
    
    try:
        success = asyncio.run(fix_node_id_column())
        if success:
            print("\n✅ node_id column fix completed successfully!")
        else:
            print("\n❌ node_id column fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")