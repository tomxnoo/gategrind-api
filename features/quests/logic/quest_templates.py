"""
Quest Templates - Unified quest generator with dynamic themes and modifiers
Incorporates movement data for flexible, tiered quest creation
"""

try:
    from core.config import MOVEMENT_DATA, QUEST_THEMES, QUEST_MODIFIERS, WEEKLY_CONTRACT_TEMPLATES
except ImportError:
    from core.config import MOVEMENT_DATA, QUEST_THEMES, QUEST_MODIFIERS, WEEKLY_CONTRACT_TEMPLATES

import random

def get_user_tier_from_level(level: int) -> int:
    """Determine user tier based on level for quest generation."""
    if level < 10: return 1
    if level < 20: return 2
    if level < 35: return 3
    if level < 50: return 4
    return 5

def generate_daily_quest(tier: int, user_level: int, bot=None):
    """
    Generates a single, unified daily quest with a theme and a chance for a modifier.
    Optionally accepts a bot instance for future extensibility (DB/cache access).
    """
    # 1. Select a random stat theme (STR, END, TECH)
    stat_themes = ["STR", "END", "TECH"]
    chosen_stat = random.choice(stat_themes)
    theme_stat = random.choice(list(QUEST_THEMES.keys()))
    theme_info = QUEST_THEMES[theme_stat]

    # 2. Filter available movements by the chosen theme and user's max tier
    possible_movements = [
        m for m, data in MOVEMENT_DATA.items()
        if data['stat'] == theme_stat and data['tier'] <= tier
    ]
    # Ensure there's a fallback if the pool is empty
    if not possible_movements:
        possible_movements = [m for m, data in MOVEMENT_DATA.items() if data['tier'] <= tier]
        if not possible_movements: # Absolute fallback
             possible_movements = ["Standard Push-Ups"]

    # 3. Select 3 unique movements for the quest
    num_movements = 3
    if len(possible_movements) < num_movements:
        movements_for_quest = random.choices(possible_movements, k=num_movements)
    else:
        movements_for_quest = random.sample(possible_movements, k=num_movements)

    # 4. Determine reps based on tier
    reps_per_set = 5 + (tier * 2)
    num_sets = 4

    # 5. Apply a modifier (25% chance)
    modifier = None
    if random.random() < 0.25:
        modifier = random.choice(list(QUEST_MODIFIERS.values()))
        reps_per_set = int(reps_per_set * modifier.get("rep_mult", 1.0))

    # 6. Calculate total XP reward
    base_xp_reward = 0
    for move in movements_for_quest:
        xp_per_rep = MOVEMENT_DATA.get(move, {}).get("xp", 1)
        base_xp_reward += (xp_per_rep * reps_per_set * num_sets)

    final_xp_reward = int(base_xp_reward * modifier.get("xp_mult", 1.0) if modifier else base_xp_reward)

    # 7. Assemble the quest object
    quest = {
        "Tier": tier,
        "QuestName": f"T{tier}: {theme_info['name']}",
        "Flavor": random.choice(theme_info['flavor']),
        "Movements": movements_for_quest,
        "Target": {"sets": num_sets, "reps": reps_per_set},
        "Progress": {move: {"sets": 0, "reps": 0} for move in movements_for_quest},
        "XPReward": final_xp_reward,
        "BuffReward": None,  # Add buff logic if needed
        "Modifier": modifier,
        "active": False,
        "_completed_flag": False,
        "_new_format": True
    }
    return quest

# --- Enhanced Weekly Contract Generator ---
def generate_weekly_contract(tier: int, bot=None) -> dict:
    """
    Generates a weekly contract quest. Optionally accepts a bot instance for future extensibility (DB/cache access).
    """
    template = random.choice(WEEKLY_CONTRACT_TEMPLATES)
    final_objectives = []
    for obj_template in template["objectives"]:
        obj = obj_template.copy()
        target = int(obj.get("target_mult", 1) * tier)
        if obj["type"] in ("training_days", "complete_dailies", "unique_movements"):
            target = obj.get("target", 3)
        if obj["type"] == "stat_reps":
            chosen_stat = random.choice(["STR", "END", "TECH"])
            obj["stat_focus"] = chosen_stat
            obj["desc"] = f"Perform {target} reps of {chosen_stat}-based exercises"
        elif obj["type"] == "tier_reps":
            obj["tier_focus"] = tier
            obj["desc"] = f"Perform {target} reps from Tier {tier} or higher movements"
        else:
            obj["desc"] = f"{obj['type'].replace('_', ' ').title()}: 0 / {target}"
        obj["target"] = target
        final_objectives.append(obj)
    contract = {
        "Tier": tier,
        "ContractName": f"T{tier}: {template['name']}",
        "Flavor": template['flavor'],
        "Objectives": final_objectives,
        "XPReward": 500 * tier,
        "BuffReward": "RareLootBoost",
        "Active": False,
        "_completed_flag": False
    }
    return contract