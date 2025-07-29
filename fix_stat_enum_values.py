#!/usr/bin/env python3
"""
Fix the stat values in the database to match the expected enum values.
The model expects: STR, END, TECH
But we stored: strength, endurance, flexibility, etc.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_stat_enum_values():
    """Update stat values to match the enum."""
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
        
        # Fix movement_categories.primary_stat values
        print("\n[FIX] Fixing movement_categories.primary_stat values...")
        
        updates = [
            ("UPDATE movement_categories SET primary_stat = 'STR' WHERE primary_stat IN ('strength', 'str');", "strength -> STR"),
            ("UPDATE movement_categories SET primary_stat = 'END' WHERE primary_stat IN ('endurance', 'end');", "endurance -> END"),
            ("UPDATE movement_categories SET primary_stat = 'TECH' WHERE primary_stat IN ('flexibility', 'technique', 'tech');", "flexibility/technique -> TECH"),
        ]
        
        for query, description in updates:
            # Execute the update query
            result = await conn.execute(query)
            # Extract row count from result string (e.g., "UPDATE 5")
            rows_updated = int(result.split()[-1]) if result and result.startswith('UPDATE') else 0
            print(f"  [OK] Updated {rows_updated} rows: {description}")
        
        # Fix movements.stat_reward_type values
        print("\n[FIX] Fixing movements.stat_reward_type values...")
        
        for query, description in updates:
            # Adapt query for movements table
            movements_query = query.replace("movement_categories", "movements").replace("primary_stat", "stat_reward_type")
            result = await conn.execute(movements_query)
            # Extract row count from result string (e.g., "UPDATE 5")
            rows_updated = int(result.split()[-1]) if result and result.startswith('UPDATE') else 0
            print(f"  [OK] Updated {rows_updated} rows: {description}")
        
        # Verify the fix
        print("\n[VERIFY] Verifying updated values...")
        
        # Check movement_categories
        cat_stats = await conn.fetch("""
            SELECT DISTINCT primary_stat, COUNT(*) as count 
            FROM movement_categories 
            GROUP BY primary_stat 
            ORDER BY primary_stat;
        """)
        
        print("\nMovement categories by stat:")
        for row in cat_stats:
            print(f"  {row['primary_stat']}: {row['count']} categories")
        
        # Check movements
        mov_stats = await conn.fetch("""
            SELECT DISTINCT stat_reward_type, COUNT(*) as count 
            FROM movements 
            GROUP BY stat_reward_type 
            ORDER BY stat_reward_type;
        """)
        
        print("\nMovements by stat reward type:")
        for row in mov_stats:
            print(f"  {row['stat_reward_type']}: {row['count']} movements")
        
        await conn.close()
        
        print("\n[SUCCESS] Stat enum values fixed!")
        print("\nNext steps:")
        print("1. The Skill Tree panel should now load without errors")
        print("2. You should see all categories and movements")
        print("3. Test movement logging functionality")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("STAT ENUM VALUES FIX")
    print("=" * 70)
    print()
    print("This will update stat values to match the expected enum:")
    print("- strength -> STR")
    print("- endurance -> END") 
    print("- flexibility/technique -> TECH")
    print()
    
    try:
        success = asyncio.run(fix_stat_enum_values())
        if success:
            print("\n[SUCCESS] Fix completed successfully!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")