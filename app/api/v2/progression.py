"""
Progression API endpoints for V2.

This module provides REST API endpoints for user progression operations including
XP addition, level calculations, and progression tracking. It implements endpoints
for managing user advancement across different categories (global, strength, endurance, technique).
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

from app.application.services.progression_service import ProgressionService, ProgressionResult
from app.infrastructure.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.auth import get_current_user_id


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/progression",
    tags=["progression"],
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


async def get_progression_service() -> ProgressionService:
    """
    Dependency injection for ProgressionService.
    
    Returns:
        ProgressionService: Instance of the progression service
    """
    return ProgressionService()


# Request/Response Models
class AuraUpdateInfo(BaseModel):
    """Model for aura update information in API responses."""
    previous_aura: float = Field(..., description="Previous aura value")
    new_aura: float = Field(..., description="New aura value after update")
    change: float = Field(..., description="Change in aura value")
    reason: str = Field(..., description="Reason for aura change")


class AddXPRequest(BaseModel):
    """Request model for adding XP to a user."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    amount: int = Field(..., description="Amount of XP to add", gt=0)
    category: str = Field(..., description="XP category (global, strength, endurance, technique)")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = {'global', 'strength', 'endurance', 'technique'}
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v


class LevelProgressRequest(BaseModel):
    """Request model for getting level progress."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    category: str = Field(default='global', description="Category to check progress for")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = {'global', 'strength', 'endurance', 'technique'}
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v


class ProgressionResponse(BaseModel):
    """Response model for progression operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Dict[str, Any] = Field(..., description="Progression result data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LevelProgressResponse(BaseModel):
    """Response model for level progress information."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Dict[str, Any] = Field(..., description="Level progress data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Service status")
    database_connection: Optional[str] = Field(None, description="Database connection status")
    users_count: Optional[int] = Field(None, description="Number of users in database")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CategoriesResponse(BaseModel):
    """Response model for valid categories."""
    categories: List[str] = Field(..., description="List of valid XP categories")
    description: str = Field(..., description="Description of the categories")


# Dependency to get ProgressionService
async def get_progression_service(session: AsyncSession = Depends(get_async_session)) -> ProgressionService:
    """Dependency to create and return a ProgressionService instance."""
    return ProgressionService(session=session)


@router.post("/add-xp", response_model=ProgressionResponse, status_code=status.HTTP_200_OK)
async def add_xp(
    request: AddXPRequest,
    progression_service: ProgressionService = Depends(get_progression_service)
) -> ProgressionResponse:
    """
    Add XP to a user in the specified category.
    
    This endpoint handles XP addition and automatically processes:
    - Level-up calculations
    - Stat point rewards
    - Aura updates
    - Transaction management
    
    Args:
        request: XP addition request containing user_id, amount, and category
        progression_service: Injected ProgressionService instance
        
    Returns:
        ProgressionResponse: Complete progression update information
        
    Raises:
        HTTPException: 400 for validation errors, 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Adding {request.amount} XP to user {request.user_id} in category {request.category}")
        
        # Add XP and get progression result
        result = await progression_service.add_xp(
            user_id=request.user_id,
            amount=request.amount,
            category=request.category
        )
        
        # Format response message
        message_parts = [f"Added {request.amount} XP to {request.category}"]
        
        if result.level_changes:
            for category, changes in result.level_changes.items():
                message_parts.append(
                    f"{category} leveled up from {changes['previous']} to {changes['new']}"
                )
        
        if result.stat_points_awarded:
            total_points = sum(result.stat_points_awarded.values())
            message_parts.append(f"Awarded {total_points} total stat points")
        
        aura_change = result.new_aura - result.previous_aura
        if aura_change != 0:
            message_parts.append(f"Aura changed by {aura_change}")
        
        message = ". ".join(message_parts)
        
        logger.info(f"Successfully processed XP addition for user {request.user_id}: {message}")
        
        return ProgressionResponse(
            success=True,
            message=message,
            data=result.to_dict()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in add_xp: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in add_xp: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in add_xp: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing XP addition"
            )


@router.post("/level-progress", response_model=LevelProgressResponse, status_code=status.HTTP_200_OK)
async def get_level_progress(
    request: LevelProgressRequest,
    progression_service: ProgressionService = Depends(get_progression_service)
) -> LevelProgressResponse:
    """
    Get level progress information for a user in a specific category.
    
    This endpoint provides detailed information about:
    - Current level and XP
    - XP required for next level
    - Progress percentage
    - XP remaining to next level
    
    Args:
        request: Level progress request containing user_id and category
        progression_service: Injected ProgressionService instance
        
    Returns:
        LevelProgressResponse: Level progress information
        
    Raises:
        HTTPException: 400 for validation errors, 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Getting level progress for user {request.user_id} in category {request.category}")
        
        # Get level progress
        progress = await progression_service.calculate_level_progress(
            user_id=request.user_id,
            category=request.category
        )
        
        logger.info(f"Successfully retrieved level progress for user {request.user_id}")
        
        return LevelProgressResponse(
            success=True,
            data={
                "user_id": request.user_id,
                "category": request.category,
                **progress
            }
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in get_level_progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in get_level_progress: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in get_level_progress: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving level progress"
            )


@router.get("/level-progress/{user_id}", response_model=LevelProgressResponse, status_code=status.HTTP_200_OK)
async def get_level_progress_by_path(
    user_id: int,
    category: str = "global",
    progression_service: ProgressionService = Depends(get_progression_service)
) -> LevelProgressResponse:
    """
    Get level progress information for a user via path parameters.
    
    Alternative endpoint for getting level progress using path parameters
    instead of request body. Useful for simple GET requests.
    
    Args:
        user_id: User's database ID
        category: XP category to check (default: global)
        progression_service: Injected ProgressionService instance
        
    Returns:
        LevelProgressResponse: Level progress information
        
    Raises:
        HTTPException: 400 for validation errors, 404 for user not found, 500 for server errors
    """
    # Validate category
    valid_categories = {'global', 'strength', 'endurance', 'technique'}
    if category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category '{category}'. Must be one of: {valid_categories}"
        )
    
    # Create request object and delegate to main endpoint logic
    request = LevelProgressRequest(user_id=user_id, category=category)
    return await get_level_progress(request, progression_service)


@router.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
async def health_check(
    progression_service: ProgressionService = Depends(get_progression_service)
) -> HealthCheckResponse:
    """
    Perform a health check for the ProgressionService.
    
    This endpoint verifies:
    - Service availability
    - Database connectivity
    - Basic functionality
    
    Returns:
        HealthCheckResponse: Health check results
    """
    try:
        logger.info("Performing progression service health check")
        
        # Perform health check
        health_data = await progression_service.health_check()
        
        # Add timestamp
        health_data["timestamp"] = datetime.now(timezone.utc)
        
        logger.info(f"Health check completed: {health_data['status']}")
        
        return HealthCheckResponse(**health_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            service="ProgressionService",
            status="unhealthy",
            error=str(e),
            timestamp=datetime.now(timezone.utc)
        )


# Additional utility endpoints

@router.get("/categories", response_model=CategoriesResponse, status_code=status.HTTP_200_OK)
async def get_valid_categories() -> CategoriesResponse:
    """
    Get list of valid XP categories.
    
    Returns:
        CategoriesResponse containing list of valid categories
    """
    return CategoriesResponse(
        categories=list(ProgressionService.VALID_CATEGORIES),
        description="Valid XP categories for progression operations"
    )


@router.get("/xp-formula/{level}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_xp_formula_info(
    level: int,
    progression_service: ProgressionService = Depends(get_progression_service)
) -> Dict[str, Any]:
    """
    Get XP formula information for a specific level.
    
    This endpoint provides information about the XP requirements
    for reaching a specific level using the formula: 100 * (level ^ 1.5)
    
    Args:
        level: Target level to calculate XP for
        progression_service: Injected ProgressionService instance
        
    Returns:
        Dict containing XP formula information
        
    Raises:
        HTTPException: 400 for invalid level values
    """
    if level < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level must be 1 or greater"
        )
    
    if level > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level must be 1000 or less"
        )
    
    try:
        # Calculate XP requirements
        total_xp_required = progression_service._calculate_xp_for_level(level)
        
        if level > 1:
            previous_level_xp = progression_service._calculate_xp_for_level(level - 1)
            xp_for_this_level = total_xp_required - previous_level_xp
        else:
            previous_level_xp = 0
            xp_for_this_level = 0
        
        return {
            "level": level,
            "total_xp_required": round(total_xp_required, 2),
            "xp_for_this_level": round(xp_for_this_level, 2),
            "previous_level_total_xp": round(previous_level_xp, 2),
            "formula": "100 * (level ^ 1.5) per level",
            "description": f"To reach level {level}, you need {round(total_xp_required, 2)} total XP"
        }
        
    except Exception as e:
        logger.error(f"Error calculating XP formula for level {level}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating XP requirements"
        )


class UnlockSkillRequest(BaseModel):
    """Request model for unlocking a skill tree node."""
    node_id: str = Field(..., description="ID of the skill tree node to unlock", min_length=1)


class UnlockSkillResponse(BaseModel):
    """Response model for skill unlock operations."""
    success: bool = Field(..., description="Whether the unlock was successful")
    message: str = Field(..., description="Human-readable message")
    data: Dict[str, Any] = Field(..., description="Unlock result data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@router.post("/unlock-skill", response_model=UnlockSkillResponse, status_code=status.HTTP_200_OK)
async def unlock_skill(
    request: UnlockSkillRequest,
    user_id: int = Depends(get_current_user_id),
    progression_service: ProgressionService = Depends(get_progression_service)
) -> UnlockSkillResponse:
    """
    Unlock a skill tree node for a user.
    
    This endpoint handles skill unlocking and automatically processes:
    - Requirement validation (stats, skill points, prerequisites, level)
    - Skill point deduction
    - UserSkillProgress record creation
    - Aura updates
    - Transaction management
    
    Args:
        request: Skill unlock request containing user_id and node_id
        progression_service: Injected ProgressionService instance
        
    Returns:
        UnlockSkillResponse: Complete skill unlock information
        
    Raises:
        HTTPException: 400 for validation/requirement errors, 404 for user/node not found, 500 for server errors
    """
    try:
        logger.info(f"Unlocking skill node {request.node_id} for user {user_id}")
        
        # Unlock skill and get progression result
        result = await progression_service.unlock_skill(
            user_id=user_id,
            node_id=request.node_id
        )
        
        # Format response message
        message_parts = [f"Successfully unlocked skill: {result.node_name}"]
        
        if result.skill_points_deducted:
            total_deducted = result.skill_points_deducted.get('total', 0)
            if total_deducted > 0:
                message_parts.append(f"Deducted {total_deducted} skill points")
        
        aura_change = result.new_aura - result.previous_aura
        if aura_change != 0:
            message_parts.append(f"Aura increased by {aura_change}")
        
        message = ". ".join(message_parts)
        
        logger.info(f"Successfully unlocked skill for user {user_id}: {message}")
        
        return UnlockSkillResponse(
            success=True,
            message=message,
            data=result.to_dict()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in unlock_skill: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User or node not found in unlock_skill: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            logger.error(f"Unexpected error in unlock_skill: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while unlocking skill"
            )