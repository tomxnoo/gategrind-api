#!/usr/bin/env python3
"""
Production-safe deployment script for awakening_sessions.user_id column fix.

This script can be run in any environment and will:
1. Try to apply the Alembic migration first
2. Fall back to manual SQL execution if needed
3. Verify the fix was applied successfully
4. Provide clear feedback on success/failure
"""

import asyncio
import os
import sys
import subprocess
from urllib.parse import urlparse


def run_alembic_migration():
    """Try to apply the migration using Alembic."""
    print("Attempting to apply migration using Alembic...")
    
    try:
        # Try to run the specific migration
        result = subprocess.run(
            ["alembic", "upgrade", "awaken_user_id_fix"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("SUCCESS: Alembic migration applied successfully")
            return True
        else:
            print(f"WARNING: Alembic migration failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("WARNING: Alembic migration timed out")
        return False
    except FileNotFoundError:
        print("WARNING: Alembic not found in PATH")
        return False
    except Exception as e:
        print(f"WARNING: Alembic migration error: {e}")
        return False


async def apply_manual_fix():
    """Apply the fix using direct SQL execution."""
    print("Applying manual SQL fix...")
    
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
            # Try some common variations
            db_url = os.getenv('DB_URL') or os.getenv('POSTGRES_URL')
            
        if not db_url:
            # Use default from config
            db_url = "postgresql://user:password@localhost/ros_db"
            print(f"Using default database URL: {db_url}")
        
        # Normalize URL for asyncpg
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        
        print(f"Connecting to database: {parsed.hostname}:{parsed.port or 5432}")
        
        conn = await asyncpg.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'user',
            password=parsed.password or 'password',
            database=parsed.path[1:] if parsed.path else 'ros_db'
        )
        
        # Apply the fix with comprehensive error handling
        await conn.execute("""
            DO $$ 
            DECLARE
                column_exists BOOLEAN;
                table_exists BOOLEAN;
            BEGIN
                -- Check if table exists
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'awakening_sessions'
                ) INTO table_exists;
                
                IF NOT table_exists THEN
                    RAISE EXCEPTION 'awakening_sessions table does not exist';
                END IF;
                
                -- Check if column already exists
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'awakening_sessions' 
                    AND column_name = 'user_id'
                ) INTO column_exists;
                
                IF column_exists THEN
                    RAISE NOTICE 'user_id column already exists - no action needed';
                    RETURN;
                END IF;
                
                -- Add the column
                ALTER TABLE awakening_sessions 
                ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
                
                -- Add foreign key constraint if ascendants table exists
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ascendants') THEN
                    ALTER TABLE awakening_sessions 
                    ADD CONSTRAINT fk_awakening_sessions_user_id 
                    FOREIGN KEY (user_id) REFERENCES ascendants(id);
                END IF;
                
                -- Add index for performance
                CREATE INDEX IF NOT EXISTS idx_awakening_sessions_user_id 
                ON awakening_sessions(user_id);
                
                -- Remove the default value
                ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
                
                RAISE NOTICE 'Successfully added user_id column to awakening_sessions';
                
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE EXCEPTION 'Fix failed: %', SQLERRM;
            END $$;
        """)
        
        await conn.close()
        print("SUCCESS: Manual SQL fix applied successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Manual fix failed: {e}")
        return False


async def verify_fix():
    """Verify that the fix was applied correctly."""
    print("Verifying fix...")
    
    try:
        import asyncpg
        
        # Get database connection info
        db_url = os.getenv('DATABASE_URL', "postgresql://user:password@localhost/ros_db")
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        parsed = urlparse(db_url)
        
        conn = await asyncpg.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'user',
            password=parsed.password or 'password',
            database=parsed.path[1:] if parsed.path else 'ros_db'
        )
        
        # Check if column exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            );
        """)
        
        if column_exists:
            print("SUCCESS: user_id column exists in awakening_sessions table")
            
            # Check constraints and indexes
            constraints = await conn.fetch("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'awakening_sessions' 
                AND constraint_name LIKE '%user_id%';
            """)
            
            indexes = await conn.fetch("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'awakening_sessions' 
                AND indexname LIKE '%user_id%';
            """)
            
            print(f"Foreign key constraints: {len(constraints)}")
            print(f"Indexes: {len(indexes)}")
            
            await conn.close()
            return True
        else:
            print("ERROR: user_id column still does not exist")
            await conn.close()
            return False
            
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
        return False


async def main():
    """Main deployment function."""
    print("=" * 60)
    print("AWAKENING SESSIONS DATABASE FIX DEPLOYMENT")
    print("=" * 60)
    print("")
    
    success = False
    
    # Step 1: Try Alembic migration
    if run_alembic_migration():
        success = True
    else:
        # Step 2: Fall back to manual fix
        print("")
        print("Falling back to manual SQL approach...")
        success = await apply_manual_fix()
    
    print("")
    
    # Step 3: Verify the fix
    if success:
        if await verify_fix():
            print("")
            print("=" * 60)
            print("SUCCESS: Awakening sessions fix deployed successfully!")
            print("=" * 60)
            print("")
            print("Next steps:")
            print("1. Restart your application")
            print("2. Test user registration")
            print("3. The 'column awakening_sessions.user_id does not exist' error should be resolved")
            print("")
            return True
        else:
            success = False
    
    if not success:
        print("")
        print("=" * 60)
        print("FAILED: Unable to apply the fix")
        print("=" * 60)
        print("")
        print("Manual steps:")
        print("1. Connect to your PostgreSQL database")
        print("2. Run the SQL commands from PRODUCTION_DATABASE_FIX.md")
        print("3. Restart your application")
        print("")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)