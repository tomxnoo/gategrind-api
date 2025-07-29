#!/usr/bin/env python3
"""
Replit-specific script to test available_points field
Works with Replit's environment and URL structure
"""

import requests
import json
import sys
import os

# Replit Configuration
# Update YOUR_REPL_NAME and YOUR_USERNAME for your specific Replit
REPL_NAME = "your-repl-name"  # Replace with your actual repl name
USERNAME = "your-username"    # Replace with your Replit username

# Try multiple URL patterns that work in Replit
POSSIBLE_URLS = [
    "https://your-repl-name.your-username.repl.co",  # Standard Replit URL
    "http://localhost:5000",  # Local development
    "http://0.0.0.0:5000",    # Alternative local
]

DISCORD_USER_ID = "123456789"  # Replace with test Discord ID

def find_working_url():
    """Find which URL works for the Replit environment"""
    for url in POSSIBLE_URLS:
        try:
            response = requests.get(f"{url}/api/v2/auth/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Found working URL: {url}")
                return url
        except:
            continue
    
    print("❌ No working URL found. Please update the POSSIBLE_URLS list with your Replit URL")
    return None

def get_mock_token():
    """Create a simple mock token for testing (Replit dev mode)"""
    # In Replit dev mode, you might need a different approach
    # This creates a basic token structure for testing
    import base64
    
    mock_payload = {
        "user_id": 1,
        "discord_id": DISCORD_USER_ID,
        "username": "TestUser"
    }
    
    # Simple base64 encoding (not secure, just for testing)
    token_data = base64.b64encode(json.dumps(mock_payload).encode()).decode()
    return f"mock.{token_data}.signature"

def test_health_endpoint(base_url):
    """Test if the API is responding"""
    try:
        response = requests.get(f"{base_url}/api/v2/auth/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_with_mock_auth(base_url):
    """Test the profiles endpoint with mock authentication"""
    try:
        # Try with a simple mock token first
        mock_token = get_mock_token()
        headers = {
            "Authorization": f"Bearer {mock_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{base_url}/api/v2/profiles/me",
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Mock Auth Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success with mock auth!")
            print(json.dumps(data, indent=2))
            
            if "available_points" in data:
                print(f"\n🎯 AVAILABLE POINTS: {data['available_points']}")
            else:
                print("\n❌ available_points field missing")
        else:
            print(f"Mock auth failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Mock auth test error: {e}")

def main():
    print("🚀 Replit-specific test for available_points")
    print("=" * 50)
    
    # Step 1: Find working URL
    print("1️⃣ Finding working Replit URL...")
    base_url = find_working_url()
    
    if not base_url:
        print("\n💡 REPLIT SETUP INSTRUCTIONS:")
        print("1. Update REPL_NAME and USERNAME in this script")
        print("2. Make sure your server is running in Replit")
        print("3. Check your Replit URL format")
        print("4. Ensure your app is listening on 0.0.0.0:5000")
        sys.exit(1)
    
    # Step 2: Test health
    print("\n2️⃣ Testing API health...")
    if not test_health_endpoint(base_url):
        print("❌ API not responding. Check your Replit server.")
        sys.exit(1)
    
    # Step 3: Test with mock auth
    print("\n3️⃣ Testing profiles endpoint...")
    test_with_mock_auth(base_url)
    
    print("\n🏁 Replit test complete!")
    print("\n💡 If this doesn't work, your Replit might need:")
    print("   - Database connection enabled")
    print("   - Environment variables set")
    print("   - Proper authentication setup")

if __name__ == "__main__":
    main()