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
    InsufficientRequirementsError,
    ActiveSessionExistsError
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
            ascendant_id=request.user_id,  # Map user_id to ascendant_id
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
    except ActiveSessionExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
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
            trial_id=request.trial_id,
            progress_data=request.progress_data
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
        progress = await service.get_dungeon_progress(ascendant_id=user_id)
        
        if not progress:
            # Return empty progress instead of 404
            return DungeonProgressResponse(
                ascendant_id=user_id,
                highest_level_completed=0,
                total_completions=0,
                total_shadow_keys_spent=0
            )
        
        return DungeonProgressResponse(
            ascendant_id=progress.ascendant_id,
            highest_level_completed=progress.highest_level_completed or 0,
            total_completions=progress.total_completions or 0,
            total_shadow_keys_spent=progress.total_shadow_keys_spent or 0
        )
        
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


@router.post("/recover", response_model=DungeonSessionResponse)
async def recover_session(
    user_id: int,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Recover an active dungeon session for a user.
    
    Args:
        user_id: The user ID to recover session for
        
    Returns:
        DungeonSessionResponse: Active session details if found
        
    Raises:
        HTTPException: If no active session found
    """
    try:
        session_data = await service.recover_session(ascendant_id=user_id)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active dungeon session found"
            )
        
        # Convert to response model
        return DungeonSessionResponse(
            session_id=str(session_data['session_id']),
            user_id=user_id,
            dungeon_level=session_data['level'],
            trials_completed=sum(1 for t in session_data['trials'] if t['is_completed']),
            total_trials=len(session_data['trials']),
            is_completed=session_data['status'] == 'completed',
            created_at=session_data['created_at'].isoformat(),
            expires_at=session_data['expires_at'].isoformat(),
            daily_modifier=None  # Would need to fetch if needed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recover session: {str(e)}"
        )


@router.post("/abandon/{session_id}")
async def abandon_session(
    session_id: int,
    user_id: int,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Abandon an active dungeon session.
    
    Args:
        session_id: The session to abandon
        user_id: The user abandoning the session
        
    Returns:
        Dict with abandonment confirmation
        
    Raises:
        HTTPException: If session not found or unauthorized
    """
    try:
        result = await service.abandon_session(
            session_id=session_id,
            ascendant_id=user_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to abandon session: {str(e)}"
        )


@router.get("/session/{session_id}/details")
async def get_session_details(
    session_id: int,
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Get detailed information about a dungeon session.
    
    Args:
        session_id: The session to get details for
        
    Returns:
        Dict containing full session details
        
    Raises:
        HTTPException: If session not found
    """
    try:
        details = await service.get_session_details(session_id=session_id)
        
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session details: {str(e)}"
        )


@router.get("/daily-modifier")
async def get_daily_modifier(
    service: DungeonService = Depends(get_dungeon_service)
):
    """
    Get the current daily modifier.
    
    Returns:
        Dict containing daily modifier details or null
    """
    try:
        modifier = await service.get_daily_modifier()
        return {"daily_modifier": modifier}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get daily modifier: {str(e)}"
        )


# Export for easy import
__all__ = ["router"]