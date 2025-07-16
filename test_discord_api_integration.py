#!/usr/bin/env python3
"""
Test script to verify Discord bot can communicate with FastAPI
"""

import asyncio
import discord
from core.api_client import api_client

class MockDiscordUser:
    """Mock Discord user for testing"""
    def __init__(self, user_id: int, username: str):
        self.id = user_id
        self.name = username
        self.display_name = username
        self.display_avatar = MockAvatar()

class MockAvatar:
    """Mock Discord avatar"""
    @property
    def url(self):
        return "https://cdn.discordapp.com/embed/avatars/0.png"

async def test_api_integration():
    """Test Discord bot API integration"""
    print("🤖 Testing Discord Bot API Integration")
    print("=" * 50)
    
    # Create mock Discord user
    mock_user = MockDiscordUser(123456789, "test_user")
    
    try:
        # Test 1: Get user profile
        print("\n1. Testing get_user_profile...")
        profile_data = await api_client.get_user_profile(mock_user)
        print(f"✅ Profile data: {profile_data['username']} (Level {profile_data['level']})")
        
        # Test 2: Get daily quests
        print("\n2. Testing get_daily_quests...")
        quests_data = await api_client.get_daily_quests(mock_user)
        # quests_data is a list directly
        print(f"✅ Daily quests: {len(quests_data)} quests found")
        
        # Test 3: Get quest history
        print("\n3. Testing get_quest_history...")
        history_data = await api_client.get_quest_history(mock_user, limit=5)
        # history_data is a list directly
        print(f"✅ Quest history: {len(history_data)} completed quests")
        
        # Test 4: Get rep history
        print("\n4. Testing get_rep_history...")
        rep_data = await api_client.get_rep_history(mock_user, limit=5)
        # rep_data is a list directly
        print(f"✅ Rep history: {len(rep_data)} logged sessions")
        
        # Test 5: Get available movements
        print("\n5. Testing get_available_movements...")
        movements_data = await api_client.get_available_movements(mock_user)
        # movements_data is a list directly
        print(f"✅ Available movements: {len(movements_data)} movement types")
        
        # Test 6: Get logging stats
        print("\n6. Testing get_logging_stats...")
        stats_data = await api_client.get_logging_stats(mock_user)
        # stats_data is a dict directly
        print(f"✅ Logging stats: {stats_data.get('total_sessions', stats_data.get('total_workouts', 0))} total sessions")
        
        # Test 7: Health check
        print("\n7. Testing health check...")
        health_data = await api_client.get_health_status()
        print(f"✅ API Health: {health_data.get('status', 'unknown')}")
        
        print("\n🎉 All API integration tests passed!")
        print("Discord bot can successfully communicate with FastAPI backend.")
        
    except Exception as e:
        print(f"\n❌ API integration test failed: {e}")
        print("Make sure the FastAPI server is running with: python test_fastapi_only.py")

if __name__ == "__main__":
    asyncio.run(test_api_integration())