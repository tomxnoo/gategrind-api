from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from features.user.logic.user_data import load_user_data, save_user_data
import random
import asyncio
from core.config import BUFF_DEFINITIONS

async def apply_buff(bot, user_id: int, buff_id: str, user_data=None) -> dict:
    """Apply a buff to the user (async)"""
    if buff_id not in BUFF_DEFINITIONS:
        return {"success": False, "error": "Invalid buff ID"}
    buff_def = BUFF_DEFINITIONS[buff_id]
    data = user_data if user_data is not None else await load_user_data(user_id)
    user_data = data
    if buff_def["type"] == "active":
        # Add to active buffs
        active_buffs = user_data.setdefault("active_buffs", {})
        # Check if buff is already active
        if buff_id in active_buffs:
            # Refresh duration
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=buff_def["duration_hours"])
        else:
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=buff_def["duration_hours"])
        active_buffs[buff_id] = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "effects": buff_def["effects"],
            "name": buff_def["name"],
            "description": buff_def["description"]
        }
        # Update weekly contract progress for earning a buff or badge
        try:
            from features.quests.weekly_ui.weekly_contract_panel import update_weekly_progress
            await update_weekly_progress(user_id, bot, movement="buff", count=1)
        except Exception as e:
            print(f"[BuffEngine] Could not update weekly contract progress for buff: {e}")
        return {"success": True, "type": "active", "buff": buff_def}
    elif buff_def["type"] == "consumable":
        # Apply instant effects
        effects = buff_def["effects"]
        if "remove_cooldowns" in effects:
            user_data["cooldowns"] = {}
        if "instant_xp" in effects:
            from features.user.logic.xp_engine import add_xp
            await add_xp(user_id, effects["instant_xp"])
        if "complete_quest" in effects:
            await complete_random_quest(user_id)
        if "reset_daily_quests" in effects:
            await reset_daily_quests(user_id)
        # Update weekly contract progress for earning a buff or badge
        try:
            from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress
            await update_weekly_progress(user_id, bot, movement="buff", count=1)
        except Exception as e:
            print(f"[BuffEngine] Could not update weekly contract progress for buff: {e}")
        return {"success": True, "type": "consumable", "buff": buff_def}
    return {"success": False, "error": "Unknown buff type"}

async def get_active_buffs(user_id: int, user_data=None) -> list[dict]:
    """Get all currently active buffs for a user (async)"""
    data = user_data if user_data is not None else await load_user_data(user_id)
    user_data = data
    active_buffs = user_data.get("active_buffs", {})
    if isinstance(active_buffs, list):
        # Legacy or corrupted data: convert list to dict
        active_buffs = {str(i): buff for i, buff in enumerate(active_buffs)}
        user_data["active_buffs"] = active_buffs
    current_time = datetime.now()
    valid_buffs = []
    expired_buffs = []
    for buff_id, buff_data in active_buffs.items():
        end_time = datetime.fromisoformat(buff_data["end_time"])
        if current_time < end_time:
            # Calculate remaining time
            remaining = end_time - current_time
            buff_data["remaining_hours"] = remaining.total_seconds() / 3600
            buff_data["buff_id"] = buff_id
            valid_buffs.append(buff_data)
        else:
            expired_buffs.append(buff_id)
    # Clean up expired buffs
    if expired_buffs:
        for buff_id in expired_buffs:
            del active_buffs[buff_id]
    # Patch: also update max_xp in user_data to match XP scaling
    try:
        from features.user.logic.xp_engine import get_xp_required_for_level
        level = user_data.get("level", 1)
        user_data["xp_max"] = get_xp_required_for_level(level)
    except Exception:
        pass
    return valid_buffs

async def calculate_buff_multipliers(user_id: int, user_data=None) -> Dict:
    """Calculate all active buff multipliers for XP calculations"""
    active_buffs = await get_active_buffs(user_id, user_data=user_data)
    try:
        from features.user.logic.class_evolution import get_passive_bonuses
        passive_buffs = await get_passive_bonuses(user_id)
    except ImportError:
        passive_buffs = {}
    multipliers = {
        "xp_bonus": 0,
        "quest_xp_bonus": 0,
        "cooldown_reduction": 0,
        "xp_multiplier": 1.0
    }
    # Apply active buff effects
    for buff in active_buffs:
        effects = buff.get("effects", {})
        for effect, value in effects.items():
            if effect in multipliers:
                if effect == "xp_multiplier":
                    multipliers[effect] *= value
                else:
                    multipliers[effect] += value
    # Apply passive buff effects
    for effect, value in passive_buffs.items():
        if effect in multipliers:
            multipliers[effect] += value
    return multipliers

def grant_random_buff(bot, user_id: int, rarity_weights: Optional[Dict] = None) -> Optional[Dict]:
    """Grant a random buff based on rarity weights"""
    if rarity_weights is None:
        rarity_weights = {"common": 0.5, "uncommon": 0.3, "rare": 0.15, "legendary": 0.05}
    rarity_roll = random.random()
    selected_rarity = "common"
    cumulative = 0
    for rarity, weight in rarity_weights.items():
        cumulative += weight
        if rarity_roll <= cumulative:
            selected_rarity = rarity
            break
    available_buffs = [buff_id for buff_id, buff_def in BUFF_DEFINITIONS.items() 
                      if buff_def["rarity"] == selected_rarity and buff_def["type"] == "active"]
    if not available_buffs:
        return None
    buff_id = random.choice(available_buffs)
    # Await the coroutine since apply_buff is async
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            coro = apply_buff(bot, user_id, buff_id)
            result = loop.create_task(coro)
            # WARNING: This will return a Task, not the result. In production, refactor to async everywhere.
            # For now, return None to avoid blocking.
            return None
        else:
            result = loop.run_until_complete(apply_buff(bot, user_id, buff_id))
    except RuntimeError:
        # No event loop, create one
        result = asyncio.run(apply_buff(bot, user_id, buff_id))
    if result and result.get("success"):
        return {"buff_id": buff_id, "buff": result["buff"], "rarity": selected_rarity}
    return None

async def add_consumable_buff(user_id: int, buff_id: str, quantity: int = 1) -> bool:
    """Add consumable buffs to user's inventory (async)"""
    if buff_id not in BUFF_DEFINITIONS:
        return False

    buff_def = BUFF_DEFINITIONS[buff_id]
    if buff_def["type"] != "consumable":
        return False

    user_data = await load_user_data(user_id)
    inventory = user_data.setdefault("buff_inventory", {})
    inventory[buff_id] = inventory.get(buff_id, 0) + quantity

    await save_user_data(user_id, user_data)
    return True

async def use_consumable_buff(bot, user_id: int, buff_id: str) -> dict:
    """Use a consumable buff from inventory (async)"""
    user_data = await load_user_data(user_id)
    inventory = user_data.get("buff_inventory", {})

    if buff_id not in inventory or inventory[buff_id] <= 0:
        return {"success": False, "error": "Buff not in inventory"}

    # Use the buff
    result = await apply_buff(bot, user_id, buff_id)

    if result["success"]:
        # Remove from inventory
        inventory[buff_id] -= 1
        if inventory[buff_id] <= 0:
            del inventory[buff_id]
        await save_user_data(user_id, user_data)

    return result

async def complete_random_quest(user_id: int):
    """Complete a random daily quest (for void crystal effect, async)"""
    from features.quests.daily_logic.enhanced_daily_quests import get_daily_quest_summary
    quest_data = await get_daily_quest_summary(user_id) if asyncio.iscoroutinefunction(get_daily_quest_summary) else get_daily_quest_summary(user_id)
    incomplete_quests = [q for q in quest_data["quests"] if not q.get("completed", False)]
    if incomplete_quests:
        quest = random.choice(incomplete_quests)
        quest["completed"] = True
        quest["progress"] = quest["target_reps"]
        from features.user.logic.xp_engine import add_xp, calculate_xp_for_movement
        base_xp = calculate_xp_for_movement(quest["movement"], quest["target_reps"])
        final_xp = int(base_xp * quest.get("xp_multiplier", 1.0))
        await add_xp(user_id, final_xp)
        # Save updated quest data
        user_data = await load_user_data(user_id)
        today = date.today().isoformat()
        daily_quests = user_data.get("daily_quests", {})
        today_quests = daily_quests.get(today, [])
        for q in today_quests:
            if q.get("id") == quest.get("id"):
                q.update(quest)
        daily_quests[today] = today_quests
        user_data["daily_quests"] = daily_quests
        await save_user_data(user_id, user_data)

async def reset_daily_quests(user_id: int):
    """Reset daily quests and generate new ones (for time rift effect, async)"""
    from features.quests.daily_logic.enhanced_daily_quests import generate_enhanced_daily_quests
    from datetime import datetime
    user_data = await load_user_data(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    # Clear existing daily quests
    if "daily_quests" in user_data:
        user_data["daily_quests"].pop(today, None)
    # Generate new quests
    if asyncio.iscoroutinefunction(generate_enhanced_daily_quests):
        today_quests = await generate_enhanced_daily_quests(user_id)
    else:
        today_quests = generate_enhanced_daily_quests(user_id)
    user_data["daily_quests"][today] = today_quests
    await save_user_data(user_id, user_data)
