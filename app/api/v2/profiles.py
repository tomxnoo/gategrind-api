"""
Profile API endpoints for V2.

This module provides REST API endpoints for user profile management including
comprehensive profile data retrieval that combines ascendant stats, dungeon progress,
skill tree progression, and quest information.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.infrastructure.database.session import get_async_session
from app.api.v2.dependencies.auth import get_current_user_id
from app.api.v2.schemas.profile_schemas import AscendantProfileResponse
from app.api.v2.schemas.ascendant_schemas import AscendantStatsSchema
from app.api.v2.schemas.skill_tree_schemas import UserSkillProgressResponse
from app.api.v2.schemas.dungeon_schemas import DungeonKeyResponse, DungeonProgressResponse
from app.api.v2.schemas.quest_schemas import QuestResponse
from app.infrastructure.database.models.v2.ascendants import Ascendant
from app.infrastructure.database.models.v2.stats import AscendantStats
from app.infrastructure.database.models.v2.user_skill_progress import UserSkillProgress

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/users",
    tags=["profiles"],
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


async def get_user_profile_data(
    user_id: int,
    session: AsyncSession
) -> Optional[AscendantProfileResponse]:
    """
    Fetch comprehensive user profile data from database.
    
    Args:
        user_id: The user's database ID
        session: Database session
        
    Returns:
        AscendantProfileResponse: Complete profile data or None if user not found
    """
    try:
        # Fetch user with all related data
        stmt = (
            select(Ascendant)
            .options(
                selectinload(Ascendant.stats),
                selectinload(Ascendant.skill_progress),
                # Add other relationships as needed
            )
            .where(Ascendant.id == user_id)
        )
        
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Build stats schema
        stats_data = AscendantStatsSchema(
            level=user.stats.level if user.stats else 1,
            xp=user.stats.xp if user.stats else 0,
            xp_max=user.stats.xp_max if user.stats else 100,
            str_level=user.stats.str_level if user.stats else 1,
            str_xp=user.stats.str_xp if user.stats else 0,
            end_level=user.stats.end_level if user.stats else 1,
            end_xp=user.stats.end_xp if user.stats else 0,
            tech_level=user.stats.tech_level if user.stats else 1,
            tech_xp=user.stats.tech_xp if user.stats else 0,
            aura=user.stats.aura if user.stats else 0,
            shadow_keys=user.stats.shadow_keys if user.stats else 0,
            awakening_streak=user.stats.awakening_streak if user.stats else 0
        )
        
        # Build skill progress list
        unlocked_skills = []
        if user.skill_progress:
            for skill in user.skill_progress:
                unlocked_skills.append(UserSkillProgressResponse(
                    node_id=skill.node_id,
                    unlocked_at=skill.unlocked_at
                ))
        
        # For now, return empty lists for dungeon and quest data
        # These would be populated by calling appropriate services
        dungeon_keys = []
        active_quests = []
        dungeon_progress = None
        
        # Build the complete profile response
        profile = AscendantProfileResponse(
            id=user.id,
            discord_id=user.discord_id,
            username=user.username,
            display_name=user.display_name,
            stats=stats_data,
            dungeon_progress=dungeon_progress,
            dungeon_keys=dungeon_keys,
            unlocked_skills=unlocked_skills,
            active_quests=active_quests,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return profile
        
    except Exception as e:
        logger.error(f"Error fetching user profile data for user {user_id}: {e}")
        raise


@router.get("/me/profile", response_model=AscendantProfileResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session)
) -> AscendantProfileResponse:
    """
    Get the current user's comprehensive profile.
    
    This endpoint returns a complete profile including:
    - Core ascendant information (ID, discord_id, username, display_name)
    - Detailed stats breakdown (levels, XP, aura, shadow keys, awakening streak)
    - Dungeon system data (progress, keys)
    - Skill tree progression (unlocked skills)
    - Quest system data (active quests)
    - Timestamps (created_at, updated_at)
    
    Returns:
        AscendantProfileResponse: Complete user profile data
        
    Raises:
        HTTPException: 404 if user not found, 500 for server errors
    """
    try:
        logger.info(f"Fetching profile for user {current_user_id}")
        
        profile = await get_user_profile_data(current_user_id, session)
        
        if not profile:
            logger.warning(f"User {current_user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {current_user_id} not found"
            )
        
        logger.info(f"Successfully fetched profile for user {current_user_id}")
        return profile
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching profile for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching user profile"
        )