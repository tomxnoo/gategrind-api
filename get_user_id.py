#!/usr/bin/env python3
"""
Quick script to get your user ID from Discord ID for testing.
"""

import asyncio
import sys
import os

# Enable development mode
os.environ["DEVELOPMENT_MODE"] = "true"

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.database.session import get_async_session
from app.infrastructure.database.models.v2 import Ascendant
from sqlalchemy import select


async def get_user_id():
    """Get user ID by Discord ID."""
    print("=== Finding Your User ID ===\n")
    
    session_gen = get_async_session()
    session = await session_gen.__anext__()
    
    try:
        # List all users
        stmt = select(Ascendant).limit(10)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        if users:
            print("Available users:")
            for user in users:
                print(f"  ID: {user.id}, Discord: {user.discord_id}, Username: {user.username}")
                print(f"    Level: {user.level}, Skill Points: STR:{user.strength_points} END:{user.endurance_points} TECH:{user.technique_points}")
                print()
        else:
            print("No users found in database")
            
        # Ask for Discord ID
        discord_id = input("Enter your Discord ID (or press Enter to use first user): ").strip()
        
        if discord_id:
            stmt = select(Ascendant).where(Ascendant.discord_id == discord_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f"\n✅ Found your user!")
                print(f"Database ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Use this ID in admin commands: {user.id}")
            else:
                print(f"\n❌ No user found with Discord ID: {discord_id}")
        elif users:
            user = users[0]
            print(f"\n✅ Using first user:")
            print(f"Database ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Use this ID in admin commands: {user.id}")
    
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(get_user_id())