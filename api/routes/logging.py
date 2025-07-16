from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import asyncpg
from datetime import datetime

from api.models.common import SuccessResponse
from api.dependencies import get_db_pool, get_current_user, is_development_mode

router = APIRouter()

class RepLogRequest(BaseModel):
    movement: str
    reps: int
    sets: int = 1
    notes: Optional[str] = None

class RepLogEntry(BaseModel):
    log_id: int
    movement: str
    reps: int
    sets: int
    total_reps: int
    notes: Optional[str]
    logged_at: datetime
    xp_gained: int
    stat_gains: dict

def get_mock_rep_history() -> List[RepLogEntry]:
    """Get mock rep history for development mode"""
    return [
        RepLogEntry(
            log_id=1,
            movement="Push-ups",
            reps=15,
            sets=3,
            total_reps=45,
            notes="Felt strong today!",
            logged_at=datetime.now(),
            xp_gained=25,
            stat_gains={"STR": 15, "END": 10}
        ),
        RepLogEntry(
            log_id=2,
            movement="Pull-ups",
            reps=8,
            sets=2,
            total_reps=16,
            notes="Working on form",
            logged_at=datetime.now(),
            xp_gained=30,
            stat_gains={"STR": 20, "TECH": 10}
        )
    ]

@router.post("/reps", response_model=SuccessResponse)
async def log_reps(
    rep_log: RepLogRequest,
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Log reps for a movement"""
    # Development mode: return mock success
    if is_development_mode() or db_pool is None:
        total_reps = rep_log.reps * rep_log.sets
        xp_gained = total_reps * 2  # Mock XP calculation
        
        # Mock stat gains based on movement type
        stat_gains = {}
        movement_lower = rep_log.movement.lower()
        if "push" in movement_lower:
            stat_gains = {"STR": total_reps, "END": total_reps // 2}
        elif "pull" in movement_lower:
            stat_gains = {"STR": total_reps, "TECH": total_reps // 3}
        elif "squat" in movement_lower or "lunge" in movement_lower:
            stat_gains = {"STR": total_reps // 2, "END": total_reps}
        else:
            stat_gains = {"STR": total_reps // 2, "END": total_reps // 2}
        
        return SuccessResponse(
            message=f"Logged {total_reps} {rep_log.movement} reps! (development mode)",
            data={
                "movement": rep_log.movement,
                "reps": rep_log.reps,
                "sets": rep_log.sets,
                "total_reps": total_reps,
                "xp_gained": xp_gained,
                "stat_gains": stat_gains,
                "user_id": current_user["user_id"],
                "mode": "development"
            }
        )
    
    # Production mode: use database and existing logging logic
    try:
        # Import existing logging logic
        from features.logging.cog import process_rep_log
        
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
        
        bot = MockBot(db_pool)
        result = await process_rep_log(
            bot, 
            current_user["user_id"], 
            rep_log.movement, 
            rep_log.reps,
            rep_log.sets,
            rep_log.notes
        )
        
        return SuccessResponse(
            message=f"Logged {rep_log.reps * rep_log.sets} {rep_log.movement} reps!",
            data=result
        )
        
    except Exception as e:
        print(f"[ERROR] Failed to log reps: {e}")
        raise HTTPException(status_code=500, detail="Failed to log reps")

@router.get("/reps/history", response_model=List[RepLogEntry])
async def get_rep_history(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool),
    limit: int = 20,
    movement: Optional[str] = None
):
    """Get user's rep logging history"""
    # Development mode: return mock data
    if is_development_mode() or db_pool is None:
        mock_history = get_mock_rep_history()
        if movement:
            mock_history = [entry for entry in mock_history if movement.lower() in entry.movement.lower()]
        return mock_history[:limit]
    
    # Production mode: use database
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT log_id, movement, reps, sets, notes, logged_at, xp_gained, stat_gains
                FROM rep_logs 
                WHERE user_id = $1
            """
            params = [current_user["user_id"]]
            
            if movement:
                query += " AND movement ILIKE $2"
                params.append(f"%{movement}%")
            
            query += " ORDER BY logged_at DESC LIMIT $" + str(len(params) + 1)
            params.append(limit)
            
            rows = await conn.fetch(query, *params)
            
            return [
                RepLogEntry(
                    log_id=row["log_id"],
                    movement=row["movement"],
                    reps=row["reps"],
                    sets=row["sets"],
                    total_reps=row["reps"] * row["sets"],
                    notes=row["notes"],
                    logged_at=row["logged_at"],
                    xp_gained=row["xp_gained"],
                    stat_gains=row["stat_gains"] or {}
                )
                for row in rows
            ]
            
    except Exception as e:
        print(f"[ERROR] Failed to get rep history: {e}")
        return []

@router.get("/movements", response_model=List[str])
async def get_available_movements(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Get list of available movements for logging"""
    # Development mode: return mock movements
    if is_development_mode() or db_pool is None:
        return [
            "Push-ups",
            "Pull-ups", 
            "Squats",
            "Lunges",
            "Pike Push-ups",
            "Diamond Push-ups",
            "Lateral Raises",
            "Plank",
            "Burpees",
            "Mountain Climbers"
        ]
    
    # Production mode: get from exercise library
    try:
        # Import exercise library
        from features.quests.logic.daily_quests.exercise_library import EXERCISE_LIBRARY
        
        movements = []
        for category in EXERCISE_LIBRARY.values():
            for exercise in category:
                movements.append(exercise["name"])
        
        return sorted(movements)
        
    except Exception as e:
        print(f"[ERROR] Failed to get movements: {e}")
        return []

@router.get("/stats/summary", response_model=dict)
async def get_logging_stats(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool),
    days: int = 7
):
    """Get user's logging statistics summary"""
    # Development mode: return mock stats
    if is_development_mode() or db_pool is None:
        return {
            "total_reps": 450,
            "total_sets": 32,
            "total_workouts": 5,
            "favorite_movement": "Push-ups",
            "streak_days": 3,
            "xp_gained": 890,
            "period_days": days,
            "daily_average": 90,
            "mode": "development"
        }
    
    # Production mode: calculate from database
    try:
        async with db_pool.acquire() as conn:
            # Get stats for the specified period
            query = """
                SELECT 
                    SUM(reps * sets) as total_reps,
                    SUM(sets) as total_sets,
                    COUNT(DISTINCT DATE(logged_at)) as total_workouts,
                    SUM(xp_gained) as total_xp,
                    movement,
                    COUNT(*) as movement_count
                FROM rep_logs 
                WHERE user_id = $1 
                AND logged_at >= NOW() - INTERVAL '%s days'
                GROUP BY movement
                ORDER BY movement_count DESC
            """
            
            rows = await conn.fetch(query, current_user["user_id"], days)
            
            if not rows:
                return {"message": "No logging data found for this period"}
            
            total_reps = sum(row["total_reps"] or 0 for row in rows)
            total_sets = sum(row["total_sets"] or 0 for row in rows)
            total_workouts = max(row["total_workouts"] or 0 for row in rows)
            total_xp = sum(row["total_xp"] or 0 for row in rows)
            favorite_movement = rows[0]["movement"] if rows else "None"
            
            return {
                "total_reps": total_reps,
                "total_sets": total_sets,
                "total_workouts": total_workouts,
                "favorite_movement": favorite_movement,
                "xp_gained": total_xp,
                "period_days": days,
                "daily_average": total_reps // max(days, 1)
            }
            
    except Exception as e:
        print(f"[ERROR] Failed to get logging stats: {e}")
        return {"error": "Failed to calculate stats"}