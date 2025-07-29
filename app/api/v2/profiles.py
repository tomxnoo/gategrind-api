"""V2 Profiles API endpoints.

This module provides endpoints for managing user profiles in the V2 API.
It includes functionality for retrieving and updating user profile information.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.config import settings
from app.api.v2.dependencies.auth import get_current_user_id, get_db_session_or_none
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.api.v2.schemas.profile_schemas import AscendantProfileResponse, AvailablePointsSchema

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/debug")
async def debug_env():
    """Debug endpoint to check environment variables."""
    import os
    return {
        "DEV_MODE": os.getenv("DEV_MODE", "NOT_SET"),
        "environment": settings.environment,
        "is_development": settings.is_development()
    }


@router.get("/me", response_model=AscendantProfileResponse)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user_id),
    db_session: Optional[AsyncSession] = Depends(get_db_session_or_none)
) -> AscendantProfileResponse:
    """
    Get the current user's profile.
    
    Returns comprehensive profile information including stats, progression,
    and available skill points for the authenticated user.
    
    Args:
        current_user_id: The authenticated user's ID
        db_session: Database session (None in development mode)
        
    Returns:
        AscendantProfileResponse: The user's profile data including available skill points
        
    Raises:
        HTTPException: If user not found or database error
    """
    # In development mode, return mock data
    if settings.DEV_MODE:
        from app.api.v2.schemas.ascendant_schemas import AscendantStatsSchema
        
        return AscendantProfileResponse(
            id=current_user_id,
            discord_id="123456789012345678",
            username="DevUser",
            stats=AscendantStatsSchema(
                str_level=10,
                str_xp=2500.0,
                end_level=8,
                end_xp=1800.0,
                tech_level=12,
                tech_xp=3200.0
            ),
            available_points=AvailablePointsSchema(
                strength=5,
                endurance=3,
                technique=7
            ),
            dungeon_progress=None,
            dungeon_keys=[],
            unlocked_skills=[],
            active_quests=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    # Production mode - fetch from database
    if db_session is None:
        raise HTTPException(
            status_code=500,
            detail="Database session not available"
        )
    
    try:
        # Query the Ascendant model for the user's profile with eager loading
        # Note: current_user_id is the actual user ID from JWT, not discord_id
        result = await db_session.execute(
            select(Ascendant)
            .options(selectinload(Ascendant.stats))
            .where(Ascendant.id == current_user_id)
        )
        ascendant = result.scalar_one_or_none()
        
        if not ascendant:
            raise HTTPException(
                status_code=404,
                detail="User profile not found"
            )
        
        # For now, return a simplified response based on the Ascendant model
        # TODO: Implement full profile assembly with related data
        from app.api.v2.schemas.ascendant_schemas import AscendantStatsSchema
        
        # Build stats object, handling case where stats might not exist
        if ascendant.stats:
            stats = AscendantStatsSchema(
                str_level=ascendant.stats.str_level,
                str_xp=ascendant.stats.str_xp,
                end_level=ascendant.stats.end_level,
                end_xp=ascendant.stats.end_xp,
                tech_level=ascendant.stats.tech_level,
                tech_xp=ascendant.stats.tech_xp,
                str_value=ascendant.stats.str_value,
                end_value=ascendant.stats.end_value,
                tech_value=ascendant.stats.tech_value
            )
        else:
            # Default stats if none exist
            stats = AscendantStatsSchema(
                str_level=1,
                str_xp=0.0,
                end_level=1,
                end_xp=0.0,
                tech_level=1,
                tech_xp=0.0,
                str_value=10,
                end_value=10,
                tech_value=10
            )
        
        # Build available points from the ascendant model
        available_points = AvailablePointsSchema(
            strength=ascendant.strength_points or 0,
            endurance=ascendant.endurance_points or 0,
            technique=ascendant.technique_points or 0
        )
        
        return AscendantProfileResponse(
            id=ascendant.id,
            discord_id=ascendant.discord_id,
            username=ascendant.username,
            stats=stats,
            available_points=available_points,
            dungeon_progress=None,  # TODO: Implement dungeon progress retrieval
            dungeon_keys=[],  # TODO: Implement dungeon keys retrieval
            unlocked_skills=[],  # TODO: Implement skills retrieval
            active_quests=[],  # TODO: Implement quests retrieval
            created_at=ascendant.created_at,
            updated_at=ascendant.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve profile: {str(e)}"
        )