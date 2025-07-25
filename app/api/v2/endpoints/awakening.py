"""
Awakening System API Endpoints

Provides REST API endpoints for the awakening system including:
- Daily session management
- Quest completion
- Progress tracking
- Administrative functions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.application.services.awakening_service import AwakeningService
from app.application.services.awakening_admin_service import AwakeningAdminService
from app.infrastructure.database.session import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.admin import require_admin
from app.api.v2.schemas.awakening import (
    AwakeningActionRequest,
    AwakeningActionResponse,
    QuestCompletionRequest,
    QuestCompletionResponse,
    AwakeningStatusResponse,
    AwakeningHistoryResponse,
    AwakeningResetResponse,
    AwakeningHealthResponse,
    AdminResetRequest,
    AdminProgressAdjustmentRequest,
    SystemStatsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/awakening", tags=["awakening"])


@router.post("/action", response_model=AwakeningActionResponse)
async def create_awakening_session(
    request: AwakeningActionRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
) -> AwakeningActionResponse:
    """
    Create or retrieve today's awakening session for the user.
    
    Args:
        request: Contains user_id and readiness_level
        current_user: Authenticated user information
        db: Database session
        
    Returns:
        AwakeningActionResponse with session data and quests
        
    Raises:
        HTTPException: If user not found or invalid readiness level
    """
    try:
        awakening_service = AwakeningService(db)
        
        # Validate readiness level
        if not (1 <= request.readiness_level <= 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Readiness level must be between 1 and 10"
            )
        
        # Get or create daily session
        session_data = await awakening_service.get_or_create_daily_session(
            user_id=request.user_id,
            readiness_level=request.readiness_level
        )
        
        return AwakeningActionResponse(**session_data)
        
    except ValueError as e:
        logger.error(f"Validation error in create_awakening_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating awakening session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create awakening session"
        )


@router.post("/complete-quest/{quest_id}", response_model=QuestCompletionResponse)
async def complete_quest(
    quest_id: int,
    request: QuestCompletionRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
) -> QuestCompletionResponse:
    """
    Complete a quest with user's movement progress.
    
    Args:
        quest_id: ID of the quest to complete
        request: Contains user progress data
        current_user: Authenticated user information
        db: Database session
        
    Returns:
        QuestCompletionResponse with completion status and rewards
        
    Raises:
        HTTPException: If quest not found or insufficient progress
    """
    try:
        awakening_service = AwakeningService(db)
        
        completion_data = await awakening_service.complete_quest(
            quest_id=quest_id,
            user_progress=request.progress_data
        )
        
        return QuestCompletionResponse(**completion_data)
        
    except ValueError as e:
        logger.error(f"Validation error in complete_quest: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing quest {quest_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete quest"
        )


@router.get("/status/{user_id}", response_model=AwakeningStatusResponse)
async def get_awakening_status(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
) -> AwakeningStatusResponse:
    """
    Get current awakening status for a user.
    
    Args:
        user_id: ID of the user
        current_user: Authenticated user information
        db: Database session
        
    Returns:
        AwakeningStatusResponse with current session and progress
        
    Raises:
        HTTPException: If user not found
    """
    try:
        awakening_service = AwakeningService(db)
        
        status_data = await awakening_service.get_awakening_status(user_id)
        
        return AwakeningStatusResponse(**status_data)
        
    except Exception as e:
        logger.error(f"Error getting awakening status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get awakening status"
        )


@router.post("/reset/{user_id}", response_model=AwakeningResetResponse)
async def reset_daily_session(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
) -> AwakeningResetResponse:
    """
    Reset today's awakening session for a user.
    
    Args:
        user_id: ID of the user
        current_user: Authenticated user information
        db: Database session
        
    Returns:
        AwakeningResetResponse with new session data
        
    Raises:
        HTTPException: If user not found or no session to reset
    """
    try:
        awakening_service = AwakeningService(db)
        
        reset_data = await awakening_service.reset_daily_session(user_id)
        
        return AwakeningResetResponse(**reset_data)
        
    except ValueError as e:
        logger.error(f"Validation error in reset_daily_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resetting daily session for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset daily session"
        )


@router.get("/history/{user_id}", response_model=AwakeningHistoryResponse)
async def get_awakening_history(
    user_id: int,
    limit: Optional[int] = 30,
    offset: Optional[int] = 0,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
) -> AwakeningHistoryResponse:
    """
    Get awakening history for a user.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        current_user: Authenticated user information
        db: Database session
        
    Returns:
        AwakeningHistoryResponse with historical session data
        
    Raises:
        HTTPException: If user not found
    """
    try:
        awakening_service = AwakeningService(db)
        
        history_data = await awakening_service.get_awakening_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return AwakeningHistoryResponse(**history_data)
        
    except Exception as e:
        logger.error(f"Error getting awakening history for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get awakening history"
        )


@router.get("/health", response_model=AwakeningHealthResponse)
async def get_awakening_health(
    db = Depends(get_db)
) -> AwakeningHealthResponse:
    """
    Get health status of the awakening system.
    
    Args:
        db: Database session
        
    Returns:
        AwakeningHealthResponse with system health metrics
    """
    try:
        awakening_service = AwakeningService(db)
        
        health_data = await awakening_service.get_system_health()
        
        return AwakeningHealthResponse(**health_data)
        
    except Exception as e:
        logger.error(f"Error getting awakening system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )


# Administrative endpoints
@router.post("/admin/reset/{user_id}", response_model=AwakeningResetResponse)
async def admin_reset_user_session(
    user_id: int,
    request: AdminResetRequest,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
) -> AwakeningResetResponse:
    """
    Administrative reset of user's awakening session.
    
    Args:
        user_id: ID of the user
        request: Contains reset options and reason
        current_user: Authenticated admin user
        db: Database session
        
    Returns:
        AwakeningResetResponse with reset confirmation
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    try:
        admin_service = AwakeningAdminService(db)
        
        reset_data = await admin_service.manual_reset_user_session(
            user_id=user_id,
            admin_id=current_user["id"],
            reason=request.reason,
            reset_streak=request.reset_streak,
            reset_progress=request.reset_progress
        )
        
        return AwakeningResetResponse(**reset_data)
        
    except ValueError as e:
        logger.error(f"Validation error in admin_reset_user_session: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in admin reset for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user session"
        )


@router.post("/admin/adjust-progress/{user_id}")
async def admin_adjust_user_progress(
    user_id: int,
    request: AdminProgressAdjustmentRequest,
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
) -> JSONResponse:
    """
    Administrative adjustment of user's awakening progress.
    
    Args:
        user_id: ID of the user
        request: Contains progress adjustments and reason
        current_user: Authenticated admin user
        db: Database session
        
    Returns:
        JSONResponse with adjustment confirmation
        
    Raises:
        HTTPException: If user not found or unauthorized
    """
    try:
        admin_service = AwakeningAdminService(db)
        
        await admin_service.adjust_user_progress(
            user_id=user_id,
            admin_id=current_user["id"],
            adjustments=request.adjustments,
            reason=request.reason
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "User progress adjusted successfully",
                "user_id": user_id,
                "adjusted_by": current_user["id"],
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error in admin_adjust_user_progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adjusting progress for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust user progress"
        )


@router.get("/admin/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: dict = Depends(require_admin),
    db = Depends(get_db)
) -> SystemStatsResponse:
    """
    Get system-wide awakening statistics.
    
    Args:
        current_user: Authenticated admin user
        db: Database session
        
    Returns:
        SystemStatsResponse with system metrics
        
    Raises:
        HTTPException: If unauthorized
    """
    try:
        admin_service = AwakeningAdminService(db)
        
        stats_data = await admin_service.get_system_stats()
        
        return SystemStatsResponse(**stats_data)
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system statistics"
        )