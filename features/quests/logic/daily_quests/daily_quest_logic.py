"""
Daily Quest Logic - Core functionality for daily quest management
"""

from datetime import datetime, timedelta, date
from features.quests.logic.quest_templates import generate_daily_quest, get_user_tier_from_level
from features.quests.logic.daily_quests.generate_daily_quests import generate_daily_quests
from features.user.logic.xp_engine import add_xp
from core.database.db import get_unified_user_data, update_user_json_data

def _require_bot(bot):
    """Helper function to ensure bot is provided"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")

async def get_today_quests(user_id: int, bot=None):
    """Get today's daily quests for a user"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        
        # Check if quests need to be generated for today
        last_generated = daily_quests.get("last_generated")
        today = datetime.utcnow().date()
        
        if not last_generated or datetime.fromisoformat(last_generated).date() < today:
            # Generate new quests for today
            user_level = user_data.get("level", 1)
            new_quests = await generate_daily_quests(user_id, user_level, bot)
            
            # Save the new quests
            daily_quests["quests"] = new_quests
            daily_quests["last_generated"] = datetime.utcnow().isoformat()
            user_data["daily_quests"] = daily_quests
            
            await update_user_json_data(conn, user_id, user_data, bot=bot)
            
        return daily_quests.get("quests", [])

async def activate_quest(user_id: int, quest_id: str, bot=None):
    """Activate a specific daily quest"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        quests = daily_quests.get("quests", [])
        
        for quest in quests:
            if quest.get("id") == quest_id:
                quest["active"] = True
                quest["activated_at"] = datetime.utcnow().isoformat()
                break
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def activate_daily_quest(user_id: int, quest_id: str, bot=None):
    """Alias for activate_quest for backward compatibility"""
    return await activate_quest(user_id, quest_id, bot)

async def complete_quest(user_id: int, quest_id: str, bot=None):
    """Complete a specific daily quest"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        quests = daily_quests.get("quests", [])
        
        for quest in quests:
            if quest.get("id") == quest_id:
                quest["completed"] = True
                quest["completed_at"] = datetime.utcnow().isoformat()
                
                # Award XP
                xp_reward = quest.get("xp_reward", 50)
                await add_xp(user_id, xp_reward)
                break
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def update_quest_progress(user_id: int, movement: str, reps: int, bot=None):
    """Update progress on daily quests based on movement and reps"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        quests = daily_quests.get("quests", [])
        
        completed_quests = []
        
        for quest in quests:
            if quest.get("active", False) and not quest.get("completed", False):
                # Check if this movement matches the quest
                quest_movement = quest.get("movement", "").lower()
                if movement.lower() in quest_movement or quest_movement in movement.lower():
                    # Update progress
                    current_progress = quest.get("progress", 0)
                    target = quest.get("target", quest.get("Target", 0))
                    
                    new_progress = current_progress + reps
                    quest["progress"] = new_progress
                    
                    # Check if completed
                    if new_progress >= target:
                        quest["completed"] = True
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Award XP
                        xp_reward = quest.get("xp_reward", 50)
                        await add_xp(user_id, xp_reward)
                        
                        completed_quests.append(quest)
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return completed_quests

async def abandon_daily_quests(user_id: int, bot=None):
    """Abandon all daily quests"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        quests = daily_quests.get("quests", [])
        
        for quest in quests:
            quest["active"] = False
            quest["abandoned"] = True
            quest["abandoned_at"] = datetime.utcnow().isoformat()
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def abandon_specific_quest(user_id: int, quest_id: str, bot=None):
    """Abandon a specific daily quest"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        daily_quests = user_data.get("daily_quests", {})
        quests = daily_quests.get("quests", [])
        
        for quest in quests:
            if quest.get("id") == quest_id:
                quest["active"] = False
                quest["abandoned"] = True
                quest["abandoned_at"] = datetime.utcnow().isoformat()
                break
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def reroll_daily_quests(user_id: int, bot=None):
    """Reroll daily quests for a user"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        user_level = user_data.get("level", 1)
        
        # Generate new quests
        new_quests = await generate_daily_quests(user_id, user_level, bot)
        
        # Update user data
        user_data.setdefault("daily_quests", {})
        user_data["daily_quests"]["quests"] = new_quests
        user_data["daily_quests"]["last_generated"] = datetime.utcnow().isoformat()
        user_data["daily_quests"]["last_reroll"] = datetime.utcnow().isoformat()
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return new_quests