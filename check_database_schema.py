"""
Script to check database schema and create missing user_json_data table
"""
import os
import sys
import asyncio
import asyncpg

# Add project root to path for imports
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def check_database_schema():
    """Check database schema and create missing tables"""
    print("🔍 Checking Database Schema")
    print("=" * 40)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found")
            return False
            
        conn = await asyncpg.connect(database_url)
        print("✅ Database connection established")
        
        # Check what tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📋 Found {len(tables)} tables:")
        table_names = []
        for table in tables:
            table_name = table['table_name']
            table_names.append(table_name)
            print(f"   - {table_name}")
        
        # Check if user_json_data table exists
        if 'user_json_data' not in table_names:
            print("\n⚠️  user_json_data table is missing!")
            print("🔧 Creating user_json_data table...")
            
            await conn.execute("""
                CREATE TABLE user_json_data (
                    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                    data JSONB NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            print("✅ user_json_data table created successfully!")
            
            # Create an index for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_json_data_user_id ON user_json_data(user_id);
            """)
            
            print("✅ Index created for user_json_data table")
            
        else:
            print("✅ user_json_data table exists")
            
            # Check the structure
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'user_json_data'
                ORDER BY ordinal_position
            """)
            
            print("📋 user_json_data table structure:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Check if we have any users without user_json_data entries
        users_without_json = await conn.fetch("""
            SELECT u.user_id, u.username 
            FROM users u 
            LEFT JOIN user_json_data ujd ON u.user_id = ujd.user_id 
            WHERE ujd.user_id IS NULL
        """)
        
        if users_without_json:
            print(f"\n⚠️  Found {len(users_without_json)} users without user_json_data entries")
            print("🔧 Creating user_json_data entries for existing users...")
            
            for user in users_without_json:
                await conn.execute("""
                    INSERT INTO user_json_data (user_id, data)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id) DO NOTHING
                """, user['user_id'], '{}')
                
                print(f"   ✅ Created entry for user {user['user_id']} ({user['username']})")
        else:
            print("✅ All users have user_json_data entries")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_awakening_after_fix():
    """Test awakening service after fixing the schema"""
    print("\n🧪 Testing Awakening Service After Schema Fix")
    print("=" * 50)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        conn = await asyncpg.connect(database_url)
        
        # Get the first available user
        user = await conn.fetchrow("SELECT user_id FROM users ORDER BY user_id LIMIT 1")
        if not user:
            print("❌ No users found")
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
            print(f"✅ Successfully created awakening session!")
            print(f"   - Awakening ID: {result['awakening_id']}")
            print(f"   - Quest count: {result['quest_count']}")
            print(f"   - Readiness level: {result['readiness_level']}")
            
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
    print("🔧 Database Schema Fix for Awakening System")
    print("=" * 50)
    
    # Check and fix database schema
    schema_ok = await check_database_schema()
    
    if schema_ok:
        # Test awakening service
        await test_awakening_after_fix()
        
        print("\n🎉 Database schema fix complete!")
        print("\n🚀 Now try the API server:")
        print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Failed to fix database schema. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())