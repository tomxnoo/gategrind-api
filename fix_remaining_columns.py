#!/usr/bin/env python3
"""
Fix the remaining column issues that couldn't be handled by the main schema sync.
Specifically handles the movement_categories.primary_stat column.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_remaining_columns():
    """Fix specific remaining column issues."""
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
        
        # Fix movement_categories.primary_stat column
        print("\n🔧 Fixing movement_categories.primary_stat column...")
        
        # Check if column exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'movement_categories' 
                AND column_name = 'primary_stat'
            );
        """)
        
        if column_exists:
            print("✓ primary_stat column already exists")
        else:
            try:
                # Add the column with proper VARCHAR length
                await conn.execute("""
                    ALTER TABLE movement_categories 
                    ADD COLUMN primary_stat VARCHAR(50) NOT NULL DEFAULT 'strength';
                """)
                print("✓ Added primary_stat column (VARCHAR(50))")
                
                # Remove the default after adding
                await conn.execute("""
                    ALTER TABLE movement_categories 
                    ALTER COLUMN primary_stat DROP DEFAULT;
                """)
                print("✓ Removed temporary default")
                
            except Exception as e:
                print(f"❌ Failed to add primary_stat column: {e}")
        
        # Fix movements.stat_reward_type column if needed
        print("\n🔧 Fixing movements.stat_reward_type column...")
        
        stat_reward_column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'movements' 
                AND column_name = 'stat_reward_type'
            );
        """)
        
        if stat_reward_column_exists:
            print("✓ stat_reward_type column already exists")
        else:
            try:
                # Add the column with proper VARCHAR length
                await conn.execute("""
                    ALTER TABLE movements 
                    ADD COLUMN stat_reward_type VARCHAR(50) NOT NULL DEFAULT 'strength';
                """)
                print("✓ Added stat_reward_type column (VARCHAR(50))")
                
                # Remove the default after adding
                await conn.execute("""
                    ALTER TABLE movements 
                    ALTER COLUMN stat_reward_type DROP DEFAULT;
                """)
                print("✓ Removed temporary default")
                
            except Exception as e:
                print(f"❌ Failed to add stat_reward_type column: {e}")
        
        # Fix any remaining columns from the awakening system that had integer issues
        print("\n🔧 Fixing remaining awakening system columns...")
        
        awakening_fixes = [
            ("awakening_quests", "progress_reps", "INTEGER", "0"),
            ("awakening_quests", "progress_time", "INTEGER", "0"),
            ("awakening_quests", "progress_distance", "INTEGER", "0"),
            ("awakening_rewards", "shadow_keys", "INTEGER", "0"),
            ("awakening_rewards", "xp_gained", "INTEGER", "0"),
            ("awakening_rewards", "stat_points", "INTEGER", "0"),
            ("awakening_rewards", "streak_bonus", "INTEGER", "0"),
            ("awakening_rewards", "aura_change", "INTEGER", "0"),
            ("user_awakening_progress", "progress_reps", "INTEGER", "0"),
            ("user_awakening_progress", "progress_time", "INTEGER", "0"),
            ("user_awakening_progress", "progress_distance", "INTEGER", "0"),
            ("user_awakening_progress", "rewards_claimed", "BOOLEAN", "false"),
        ]
        
        for table_name, column_name, column_type, default_val in awakening_fixes:
            try:
                # Check if column exists
                exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = $1 AND column_name = $2
                    );
                """, table_name, column_name)
                
                if not exists:
                    await conn.execute(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {column_type} NOT NULL DEFAULT {default_val};
                    """)
                    
                    await conn.execute(f"""
                        ALTER TABLE {table_name} 
                        ALTER COLUMN {column_name} DROP DEFAULT;
                    """)
                    
                    print(f"✓ Added {table_name}.{column_name}")
                
            except Exception as e:
                print(f"! Warning: Could not add {table_name}.{column_name}: {e}")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: Remaining column fixes completed!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. Test the Awakening system")
        print("4. All remaining schema errors should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("REMAINING DATABASE COLUMN FIXES")
    print("=" * 70)
    
    try:
        success = asyncio.run(fix_remaining_columns())
        if success:
            print("\n✅ All remaining fixes completed successfully!")
        else:
            print("\n❌ Some fixes failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")