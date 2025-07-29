#!/usr/bin/env python3
"""
Fix the movements table structure to add the missing category_id column.
"""

import asyncio
import os
from urllib.parse import urlparse

async def fix_movements_table():
    """Fix the movements table structure."""
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
        
        # Check movements table structure
        print("\n=== MOVEMENTS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'movements'
            ORDER BY ordinal_position;
        """)
        
        existing_columns = []
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
            existing_columns.append(col['column_name'])
        
        # Check if category_id column exists
        if 'category_id' in existing_columns:
            print("\n✓ category_id column already exists in movements table")
        else:
            print("\n🔧 Adding category_id column to movements table...")
            
            try:
                # Add category_id column with foreign key reference
                await conn.execute("""
                    ALTER TABLE movements 
                    ADD COLUMN category_id BIGINT REFERENCES movement_categories(id);
                """)
                print("✓ Added category_id column with foreign key reference")
                
            except Exception as e:
                print(f"❌ Failed to add category_id column: {e}")
                return False
        
        # Check if node_id column exists (might be needed for the V2 schema)
        if 'node_id' not in existing_columns:
            print("\n🔧 Adding node_id column to movements table...")
            
            try:
                # Add node_id column (nullable for now since we don't have skill tree nodes yet)
                await conn.execute("""
                    ALTER TABLE movements 
                    ADD COLUMN node_id BIGINT;
                """)
                print("✓ Added node_id column (nullable)")
                
            except Exception as e:
                print(f"! Warning: Could not add node_id column: {e}")
        
        # Check other expected columns
        expected_columns = [
            ('name', 'VARCHAR(255)', 'NOT NULL'),
            ('description', 'TEXT', 'NULL'),
            ('xp_per_rep', 'DECIMAL(5,2)', 'NULL'),
            ('stat_reward_type', 'VARCHAR(50)', 'NULL'),
            ('created_at', 'TIMESTAMP WITH TIME ZONE', 'NOT NULL'),
            ('updated_at', 'TIMESTAMP WITH TIME ZONE', 'NOT NULL')
        ]
        
        for col_name, col_type, nullable in expected_columns:
            if col_name not in existing_columns:
                print(f"\n🔧 Adding missing column {col_name}...")
                
                try:
                    if nullable == 'NOT NULL':
                        # Add with default first, then remove default
                        if col_name in ['created_at', 'updated_at']:
                            await conn.execute(f"""
                                ALTER TABLE movements 
                                ADD COLUMN {col_name} {col_type} DEFAULT CURRENT_TIMESTAMP;
                            """)
                            await conn.execute(f"""
                                ALTER TABLE movements 
                                ALTER COLUMN {col_name} DROP DEFAULT;
                            """)
                        else:
                            default_val = "'default'" if 'VARCHAR' in col_type else "0"
                            await conn.execute(f"""
                                ALTER TABLE movements 
                                ADD COLUMN {col_name} {col_type} NOT NULL DEFAULT {default_val};
                            """)
                            await conn.execute(f"""
                                ALTER TABLE movements 
                                ALTER COLUMN {col_name} DROP DEFAULT;
                            """)
                    else:
                        await conn.execute(f"""
                            ALTER TABLE movements 
                            ADD COLUMN {col_name} {col_type};
                        """)
                    
                    print(f"✓ Added {col_name} column")
                    
                except Exception as e:
                    print(f"! Warning: Could not add {col_name} column: {e}")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: Movements table structure fixed!")
        print("\nNext steps:")
        print("1. Run the skill tree seeding script again: python fix.py")
        print("2. Test the Skill Tree panel")
        print("3. Movements should now be properly linked to categories")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("MOVEMENTS TABLE STRUCTURE FIX")
    print("=" * 70)
    
    try:
        success = asyncio.run(fix_movements_table())
        if success:
            print("\n✅ Movements table fix completed successfully!")
        else:
            print("\n❌ Movements table fix failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")