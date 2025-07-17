from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import asyncpg

from api.models.quest import Quest
from api.models.common import SuccessResponse
from api.dependencies import get_db_pool_optional, get_current_user, is_development_mode

router = APIRouter()

def get_mock_daily_quests() -> List[dict]:
    """Get mock daily quests for development mode"""
    return [
        {
            "quest_id": 1,
            "name": "Morning Workout",
            "description": "Complete 30 push-ups and 20 squats",
            "type": "daily",
            "xp_reward": 50,
            "stat_rewards": {"STR": 25, "END": 15},
            "status": "available",
            "progress": 0,
            "max_progress": 1,
            "expires_at": "2024-12-31T23:59:59"
        },
        {
            "quest_id": 2,
            "name": "Study Session",
            "description": "Study for 2 hours",
            "type": "daily",
            "xp_reward": 75,
            "stat_rewards": {"TECH": 50},
            "status": "in_progress",
            "progress": 1,
            "max_progress": 2,
            "expires_at": "2024-12-31T23:59:59"
        },
        {
            "quest_id": 3,
            "name": "Meditation",
            "description": "Meditate for 15 minutes",
            "type": "daily",
            "xp_reward": 30,
            "stat_rewards": {"TECH": 35},
            "status": "completed",
            "progress": 1,
            "max_progress": 1,
            "expires_at": "2024-12-31T23:59:59"
        }
    ]

@router.get("/daily", response_model=List[dict])
async def get_daily_quests(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get user's daily quests"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return get_mock_daily_quests()
    
    # Production mode: use database
    try:
        # Import the existing quest logic
        from features.quests.logic.daily_quests.daily_quest_logic import get_today_quests
        
        # Create a mock bot object with db_pool
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
                self.redis = None  # Add redis attribute for compatibility
        
        bot = MockBot(db_pool)
        quests = await get_today_quests(current_user["user_id"], bot)
        
        # Return the quests as-is for now
        # Later we'll transform them to match our Pydantic models
        return quests if quests else []
        
    except Exception as e:
        print(f"[ERROR] Failed to get daily quests: {e}")
        return []

@router.post("/daily/{quest_id}/activate", response_model=SuccessResponse)
async def activate_daily_quest(
    quest_id: int,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Activate a daily quest"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message="Quest activated successfully (development mode)",
            data={"quest_id": quest_id, "user_id": current_user["user_id"], "mode": "development"}
        )
    
    # Production mode: use database
    try:
        from features.quests.logic.daily_quests.daily_quest_logic import activate_quest
        
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        success = await activate_quest(current_user["user_id"], quest_id, bot)
        
        if success:
            return SuccessResponse(
                message="Quest activated successfully",
                data={"quest_id": quest_id, "user_id": current_user["user_id"]}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to activate quest")
            
    except Exception as e:
        print(f"[ERROR] Failed to activate quest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/daily/{quest_id}/complete", response_model=SuccessResponse)
async def complete_daily_quest(
    quest_id: int,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Complete a daily quest"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        return SuccessResponse(
            message="Quest completed successfully! (development mode)",
            data={
                "quest_id": quest_id, 
                "user_id": current_user["user_id"], 
                "xp_gained": 50,
                "stat_gains": {"STR": 25, "END": 15},
                "mode": "development"
            }
        )
    
    # Production mode: use database
    try:
        from features.quests.logic.daily_quests.daily_quest_logic import complete_quest
        
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        result = await complete_quest(current_user["user_id"], quest_id, bot)
        
        if result:
            return SuccessResponse(
                message="Quest completed successfully!",
                data={"quest_id": quest_id, "user_id": current_user["user_id"], "rewards": result}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to complete quest")
            
    except Exception as e:
        print(f"[ERROR] Failed to complete quest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/weekly", response_model=List[dict])
async def get_weekly_quests(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Get user's weekly quests"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return [
            {
                "quest_id": 101,
                "name": "Weekly Fitness Goal",
                "description": "Complete 5 workout sessions this week",
                "type": "weekly",
                "xp_reward": 200,
                "stat_rewards": {"STR": 100, "END": 75},
                "status": "in_progress",
                "progress": 3,
                "max_progress": 5,
                "expires_at": "2024-12-31T23:59:59"
            }
        ]
    
    # Production mode: placeholder for weekly quest logic
    return []

@router.get("/history", response_model=List[dict])
async def get_quest_history(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
    limit: int = 10
):
    """Get user's quest completion history"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        return [
            {
                "quest_id": 5,
                "name": "Yesterday's Challenge",
                "type": "daily",
                "completed_at": "2024-12-30T18:30:00",
                "xp_gained": 75,
                "stat_gains": {"STR": 30, "TECH": 20}
            },
            {
                "quest_id": 4,
                "name": "Morning Routine",
                "type": "daily", 
                "completed_at": "2024-12-30T08:15:00",
                "xp_gained": 50,
                "stat_gains": {"END": 25, "TECH": 15}
            }
        ]
    
    # Production mode: use database
    return []