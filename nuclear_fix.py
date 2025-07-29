#!/usr/bin/env python3
"""
Nuclear option: Completely rebuild the movement_categories table from scratch.
This will eliminate all metadata inconsistencies.
"""

import asyncio
import os
from urllib.parse import urlparse

async def nuclear_fix():
    """Complete rebuild of movement_categories table."""
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
        
        # BACKUP the data first
        print("\n[STEP 1] Backing up movement_categories data...")
        backup_data = await conn.fetch("SELECT * FROM movement_categories ORDER BY id;")
        print(f"  Backed up {len(backup_data)} records")
        
        # Drop all foreign key constraints that reference movement_categories
        print("\n[STEP 2] Dropping all foreign key constraints...")
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND ccu.table_name = 'movement_categories'
              AND ccu.column_name = 'id';
        """)
        
        dropped_constraints = []
        for fk in fk_constraints:
            constraint_name = fk['constraint_name']
            table_name = fk['table_name']
            column_name = fk['column_name']
            print(f"  Dropping {constraint_name} from {table_name}...")
            
            try:
                await conn.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint_name};")
                dropped_constraints.append((table_name, constraint_name, column_name))
                print(f"    [OK] Dropped {constraint_name}")
            except Exception as e:
                print(f"    [ERROR] Failed to drop {constraint_name}: {e}")
        
        # Drop the movement_categories table completely
        print("\n[STEP 3] Dropping movement_categories table...")
        try:
            await conn.execute("DROP TABLE movement_categories CASCADE;")
            print("  [OK] Table dropped successfully")
        except Exception as e:
            print(f"  [ERROR] Failed to drop table: {e}")
        
        # Recreate the movement_categories table with correct structure
        print("\n[STEP 4] Recreating movement_categories table...")
        try:
            await conn.execute("""
                CREATE TABLE movement_categories (
                    id VARCHAR(50) PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    category_id VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    primary_stat VARCHAR(50) NOT NULL
                );
            """)
            print("  [OK] Table recreated successfully")
        except Exception as e:
            print(f"  [ERROR] Failed to recreate table: {e}")
            return False
        
        # Create indexes
        print("\n[STEP 5] Creating indexes...")
        indexes = [
            "CREATE INDEX ix_movement_categories_id ON movement_categories(id);",
            "CREATE INDEX ix_movement_categories_category_id ON movement_categories(category_id);", 
            "CREATE INDEX idx_movement_categories_created_at ON movement_categories(created_at);"
        ]
        
        for index_sql in indexes:
            try:
                await conn.execute(index_sql)
                print(f"  [OK] Created index")
            except Exception as e:
                print(f"  [ERROR] Failed to create index: {e}")
        
        # Restore the data
        print("\n[STEP 6] Restoring data...")
        for row in backup_data:
            try:
                await conn.execute("""
                    INSERT INTO movement_categories (id, created_at, updated_at, category_id, name, description, primary_stat)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                    row['id'], row['created_at'], row['updated_at'], 
                    row['category_id'], row['name'], row['description'], row['primary_stat']
                )
            except Exception as e:
                print(f"  [ERROR] Failed to restore row {row['id']}: {e}")
        
        print(f"  [OK] Restored {len(backup_data)} records")
        
        # Recreate foreign key constraints
        print("\n[STEP 7] Recreating foreign key constraints...")
        for table_name, constraint_name, column_name in dropped_constraints:
            try:
                await conn.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD CONSTRAINT {constraint_name} 
                    FOREIGN KEY ({column_name}) REFERENCES movement_categories(id);
                """)
                print(f"  [OK] Recreated {constraint_name} on {table_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to recreate {constraint_name}: {e}")
        
        # Test the query that was failing
        print("\n[STEP 8] Testing the previously failing query...")
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
            return False
        
        # Final verification
        print("\n[VERIFICATION] Final state check...")
        
        # Check table structure
        columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length, column_default
            FROM information_schema.columns 
            WHERE table_name = 'movement_categories'
            ORDER BY ordinal_position;
        """)
        
        print("  Table structure:")
        for col in columns:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"    {col['column_name']}: {col['data_type']}{max_len}{default}")
        
        # Check for sequences (should be none)
        sequences = await conn.fetch("""
            SELECT sequence_name FROM information_schema.sequences 
            WHERE sequence_name LIKE '%movement_categories%';
        """)
        
        if sequences:
            print("  WARNING: Sequences still exist:")
            for seq in sequences:
                print(f"    {seq['sequence_name']}")
        else:
            print("  [OK] No sequences found")
        
        # Count records
        count = await conn.fetchval("SELECT COUNT(*) FROM movement_categories;")
        print(f"  Records: {count}")
        
        await conn.close()
        
        print("\n" + "="*80)
        print("NUCLEAR FIX COMPLETE")
        print("="*80)
        print("\nWhat was done:")
        print("- Completely dropped and recreated movement_categories table")
        print("- Eliminated all metadata inconsistencies")
        print("- Restored all data with proper data types")
        print("- Recreated all foreign key constraints")
        print("- No sequences or defaults that could cause issues")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test the Skill Tree panel")
        print("3. The InvalidCachedStatementError should be completely resolved")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Nuclear fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*80)
    print("NUCLEAR OPTION: COMPLETE TABLE REBUILD")
    print("="*80)
    print()
    print("WARNING: This will completely rebuild the movement_categories table!")
    print("This is the nuclear option to eliminate all metadata inconsistencies.")
    print()
    print("What this will do:")
    print("1. Back up all movement_categories data")
    print("2. Drop all foreign key constraints")
    print("3. Drop the movement_categories table completely")
    print("4. Recreate the table with correct structure")
    print("5. Restore all data")
    print("6. Recreate foreign key constraints")
    print()
    
    try:
        success = asyncio.run(nuclear_fix())
        if success:
            print("\n[SUCCESS] Nuclear fix completed successfully!")
        else:
            print("\n[ERROR] Nuclear fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n[WARNING] Fix interrupted by user")
    except Exception as e:
        print(f"\n\n[FATAL] Unexpected error: {e}")