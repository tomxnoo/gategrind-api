from core.config import MOVEMENT_DATA, XP_MULTIPLIER_PER_LEVEL
import math
from typing import Optional

from core.database import db

def get_xp_required_for_level(level: int) -> int:
    return int(100 * (XP_MULTIPLIER_PER_LEVEL ** (level - 1)))

async def add_stat_xp(connection, user_id: int, movement: str, reps: int, bot=None):
    movement_info = MOVEMENT_DATA.get(movement)
    if not movement_info:
        return

    BASE_REP_VALUE = 0.5
    TIER_MULTIPLIERS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 2.0, 5: 2.5}

    target_stat = movement_info["stat"]
    exercise_tier = movement_info["tier"]

    is_hold = "Hold" in movement or "Plank" in movement or "Sit" in movement
    effective_reps = math.ceil(reps / 5) if is_hold else reps

    tier_multiplier = TIER_MULTIPLIERS.get(exercise_tier, 1.0)
    stat_xp_gained = (BASE_REP_VALUE * effective_reps) * tier_multiplier

    stats = await db.get_user_stats(connection, user_id)
    current_stat = stats[target_stat]
    current_stat['xp'] += stat_xp_gained

    xp_for_next_level = 100 * current_stat['level']
    while current_stat['xp'] >= xp_for_next_level:
        current_stat['level'] += 1
        current_stat['xp'] -= xp_for_next_level
        xp_for_next_level = 100 * current_stat['level']

    await db.update_user_stat(connection, user_id, target_stat, current_stat['level'], current_stat['xp'], bot=bot)

async def add_xp(connection, user_id: int, xp_to_add: int, movement: Optional[str] = None, reps: int = 0, bot=None):
    if movement and reps > 0:
        await add_stat_xp(connection, user_id, movement, reps, bot=bot)
    user_data = await db.get_user(connection, user_id)
    if not user_data:
        user_data = {}
    current_xp = user_data.get("xp", 0)
    current_level = user_data.get("level", 1)
    final_xp_gain = xp_to_add
    new_xp = current_xp + final_xp_gain
    new_level = current_level
    xp_for_next_level = user_data.get("xp_max") or get_xp_required_for_level(new_level)
    leveled_up = False
    while new_xp >= xp_for_next_level:
        new_xp -= xp_for_next_level
        new_level += 1
        xp_for_next_level = get_xp_required_for_level(new_level)
        leveled_up = True
    await db.update_user(connection, user_id, xp=new_xp, level=new_level, xp_max=xp_for_next_level, bot=bot)
    return {"xp_gain": final_xp_gain, "leveled_up": leveled_up, "new_level": new_level}

def calculate_xp_for_movement(movement: str, reps: int) -> int:
    movement_info = MOVEMENT_DATA.get(movement)
    if not movement_info:
        return 0
    xp_per_rep = movement_info["xp"]
    return math.ceil(xp_per_rep * reps)