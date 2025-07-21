"""
Simple test script to diagnose awakening API issues
"""
import os
import asyncio
import asyncpg
from datetime import date

async def test_database_connection():
    """Test if we can connect to the database and check awakening tables"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("💡 Set DEV_MODE=true in your .env file to run without database")
        return False
    
    try:
        print(f"🔌 Attempting to connect to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection successful")
        
        # Check if awakening tables exist
        tables_to_check = ['awakening_sessions', 'awakening_quests', 'readiness_history']
        
        for table in tables_to_check:
            try:
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                    table
                )
                if result > 0:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
            except Exception as e:
                print(f"❌ Error checking table '{table}': {e}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Options:")
        print("   1. Set DEV_MODE=true in your .env file to run without database")
        print("   2. Run database migrations: python scripts/simple_migrate.py")
        print("   3. Check your DATABASE_URL configuration")
        return False

async def test_dev_mode():
    """Test development mode configuration"""
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    print(f"🔧 DEV_MODE: {dev_mode}")
    
    if dev_mode:
        print("✅ Running in development mode - database not required")
        return True
    else:
        print("⚠️  Running in production mode - database required")
        return False

async def main():
    """Main test function"""
    print("🔍 Diagnosing Awakening API Issues")
    print("=" * 50)
    
    # Check development mode
    is_dev = await test_dev_mode()
    print()
    
    # Check database if not in dev mode
    if not is_dev:
        db_ok = await test_database_connection()
        print()
        
        if not db_ok:
            print("🛠️  RECOMMENDED SOLUTION:")
            print("Add this to your .env file:")
            print("DEV_MODE=true")
            print()
            print("This will allow the API to run with mock data for testing.")
    
    print("🚀 Try starting the API server with:")
    print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(main())