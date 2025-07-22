import asyncio
import logging
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_current_user, get_db_pool_optional
from api.models.awakening import (
    AwakeningActionRequest, 
    AwakeningHistory, 
    AwakeningStatusResponse
)
from api.models.user import UserProfile as User
from core.config import settings
from features.awakening.logic.awakening_service import AwakeningService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_awakening_service(
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
) -> AwakeningService:
    if settings.DEV_MODE:
        from features.awakening.logic.mock_awakening_service import (
            MockAwakeningService,
        )  # Moved import here

        logger.info("Using MockAwakeningService")
        return MockAwakeningService()
    if db_pool is None:
        raise HTTPException(
            status_code=503, detail="Database connection is not available"
        )
    logger.info("Using AwakeningService with database pool")
    return AwakeningService(db_pool)


@router.post("/action", response_model=AwakeningStatusResponse)
async def process_awakening_action(
    request: AwakeningActionRequest,
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    try:
        logger.info(
            f"Processing awakening action for user {current_user.user_id} with readiness {request.readiness_level}"
        )
        status = await service.process_awakening(
            current_user.user_id, request.readiness_level
        )
        return status
    except Exception as e:
        logger.exception(
            f"Error processing awakening action for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete_quest/{quest_id}", response_model=AwakeningStatusResponse)
async def complete_quest(
    quest_id: int,
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    try:
        logger.info(
            f"Completing quest {quest_id} for user {current_user.user_id}"
        )
        status = await service.complete_quest(current_user.user_id, quest_id)
        return status
    except Exception as e:
        logger.exception(
            f"Error completing quest {quest_id} for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily_briefing", response_model=AwakeningStatusResponse)
async def get_daily_briefing(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    try:
        logger.info(f"Fetching daily briefing for user {current_user.user_id}")
        status = await service.get_awakening_status(current_user.user_id)
        if not status or not status.get('active_session'):
            raise HTTPException(
                status_code=404, detail="No active awakening session found."
            )
        return status
    except Exception as e:
        logger.exception(
            f"Error fetching daily briefing for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=AwakeningHistory)
async def get_awakening_history(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        logger.info(f"Fetching awakening history for user {current_user.user_id}")
        history = await service.get_awakening_history(current_user.user_id, limit)
        return history
    except Exception as e:
        logger.exception(
            f"Error fetching awakening history for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AwakeningStatusResponse)
async def get_awakening_status(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
    include_quests: bool = Query(False),
):
    try:
        logger.info(f"Fetching awakening status for user {current_user.user_id}")
        status = await service.get_awakening_status(
            current_user.user_id, include_quests=include_quests
        )
        return status
    except Exception as e:
        logger.exception(
            f"Error fetching awakening status for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recover", response_model=AwakeningStatusResponse)
async def recover_session(
    current_user: User = Depends(get_current_user),
    service: AwakeningService = Depends(get_awakening_service),
):
    try:
        logger.info(f"Attempting to recover session for user {current_user.user_id}")
        status = await service.recover_session(current_user.user_id)
        return status
    except Exception as e:
        logger.exception(
            f"Error recovering session for user {current_user.user_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=f"Recovery failed: {str(e)}")