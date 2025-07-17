"""
Generate Daily Quests - Quest generation logic for daily quests
"""

import random
from datetime import datetime
from features.user.logic.xp_engine import MOVEMENT_DATA

def pick_main_buff():
    import random
    buffs = ["xp_boost_5", "recovery_aura", "shadow_focus", None]
    return random.choice(buffs)

def pick_side_buff():
    import random
    side_buffs = ["bonus_log_chance", "focus_hint", None, None]
    return random.choice(side_buffs)

QUEST_NAMES = {
    1: "Veins of the Abyss",
    2: "Ritual of the Core",
    3: "Iron Cradle",
    4: "Whispers of the Flesh",
    5: "Burden of Bone",
    6: "Elegy of Sinew",
    7: "Grim Edict",
    8: "Oath to Obsidian",
    9: "Feast of the Hollow",
    10: "The Nameless Reign",
}

QUEST_QUOTES = {
    1: "The path begins in silence.",
    2: "Steel your breath for the shaping.",
    3: "Pain teaches what memory forgets.",
    4: "Your flesh remembers. Make it earn the silence.",
    5: "The marrow bends before it breaks.",
    6: "Scars do not speak. They judge.",
    7: "You are your burden. Carry it.",
    8: "The forge sings for no one.",
    9: "Ritual is strength made obedient.",
    10: "What rises from the grave no longer fears the dark.",
}

def get_unlocked_tiers(level: int):
    return list(range(1, min(11, (level - 1) // 5 + 2)))  # +1 tier every 5 levels

def get_daily_quest_count(level: int) -> int:
    return min(3 + (level // 10), 7)

def get_movements_by_tier(tiers: list[int]):
    return [m for m, info in MOVEMENT_DATA.items() if info["tier"] in tiers]

def reps_for_tier(tier: int):
    return 20 + (tier - 1) * 10  # Tier 1: 20 → Tier 10: 110

def roll_buff(tier: int):
    if random.random() < 0.3:
        buff_value = 5 + (tier // 3) * 5  # Tier 3+ = +10%, Tier 6+ = +15%
        return f"+{buff_value}% XP for 24h"
    return None

def calculate_xp_reward(movements: dict):
    total = 0
    for move, reps in movements.items():
        xp_per_rep = MOVEMENT_DATA.get(move, {}).get("xp", 1)
        total += reps * xp_per_rep
    return int(total)

async def generate_daily_quests(user_id: int, level: int, bot=None):
    """Generate daily quests for a user"""
    tiers = get_unlocked_tiers(level)
    quest_count = get_daily_quest_count(level)
    all_quests = []

    for i in range(quest_count):
        tier = random.choice(tiers)
        reps = reps_for_tier(tier)

        pool = get_movements_by_tier([t for t in tiers if t <= tier])
        
        # Fix: Handle cases where pool has fewer movements than needed
        movement_count = min(4, len(pool))  # Use available movements, max 4
        if movement_count == 0:
            # Fallback: use all available movements regardless of tier
            pool = list(MOVEMENT_DATA.keys())
            movement_count = min(4, len(pool))
        
        chosen = random.sample(pool, k=movement_count)

        targets = {m: reps for m in chosen}
        progress = {m: 0 for m in chosen}

        quest = {
            "id": f"daily_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}_{i}",  # Add unique ID
            "tier": tier,
            "Tier": tier,  # Keep uppercase for legacy compatibility
            "QuestName": QUEST_NAMES.get(tier, f"Tier {tier} Quest"),
            "Flavor": QUEST_QUOTES.get(tier, ""),
            "movements": chosen,
            "Movements": chosen,  # Keep uppercase for legacy compatibility
            "targets": targets,
            "Targets": targets,   # Keep uppercase for legacy compatibility
            "target": {"sets": 1, "reps": reps},  # New format for awakening system
            "progress": {m: {"sets": 0, "reps": 0} for m in chosen},  # New format
            "Progress": progress,  # Legacy format
            "BuffReward": roll_buff(tier),
            "xp_reward": calculate_xp_reward(targets),
            "XPReward": calculate_xp_reward(targets),  # Legacy compatibility
            "active": False,
            "Active": False,
            "completed": False,
            "Completed": False,
            "_completed_flag": False,
            "_new_format": True
        }

        all_quests.append(quest)

    return all_quests