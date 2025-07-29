#!/usr/bin/env python3
"""
Simple script to test the available_points field in /api/v2/profiles/me
Works on Replit with DEV_MODE=false (production environment)
"""

import requests
import json
import sys

# Configuration - Update these for your Replit environment
BASE_URL = "http://localhost:5000"  # Change to your Replit URL if different
DISCORD_USER_ID = "123456789"  # Replace with a real Discord user ID for testing

def get_jwt_token():
    """Get a JWT token using the V2 authentication endpoint"""
    try:
        # Use V2 auth login endpoint
        response = requests.post(
            f"{BASE_URL}/api/v2/auth/login",
            json={
                "discord_id": DISCORD_USER_ID,
                "username": "TestUser"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        
        print(f"❌ V2 login failed: {response.status_code} - {response.text}")
        
        # If login fails, try registration first
        print("🔄 Attempting user registration...")
        reg_response = requests.post(
            f"{BASE_URL}/api/v2/auth/register",
            json={
                "discord_id": DISCORD_USER_ID,
                "username": "TestUser",
                "display_name": "Test User"
            },
            timeout=10
        )
        
        if reg_response.status_code == 200:
            reg_data = reg_response.json()
            print("✅ User registered successfully")
            return reg_data.get("access_token")
        
        print(f"❌ Registration failed: {reg_response.status_code} - {reg_response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error getting JWT token: {e}")
        return None

def test_profiles_endpoint(token):
    """Test the /api/v2/profiles/me endpoint"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v2/profiles/me",
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Profile data:")
            print(json.dumps(data, indent=2))
            
            # Check for available_points specifically
            if "available_points" in data:
                print(f"\n🎯 AVAILABLE POINTS: {data['available_points']}")
                print("✅ available_points field is working!")
            else:
                print("\n❌ available_points field is missing from response")
                print("Available fields:", list(data.keys()))
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing endpoint: {e}")

def main():
    print("🚀 Testing available_points in /api/v2/profiles/me")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 Discord User ID: {DISCORD_USER_ID}")
    print("-" * 50)
    
    # Step 1: Get JWT token
    print("1️⃣ Getting JWT token...")
    token = get_jwt_token()
    
    if not token:
        print("❌ Failed to get JWT token. Make sure:")
        print("   - Your server is running on the correct port")
        print("   - The auth endpoints are working")
        print("   - Update DISCORD_USER_ID in this script")
        sys.exit(1)
    
    print(f"✅ Got token: {token[:20]}...")
    
    # Step 2: Test profiles endpoint
    print("\n2️⃣ Testing /api/v2/profiles/me...")
    test_profiles_endpoint(token)
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    main()