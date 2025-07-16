#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""

import httpx
import json
import asyncio

BASE_URL = "http://localhost:8000"

async def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Get Discord OAuth URL
        print("\n1. Testing Discord OAuth URL...")
        try:
            response = await client.get(f"{BASE_URL}/api/auth/discord/url")
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 2: Development login
        print("\n2. Testing development login...")
        try:
            login_data = {
                "discord_id": "123456789",
                "username": "test_user"
            }
            response = await client.post(
                f"{BASE_URL}/api/auth/dev/login",
                json=login_data
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Store token for further tests
            if response.status_code == 200:
                token = data["access_token"]
                print(f"✅ Got token: {token[:50]}...")
                
                # Test 3: Get current user info
                print("\n3. Testing get current user info...")
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{BASE_URL}/api/auth/me",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Test 4: Test protected endpoint with token
                print("\n4. Testing protected endpoint (user profile) with token...")
                response = await client.get(
                    f"{BASE_URL}/api/users/me",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Test 5: Logout
                print("\n5. Testing logout...")
                response = await client.post(
                    f"{BASE_URL}/api/auth/logout",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test 6: Test protected endpoint without token
        print("\n6. Testing protected endpoint without token...")
        try:
            response = await client.get(f"{BASE_URL}/api/users/me")
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_endpoints())