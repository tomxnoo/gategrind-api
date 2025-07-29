#!/usr/bin/env python3
"""
Simple, production-safe fix for awakening_sessions.user_id column.
"""

import asyncio
import os
from urllib.parse import urlparse

async def apply_fix():
    """Apply the awakening_sessions.user_id column fix."""
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
        
        print(f"Connecting to database...")
        
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
        
        # Step 1: Check if column exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'awakening_sessions' 
                AND column_name = 'user_id'
            );
        """)
        
        if column_exists:
            print("SUCCESS: user_id column already exists - no action needed")
            await conn.close()
            return True
        
        print("Adding user_id column to awakening_sessions table...")
        
        # Step 2: Add the column with default value
        await conn.execute("""
            ALTER TABLE awakening_sessions 
            ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
        """)
        print("✓ Column added")
        
        # Step 3: Add foreign key constraint (if ascendants table exists)
        try:
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
                print("✓ Foreign key constraint added")
            else:
                print("! Skipped foreign key constraint - ascendants table not found")
        except Exception as e:
            print(f"! Warning: Could not add foreign key constraint: {e}")
        
        # Step 4: Add index
        try:
            await conn.execute("""
                CREATE INDEX idx_awakening_sessions_user_id 
                ON awakening_sessions(user_id);
            """)
            print("✓ Index added")
        except Exception as e:
            print(f"! Warning: Could not add index: {e}")
        
        # Step 5: Remove default value
        await conn.execute("""
            ALTER TABLE awakening_sessions 
            ALTER COLUMN user_id DROP DEFAULT;
        """)
        print("✓ Default value removed")
        
        await conn.close()
        
        print("\n🎉 SUCCESS: awakening_sessions.user_id column fix completed!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. Test user registration")
        print("3. The error should be resolved")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Fix failed: {e}")
        print("\nManual fix instructions:")
        print("1. Connect to your PostgreSQL database")
        print("2. Run this SQL:")
        print("""
        ALTER TABLE awakening_sessions ADD COLUMN user_id INTEGER NOT NULL DEFAULT 1;
        ALTER TABLE awakening_sessions ADD CONSTRAINT fk_awakening_sessions_user_id 
            FOREIGN KEY (user_id) REFERENCES ascendants(id);
        CREATE INDEX idx_awakening_sessions_user_id ON awakening_sessions(user_id);
        ALTER TABLE awakening_sessions ALTER COLUMN user_id DROP DEFAULT;
        """)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AWAKENING SESSIONS USER_ID COLUMN FIX")
    print("=" * 60)
    
    try:
        success = asyncio.run(apply_fix())
        if success:
            print("\n✅ Fix completed successfully!")
        else:
            print("\n❌ Fix failed - see instructions above")
    except KeyboardInterrupt:
        print("\n\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")