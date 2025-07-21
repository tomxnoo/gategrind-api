"""
Script to check existing users and create a test user if needed
"""
import os
import sys
import asyncio
import asyncpg
from datetime import datetime

# Add project root to path for imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def check_and_fix_users():
    """Check existing users and create a test user if needed"""
    print("👥 Checking Users in Database")
    print("=" * 40)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
            
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection established")
        
        # Check existing users
        users = await conn.fetch("SELECT user_id, username, created_at FROM users ORDER BY user_id")
        
        if users:
            print(f"✅ Found {len(users)} existing users:")
            for user in users:
                print(f"   - ID: {user['user_id']}, Username: {user['username']}, Created: {user['created_at']}")
        else:
            print("⚠️  No users found in database")
            
            # Create a test user
            print("\n🔧 Creating test user...")
            test_user_id = 123456789  # Discord-like user ID
            test_username = "test_user"
            
            await conn.execute("""
                INSERT INTO users (user_id, username, created_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING
            """, test_user_id, test_username, datetime.utcnow())
            
            print(f"✅ Created test user: ID={test_user_id}, Username={test_username}")
            
            # Verify creation
            new_user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", test_user_id)
            if new_user:
                print(f"✅ Test user verified: {dict(new_user)}")
            else:
                print("❌ Failed to create test user")
                return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_awakening_with_real_user():
    """Test awakening service with a real user ID"""
    print("\n🧪 Testing Awakening Service with Real User")
    print("=" * 50)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(database_url)
        
        # Get the first available user
        user = await conn.fetchrow("SELECT user_id FROM users ORDER BY user_id LIMIT 1")
        if not user:
            print("❌ No users found - run the user creation first")
            return False
            
        test_user_id = user['user_id']
        print(f"🎯 Using user ID: {test_user_id}")
        
        # Import and test awakening service
        from features.awakening.logic.awakening_service import AwakeningService
        from api.models.awakening import ReadinessLevel
        
        service = AwakeningService(bot=None)
        
        # Test create_awakening_session
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
            import traceback
            traceback.print_exc()
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🔍 User Database Check and Fix")
    print("=" * 50)
    
    # Check and fix users
    users_ok = await check_and_fix_users()
    
    if users_ok:
        # Test awakening service with real user
        await test_awakening_with_real_user()
        
        print("\n🎉 Database setup complete!")
        print("\n🚀 Now try the API server:")
        print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Failed to set up users. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())