"""
Enhanced test script to test awakening service logic directly
"""
import os
import sys
import asyncio
import asyncpg
from datetime import date

# Add project root to path for imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def test_awakening_service():
    """Test the awakening service directly to identify runtime issues"""
    print("🧪 Testing Awakening Service Logic")
    print("=" * 50)
    
    try:
        # Import the awakening service
        from features.awakening.logic.awakening_service import AwakeningService
        from api.models.awakening import ReadinessLevel
        print("✅ Successfully imported AwakeningService")
        
        # Test database connection
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
            
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection established")
        
        # Initialize service
        service = AwakeningService(bot=None)
        print("✅ AwakeningService initialized")
        
        # Test user ID (using 1 for testing)
        test_user_id = 1
        
        # Test get_today_awakening
        print(f"\n🔍 Testing get_today_awakening for user {test_user_id}...")
        today_awakening = await service.get_today_awakening(test_user_id, conn)
        if today_awakening:
            print(f"✅ Found existing awakening: {today_awakening}")
        else:
            print("ℹ️  No awakening found for today (this is normal)")
        
        # Test cleanup_orphaned_sessions
        print(f"\n🧹 Testing cleanup_orphaned_sessions for user {test_user_id}...")
        cleaned_count = await service.cleanup_orphaned_sessions(test_user_id, conn)
        print(f"✅ Cleaned up {cleaned_count} orphaned sessions")
        
        # Test create_awakening_session (only if no existing awakening)
        if not today_awakening:
            print(f"\n🚀 Testing create_awakening_session for user {test_user_id}...")
            try:
                result = await service.create_awakening_session(
                    test_user_id, 
                    ReadinessLevel.STANDARD, 
                    conn
                )
                print(f"✅ Successfully created awakening session: {result}")
            except Exception as e:
                print(f"❌ Error creating awakening session: {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
        else:
            print("ℹ️  Skipping awakening creation (already exists for today)")
        
        await conn.close()
        print("\n✅ All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_config_imports():
    """Test if configuration imports are working"""
    print("\n🔧 Testing Configuration Imports")
    print("=" * 30)
    
    try:
        from core.config import QUEST_THEMES, MOVEMENT_DATA
        print(f"✅ QUEST_THEMES imported: {len(QUEST_THEMES) if QUEST_THEMES else 0} themes")
        print(f"✅ MOVEMENT_DATA imported: {len(MOVEMENT_DATA) if MOVEMENT_DATA else 0} movements")
        
        if not QUEST_THEMES:
            print("⚠️  QUEST_THEMES is empty - this might cause issues")
        if not MOVEMENT_DATA:
            print("⚠️  MOVEMENT_DATA is empty - this might cause issues")
            
        return True
    except Exception as e:
        print(f"❌ Config import error: {e}")
        return False

async def test_user_data_functions():
    """Test user data functions"""
    print("\n👤 Testing User Data Functions")
    print("=" * 30)
    
    try:
        from core.database.db import get_unified_user_data
        print("✅ get_unified_user_data imported successfully")
        
        # Test with database connection
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            conn = await asyncpg.connect(database_url)
            user_data = await get_unified_user_data(conn, 1, None)
            print(f"✅ User data retrieved: {list(user_data.keys()) if user_data else 'None'}")
            await conn.close()
        
        return True
    except Exception as e:
        print(f"❌ User data function error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🔍 Enhanced Awakening Service Diagnostics")
    print("=" * 60)
    
    # Test configuration imports first
    config_ok = await test_config_imports()
    
    # Test user data functions
    user_data_ok = await test_user_data_functions()
    
    # Test awakening service if other tests pass
    if config_ok and user_data_ok:
        service_ok = await test_awakening_service()
        
        if service_ok:
            print("\n🎉 All tests passed! The awakening service should work correctly.")
        else:
            print("\n❌ Awakening service test failed. Check the error details above.")
    else:
        print("\n❌ Configuration or user data tests failed. Fix these issues first.")
    
    print("\n🚀 If tests pass, try the API server:")
    print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(main())