"""
Awakening API endpoints for V2.

This module provides REST API endpoints for the daily awakening system including
quest generation, completion tracking, progress monitoring, and session management.
It implements endpoints for managing daily awakening sessions and quest progression.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

from app.application.services.awakening_service import AwakeningService
from app.application.services.progression_service import ProgressionService
from app.infrastructure.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v2.dependencies.auth import get_current_user_id, get_db_session_or_none


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/awakening",
    tags=["awakening"],
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


# Request/Response Models
class AwakeningActionRequest(BaseModel):
    """Request model for awakening action."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    readiness_level: str = Field(..., description="User's readiness level (low, medium, high)")
    
    @field_validator('readiness_level')
    @classmethod
    def validate_readiness_level(cls, v):
        valid_levels = {'low', 'medium', 'high'}
        if v not in valid_levels:
            raise ValueError(f"Readiness level must be one of: {valid_levels}")
        return v


class CompleteQuestRequest(BaseModel):
    """Request model for completing a quest."""
    user_id: int = Field(..., description="User's database ID", gt=0)
    progress_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional progress data")


class AwakeningResponse(BaseModel):
    """Response model for awakening operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Dict[str, Any] = Field(..., description="Awakening result data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Dependency to get AwakeningService
async def get_awakening_service(session: Optional[AsyncSession] = Depends(get_db_session_or_none)) -> AwakeningService:
    """Dependency to create and return an AwakeningService instance."""
    if session is None:
        # In development mode, return mock service
        from features.awakening.logic.mock_awakening_service import MockAwakeningService
        return MockAwakeningService()
    
    # Production mode - use real service
    progression_service = ProgressionService(session=session)
    return AwakeningService(session=session, progression_service=progression_service)


@router.post("/action", response_model=AwakeningResponse, status_code=status.HTTP_200_OK)
async def process_awakening_action(
    request: AwakeningActionRequest,
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> AwakeningResponse:
    """
    Process an awakening action and create/retrieve daily session.
    
    This endpoint handles:
    - Creating new daily awakening sessions
    - Generating personalized quests based on readiness level
    - Returning session and quest information
    
    Args:
        request: Awakening action request containing user_id and readiness_level
        awakening_service: Injected AwakeningService instance
        
    Returns:
        AwakeningResponse: Complete awakening session and quest information
        
    Raises:
        HTTPException: 400 for validation errors, 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Processing awakening action for user {request.user_id} with readiness {request.readiness_level}")
        
        # Get or create daily session
        session_data = await awakening_service.get_or_create_daily_session(
            user_id=request.user_id,
            readiness_level=request.readiness_level
        )
        
        message = f"Daily awakening session ready with {len(session_data.get('quests', []))} quests"
        
        logger.info(f"Successfully processed awakening action for user {request.user_id}")
        
        return AwakeningResponse(
            success=True,
            message=message,
            data=session_data
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in awakening action: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in awakening action: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {request.user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in awakening action: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while processing awakening action"
            )


@router.post("/complete-quest/{quest_id}", response_model=AwakeningResponse, status_code=status.HTTP_200_OK)
async def complete_quest(
    quest_id: int,
    request: CompleteQuestRequest,
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> AwakeningResponse:
    """
    Complete a specific awakening quest.
    
    This endpoint handles:
    - Marking quests as completed
    - Awarding XP and rewards
    - Updating user progress
    
    Args:
        quest_id: ID of the quest to complete
        request: Quest completion request containing user_id and optional progress_data
        awakening_service: Injected AwakeningService instance
        
    Returns:
        AwakeningResponse: Quest completion result and updated progress
        
    Raises:
        HTTPException: 400 for validation errors, 404 for quest/user not found, 500 for server errors
    """
    try:
        logger.info(f"Completing quest {quest_id} for user {request.user_id}")
        
        # Complete the quest
        result = await awakening_service.complete_quest(
            user_id=request.user_id,
            quest_id=quest_id,
            progress_data=request.progress_data
        )
        
        message = f"Quest {quest_id} completed successfully"
        if result.get('xp_awarded'):
            message += f" - {result['xp_awarded']} XP awarded"
        
        logger.info(f"Successfully completed quest {quest_id} for user {request.user_id}")
        
        return AwakeningResponse(
            success=True,
            message=message,
            data=result
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in quest completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"Quest or user not found in quest completion: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quest {quest_id} or user {request.user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in quest completion: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while completing quest"
            )


@router.get("/status/{user_id}", response_model=AwakeningResponse, status_code=status.HTTP_200_OK)
async def get_awakening_status(
    user_id: int,
    include_quests: bool = True,
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> AwakeningResponse:
    """
    Get current awakening status for a user.
    
    This endpoint returns:
    - Current awakening session information
    - Quest progress and completion status
    - Streak information
    - Overall awakening progress
    
    Args:
        user_id: User's database ID
        include_quests: Whether to include detailed quest information
        awakening_service: Injected AwakeningService instance
        
    Returns:
        AwakeningResponse: Current awakening status and progress
        
    Raises:
        HTTPException: 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Getting awakening status for user {user_id}")
        
        # Get awakening progress
        status_data = await awakening_service.get_awakening_progress(
            user_id=user_id,
            include_quests=include_quests
        )
        
        if not status_data:
            message = "No awakening session found for today"
            status_data = {"session": None, "quests": [], "progress": {}}
        else:
            completed_quests = len([q for q in status_data.get('quests', []) if q.get('completed')])
            total_quests = len(status_data.get('quests', []))
            message = f"Awakening status: {completed_quests}/{total_quests} quests completed"
        
        logger.info(f"Successfully retrieved awakening status for user {user_id}")
        
        return AwakeningResponse(
            success=True,
            message=message,
            data=status_data
        )
        
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in awakening status: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in awakening status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving awakening status"
            )


@router.post("/reset/{user_id}", response_model=AwakeningResponse, status_code=status.HTTP_200_OK)
async def reset_awakening_session(
    user_id: int,
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> AwakeningResponse:
    """
    Reset the current awakening session for a user.
    
    This endpoint allows users to:
    - Reset their daily awakening session
    - Generate new quests
    - Start fresh with their awakening progress
    
    Args:
        user_id: User's database ID
        awakening_service: Injected AwakeningService instance
        
    Returns:
        AwakeningResponse: Reset confirmation and new session information
        
    Raises:
        HTTPException: 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Resetting awakening session for user {user_id}")
        
        # Reset the session
        result = await awakening_service.reset_daily_session(user_id=user_id)
        
        message = "Awakening session reset successfully"
        
        logger.info(f"Successfully reset awakening session for user {user_id}")
        
        return AwakeningResponse(
            success=True,
            message=message,
            data=result
        )
        
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in awakening reset: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in awakening reset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while resetting awakening session"
            )


@router.get("/history/{user_id}", response_model=AwakeningResponse, status_code=status.HTTP_200_OK)
async def get_awakening_history(
    user_id: int,
    limit: int = 10,
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> AwakeningResponse:
    """
    Get awakening history for a user.
    
    This endpoint returns:
    - Historical awakening sessions
    - Completion statistics
    - Streak information
    - Progress trends
    
    Args:
        user_id: User's database ID
        limit: Maximum number of historical sessions to return
        awakening_service: Injected AwakeningService instance
        
    Returns:
        AwakeningResponse: Historical awakening data
        
    Raises:
        HTTPException: 404 for user not found, 500 for server errors
    """
    try:
        logger.info(f"Getting awakening history for user {user_id} (limit: {limit})")
        
        # Get awakening history
        history_data = await awakening_service.get_awakening_history(
            user_id=user_id,
            limit=limit
        )
        
        message = f"Retrieved {len(history_data.get('sessions', []))} historical awakening sessions"
        
        logger.info(f"Successfully retrieved awakening history for user {user_id}")
        
        return AwakeningResponse(
            success=True,
            message=message,
            data=history_data
        )
        
    except Exception as e:
        if "not found" in str(e).lower():
            logger.warning(f"User not found in awakening history: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        else:
            logger.error(f"Unexpected error in awakening history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving awakening history"
            )


@router.get("/health", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def health_check(
    awakening_service: AwakeningService = Depends(get_awakening_service)
) -> Dict[str, Any]:
    """
    Health check endpoint for the awakening service.
    
    Returns:
        Dict[str, Any]: Service health status and basic metrics
    """
    try:
        # Basic health check - could be expanded with more detailed checks
        return {
            "service": "awakening",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc),
            "version": "v2"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service health check failed"
        )