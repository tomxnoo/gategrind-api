"""
Awakening System API Routes
Handles awakening ritual, quest generation, and daily briefings
"""

import sentry_sdk
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import asyncpg

from api.dependencies import get_current_user, get_db_pool_optional, is_development_mode
from api.models.awakening import (
    ReadinessLevel, AwakeningCreate, AwakeningResponse, 
    DailyBriefing
)
from api.models.common import SuccessResponse
from features.awakening.logic.awakening_service import AwakeningService
from core.config import QUEST_THEMES, MOVEMENT_DATA

router = APIRouter(tags=["awakening"])

@router.get("/status", response_model=Dict[str, Any])
async def get_awakening_status(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get current awakening status for the user"""
    
    # Development mode: return mock status
    if is_development_mode() or db_pool is None:
        return {
            "status": "pending",
            "awakened": False,
            "quests_available": False,
            "readiness_level": None,
            "quest_count": 0,
            "quests": [],
            "mode": "development"
        }
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        awakening_service = AwakeningService(bot=None)
        status_data = await awakening_service.get_awakening_status(user_id, conn)
        return status_data

class AwakeningRequest(BaseModel):
    """Request model for awakening ritual"""
    readiness_level: ReadinessLevel

@router.post("/awaken", response_model=AwakeningResponse)
async def perform_awakening(
    request: AwakeningRequest,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Perform daily awakening ritual and generate quests"""
    
    # Development mode: return mock awakening
    if is_development_mode() or db_pool is None:
        from api.models.awakening import Awakening, AwakeningStatus
        mock_awakening = Awakening(
            id=1,
            user_id=current_user["user_id"],
            readiness_level=request.readiness_level,
            awakening_date=date.today(),
            status=AwakeningStatus.AWAKENED,
            quest_count=3,
            awakened_at=datetime.utcnow()
        )
        
        return AwakeningResponse(
            awakening=mock_awakening,
            quests=[
                {
                    "id": 1,
                    "title": "Shadow Strike: Push-ups",
                    "description": "Complete 3 sets of 10 Push-ups",
                    "tier": 1,
                    "xp_reward": 25,
                    "status": "available"
                }
            ],
            readiness_effects={
                "difficulty_modifier": 1.0,
                "xp_modifier": 1.0,
                "description": "Development mode"
            },
            daily_briefing={
                "awakening_summary": "Development awakening completed",
                "quest_overview": ["Mock quest for testing"],
                "readiness_impact": "Development testing",
                "motivation_message": "Testing the system!",
                "progress_highlights": {}
            }
        )
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        try:
            awakening_service = AwakeningService(bot=None)
            
            # Create awakening session and generate quests
            result = await awakening_service.create_awakening_session(
                user_id, request.readiness_level, conn
            )
            
            # Get daily briefing
            briefing = await awakening_service.get_daily_briefing(user_id, conn)
            
            # Create response model
            from api.models.awakening import Awakening, AwakeningStatus
            awakening = Awakening(
                id=result["awakening_id"],
                user_id=user_id,
                readiness_level=request.readiness_level,
                awakening_date=date.today(),
                status=AwakeningStatus.AWAKENED,
                quest_count=result["quest_count"],
                generated_quests=[q["id"] for q in result["quests"]],
                awakened_at=datetime.fromisoformat(result["awakened_at"].replace('Z', '+00:00'))
            )
            
            return AwakeningResponse(
                awakening=awakening,
                quests=result["quests"],
                readiness_effects={
                    "difficulty_modifier": 1.0,  # This should come from readiness effects
                    "xp_modifier": 1.0,
                    "description": f"{request.readiness_level.value} energy level"
                },
                daily_briefing=briefing
            )
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to perform awakening: {str(e)}"
            )

@router.get("/quests", response_model=List[Dict[str, Any]])
async def get_awakening_quests(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get today's awakening quests for the current user"""
    
    user_id = current_user["user_id"]
    
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("api_endpoint", "get_awakening_quests")
        scope.set_context("user", {"user_id": user_id})
        scope.set_context("request", {"endpoint": "/awakening/quests"})
    
    sentry_sdk.add_breadcrumb(
        message=f"API: Getting awakening quests for user {user_id}",
        level="info",
        category="api"
    )
    
    # Development mode: return mock quests
    if is_development_mode() or db_pool is None:
        sentry_sdk.add_breadcrumb(
            message="API: Returning mock quests (development mode)",
            level="info",
            category="api"
        )
        return [
            {
                "id": 1,
                "title": "Shadow Strike: Push-ups",
                "description": "Complete 3 sets of 10 Push-ups",
                "tier": 1,
                "xp_reward": 25,
                "status": "available",
                "progress": {"current_sets": 0, "current_reps": 0, "completed": False}
            }
        ]
    
    try:
        async with db_pool.acquire() as conn:
            awakening_service = AwakeningService(bot=None)
            today_awakening = await awakening_service.get_today_awakening(user_id, conn)
            
            if not today_awakening:
                sentry_sdk.add_breadcrumb(
                    message=f"API: No awakening found for user {user_id} today",
                    level="warning",
                    category="api"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No awakening found for today. Please perform awakening ritual first."
                )
            
            sentry_sdk.add_breadcrumb(
                message=f"API: Found awakening session {today_awakening['id']} for user {user_id}",
                level="info",
                category="api"
            )
            
            # Get quest details
            quests = await conn.fetch(
                """
                SELECT * FROM awakening_quests 
                WHERE awakening_session_id = $1
                ORDER BY id
                """,
                today_awakening["id"]
            )
            
            sentry_sdk.add_breadcrumb(
                message=f"API: Retrieved {len(quests)} raw quests from database",
                level="info",
                category="database"
            )
            
            # Log raw quest data for debugging
            if quests:
                sample_quest = dict(quests[0])
                sentry_sdk.add_breadcrumb(
                    message=f"API: Sample raw quest data: {sample_quest}",
                    level="info",
                    category="quest_data"
                )
            
            # Transform quest data for API response
            formatted_quests = []
            for quest in quests:
                try:
                    quest_dict = dict(quest)
                    quest_data = quest_dict["quest_data"]
                    
                    # Ensure quest_data is a dict (it might be JSON string)
                    if isinstance(quest_data, str):
                        import json
                        quest_data = json.loads(quest_data)
                    
                    formatted_quest = {
                        "id": quest_dict["id"],
                        "title": quest_data.get("title", "Unknown Quest"),
                        "description": quest_data.get("description", "No description"),
                        "tier": quest_dict["tier"],
                        "xp_reward": quest_dict["xp_reward"],
                        "status": quest_dict["status"],
                        "movement": quest_data.get("movement", "Unknown"),
                        "target_sets": quest_data.get("target_sets", 1),
                        "target_reps": quest_data.get("target_reps", 1),
                        "progress": quest_data.get("progress", {"current_sets": 0, "current_reps": 0, "completed": False})
                    }
                    
                    formatted_quests.append(formatted_quest)
                    
                    sentry_sdk.add_breadcrumb(
                        message=f"API: Formatted quest {quest_dict['id']}: {formatted_quest}",
                        level="info",
                        category="quest_formatting"
                    )
                    
                except Exception as format_error:
                    sentry_sdk.capture_exception(format_error)
                    sentry_sdk.add_breadcrumb(
                        message=f"API: Error formatting quest {quest.get('id', 'unknown')}: {format_error}",
                        level="error",
                        category="quest_formatting"
                    )
                    # Continue with other quests
                    continue
            
            sentry_sdk.add_breadcrumb(
                message=f"API: Successfully formatted {len(formatted_quests)} quests for response",
                level="info",
                category="api"
            )
            
            return formatted_quests
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.add_breadcrumb(
            message=f"API: Unexpected error in get_awakening_quests: {e}",
            level="error",
            category="api"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve quests: {str(e)}"
        )

@router.get("/debug/quests", response_model=Dict[str, Any])
async def debug_awakening_quests(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Debug endpoint to see raw quest data structure"""
    
    user_id = current_user["user_id"]
    
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("api_endpoint", "debug_awakening_quests")
        scope.set_context("user", {"user_id": user_id})
    
    sentry_sdk.add_breadcrumb(
        message=f"DEBUG API: Getting raw quest data for user {user_id}",
        level="info",
        category="debug"
    )
    
    if is_development_mode() or db_pool is None:
        return {
            "mode": "development",
            "message": "Database not available in development mode",
            "mock_data": True
        }
    
    try:
        async with db_pool.acquire() as conn:
            awakening_service = AwakeningService(bot=None)
            today_awakening = await awakening_service.get_today_awakening(user_id, conn)
            
            if not today_awakening:
                return {
                    "error": "No awakening found for today",
                    "user_id": user_id,
                    "date": date.today().isoformat()
                }
            
            # Get raw quest data
            quests = await conn.fetch(
                """
                SELECT id, awakening_session_id, quest_data, tier, xp_reward, 
                       status, progress, completed_at, created_at, updated_at
                FROM awakening_quests 
                WHERE awakening_session_id = $1
                ORDER BY id
                """,
                today_awakening["id"]
            )
            
            debug_data = {
                "awakening_session": today_awakening,
                "quest_count": len(quests),
                "raw_quests": [],
                "configuration": {
                    "quest_themes_keys": list(QUEST_THEMES.keys()) if QUEST_THEMES else None,
                    "movement_data_count": len(MOVEMENT_DATA) if MOVEMENT_DATA else 0,
                    "sample_movement": list(MOVEMENT_DATA.keys())[:3] if MOVEMENT_DATA else None
                }
            }
            
            for quest in quests:
                quest_dict = dict(quest)
                debug_data["raw_quests"].append({
                    "id": quest_dict["id"],
                    "quest_data": quest_dict["quest_data"],
                    "quest_data_type": type(quest_dict["quest_data"]).__name__,
                    "tier": quest_dict["tier"],
                    "xp_reward": quest_dict["xp_reward"],
                    "status": quest_dict["status"],
                    "progress": quest_dict["progress"],
                    "progress_type": type(quest_dict["progress"]).__name__,
                    "created_at": quest_dict["created_at"].isoformat() if quest_dict["created_at"] else None
                })
            
            sentry_sdk.add_breadcrumb(
                message=f"DEBUG API: Returning debug data with {len(quests)} quests",
                level="info",
                category="debug"
            )
            
            return debug_data
            
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {
            "error": f"Debug endpoint failed: {str(e)}",
            "user_id": user_id,
            "exception_type": type(e).__name__
        }

@router.post("/quests/{quest_id}/complete", response_model=SuccessResponse)
async def complete_awakening_quest(
    quest_id: int,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Mark an awakening quest as completed"""
    
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message="Quest completed successfully (development mode)",
            data={
                "quest_id": quest_id,
                "xp_gained": 25,
                "awakening_completed": False,
                "mode": "development"
            }
        )
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        try:
            awakening_service = AwakeningService(bot=None)
            result = await awakening_service.complete_awakening_quest(user_id, quest_id, conn)
            
            return SuccessResponse(
                message="Quest completed successfully!",
                data=result
            )
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete quest: {str(e)}"
            )

@router.get("/briefing", response_model=DailyBriefing)
async def get_daily_briefing(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get daily briefing after awakening"""
    
    # Development mode: return mock briefing
    if is_development_mode() or db_pool is None:
        return DailyBriefing(
            awakening_summary="Development mode awakening with 1 quest",
            quest_overview=["Mock quest for testing"],
            readiness_impact="Development testing mode",
            motivation_message="Testing the awakening system!",
            progress_highlights={
                "weekly_completions": 0,
                "weekly_xp": 0,
                "consistency_streak": 0,
                "average_readiness": "standard"
            }
        )
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        awakening_service = AwakeningService(bot=None)
        briefing = await awakening_service.get_daily_briefing(user_id, conn)
        
        if "error" in briefing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=briefing["error"]
            )
        
        return DailyBriefing(**briefing)

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_awakening_history(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
    limit: int = 7
):
    """Get user's awakening history"""
    
    # Development mode: return mock history
    if is_development_mode() or db_pool is None:
        return [
            {
                "date": date.today().isoformat(),
                "readiness_level": "standard",
                "status": "awakened",
                "quest_count": 3,
                "completed_quests": 0,
                "total_xp_gained": 0
            }
        ]
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        history = await conn.fetch(
            """
            SELECT awakening_date, readiness_level, status, quest_count, 
                   array_length(completed_quests, 1) as completed_count,
                   total_xp_gained
            FROM awakening_sessions 
            WHERE user_id = $1 
            ORDER BY awakening_date DESC 
            LIMIT $2
            """,
            user_id, limit
        )
        
        return [
            {
                "date": record["awakening_date"].isoformat(),
                "readiness_level": record["readiness_level"],
                "status": record["status"],
                "quest_count": record["quest_count"],
                "completed_quests": record["completed_count"] or 0,
                "total_xp_gained": record["total_xp_gained"]
            }
            for record in history
        ]