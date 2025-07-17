"""
Awakening System API Routes
Handles awakening ritual, quest generation, and daily briefings
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
import asyncpg
from datetime import date, datetime

from api.dependencies import get_current_user, get_db_pool_optional, is_development_mode
from api.models.common import SuccessResponse, ErrorResponse
from api.models.awakening import (
    Awakening, AwakeningCreate, AwakeningResponse, 
    ReadinessLevel, AwakeningStatus, DailyBriefing
)
from features.awakening.logic.awakening_service import AwakeningService

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_awakening_status(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get today's awakening status for the current user"""
    
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return {
            "awakening_exists": False,
            "status": "pending",
            "readiness_level": None,
            "quest_count": 0,
            "completed_quests": 0,
            "total_xp_gained": 0,
            "mode": "development"
        }
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        awakening_service = AwakeningService(bot=None)  # TODO: Pass bot instance
        today_awakening = await awakening_service.get_today_awakening(user_id, conn)
        
        if not today_awakening:
            return {
                "awakening_exists": False,
                "status": "pending",
                "readiness_level": None,
                "quest_count": 0,
                "completed_quests": 0,
                "total_xp_gained": 0
            }
        
        return {
            "awakening_exists": True,
            "awakening_id": today_awakening["id"],
            "status": today_awakening["status"],
            "readiness_level": today_awakening["readiness_level"],
            "quest_count": today_awakening["quest_count"],
            "completed_quests": len(today_awakening["completed_quests"]),
            "total_quests": len(today_awakening["generated_quests"]),
            "total_xp_gained": today_awakening["total_xp_gained"],
            "awakened_at": today_awakening["awakened_at"],
            "completed_at": today_awakening["completed_at"]
        }

@router.post("/awaken", response_model=AwakeningResponse)
async def perform_awakening(
    readiness_level: ReadinessLevel,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Perform the daily awakening ritual and generate quests"""
    
    # Development mode: return mock awakening
    if is_development_mode() or db_pool is None:
        mock_quests = [
            {
                "id": 1,
                "title": "Shadow Strike: Push-ups",
                "description": "Standard protocol, operative. Execute with precision.\n\n**Strength Foundation**\n\nComplete 3 sets of 10 Push-ups. Focus on proper form.",
                "tier": 1,
                "movement": "Push-ups",
                "target_sets": 3,
                "target_reps": 10,
                "xp_reward": 25,
                "status": "available"
            }
        ]
        
        return AwakeningResponse(
            awakening=Awakening(
                id=1,
                user_id=current_user["user_id"],
                readiness_level=readiness_level,
                awakening_date=date.today(),
                status=AwakeningStatus.AWAKENED,
                generated_quests=[1],
                quest_count=1,
                awakened_at=datetime.utcnow()
            ),
            quests=mock_quests,
            readiness_effects={
                "difficulty_modifier": 1.0,
                "xp_modifier": 1.0,
                "description": "Development mode"
            },
            daily_briefing={
                "awakening_summary": "Development mode awakening",
                "quest_overview": ["Mock quest generated"],
                "readiness_impact": "Development testing",
                "motivation_message": "Testing the awakening system!"
            }
        )
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        try:
            awakening_service = AwakeningService(bot=None)  # TODO: Pass bot instance
            
            # Create awakening session and generate quests
            awakening_result = await awakening_service.create_awakening_session(
                user_id, readiness_level, conn
            )
            
            # Get daily briefing
            briefing = await awakening_service.get_daily_briefing(user_id, conn)
            
            # Get readiness effects for response
            readiness_effects = awakening_service._get_readiness_effects(readiness_level)
            
            return AwakeningResponse(
                awakening=Awakening(
                    id=awakening_result["awakening_id"],
                    user_id=user_id,
                    readiness_level=readiness_level,
                    awakening_date=date.today(),
                    status=AwakeningStatus.AWAKENED,
                    generated_quests=[q["id"] for q in awakening_result["quests"]],
                    quest_count=awakening_result["quest_count"],
                    awakened_at=datetime.fromisoformat(awakening_result["awakened_at"].replace('Z', '+00:00'))
                ),
                quests=awakening_result["quests"],
                readiness_effects={
                    "difficulty_modifier": readiness_effects.difficulty_modifier,
                    "xp_modifier": readiness_effects.xp_modifier,
                    "description": readiness_effects.description
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
    
    # Development mode: return mock quests
    if is_development_mode() or db_pool is None:
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
    
    user_id = current_user["user_id"]
    
    async with db_pool.acquire() as conn:
        awakening_service = AwakeningService(bot=None)
        today_awakening = await awakening_service.get_today_awakening(user_id, conn)
        
        if not today_awakening:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No awakening found for today. Please perform awakening ritual first."
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
        
        return [
            {
                "id": quest["id"],
                "title": quest["quest_data"]["title"],
                "description": quest["quest_data"]["description"],
                "tier": quest["tier"],
                "xp_reward": quest["xp_reward"],
                "status": quest["status"],
                "movement": quest["quest_data"]["movement"],
                "target_sets": quest["quest_data"]["target_sets"],
                "target_reps": quest["quest_data"]["target_reps"],
                "progress": quest["progress"]
            }
            for quest in quests
        ]

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