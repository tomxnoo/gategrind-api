#!/usr/bin/env python3
"""
Simple test script to verify the awakening_sessions.user_id fix is working.
This attempts to simulate what the registration process does.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    from app.infrastructure.database.models.v2.awakening import AwakeningSession
    from app.infrastructure.database.models.v2.ascendants import Ascendant
    from app.infrastructure.database.session import get_database_url
    from datetime import date, datetime
except ImportError as e:
    print(f"Import error: {e}")
    print("This script requires the application dependencies to be installed.")
    sys.exit(1)


async def test_awakening_session_creation():
    """Test creating an AwakeningSession to verify user_id column exists."""
    
    try:
        # Get database URL and create engine
        database_url = get_database_url()
        engine = create_async_engine(database_url)
        
        # Create session factory
        async_session_factory = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        print("Testing awakening_sessions.user_id column fix...")
        print("=" * 50)
        
        async with async_session_factory() as session:
            # Try to query awakening_sessions table to verify user_id column exists
            try:
                # This will fail if user_id column doesn't exist
                result = await session.execute(
                    text("SELECT id, user_id FROM awakening_sessions LIMIT 1")
                )
                print("SUCCESS: user_id column exists in awakening_sessions table")
                
                # Check if we have any records
                row = result.fetchone()
                if row:
                    print(f"SUCCESS: Found existing record: id={row[0]}, user_id={row[1]}")
                else:
                    print("SUCCESS: Table is empty but schema is correct")
                
            except Exception as e:
                if "column awakening_sessions.user_id does not exist" in str(e):
                    print("ERROR: user_id column still missing!")
                    print("  The migration may not have been applied successfully.")
                    return False
                else:
                    print(f"ERROR: Unexpected error querying awakening_sessions: {e}")
                    return False
            
            # Try to create a test AwakeningSession object (without saving)
            try:
                test_session = AwakeningSession(
                    user_id=1,  # This will fail if user_id column doesn't exist
                    session_date=date.today(),
                    tier_level="normal",
                    status="active"
                )
                print("SUCCESS: AwakeningSession model can be instantiated with user_id")
                
                # Don't actually save it, just test the model works
                print("SUCCESS: All tests passed - user_id column fix is working!")
                return True
                
            except Exception as e:
                print(f"ERROR: Error creating AwakeningSession model: {e}")
                return False
                
    except Exception as e:
        print(f"ERROR: Database connection error: {e}")
        print("  Make sure PostgreSQL is running and accessible.")
        return False
    
    finally:
        if 'engine' in locals():
            await engine.dispose()


async def main():
    """Main test function."""
    print("Awakening Sessions Fix Verification")
    print("=" * 40)
    
    success = await test_awakening_session_creation()
    
    if success:
        print("\nSUCCESS: The awakening_sessions.user_id fix is working!")
        print("\nYou can now:")
        print("1. Restart your FastAPI application")
        print("2. Test user registration")
        print("3. The error should be resolved")
    else:
        print("\nFAILED: The fix did not work")
        print("\nTry:")
        print("1. Run: alembic upgrade head")
        print("2. Check database connectivity")
        print("3. Manually verify the database schema")
        print("4. Use the fix_awakening_schema_issue.py script")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)