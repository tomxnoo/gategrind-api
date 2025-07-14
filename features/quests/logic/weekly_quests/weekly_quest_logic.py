from core.database.db import get_unified_user_data, update_user_json_data
from core.redis_cache import invalidate_user_json_cache

def _require_bot(bot):
    """Helper function to ensure bot is provided"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")

async def abandon_weekly_contract(bot, user_id: int):
    """Abandon the user's current active weekly contract."""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        contracts = user_data.get("weekly_contracts", {}).get("contracts", [])
        for contract in contracts:
            contract["active"] = False
            contract["Active"] = False
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        await invalidate_user_json_cache(bot, user_id)
        return True

# Fixed parameter order to match daily_quest_logic.py
async def abandon_daily_quests(user_id: int, bot=None):
    """Abandon all daily quests for the user."""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        quests = user_data.get("daily_quests", {}).get("quests", [])
        for quest in quests:
            quest["active"] = False
            quest["Active"] = False
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        await invalidate_user_json_cache(bot, user_id)
        return True