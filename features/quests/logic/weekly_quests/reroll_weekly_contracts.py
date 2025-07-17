"""
Weekly Contract Reroll Logic
"""

from datetime import datetime, timedelta, date
from features.quests.logic.quest_templates import generate_weekly_contract, get_user_tier_from_level
from core.database.db import get_unified_user_data, update_user_json_data

def _require_bot(bot):
    """Helper function to ensure bot is provided"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")

async def reroll_weekly_contracts(user_id: int, bot=None):
    """Reroll the user's weekly contracts"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        user_level = user_data.get("level", 1)
        user_tier = get_user_tier_from_level(user_level)
        
        # Generate new weekly contract
        new_contract = generate_weekly_contract(user_tier, bot)
        
        # Update user data
        user_data.setdefault("weekly_contracts", {})
        user_data["weekly_contracts"]["contracts"] = [new_contract]
        user_data["weekly_contracts"]["last_reroll"] = datetime.utcnow().isoformat()
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return new_contract