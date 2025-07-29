"""
Admin commands for progression system testing and management.

This module provides admin-only endpoints for testing and managing user progression,
including granting XP, skill points, levels, and other progression-related operations.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.application.services.progression_service import ProgressionService
from app.infrastructure.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v2.dependencies.auth import get_current_user_id
from app.infrastructure.database.models.v2 import Ascendant
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/admin/progression",
    tags=["admin", "progression"],
    responses={
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


# Request Models
class GrantXPRequest(BaseModel):
    """Request model for granting XP to a user."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    amount: int = Field(..., description="Amount of XP to grant", gt=0)
    category: str = Field(default="global", description="XP category (global, strength, endurance, technique)")


class GrantSkillPointsRequest(BaseModel):
    """Request model for granting skill points to a user."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    strength_points: int = Field(default=0, description="Strength skill points to grant", ge=0)
    endurance_points: int = Field(default=0, description="Endurance skill points to grant", ge=0)
    technique_points: int = Field(default=0, description="Technique skill points to grant", ge=0)
    shadow_essence: int = Field(default=0, description="Shadow essence (universal skill points) to grant", ge=0)


class SetLevelRequest(BaseModel):
    """Request model for setting user level."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    level: int = Field(..., description="Target level", ge=1, le=1000)


class GrantStatsRequest(BaseModel):
    """Request model for granting direct stat values."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    str_value: int = Field(default=0, description="Strength stat value to grant", ge=0)
    end_value: int = Field(default=0, description="Endurance stat value to grant", ge=0)
    tech_value: int = Field(default=0, description="Technique stat value to grant", ge=0)


class AdminResponse(BaseModel):
    """Response model for admin operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Dict[str, Any] = Field(..., description="Operation result data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Dependency to get ProgressionService
async def get_progression_service(session: AsyncSession = Depends(get_async_session)) -> ProgressionService:
    """Dependency to create and return a ProgressionService instance."""
    return ProgressionService(session=session)


async def verify_admin_access(user_id: int = Depends(get_current_user_id)) -> int:
    """Verify admin access - for now, just return user_id. In production, add proper admin checks."""
    # TODO: Add proper admin role verification
    # For now, allowing any authenticated user for testing purposes
    return user_id


@router.post("/grant-xp", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def grant_xp(
    request: GrantXPRequest,
    admin_user_id: int = Depends(verify_admin_access),
    progression_service: ProgressionService = Depends(get_progression_service)
) -> AdminResponse:
    """
    Grant XP to a user (Admin only).
    
    This endpoint allows admins to grant XP to any user for testing purposes.
    It automatically processes level-ups, stat point awards, and aura updates.
    """
    try:
        logger.info(f"Admin {admin_user_id} granting {request.amount} {request.category} XP to user {request.user_id}")
        
        # Grant XP using progression service
        result = await progression_service.add_xp(
            user_id=request.user_id,
            amount=request.amount,
            category=request.category
        )
        
        # Format response message
        message_parts = [f"Granted {request.amount} {request.category} XP"]
        
        if result.level_changes:
            for category, changes in result.level_changes.items():
                message_parts.append(
                    f"{category} leveled up from {changes['previous']} to {changes['new']}"
                )
        
        if result.stat_points_awarded:
            total_points = sum(result.stat_points_awarded.values())
            message_parts.append(f"Awarded {total_points} skill points")
        
        aura_change = result.new_aura - result.previous_aura
        if aura_change != 0:
            message_parts.append(f"Aura changed by {aura_change}")
        
        message = ". ".join(message_parts)
        
        return AdminResponse(
            success=True,
            message=message,
            data=result.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Admin XP grant failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/grant-skill-points", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def grant_skill_points(
    request: GrantSkillPointsRequest,
    admin_user_id: int = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_async_session)
) -> AdminResponse:
    """
    Grant skill points directly to a user (Admin only).
    
    This endpoint allows admins to directly grant skill points for testing
    skill tree unlocking without having to level up users.
    """
    try:
        logger.info(f"Admin {admin_user_id} granting skill points to user {request.user_id}")
        
        # Get user
        stmt = select(Ascendant).where(Ascendant.id == request.user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        
        # Grant skill points
        original_str = user.strength_points
        original_end = user.endurance_points
        original_tech = user.technique_points
        original_shadow = user.skill_points
        
        user.strength_points += request.strength_points
        user.endurance_points += request.endurance_points
        user.technique_points += request.technique_points
        user.skill_points += request.shadow_essence
        
        await session.commit()
        
        # Format response
        changes = []
        if request.strength_points > 0:
            changes.append(f"Strength: {original_str} → {user.strength_points}")
        if request.endurance_points > 0:
            changes.append(f"Endurance: {original_end} → {user.endurance_points}")
        if request.technique_points > 0:
            changes.append(f"Technique: {original_tech} → {user.technique_points}")
        if request.shadow_essence > 0:
            changes.append(f"Shadow Essence: {original_shadow} → {user.skill_points}")
        
        message = f"Granted skill points to {user.username}: " + ", ".join(changes)
        
        return AdminResponse(
            success=True,
            message=message,
            data={
                "user_id": request.user_id,
                "skill_points_granted": {
                    "strength_points": request.strength_points,
                    "endurance_points": request.endurance_points,
                    "technique_points": request.technique_points,
                    "shadow_essence": request.shadow_essence
                },
                "new_totals": {
                    "strength_points": user.strength_points,
                    "endurance_points": user.endurance_points,
                    "technique_points": user.technique_points,
                    "skill_points": user.skill_points
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Admin skill points grant failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant skill points"
        )


@router.post("/set-level", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def set_level(
    request: SetLevelRequest,
    admin_user_id: int = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_async_session)
) -> AdminResponse:
    """
    Set a user's level directly (Admin only).
    
    This endpoint allows admins to set a user's level and automatically
    calculates the appropriate XP and skill points for that level.
    """
    try:
        logger.info(f"Admin {admin_user_id} setting user {request.user_id} to level {request.level}")
        
        # Get user
        stmt = select(Ascendant).where(Ascendant.id == request.user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        
        # Calculate XP for target level using progression service formula
        progression_service = ProgressionService(session=session)
        target_xp = progression_service._calculate_xp_for_level(request.level)
        
        # Calculate skill points (1 per level for each stat)
        skill_points_per_stat = request.level - 1  # Level 1 gives 0, level 2 gives 1, etc.
        
        original_level = user.level
        original_xp = user.global_xp
        
        # Set new values
        user.level = request.level
        user.global_xp = int(target_xp)
        user.strength_points = skill_points_per_stat
        user.endurance_points = skill_points_per_stat
        user.technique_points = skill_points_per_stat
        
        # Recalculate aura
        new_aura = await progression_service._calculate_and_update_aura(session, user)
        
        await session.commit()
        
        message = f"Set {user.username} to level {request.level} (was {original_level})"
        
        return AdminResponse(
            success=True,
            message=message,
            data={
                "user_id": request.user_id,
                "level_change": {
                    "previous": original_level,
                    "new": user.level
                },
                "xp_change": {
                    "previous": original_xp,
                    "new": user.global_xp
                },
                "skill_points_set": {
                    "strength_points": user.strength_points,
                    "endurance_points": user.endurance_points,
                    "technique_points": user.technique_points
                },
                "new_aura": new_aura
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Admin set level failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set user level"
        )


@router.post("/grant-stats", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def grant_stats(
    request: GrantStatsRequest,
    admin_user_id: int = Depends(verify_admin_access),
    progression_service: ProgressionService = Depends(get_progression_service)
) -> AdminResponse:
    """
    Grant direct stat values to a user (Admin only).
    
    This endpoint allows admins to grant stat values directly for testing
    stat requirements on skill nodes.
    """
    try:
        logger.info(f"Admin {admin_user_id} granting stats to user {request.user_id}")
        
        # Use progression service to add stat rewards
        result = await progression_service.add_stat_rewards(
            user_id=request.user_id,
            str_reward=request.str_value,
            end_reward=request.end_value,
            tech_reward=request.tech_value
        )
        
        message_parts = [f"Granted stats to user {request.user_id}"]
        
        if request.str_value > 0:
            message_parts.append(f"STR +{request.str_value}")
        if request.end_value > 0:
            message_parts.append(f"END +{request.end_value}")
        if request.tech_value > 0:
            message_parts.append(f"TECH +{request.tech_value}")
            
        if result.stat_points_awarded:
            total_points = sum(result.stat_points_awarded.values())
            message_parts.append(f"Milestone rewards: {total_points} skill points")
        
        aura_change = result.new_aura - result.previous_aura
        if aura_change != 0:
            message_parts.append(f"Aura +{aura_change}")
        
        message = ". ".join(message_parts)
        
        return AdminResponse(
            success=True,
            message=message,
            data=result.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Admin stats grant failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/user-status/{user_id}", response_model=AdminResponse, status_code=status.HTTP_200_OK)
async def get_user_status(
    user_id: int,
    admin_user_id: int = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_async_session)
) -> AdminResponse:
    """
    Get detailed user progression status (Admin only).
    
    This endpoint provides comprehensive information about a user's
    progression state for admin monitoring and testing.
    """
    try:
        # Get user with stats
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Ascendant)
            .options(selectinload(Ascendant.stats))
            .where(Ascendant.id == user_id)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Get skill progress count
        from app.infrastructure.database.models.v2 import UserSkillProgress
        skill_stmt = select(UserSkillProgress).where(UserSkillProgress.ascendant_id == user_id)
        skill_result = await session.execute(skill_stmt)
        unlocked_skills = skill_result.scalars().all()
        
        user_data = {
            "user_id": user.id,
            "discord_id": user.discord_id,
            "username": user.username,
            "level": user.level,
            "global_xp": user.global_xp,
            "aura": user.aura,
            "skill_points": {
                "shadow_essence": user.skill_points,
                "strength_points": user.strength_points,
                "endurance_points": user.endurance_points,
                "technique_points": user.technique_points,
                "total": user.skill_points + user.strength_points + user.endurance_points + user.technique_points
            },
            "stats": {
                "str_level": user.stats.str_level if user.stats else 1,
                "end_level": user.stats.end_level if user.stats else 1,
                "tech_level": user.stats.tech_level if user.stats else 1,
                "str_value": user.stats.str_value if user.stats else 10,
                "end_value": user.stats.end_value if user.stats else 10,
                "tech_value": user.stats.tech_value if user.stats else 10,
            },
            "progression": {
                "unlocked_skills_count": len(unlocked_skills),
                "unlocked_skill_nodes": [skill.node_id for skill in unlocked_skills]
            }
        }
        
        return AdminResponse(
            success=True,
            message=f"User status for {user.username}",
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user status"
        )