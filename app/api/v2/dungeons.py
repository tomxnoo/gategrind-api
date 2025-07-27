"""
V2 Dungeons API - Modern FastAPI endpoints for dungeon management

This module provides:
- RESTful API endpoints for dungeon operations
- Integration with the DungeonService
- Proper error handling and validation
- Dungeon entry and trial completion endpoints
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.application.services.dungeon_service import (
    DungeonService, 
    DungeonLevelLockedError, 
    InsufficientRequirementsError
)
from app.api.v2.schemas.dungeon_schemas import (
    DungeonEntryRequest,
    DungeonEntryResponse,
    TrialCompletionRequest,
    TrialCompletionResponse,
    DungeonProgressResponse
)


# Additional response models for API endpoints
class DungeonHealthResponse(BaseModel):
    """Response model for dungeon service health check."""
    status: str
    message: str
    timestamp: str


class DungeonSessionResponse(BaseModel):
    """Response model for dungeon session data."""
    session_id: str
    user_id: int
    dungeon_level: int
    trials_completed: int
    total_trials: int
    is_completed: bool
    created_at: str
    expires_at: str
    daily_modifier: Optional[Dict[str, Any]] = None


# Router setup
router = APIRouter(prefix="/dungeons", tags=["dungeons"])


def get_dungeon_service() -> DungeonService:
    """Dependency to get DungeonService instance."""
    return DungeonService()


# API Endpoints
@router.post("/enter", response_model=DungeonEntryResponse)
async def enter_dungeon(
    request: DungeonEntryRequest,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Enter a dungeon level.
    
    Args:
        request: Dungeon entry request containing user_id and dungeon_level
        
    Returns:
        DungeonEntryResponse: Session details and trials to complete
        
    Raises:
        HTTPException: If entry requirements are not met or level is locked
    """
    try:
        response = await service.enter_dungeon(
            user_id=request.user_id,
            dungeon_level=request.dungeon_level
        )
        return response
        
    except DungeonLevelLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Dungeon level {request.dungeon_level} is locked: {str(e)}"
        )
    except InsufficientRequirementsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient requirements for dungeon level {request.dungeon_level}: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enter dungeon: {str(e)}"
        )


@router.post("/complete-trial", response_model=TrialCompletionResponse)
async def complete_trial(
    request: TrialCompletionRequest,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Complete a dungeon trial.
    
    Args:
        request: Trial completion request containing session_id and trial_data
        
    Returns:
        TrialCompletionResponse: Completion status and rewards
        
    Raises:
        HTTPException: If session is invalid or trial completion fails
    """
    try:
        response = await service.complete_trial(
            session_id=request.session_id,
            trial_data=request.trial_data
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete trial: {str(e)}"
        )


@router.get("/progress/{user_id}", response_model=DungeonProgressResponse)
async def get_dungeon_progress(
    user_id: int,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Get dungeon progress for a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        DungeonProgressResponse: User's dungeon progress data
        
    Raises:
        HTTPException: If user not found or error retrieving progress
    """
    try:
        progress = await service.get_dungeon_progress(user_id=user_id)
        
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dungeon progress not found for user {user_id}"
            )
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dungeon progress: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=DungeonSessionResponse)
async def get_dungeon_session(
    session_id: str,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Get dungeon session details.
    
    Args:
        session_id: The session identifier
        
    Returns:
        DungeonSessionResponse: Session details
        
    Raises:
        HTTPException: If session not found
    """
    try:
        # This would need to be implemented in DungeonService
        # For now, return a placeholder response
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Session retrieval endpoint not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@router.get("/health", response_model=DungeonHealthResponse)
async def dungeon_health_check(
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Health check endpoint for dungeon service.
    
    Returns:
        DungeonHealthResponse: Service health status
    """
    try:
        health_status = await service.health_check()
        return DungeonHealthResponse(
            status="healthy" if health_status else "unhealthy",
            message="Dungeon service is operational" if health_status else "Dungeon service has issues",
            timestamp=str(datetime.utcnow())
        )
        
    except Exception as e:
        return DungeonHealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            timestamp=str(datetime.utcnow())
        )


# Export for easy import
__all__ = ["router"]