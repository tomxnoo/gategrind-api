"""
Script to fix missing user_json_data table
"""
import os
import sys
import asyncio
import asyncpg

# Add project root to path for imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def fix_database_schema():
    """Create missing user_json_data table and populate it"""
    print("🔧 Fixing Database Schema")
    print("=" * 40)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
            
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection established")
        
        # Check if user_json_data table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_json_data'
            )
        """)
        
        if not table_exists:
            print("🔧 Creating user_json_data table...")
            
            # Create the table
            await conn.execute("""
                CREATE TABLE user_json_data (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                    data JSONB NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("✅ user_json_data table created!")
            
            # Create index for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_json_data_user_id ON user_json_data(user_id);
            """)
            
            print("✅ Index created for user_json_data table")
            
        else:
            print("✅ user_json_data table already exists")
        
        # Get all users and ensure they have user_json_data entries
        users = await conn.fetch("SELECT user_id, username FROM users")
        print(f"📋 Found {len(users)} users")
        
        for user in users:
            user_id = user['user_id']
            
            # Check if user has json data entry
            has_entry = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM user_json_data WHERE user_id = $1)",
                user_id
            )
            
            if not has_entry:
                # Create entry with empty JSON
                await conn.execute("""
                    INSERT INTO user_json_data (user_id, data)
                    VALUES ($1, $2)
                """, user_id, '{}')
                
                print(f"   ✅ Created user_json_data entry for user {user_id} ({user['username']})")
            else:
                print(f"   ✅ User {user_id} ({user['username']}) already has user_json_data entry")
        
        await conn.close()
        print("\n🎉 Database schema fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_awakening_service():
    """Test the awakening service after fixing the schema"""
    print("\n🧪 Testing Awakening Service")
    print("=" * 40)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(database_url)
        
        # Get the first available user
        user = await conn.fetchrow("SELECT user_id, username FROM users ORDER BY user_id LIMIT 1")
        if not user:
            print("❌ No users found")
            return False
            
        test_user_id = user['user_id']
        print(f"🎯 Testing with user: {user['username']} (ID: {test_user_id})")
        
        # Import and test awakening service
        from features.awakening.logic.awakening_service import AwakeningService
        from api.models.awakening import ReadinessLevel
        
        service = AwakeningService(bot=None)
        
        # Test create_awakening_session
        print(f"\n🚀 Creating awakening session...")
        try:
            result = await service.create_awakening_session(
                test_user_id, 
                ReadinessLevel.STANDARD, 
                conn
            )
            print(f"✅ Awakening session created successfully!")
            print(f"   - Awakening ID: {result['awakening_id']}")
            print(f"   - Quest count: {result['quest_count']}")
            print(f"   - Readiness level: {result['readiness_level']}")
            print(f"   - Generated {len(result['quests'])} quests")
            
        except Exception as e:
            print(f"❌ Error creating awakening session: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🔧 Database Schema Fix for user_json_data Table")
    print("=" * 60)
    
    # Fix database schema
    schema_fixed = await fix_database_schema()
    
    if schema_fixed:
        # Test awakening service
        test_passed = await test_awakening_service()
        
        if test_passed:
            print("\n🎉 Everything is working!")
            print("\n🚀 You can now start the API server:")
            print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
            print("\n🌟 Try the awakening endpoint: POST /api/awakening/awaken")
        else:
            print("\n⚠️  Schema fixed but awakening test failed. Check the errors above.")
    else:
        print("\n❌ Failed to fix database schema. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())