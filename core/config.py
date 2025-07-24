
import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    """Application settings"""
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() == "true"
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    # Stat Milestone Configuration
    STAT_MILESTONE_INTERVAL: int = int(os.getenv("STAT_MILESTONE_INTERVAL", "150"))

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()


# --- CLASS EVOLUTIONS ---
CLASS_EVOLUTIONS = {
    "Shadow Initiate": ["Abyssal Seeker", "Lunar Disciple"],
    "Abyssal Seeker": ["Eclipse Adept", "Spectral Rogue"],
    "Lunar Disciple": ["Celestial Sage", "Night Herald"],
    "Eclipse Adept": ["Warden of Night"],
    "Spectral Rogue": ["Warden of Night"],
    "Celestial Sage": ["Paragon of the Archive"],
    "Night Herald": ["Paragon of the Archive"],
    "Warden of Night": ["Paragon of the Archive"],
    # Paragon is the final evolution
}
# --- MOVEMENT DATA & XP MULTIPLIER ---
MOVEMENT_DATA = {
    "Push-ups": {"stat": "STR", "tier": 1, "xp": 5},
    "Squats": {"stat": "END", "tier": 1, "xp": 5},
    "Plank": {"stat": "TECH", "tier": 1, "xp": 5},
    "Pull-ups": {"stat": "STR", "tier": 2, "xp": 8},
    "Lunges": {"stat": "END", "tier": 2, "xp": 8},
    "Hollow Hold": {"stat": "TECH", "tier": 2, "xp": 8},
    # ...add more movements as needed...
}

XP_MULTIPLIER_PER_LEVEL = 1.05
# core/config.py
# Central config for all static game data, names, flavor, buffs, and balance values

# --- Tier Names and Flavors ---
TIER_NAMES = {

    1: "Shadow Initiate",
    2: "Abyssal Seeker",
    3: "Eclipse Adept",
    4: "Warden of Night",
    5: "Paragon of the Archive"
}

# --- WEEKLY CONTRACT TEMPLATES ---
WEEKLY_CONTRACT_TEMPLATES = [
    {
        "name": "The Titan's Toil",
        "flavor": "A trial of raw, unrelenting effort. The shadows reward volume.",
        "objectives": [
            {"type": "total_reps", "target_mult": 250},
            {"type": "training_days", "target": 3}
        ]
    },
    {
        "name": "The Disciple's Path",
        "flavor": "Consistency is the whetstone that sharpens the soul. Walk the path daily.",
        "objectives": [
            {"type": "complete_dailies", "target": 4},
            {"type": "total_reps", "target_mult": 100}
        ]
    },
    {
        "name": "The Specialist's Vow",
        "flavor": "Focus your power. Dominate a single aspect of your being.",
        "objectives": [
            {"type": "stat_reps", "target_mult": 150},
            {"type": "training_days", "target": 2}
        ]
    },
    {
        "name": "The Versatile Shadow",
        "flavor": "Adaptability is a weapon. Show your mastery over diverse forms.",
        "objectives": [
            {"type": "unique_movements", "target": 5},
            {"type": "complete_dailies", "target": 2}
        ]
    },
    {
        "name": "The High Requiem",
        "flavor": "Only those who push beyond their limits may claim the greatest rewards.",
        "objectives": [
            {"type": "tier_reps", "target_mult": 50},
            {"type": "complete_dailies", "target": 3}
        ]
    },
    {
        "name": "The Iron Pilgrimage",
        "flavor": "Endure the journey, one rep at a time. The Archive remembers those who persist.",
        "objectives": [
            {"type": "training_days", "target": 5},
            {"type": "total_reps", "target_mult": 200}
        ]
    },
    {
        "name": "The Shadow's Gambit",
        "flavor": "Take risks, embrace the unknown, and be rewarded for your daring.",
        "objectives": [
            {"type": "unique_movements", "target": 7},
            {"type": "stat_reps", "target_mult": 120}
        ]
    },
    {
        "name": "The Blood Oath",
        "flavor": "Sacrifice comfort for progress. Only the resolute will prevail.",
        "objectives": [
            {"type": "tier_reps", "target_mult": 80},
            {"type": "training_days", "target": 4}
        ]
    },
    {
        "name": "The Forgotten Ritual",
        "flavor": "Complete the rites of the Archive: repetition, variety, and daily devotion.",
        "objectives": [
            {"type": "total_reps", "target_mult": 150},
            {"type": "unique_movements", "target": 4},
            {"type": "complete_dailies", "target": 3}
        ]
    },
    {
        "name": "The Twin Eclipse",
        "flavor": "Balance strength and endurance. Only those who master both sides will succeed.",
        "objectives": [
            {"type": "stat_reps", "target_mult": 100},
            {"type": "stat_reps", "target_mult": 100}
        ]
    },
    {
        "name": "The Arcane Circuit",
        "flavor": "Move through the Archive's secret circuit. Leave no movement untested.",
        "objectives": [
            {"type": "unique_movements", "target": 8}
        ]
    }
]

# --- BUFFS ---
BUFFS = {
    "void_focus": {
        "name": "🎯 Void Focus",
        "description": "Reduced cooldowns by 50% for 4 hours",
        "type": "active",
        "duration_hours": 4,
        "effects": {"cooldown_reduction": 50},
        "rarity": "uncommon"
    },
    "emberlock_grit": {
        "name": "🔥 Emberlock's Grit",
        "description": "+25% XP when completing quests for 12 hours",
        "type": "active",
        "duration_hours": 12,
        "effects": {"quest_xp_bonus": 25},
        "rarity": "rare"
    },
    "phantom_might": {
        "name": "👻 Phantom Might",
        "description": "Double XP from all activities for 2 hours",
        "type": "active",
        "duration_hours": 2,
        "effects": {"xp_multiplier": 2.0},
        "rarity": "legendary"
    },
    "crimson_rage": {
        "name": "🔴 Crimson Rage",
        "description": "+30% XP gain for 6 hours",
        "type": "active",
        "duration_hours": 6,
        "effects": {"xp_bonus": 30},
        "rarity": "rare"
    },
    "shadow_veil": {
        "name": "🌫️ Shadow Veil",
        "description": "+10% XP gain for 24 hours",
        "type": "active",
        "duration_hours": 24,
        "effects": {"xp_bonus": 10},
        "rarity": "common"
    },
    "astral_ascension": {
        "name": "✨ Astral Ascension",
        "description": "Triple XP from all activities for 1 hour",
        "type": "active",
        "duration_hours": 1,
        "effects": {"xp_multiplier": 3.0},
        "rarity": "legendary"
    },
    "void_mastery": {
        "name": "🌌 Void Mastery",
        "description": "+50% quest XP bonus for 10 hours",
        "type": "active",
        "duration_hours": 10,
        "effects": {"quest_xp_bonus": 50},
        "rarity": "rare"
    },
    "eclipse_power": {
        "name": "🌙 Eclipse Power",
        "description": "+20% XP gain and -25% cooldowns for 8 hours",
        "type": "active",
        "duration_hours": 8,
        "effects": {"xp_bonus": 20, "cooldown_reduction": 25},
        "rarity": "rare"
    },
    "dragon_soul": {
        "name": "🐉 Dragon Soul",
        "description": "+40% XP gain for 4 hours",
        "type": "active",
        "duration_hours": 4,
        "effects": {"xp_bonus": 40},
        "rarity": "rare"
    },
    "phantom_speed": {
        "name": "⚡ Phantom Speed",
        "description": "-75% cooldown reduction for 3 hours",
        "type": "active",
        "duration_hours": 3,
        "effects": {"cooldown_reduction": 75},
        "rarity": "uncommon"
    },
    # Consumable Buffs (Instant Effect)
    "bloodhowl": {
        "name": "🦸 Bloodhowl",
        "description": "Instantly removes all cooldowns",
        "type": "consumable",
        "effects": {"remove_cooldowns": True},
        "rarity": "rare"
    },
    "shadow_elixir": {
        "name": "🧪 Shadow Elixir",
        "description": "Instantly gain 200 XP",
        "type": "consumable",
        "effects": {"instant_xp": 200},
        "rarity": "uncommon"
    },
    "void_crystal": {
        "name": "💎 Void Crystal",
        "description": "Complete one random daily quest instantly",
        "type": "consumable",
        "effects": {"complete_quest": True},
        "rarity": "legendary"
    },
    "shadow_potion": {
        "name": "🧪 Shadow Potion",
        "description": "Instantly gain 500 XP",
        "type": "consumable",
        "effects": {"instant_xp": 500},
        "rarity": "rare"
    },
    "void_shard": {
        "name": "💎 Void Shard",
        "description": "Instantly gain 100 XP",
        "type": "consumable",
        "effects": {"instant_xp": 100},
        "rarity": "common"
    },
    "time_rift": {
        "name": "⏰ Time Rift",
        "description": "Reset all daily quest progress and get new quests",
        "type": "consumable",
        "effects": {"reset_daily_quests": True},
        "rarity": "legendary"
    },
    "essence_of_power": {
        "name": "💀 Essence of Power",
        "description": "Instantly gain 1000 XP",
        "type": "consumable",
        "effects": {"instant_xp": 1000},
        "rarity": "legendary"
    },
    # --- Additional Buffs ---
    "lunar_resurgence": {
        "name": "🌕 Lunar Resurgence",
        "description": "+15% XP and +1 daily quest reroll for 12 hours",
        "type": "active",
        "duration_hours": 12,
        "effects": {"xp_bonus": 15, "extra_reroll": 1},
        "rarity": "rare"
    },
    "spectral_guard": {
        "name": "🛡️ Spectral Guard",
        "description": "-50% damage from failed quests for 24 hours",
        "type": "active",
        "duration_hours": 24,
        "effects": {"fail_damage_reduction": 50},
        "rarity": "epic"
    },
    "echo_of_the_void": {
        "name": "🌀 Echo of the Void",
        "description": "+10% XP, +10% cooldown reduction for 8 hours",
        "type": "active",
        "duration_hours": 8,
        "effects": {"xp_bonus": 10, "cooldown_reduction": 10},
        "rarity": "uncommon"
    },
    "ember_burst": {
        "name": "🔥 Ember Burst",
        "description": "Instantly complete a random contract objective",
        "type": "consumable",
        "effects": {"complete_objective": True},
        "rarity": "epic"
    }
}
# --- BUFF DEFINITIONS (alias for BUFFS, for compatibility) ---
BUFF_DEFINITIONS = BUFFS

# --- QUEST THEMES ---
QUEST_THEMES = {
    "STR": {
        "name": "The Crimson Path",
        "flavor": [
            "Carve your strength into the world.", "A trial of pure, unyielding power.",
            "The clang of ethereal steel rings with each rep.", "Forge your body in the fires of effort."
        ]
    },
    "END": {
        "name": "The Unending Coil",
        "flavor": [
            "Endurance is a fortress built brick by brick.", "Outlast the echoes of your own limits.",
            "Breathe the quiet rhythm of persistence.", "The long road is your proving ground."
        ]
    },
    "TECH": {
        "name": "The Argent Core",
        "flavor": [
            "Hone the center of your will.", "From stability, true power is born.",
            "Master the stillness within the storm.", "Your foundation is unshakeable."
        ]
    }
}
QUEST_MODIFIERS = {
    "shadow_rush": {"name": "🌪️ Shadow Rush", "desc": "Complete in 6 hrs for 2x XP!", "xp_mult": 2.0, "time_limit_hrs": 6},
    "bloodlust": {"name": "🩸 Bloodlust", "desc": "+50% reps for 2.5x XP!", "rep_mult": 1.5, "xp_mult": 2.5},
    "perfect_form": {"name": "✨ Perfect Form", "desc": "-30% reps, but 1.8x XP!", "rep_mult": 0.7, "xp_mult": 1.8},
    "void_surge": {"name": "🌌 Void Surge", "desc": "Triple XP for the truly dedicated.", "rep_mult": 1.0, "xp_mult": 3.0}
}

# --- Add any other static config blocks here ---

