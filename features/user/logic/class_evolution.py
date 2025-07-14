from typing import Dict, Optional
from features.user.logic.user_data import load_user_data, save_user_data

from core.config import CLASS_EVOLUTIONS

def get_class_for_level(level: int) -> dict:
    """Get the current class evolution for a level."""
    current_class = CLASS_EVOLUTIONS[1]
    for evo_level, evo_data in CLASS_EVOLUTIONS.items():
        if level >= evo_level:
            current_class = evo_data
        else:
            break
    return current_class

def get_next_evolution(level: int) -> Optional[Dict]:
    """Get the next class evolution milestone."""
    for evo_level, evo_data in sorted(CLASS_EVOLUTIONS.items()):
        if level < evo_level:
            return {"level": evo_level, "evolution": evo_data}
    return None

async def check_evolution_unlock(user_id: int, new_level: int) -> Optional[Dict]:
    """Check if user unlocked a new evolution and apply rewards."""
    user_data = await load_user_data(user_id)
    # This logic assumes you have a 'passive_buffs' system to apply rewards
    # For now, it just tracks completed evolutions.
    completed = user_data.setdefault("completed_evolutions", [])

    unlocked_evolution = None
    for evo_level, evo_data in CLASS_EVOLUTIONS.items():
        if new_level >= evo_level and evo_level not in completed:
            completed.append(evo_level)
            unlocked_evolution = {"level": evo_level, "evolution": evo_data, "unlocked": True}

    if unlocked_evolution:
        await save_user_data(user_id, user_data)
        return unlocked_evolution

    return None

async def get_passive_bonuses(user_id: int) -> Dict:
    """Get all active passive bonuses for a user."""
    user_data = await load_user_data(user_id)
    return user_data.get("passive_buffs", {})