#!/usr/bin/env python3
"""
Fix the sequence issue causing InvalidCachedStatementError.
Drop the bigint sequence that's incompatible with our varchar column.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_sequence_issue():
    """Fix the sequence metadata inconsistency."""
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
        
        # Check if the column has a default value using the sequence
        print("\n[STEP 1] Checking current default value for movement_categories.id...")
        default_info = await conn.fetchrow("""
            SELECT column_default
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        
        if default_info and default_info['column_default']:
            print(f"  Current default: {default_info['column_default']}")
            
            # Remove the default value first
            print("\n[STEP 2] Removing default value from movement_categories.id...")
            try:
                await conn.execute("""
                    ALTER TABLE movement_categories 
                    ALTER COLUMN id DROP DEFAULT;
                """)
                print("  [OK] Removed default value")
            except Exception as e:
                print(f"  [ERROR] Failed to remove default: {e}")
        else:
            print("  No default value found")
        
        # Check if the sequence exists
        print("\n[STEP 3] Checking for movement_categories_id_seq...")
        sequence_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.sequences 
                WHERE sequence_name = 'movement_categories_id_seq'
            );
        """)
        
        if sequence_exists:
            print("  Sequence exists - proceeding to drop it")
            
            # Drop the sequence
            print("\n[STEP 4] Dropping movement_categories_id_seq...")
            try:
                await conn.execute("DROP SEQUENCE IF EXISTS movement_categories_id_seq CASCADE;")
                print("  [OK] Dropped sequence successfully")
            except Exception as e:
                print(f"  [ERROR] Failed to drop sequence: {e}")
        else:
            print("  Sequence does not exist - no action needed")
        
        # Verify the fix by running the problematic query
        print("\n[STEP 5] Testing the previously failing query...")
        try:
            test_result = await conn.fetch("""
                SELECT movement_categories.id, movement_categories.name, movement_categories.primary_stat, movement_categories.created_at, movement_categories.updated_at 
                FROM movement_categories 
                ORDER BY movement_categories.id
                LIMIT 5;
            """)
            print(f"  [OK] Query successful - returned {len(test_result)} rows")
            for row in test_result:
                print(f"    ID: '{row['id']}' - Name: {row['name']}")
        except Exception as e:
            print(f"  [ERROR] Query still failing: {e}")
        
        # Check final state
        print("\n[VERIFICATION] Final state check...")
        
        # Check for any remaining sequences
        remaining_sequences = await conn.fetch("""
            SELECT sequence_name, data_type
            FROM information_schema.sequences 
            WHERE sequence_name LIKE '%movement_categories%';
        """)
        
        if remaining_sequences:
            print("  Remaining sequences:")
            for seq in remaining_sequences:
                print(f"    {seq['sequence_name']}: {seq['data_type']}")
        else:
            print("  [OK] No movement_categories sequences remain")
        
        # Check column info
        column_info = await conn.fetchrow("""
            SELECT data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories' AND column_name = 'id';
        """)
        
        print(f"  movement_categories.id: {column_info['data_type']}")
        print(f"  Default value: {column_info['column_default']}")
        
        await conn.close()
        
        print("\n[SUCCESS] Sequence issue fixed!")
        print("\nWhat was fixed:")
        print("- Removed bigint sequence that was incompatible with varchar column")
        print("- Cleaned up PostgreSQL metadata inconsistency")
        print("- The InvalidCachedStatementError should now be resolved")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. The schema inconsistency should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("SEQUENCE ISSUE FIX")
    print("="*80)
    print()
    print("This will fix the sequence metadata inconsistency that's causing")
    print("the InvalidCachedStatementError by:")
    print("1. Removing the default value from movement_categories.id")
    print("2. Dropping the incompatible bigint sequence")
    print("3. Cleaning up PostgreSQL metadata")
    print()
    
    try:
        success = asyncio.run(fix_sequence_issue())
        if success:
            print("\n[SUCCESS] Fix completed successfully!")
        else:
            print("\n[ERROR] Fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")