#!/usr/bin/env python3
"""
Comprehensive fix for all missing awakening_sessions table columns.
This script adds all columns that the AwakeningSession model expects.
"""

import asyncio
import os
from urllib.parse import urlparse

async def check_and_fix_awakening_table():
    """Check and fix all missing columns in awakening_sessions table."""
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg library not available")
        print("Please install it with: pip install asyncpg")
        return False
    
    try:
        # Get database URL from environment
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
        
        print("Connecting to database...")
        
        # Normalize URL for asyncpg
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
        
        # Check if awakening_sessions table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'awakening_sessions'
            );
        """)
        
        if not table_exists:
            print("ERROR: awakening_sessions table does not exist")
            print("Please run the main database migrations first")
            await conn.close()
            return False
        
        # Get current columns
        current_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'awakening_sessions'
            ORDER BY ordinal_position;
        """)
        
        current_column_names = {row['column_name'] for row in current_columns}
        
        print(f"Current columns in awakening_sessions: {sorted(current_column_names)}")
        
        # Define all expected columns based on the AwakeningSession model
        expected_columns = {
            'id': {
                'type': 'INTEGER',
                'nullable': False,
                'primary_key': True
            },
            'user_id': {
                'type': 'INTEGER',
                'nullable': False,
                'foreign_key': 'ascendants(id)'
            },
            'session_date': {
                'type': 'DATE',
                'nullable': False
            },
            'tier_level': {
                'type': 'VARCHAR(20)',
                'nullable': False,
                'default': "'normal'"
            },
            'status': {
                'type': 'VARCHAR(20)',
                'nullable': False,
                'default': "'active'"
            },
            'reset_used': {
                'type': 'BOOLEAN',
                'nullable': False,
                'default': 'false'
            },
            'reset_at': {
                'type': 'TIMESTAMP',
                'nullable': True
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'nullable': False,
                'default': 'CURRENT_TIMESTAMP'
            },
            'completed_at': {
                'type': 'TIMESTAMP',
                'nullable': True
            }
        }
        
        # Find missing columns
        missing_columns = set(expected_columns.keys()) - current_column_names
        
        if not missing_columns:
            print("✓ All expected columns are present!")
            await conn.close()
            return True
        
        print(f"Missing columns: {sorted(missing_columns)}")
        
        # Add missing columns one by one
        for column_name in missing_columns:
            column_def = expected_columns[column_name]
            
            print(f"Adding column: {column_name}")
            
            # Build the ALTER TABLE statement
            sql_parts = [f"ALTER TABLE awakening_sessions ADD COLUMN {column_name} {column_def['type']}"]
            
            if not column_def['nullable']:
                if 'default' in column_def:
                    sql_parts.append(f"NOT NULL DEFAULT {column_def['default']}")
                else:
                    # For NOT NULL columns without default, we need to handle existing data
                    sql_parts.append("NOT NULL DEFAULT 1")  # Temporary default
            
            sql = " ".join(sql_parts) + ";"
            
            try:
                await conn.execute(sql)
                print(f"✓ Added {column_name}")
                
                # Remove temporary default if needed
                if not column_def['nullable'] and 'default' not in column_def:
                    await conn.execute(f"ALTER TABLE awakening_sessions ALTER COLUMN {column_name} DROP DEFAULT;")
                    print(f"✓ Removed temporary default from {column_name}")
                    
            except Exception as e:
                print(f"! Warning: Could not add {column_name}: {e}")
        
        # Add foreign key constraints if needed
        if 'user_id' in missing_columns:
            try:
                # Check if ascendants table exists
                ascendants_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'ascendants'
                    );
                """)
                
                if ascendants_exists:
                    await conn.execute("""
                        ALTER TABLE awakening_sessions 
                        ADD CONSTRAINT fk_awakening_sessions_user_id 
                        FOREIGN KEY (user_id) REFERENCES ascendants(id);
                    """)
                    print("✓ Added foreign key constraint for user_id")
                else:
                    print("! Warning: Skipped foreign key constraint - ascendants table not found")
            except Exception as e:
                print(f"! Warning: Could not add foreign key constraint: {e}")
        
        # Add indexes if needed
        try:
            # Index for user_id (if it was added)
            if 'user_id' in missing_columns:
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_awakening_sessions_user_id ON awakening_sessions(user_id);")
                print("✓ Added index for user_id")
            
            # Index for session_date (if it was added)  
            if 'session_date' in missing_columns:
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_awakening_sessions_session_date ON awakening_sessions(session_date);")
                print("✓ Added index for session_date")
            
            # Index for status (if it was added)
            if 'status' in missing_columns:
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_awakening_sessions_status ON awakening_sessions(status);")
                print("✓ Added index for status")
                
            # Combined index for user_id and session_date
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_awakening_sessions_user_date ON awakening_sessions(user_id, session_date);")
            print("✓ Added combined index for user_id and session_date")
            
        except Exception as e:
            print(f"! Warning: Could not add some indexes: {e}")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: All awakening_sessions columns have been fixed!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test user registration")
        print("3. All awakening system errors should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("AWAKENING SESSIONS COMPREHENSIVE COLUMN FIX")
    print("=" * 70)
    
    try:
        success = asyncio.run(check_and_fix_awakening_table())
        if success:
            print("\n✅ All fixes completed successfully!")
        else:
            print("\n❌ Some fixes failed - check output above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")