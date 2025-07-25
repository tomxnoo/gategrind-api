from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import asyncpg
from datetime import datetime

from api.models.common import SuccessResponse
from api.dependencies import get_db_pool_optional, get_current_user, is_development_mode

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
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
):
    """Log reps for a movement"""
    from datetime import datetime, timedelta
    
    # Development mode: return mock success with comprehensive data
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
                "completed_quests": [],  # Mock empty quest completions
                "weekly_completed": [],  # Mock empty weekly completions
                "leveled_up": False,     # Mock no level up
                "mode": "development"
            }
        )
    
    # Production mode: implement full logging logic
    try:
        user_id = current_user["user_id"]
        now = datetime.utcnow()
        
        # Import required modules
        from features.user.logic.user_data import load_user_data, save_user_data
        from features.user.logic.xp_engine import calculate_xp_for_movement, add_xp
        from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
        from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress
        from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
        
        # Load user data
        data = await load_user_data(user_id)
        
        # Check cooldown (2 minutes)
        COOLDOWN_MINUTES = 2
        last_log_str = data.get("cooldowns", {}).get(rep_log.movement)
        if last_log_str:
            last_time = datetime.fromisoformat(last_log_str)
            if now - last_time < timedelta(minutes=COOLDOWN_MINUTES):
                remaining = timedelta(minutes=COOLDOWN_MINUTES) - (now - last_time)
                minutes, seconds = divmod(int(remaining.total_seconds()), 60)
                raise HTTPException(
                    status_code=429, 
                    detail=f"Cooldown active! Try again in {minutes}m {seconds}s."
                )
        
        # Rep caps
        REP_CAPS = {
            "push_ups": 500,
            "pull_ups": 300,
            "squats": 400,
            "crunches": 500,
            "planks": 300,
            "knee_raises": 400,
            "shoulder_raises": 300,
            "bicep_curls": 300
        }
        
        # Update user stats
        stats = data.setdefault("log_stats", {})
        stats.setdefault(rep_log.movement, 0)
        rep_log_data = data.setdefault("rep_log", {})
        today_str = now.strftime("%Y-%m-%d")
        movement_key = rep_log.movement.lower().replace(" ", "").replace("-", "")
        rep_log_key = f"{movement_key}_{today_str}"
        
        # Calculate XP with caps
        cap = REP_CAPS.get(rep_log.movement, 500)
        total_today = stats[rep_log.movement]
        total_reps = rep_log.reps * rep_log.sets
        xp_earned = calculate_xp_for_movement(rep_log.movement, rep_log.reps)
        
        if total_today >= cap:
            xp_earned = int(xp_earned * 0.2)
        elif total_today + total_reps > cap:
            capped = total_today + total_reps - cap
            uncapped = total_reps - capped
            xp_uncapped = calculate_xp_for_movement(rep_log.movement, uncapped)
            xp_capped = int(calculate_xp_for_movement(rep_log.movement, capped) * 0.2)
            xp_earned = xp_uncapped + xp_capped
        
        # Update data
        stats[rep_log.movement] += total_reps
        rep_log_data[rep_log_key] = rep_log_data.get(rep_log_key, 0) + total_reps
        data.setdefault("cooldowns", {})[rep_log.movement] = now.isoformat()
        
        # Add XP
        xp_result = await add_xp(user_id, xp_earned)
        
        # Update quest progress
        completed_quests = await update_quest_progress(user_id, rep_log.movement, total_reps)
        
        # Update weekly progress (need to create a mock bot object)
        class MockBot:
            def __init__(self, db_pool):
                self.db_pool = db_pool
                self.redis = None  # Add redis attribute for compatibility
        
        bot = MockBot(db_pool)
        weekly_completed = await update_weekly_progress(user_id, bot, rep_log.movement, total_reps)
        
        # Save user data
        await save_user_data(user_id, data)
        
        # Invalidate cache
        await invalidate_user_json_cache(bot, user_id)
        await get_or_cache_user_json_data(bot, user_id)
        
        return SuccessResponse(
            message=f"Logged {total_reps} {rep_log.movement} reps!",
            data={
                "movement": rep_log.movement,
                "reps": rep_log.reps,
                "sets": rep_log.sets,
                "total_reps": total_reps,
                "xp_gained": xp_earned,
                "user_id": user_id,
                "completed_quests": completed_quests or [],
                "weekly_completed": weekly_completed or [],
                "leveled_up": xp_result.get("leveled_up", False),
                "new_level": xp_result.get("new_level"),
                "mode": "production"
            }
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions (like cooldown)
    except Exception as e:
        print(f"[ERROR] Failed to log reps: {e}")
        raise HTTPException(status_code=500, detail="Failed to log reps")

@router.get("/reps/history", response_model=List[RepLogEntry])
async def get_rep_history(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
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
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)
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
        from app.application.game_data.exercise_library import EXERCISE_LIBRARY
        
        movements = []
        for category in EXERCISE_LIBRARY.values():
            for progression in category.progressions:
                movements.append(progression.display_name)
        
        return sorted(movements)
        
    except Exception as e:
        print(f"[ERROR] Failed to get movements: {e}")
        return []

@router.get("/stats/summary", response_model=dict)
async def get_logging_stats(
    current_user: dict = Depends(get_current_user),
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
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