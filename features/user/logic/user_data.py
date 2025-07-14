import json
import os
import datetime
from pathlib import Path
from datetime import datetime, timedelta

# Directory where you keep one file per user: data/users/<user_id>.json
USER_DATA_DIR = Path("data") / "users"

# Remove threading.Lock, not needed for async code

def _make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    elif isinstance(obj, timedelta):
        return obj.total_seconds()  # or str(obj) if you prefer
    return obj

async def load_user_data(user_id: int, bot=None) -> dict:
    """
    Load user data from database, including JSON fields (daily_quests, weekly_contracts, etc.)
    """
    from core.database.db import get_unified_user_data
    async with bot.db_pool.acquire() as conn:
        data = await get_unified_user_data(conn, user_id, bot=bot)
        # If daily_quests or weekly_contracts are JSON strings, parse them
        if data.get('daily_quests') and isinstance(data['daily_quests'], str):
            data['daily_quests'] = json.loads(data['daily_quests'])
        if data.get('weekly_contracts') and isinstance(data['weekly_contracts'], str):
            data['weekly_contracts'] = json.loads(data['weekly_contracts'])
        if user_id == 168786415096692736:
            print(f"[DEBUG] Loading user data - XP: {data.get('xp')}, Level: {data.get('level')}")
        return data

async def save_user_data(user_id: int, user_data: dict, bot=None):
    """
    Save user data to database, including JSON fields (daily_quests, weekly_contracts, etc.)
    """
    if bot is None or not hasattr(bot, 'db_pool'):
        raise RuntimeError("Bot with db_pool required for async DB operations in save_user_data")
    async with bot.db_pool.acquire() as conn:
        if user_id == 168786415096692736:
            print(f"[DEBUG] Saving user data - XP: {user_data.get('xp')}, Level: {user_data.get('level')}")
        user_fields = {k: v for k, v in user_data.items() 
                       if k in ['level', 'xp', 'xp_max', 'title', 'discord_username']}
        if user_fields:
            # Patch: Use raw SQL update for user fields
            await conn.execute(
                "UPDATE users SET level = $2, xp = $3, xp_max = $4, title = $5, discord_username = $6 WHERE user_id = $1",
                user_id,
                user_fields.get("level"),
                user_fields.get("xp"),
                user_fields.get("xp_max"),
                user_fields.get("title"),
                user_fields.get("discord_username"),
            )
        # Save JSON fields
        json_fields = {}
        if 'daily_quests' in user_data:
            json_fields['daily_quests'] = json.dumps(_make_json_safe(user_data['daily_quests']))
        if 'weekly_contracts' in user_data:
            json_fields['weekly_contracts'] = json.dumps(_make_json_safe(user_data['weekly_contracts']))
        if json_fields:
            for key, value in json_fields.items():
                await conn.execute(
                    "UPDATE user_json_data SET data = jsonb_set(data, $2::text[], $3::jsonb) WHERE user_id = $1",
                    user_id,
                    [key],
                    value
                )
        # Update log stats if present
        log_stats = user_data.get('log_stats', {})
        for activity, reps in log_stats.items():
            await conn.update_log_stat(user_id, activity, reps)

async def get_weekly_progress(user_id: int, bot=None) -> dict:
    """Get weekly progress (legacy compatibility)"""
    data = await load_user_data(user_id, bot=bot)
    return data.get("weekly_progress", {
        "reps": 0,
        "quests_completed": 0,
        "days_trained": []
    })

async def update_weekly_progress(user_id: int, reps=0, quest_done=False, bot=None):
    """Update weekly progress (legacy compatibility)"""
    if bot is None or not hasattr(bot, 'db_pool'):
        raise RuntimeError("Bot with db_pool required for async DB operations in update_weekly_progress")
    async with bot.db_pool.acquire() as conn:
        if reps > 0:
            # Get current walking reps and add new ones
            current_stats = await conn.get_log_stats(user_id)
            current_walking = current_stats.get('Walking', 0)
            await conn.update_log_stat(user_id, 'Walking', current_walking + reps)

async def add_recent_activity(user_id: int, activity: str, bot=None):
    """
    Add a recent activity to the user's database record
    """
    if bot is None or not hasattr(bot, 'db_pool'):
        raise RuntimeError("Bot with db_pool required for async DB operations in add_recent_activity")
    async with bot.db_pool.acquire() as conn:
        await conn.add_activity(user_id, activity)