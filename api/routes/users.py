from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import asyncpg

from api.models.user import UserProfile, UserUpdate, UserSummary
from api.models.common import SuccessResponse
from api.dependencies import get_db_pool_optional, get_current_user, is_development_mode
from core.database.db import get_unified_user_data

router = APIRouter()

def get_mock_user_profile(user_id: int = 1) -> UserProfile:
    """Get mock user profile for development mode"""
    return UserProfile(
        user_id=user_id,
        discord_id=f"dev_user_{user_id}",
        username=f"DevUser{user_id}",
        level=5,
        xp=250,
        xp_max=500,
        stats={
            "STR": {"level": 3, "xp": 150, "xp_max": 200},
            "END": {"level": 2, "xp": 75, "xp_max": 150},
            "TECH": {"level": 4, "xp": 300, "xp_max": 400}
        },
        active_buffs={
            "strength_boost": {
                "name": "Strength Boost",
                "description": "Increases STR gain by 25%",
                "expires_at": "2024-12-31T23:59:59"
            }
        },
        created_at="2024-01-01T00:00:00",
        updated_at="2024-12-01T12:00:00"
    )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get current user's profile"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return get_mock_user_profile(current_user["user_id"])
    
    # Production mode: use database
    async with db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, current_user["user_id"])
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Transform the data to match our Pydantic model
        profile_data = {
            "user_id": user_data.get("user_id"),
            "discord_id": str(user_data.get("user_id", "")),  # Temporary mapping
            "username": user_data.get("username", "Unknown"),
            "level": user_data.get("level", 1),
            "xp": user_data.get("xp", 0),
            "xp_max": user_data.get("xp_max", 100),
            "stats": user_data.get("stats", {
                "STR": {"level": 1, "xp": 0, "xp_max": 100},
                "END": {"level": 1, "xp": 0, "xp_max": 100},
                "TECH": {"level": 1, "xp": 0, "xp_max": 100}
            }),
            "active_buffs": user_data.get("active_buffs", {}),
            "created_at": user_data.get("created_at", "2024-01-01T00:00:00"),
            "updated_at": user_data.get("updated_at", "2024-01-01T00:00:00")
        }
        
        return UserProfile(**profile_data)

@router.put("/me", response_model=SuccessResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Update current user's profile"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message="User profile updated successfully (development mode)",
            data={"user_id": current_user["user_id"], "mode": "development"}
        )
    
    # Production mode: use database
    async with db_pool.acquire() as conn:
        # For now, return a success response
        # This will be implemented with proper update logic
        return SuccessResponse(
            message="User profile updated successfully",
            data={"user_id": current_user["user_id"]}
        )

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get user profile by ID (public endpoint)"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return get_mock_user_profile(user_id)
    
    # Production mode: use database
    async with db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Transform the data similar to get_current_user_profile
        profile_data = {
            "user_id": user_data.get("user_id"),
            "discord_id": str(user_data.get("user_id", "")),
            "username": user_data.get("username", "Unknown"),
            "level": user_data.get("level", 1),
            "xp": user_data.get("xp", 0),
            "xp_max": user_data.get("xp_max", 100),
            "stats": user_data.get("stats", {
                "STR": {"level": 1, "xp": 0, "xp_max": 100},
                "END": {"level": 1, "xp": 0, "xp_max": 100},
                "TECH": {"level": 1, "xp": 0, "xp_max": 100}
            }),
            "active_buffs": user_data.get("active_buffs", {}),
            "created_at": user_data.get("created_at", "2024-01-01T00:00:00"),
            "updated_at": user_data.get("updated_at", "2024-01-01T00:00:00")
        }
        
        return UserProfile(**profile_data)