from datetime import datetime, timedelta, date
from features.quests.logic.quest_templates import generate_daily_quest, get_user_tier_from_level
from features.user.logic.xp_engine import add_xp
from core.database.db import get_unified_user_data, update_user_json_data

def _require_bot(bot):
    """Helper function to ensure bot is provided"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")

async def _generate_daily_quests_for_user(user_id: int, user_data: dict = None, bot=None):
    """Generate new daily quests for a user"""
    _require_bot(bot)
    
    if user_data is None:
        async with bot.db_pool.acquire() as conn:
            user_data = await get_unified_user_data(conn, user_id, bot)
    
    # Get user level for quest generation
    user_level = user_data.get("level", 1)
    username = user_data.get("username", "Unknown")
    
    # Generate quests using the quest template system
    from features.quests.logic.daily_quests.generate_daily_quests import generate_daily_quests
    quests = generate_daily_quests(user_id, username, user_level)
    
    # Save the new quests
    today_str = date.today().isoformat()
    user_data.setdefault("daily_quests", {})["date"] = today_str
    user_data["daily_quests"]["quests"] = quests
    
    async with bot.db_pool.acquire() as conn:
        await update_user_json_data(conn, user_id, user_data, bot=bot)
    
    return quests

async def get_today_quests(user_id: int, bot=None):
    """Fetches the daily quests for a user from the database."""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        today_str = date.today().isoformat()
        quest_data = user_data.get("daily_quests", {})
        # Patch: handle legacy/malformed data
        if not isinstance(quest_data, dict):
            quest_data = {}
        if quest_data.get("date") != today_str or not quest_data.get("quests"):
            quests = await _generate_daily_quests_for_user(user_id, user_data, bot)
        else:
            quests = quest_data.get("quests", [])
        
        # Sort quests so active ones appear first
        quests.sort(key=lambda q: not q.get("active", False))
        return quests

async def activate_daily_quest(user_id: int, quest_tier: int, bot=None):
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        quests = user_data.get("daily_quests", {}).get("quests", [])
        # Set all quests to inactive first, and clear both possible keys
        for quest in quests:
            quest["active"] = False
            quest["Active"] = False
        # Then set only the selected quest to active (using only "active")
        for quest in quests:
            quest_tier_value = quest.get("tier")
            if quest_tier_value is None:
                quest_tier_value = quest.get("Tier")
            if str(quest_tier_value) == str(quest_tier):
                quest["active"] = True
                quest["Active"] = False
                break
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return user_data

async def update_quest_progress(user_id: int, movement: str, reps_done: int, bot=None) -> list:
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        quests = user_data.get("daily_quests", {}).get("quests", [])
        completed_quests = []

        for quest in quests:
            if quest.get("active") and not quest.get("_completed_flag") and movement in quest.get("movements", []):
                
                target_sets = quest["target"]["sets"]
                target_reps = quest["target"]["reps"]
                
                # Add reps to the current set
                current_sets = quest["progress"][movement]["sets"]
                current_reps = quest["progress"][movement]["reps"] + reps_done
                
                # Check if sets are completed
                while current_reps >= target_reps and current_sets < target_sets:
                    current_sets += 1
                    current_reps -= target_reps
                
                quest["progress"][movement]["sets"] = min(current_sets, target_sets)
                # Store remaining reps for the next log, or cap at target if sets are full
                quest["progress"][movement]["reps"] = 0 if current_sets == target_sets else current_reps

                # Check for full quest completion
                all_movements_done = all(
                    p["sets"] >= quest["target"]["sets"] for p in quest["progress"].values()
                )

                if all_movements_done:
                    quest["_completed_flag"] = True
                    quest["active"] = False
                    await add_xp(None, user_id, quest["xp_reward"], bot=bot)  # Pass None for connection if not available
                    completed_quests.append(quest)
                    
                    # Hook for weekly contract
                    from .weekly_contract_logic import update_weekly_contract_progress
                    await update_weekly_contract_progress(user_id, quest_completed=True, bot=bot)

        await update_user_json_data(conn, user_id, user_data, bot=bot)  # TODO: Add bot if set_user_json_data supports it
        return completed_quests

async def abandon_daily_quest(user_id: int, bot=None):
    """Abandon the user's current active daily quest (sets all to inactive)."""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        quests = user_data.get("daily_quests", {}).get("quests", [])
        for quest in quests:
            quest["active"] = False
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

# Add the plural version that the UI expects
async def abandon_daily_quests(user_id: int, bot=None):
    """Abandon all daily quests for the user (alias for abandon_daily_quest)."""
    return await abandon_daily_quest(user_id, bot)

async def reroll_daily_quests(user_id: int, bot=None):
    """Reroll the user's daily quests by deactivating all current quests, then generating a new set."""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        quests = user_data.get("daily_quests", {}).get("quests", [])
        for quest in quests:
            quest["active"] = False
            quest["Active"] = False
        await update_user_json_data(conn, user_id, user_data, bot=bot)
    return await _generate_daily_quests_for_user(user_id, bot=bot)
