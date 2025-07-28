import asyncio
import logging
from typing import Optional, Dict, Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_pool_optional
from api.models.awakening import (
    AwakeningActionRequest, 
    AwakeningHistory, 
    AwakeningStatusResponse
)
from api.models.user import UserProfile as User
from app.infrastructure.database.session import get_async_session
from app.application.services.awakening_service import AwakeningService
from app.application.services.progression_service import ProgressionService
from features.awakening.logic.mock_awakening_service import MockAwakeningService
from core.config import settings
from api.deps import is_development_mode
import os

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_awakening_service(
    session: AsyncSession = Depends(get_async_session),
):
    """Get the awakening service - mock in development mode, real service in production."""
    # Check for development mode using both environment variables
    dev_mode = (
        is_development_mode() or 
        os.getenv("DEV_MODE", "false").lower() == "true" or
        settings.DEV_MODE
    )
    
    if dev_mode:
        logger.info("Using MockAwakeningService in development mode")
        return MockAwakeningService()
    else:
        logger.info("Using real AwakeningService in production mode")
        progression_service = ProgressionService(session)
        return AwakeningService(session, progression_service)


@router.post("/action", response_model=Dict[str, Any])
async def process_awakening_action(
    request: AwakeningActionRequest,
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    """Create a new daily awakening session with personalized quests."""
    try:
        logger.info(
            f"Processing awakening action for user {current_user.user_id} with readiness {request.readiness_level}"
        )
        
        # Create new daily session
        session = await service.create_daily_session(
            current_user.user_id, request.readiness_level
        )
        
        # Return session details
        return {
            "session_id": session.id,
            "session_date": session.session_date.isoformat(),
            "tier_level": session.tier_level,
            "status": session.status,
            "quest_count": len(session.quests),
            "quests": [
                {
                    "id": q.id,
                    "type": q.quest_type,
                    "target_movement": q.target_movement,
                    "target_reps": q.target_reps,
                    "target_time": q.target_time,
                    "target_distance": q.target_distance,
                    "difficulty": q.difficulty_level,
                    "status": q.status
                }
                for q in session.quests
            ]
        }
    except Exception as e:
        logger.exception(
            f"Error processing awakening action for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/complete_quest/{quest_id}", response_model=Dict[str, Any])
async def complete_quest(
    quest_id: int,
    progress_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    """Complete a specific awakening quest with progress data."""
    try:
        logger.info(
            f"Completing quest {quest_id} for user {current_user.user_id}"
        )
        result = await service.complete_quest(
            current_user.user_id, quest_id, progress_data
        )
        return result
    except Exception as e:
        logger.exception(
            f"Error completing quest {quest_id} for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/daily_briefing", response_model=Dict[str, Any])
async def get_daily_briefing(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    """Get the daily awakening briefing with current progress."""
    try:
        logger.info(f"Fetching daily briefing for user {current_user.user_id}")
        progress = await service.get_awakening_progress(current_user.user_id)
        
        if not progress.get("has_session"):
            return {
                "has_session": False,
                "message": "No awakening session found for today. Create one to begin your daily challenge.",
                "awakening_streak": progress.get("awakening_streak", 0),
                "can_create": True
            }
        
        return progress
    except Exception as e:
        logger.exception(
            f"Error fetching daily briefing for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=Dict[str, Any])
async def get_awakening_history(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
    limit: int = Query(10, ge=1, le=100),
):
    """Get awakening session history for the user."""
    try:
        logger.info(f"Fetching awakening history for user {current_user.user_id}")
        
        # For now, return basic history structure
        # This would be expanded with actual historical data queries
        return {
            "user_id": current_user.user_id,
            "total_sessions": 0,
            "completed_sessions": 0,
            "current_streak": 0,
            "sessions": []
        }
    except Exception as e:
        logger.exception(
            f"Error fetching awakening history for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_awakening_status(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
    include_quests: bool = Query(True),
):
    """Get current awakening status and progress."""
    try:
        logger.info(f"Fetching awakening status for user {current_user.user_id}")
        progress = await service.get_awakening_progress(current_user.user_id)
        return progress
    except Exception as e:
        logger.exception(
            f"Error fetching awakening status for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=Dict[str, Any])
async def reset_daily_session(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    """Reset today's awakening session with reduced difficulty."""
    try:
        logger.info(f"Resetting awakening session for user {current_user.user_id}")
        result = await service.reset_daily_session(current_user.user_id)
        return result
    except Exception as e:
        logger.exception(
            f"Error resetting session for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/recover", response_model=Dict[str, Any])
async def recover_session(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    """Attempt to recover an awakening session (placeholder for future implementation)."""
    try:
        logger.info(f"Attempting to recover session for user {current_user.user_id}")
        
        # For now, just return current status
        progress = await service.get_awakening_progress(current_user.user_id)
        return {
            "recovered": False,
            "message": "Session recovery not yet implemented",
            "current_status": progress
        }
    except Exception as e:
        logger.exception(
            f"Error recovering session for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=f"Recovery failed: {str(e)}")