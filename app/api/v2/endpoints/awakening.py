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
from typing import Dict, Any, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
import logging
import os

from app.application.services.awakening_service import AwakeningService
from app.application.services.awakening_admin_service import AwakeningAdminService
from app.infrastructure.database.session import get_async_session
from app.api.v2.dependencies.auth import get_current_user_id
# from app.api.dependencies.admin import require_admin
from features.awakening.logic.mock_awakening_service import MockAwakeningService
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

# Global mock service instance for development mode
_mock_service_instance = None

def get_awakening_service_dev() -> MockAwakeningService:
    """
    Get mock awakening service for development mode (singleton).
    """
    global _mock_service_instance
    if _mock_service_instance is None:
        print("[SINGLETON DEBUG] Creating new MockAwakeningService instance")
        _mock_service_instance = MockAwakeningService()
    else:
        print(f"[SINGLETON DEBUG] Reusing existing MockAwakeningService instance with {len(_mock_service_instance._sessions)} sessions")
    return _mock_service_instance

def get_awakening_service(db: AsyncSession = Depends(get_async_session)) -> Union[AwakeningService, MockAwakeningService]:
    """
    Get awakening service based on environment mode.
    """
    # Check if we're in development mode
    dev_mode = (
        os.getenv("DEVELOPMENT_MODE", "false").lower() == "true" or
        os.getenv("DEV_MODE", "false").lower() == "true"
    )
    
    if dev_mode:
        return _singleton.get_service()
    else:
        return AwakeningService(db)


@router.post("/action", response_model=AwakeningActionResponse)
async def create_awakening_session(
    request: AwakeningActionRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session)
) -> AwakeningActionResponse:
    """
    Create or retrieve today's awakening session for the user.
    
    Args:
        request: Contains user_id and readiness_level
        current_user: Authenticated user information
        awakening_service: Awakening service (mock for development)
        
    Returns:
        AwakeningActionResponse with session data and quests
        
    Raises:
        HTTPException: If user not found or invalid readiness level
    """
    try:
        # Initialize awakening service with database session
        awakening_service = AwakeningService(db)
        
        # Validate readiness level
        readiness_int = {"low": 3, "medium": 5, "high": 8}.get(request.readiness_level, 5)
        if not (1 <= readiness_int <= 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid readiness level"
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


@router.post("/quests/{quest_id}/complete", response_model=QuestCompletionResponse)
async def complete_quest(
    quest_id: int,
    request: QuestCompletionRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session)
) -> QuestCompletionResponse:
    """
    Complete a quest with user's movement progress.
    
    Args:
        quest_id: ID of the quest to complete
        request: Contains user progress data
        current_user_id: Authenticated user ID
        awakening_service: Awakening service (mock for development)
        
    Returns:
        QuestCompletionResponse with completion status and rewards
        
    Raises:
        HTTPException: If quest not found or insufficient progress
    """
    try:
        # Initialize awakening service
        awakening_service = AwakeningService(db)
        
        # Complete quest
        completion_data = await awakening_service.complete_quest(
            user_id=current_user_id,
            quest_id=quest_id,
            progress_data=request.dict()
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
    include_quests: bool = False,
    db: AsyncSession = Depends(get_async_session)
) -> AwakeningStatusResponse:
    """
    Get current awakening status for a user.
    
    Args:
        user_id: ID of the user
        include_quests: Whether to include quest data in the response
        awakening_service: Awakening service (mock for development)
        
    Returns:
        AwakeningStatusResponse with current session and progress
        
    Raises:
        HTTPException: If user not found
    """
    try:
        awakening_service = AwakeningService(db)
        # Get daily session for today
        today = date.today()
        session = await awakening_service.get_daily_session(user_id, today)
        
        if not session:
            status_data = {
                "status": "pending",
                "awakened": False,
                "quests_available": False,
                "readiness_level": None,
                "quests": [],
                "active_session": None,
            }
        else:
            # Build status response
            status_data = {
                "status": session.status,
                "awakened": True,
                "quests_available": True,
                "readiness_level": session.tier_level,
                "quest_count": len(session.quests),
                "completed_quests": sum(1 for q in session.quests if q.status == "completed"),
                "total_xp_gained": sum(q.xp_reward for q in session.quests if q.status == "completed"),
                "session_theme": "Shadow Training",
                "active_session": {
                    "user_id": session.user_id,
                    "awakening_date": session.session_date.isoformat(),
                    "readiness_level": session.tier_level,
                    "status": session.status,
                    "quest_count": len(session.quests),
                    "completed_quests": sum(1 for q in session.quests if q.status == "completed"),
                    "total_xp_gained": sum(q.xp_reward for q in session.quests if q.status == "completed"),
                    "awakened_at": session.created_at.isoformat(),
                },
            }
            
            if include_quests:
                status_data["quests"] = [
                    {
                        "id": q.id,
                        "title": q.title,
                        "description": q.description,
                        "type": q.quest_type,
                        "difficulty": q.difficulty,
                        "tier": q.tier,
                        "xp_reward": q.xp_reward,
                        "status": q.status,
                        "completed": q.status == "completed",
                        "movement_name": q.movement_name,
                        "target_reps": q.target_reps,
                        "target_sets": q.target_sets,
                        "progress": q.progress or {},
                        "completed_at": q.completed_at.isoformat() if q.completed_at else None,
                        "created_at": q.created_at.isoformat()
                    }
                    for q in session.quests
                ]
        
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
    current_user_id: int = Depends(get_current_user_id),
    db = Depends(get_async_session)
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
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session)
) -> AwakeningHistoryResponse:
    """
    Get awakening history for a user.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        current_user_id: Authenticated user ID
        awakening_service: Awakening service (mock for development)
        
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
    db: AsyncSession = Depends(get_async_session)
) -> AwakeningHealthResponse:
    """
    Get health status of the awakening system.
    
    Args:
        awakening_service: Awakening service (mock for development)
        
    Returns:
        AwakeningHealthResponse with system health metrics
    """
    try:
        # Return a simple health check response
        health_data = {
            "status": "healthy",
            "uptime": "100%",
            "environment": "production",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return AwakeningHealthResponse(**health_data)
        
    except Exception as e:
        logger.error(f"Error getting awakening system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )


# Administrative endpoints are disabled due to missing require_admin dependency
# To re-enable: Create app/api/dependencies/admin.py with require_admin function


@router.get("/quests", response_model=Dict[str, Any])
async def get_awakening_quests(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get awakening quests for the current user.
    
    Args:
        current_user_id: Authenticated user ID
        awakening_service: Awakening service (mock for development)
        
    Returns:
        Dict containing quest information
        
    Raises:
        HTTPException: If unable to retrieve quests
    """
    try:
        awakening_service = AwakeningService(db)
        # Get daily session for today
        today = date.today()
        session = await awakening_service.get_daily_session(current_user_id, today)
        
        if not session:
            return {
                "quests": [],
                "quest_count": 0,
                "completed_quests": 0,
                "awakened": False
            }
        
        quests = [
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "type": q.quest_type,
                "difficulty": q.difficulty,
                "tier": q.tier,
                "xp_reward": q.xp_reward,
                "status": q.status,
                "completed": q.status == "completed",
                "movement_name": q.movement_name,
                "target_reps": q.target_reps,
                "target_sets": q.target_sets,
            }
            for q in session.quests
        ]
        return {
            "quests": quests,
            "quest_count": len(session.quests),
            "completed_quests": sum(1 for q in session.quests if q.status == "completed"),
            "awakened": True
        }
        
    except Exception as e:
        logger.error(f"Error getting awakening quests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get awakening quests"
        )


@router.get("/daily-briefing", response_model=Dict[str, Any])
async def get_daily_briefing(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get daily awakening briefing for the current user.
    
    Args:
        current_user_id: Authenticated user ID
        awakening_service: Awakening service (mock for development)
        
    Returns:
        Dict containing briefing information
        
    Raises:
        HTTPException: If unable to retrieve briefing
    """
    try:
        awakening_service = AwakeningService(db)
        # Get daily session
        today = date.today()
        session = await awakening_service.get_daily_session(current_user_id, today)
        
        if session:
            readiness = session.tier_level
            quest_count = len(session.quests)
            briefing_data = {
                "awakening_summary": f"Your {readiness} intensity session is active with {quest_count} challenges.",
                "quest_summary": f"Complete all {quest_count} quests to maximize your daily XP gains.",
                "readiness_impact": f"Your {readiness} readiness level provides balanced quest difficulty and rewards.",
                "motivation_message": "Push beyond your limits. Every rep counts towards your shadow mastery!"
            }
        else:
            briefing_data = {
                "awakening_summary": "No active awakening session. Begin your daily ritual to unlock today's challenges.",
                "quest_summary": "Quests will be generated based on your chosen readiness level.",
                "readiness_impact": "Choose your readiness level wisely - it affects quest difficulty and XP rewards.",
                "motivation_message": "The shadow realm awaits. Are you ready to awaken your true potential?"
            }
        
        return briefing_data
        
    except Exception as e:
        logger.error(f"Error getting daily briefing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get daily briefing"
        )