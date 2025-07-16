"""
Simple test script to verify FastAPI integration is working
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    """Test the FastAPI endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🧪 Testing FastAPI Integration...")
        print("=" * 50)
        
        # Test root endpoint
        try:
            response = await client.get(f"{base_url}/")
            print(f"✅ Root endpoint: {response.status_code}")
            print(f"   Response: {response.json()['message']}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test health check
        try:
            response = await client.get(f"{base_url}/api/health")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Status: {response.json()['status']}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        # Test detailed health check
        try:
            response = await client.get(f"{base_url}/api/health/detailed")
            print(f"✅ Detailed health: {response.status_code}")
            data = response.json()
            print(f"   Database: {data['data']['services']['database']}")
            print(f"   Redis: {data['data']['services']['redis']}")
        except Exception as e:
            print(f"❌ Detailed health failed: {e}")
        
        # Test user profile (should work with dev auth)
        try:
            response = await client.get(f"{base_url}/api/users/me")
            print(f"✅ User profile: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   User: {data['username']} (Level {data['level']})")
        except Exception as e:
            print(f"❌ User profile failed: {e}")
        
        # Test daily quests
        try:
            response = await client.get(f"{base_url}/api/quests/daily")
            print(f"✅ Daily quests: {response.status_code}")
            if response.status_code == 200:
                quests = response.json()
                print(f"   Found {len(quests)} daily quests")
        except Exception as e:
            print(f"❌ Daily quests failed: {e}")
        
        print("=" * 50)
        print("🎯 FastAPI Integration Test Complete!")
        print(f"📚 API Documentation: {base_url}/docs")
        print(f"📖 ReDoc Documentation: {base_url}/redoc")

if __name__ == "__main__":
    asyncio.run(test_api())