"""
Quest Data Management - Unified quest storage system
"""

from datetime import datetime
from core.database.db import get_unified_user_data, update_user_json_data

async def save_today_quests(user_id: int, quests: list, bot=None):
    """Save today's quests to the database"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")
    
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        
        # Update daily quests
        user_data.setdefault("daily_quests", {})
        user_data["daily_quests"]["quests"] = quests
        user_data["daily_quests"]["last_generated"] = datetime.utcnow().isoformat()
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def load_today_quests(user_id: int, bot=None):
    """Load today's quests from the database"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")
    
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        return daily_quests.get("quests", [])