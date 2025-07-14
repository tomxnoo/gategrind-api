
import discord
from discord.ui import Button, View
import asyncio
from features.user.logic.user_data import load_user_data, save_user_data


class EnhancedDailyQuestView(View):
    """Generate enhanced daily quests with themes and modifiers"""
    user_data = load_user_data(user_id)
    user_level = user_data.get("level", 1)
    
    # Select 2-3 random themes
    selected_themes = random.sample(list(QUEST_THEMES.keys()), min(3, len(QUEST_THEMES)))
    quests = []
    
    for theme_key in selected_themes:
        theme = QUEST_THEMES[theme_key]
        
        # Select random movement from theme
        movement = random.choice(theme["movements"])
        
        # Calculate base reps based on user level and movement difficulty
        base_reps = calculate_quest_reps(movement, user_level)
        
        # Maybe add a modifier (30% chance)
        modifier = None
        if random.random() < 0.3:
            # Higher level users get better chance at rare modifiers
            modifier_pool = [m for m, data in QUEST_MODIFIERS.items() 
                           if should_get_modifier(data["rarity"], user_level)]
            if modifier_pool:
                modifier_key = random.choice(modifier_pool)
                modifier = QUEST_MODIFIERS[modifier_key]
        
        # Apply modifier effects
        final_reps = base_reps
        xp_multiplier = 1.0
        
        if modifier:
            if "rep_multiplier" in modifier:
                final_reps = int(base_reps * modifier["rep_multiplier"])
            if "xp_multiplier" in modifier:
                xp_multiplier = modifier["xp_multiplier"]
        
        # Create quest
        quest = {
            "id": f"daily_{theme_key}_{date.today().isoformat()}",
            "theme": theme,
            "movement": movement,
            "target_reps": final_reps,
            "progress": 0,
            "completed": False,
            "BuffReward": pick_main_buff(),
            "SideBuffReward": pick_side_buff(),
            "modifier": modifier,
            "xp_multiplier": xp_multiplier,
            "flavor_text": random.choice(theme["flavor"]),
            "created_date": date.today().isoformat()
        }
        
        quests.append(quest)
    
    return quests

def calculate_quest_reps(movement: str, user_level: int) -> int:
    """Calculate appropriate rep count based on movement and user level"""
    base_reps = {
        "Push-Ups": 30,
        "Pull-Ups": 15,
        "Squats": 40,
        "Crunches": 50,
        "Planks": 120,  # seconds
        "Knee Raises": 25,
        "Dips": 20,
        "Jump Squats": 25,
        "Bulgarian Split Squats": 20,
        "L-Sit / V-Ups": 15,
        "Hollow Hold": 90,  # seconds
        "Walking": 5000  # steps
    }
    
    base = base_reps.get(movement, 30)
    # Scale with level but cap growth
    level_multiplier = 1 + (user_level - 1) * 0.1
    level_multiplier = min(level_multiplier, 2.5)  # Cap at 2.5x
    
    return int(base * level_multiplier)

def should_get_modifier(rarity: str, user_level: int) -> bool:
    """Determine if user should get a modifier based on rarity and level"""
    chances = {
        "common": 0.6,
        "uncommon": 0.3 + (user_level * 0.01),
        "rare": 0.1 + (user_level * 0.015),
        "legendary": 0.02 + (user_level * 0.008)
    }
    
    return random.random() < chances.get(rarity, 0.1)

def get_daily_quest_summary(user_id: int) -> Dict:
    """Get summary of today's quests with progress"""
    user_data = load_user_data(user_id)
    today = date.today().isoformat()
    
    daily_quests = user_data.get("daily_quests", {})
    today_quests = daily_quests.get(today, [])
    
    if not today_quests:
        # Generate new quests if none exist
        today_quests = generate_enhanced_daily_quests(user_id)
        daily_quests[today] = today_quests
        user_data["daily_quests"] = daily_quests
        save_user_data(user_id, user_data)
    
    completed = sum(1 for q in today_quests if q.get("completed", False))
    total = len(today_quests)
    
    return {
        "quests": today_quests,
        "completed": completed,
        "total": total,
        "completion_rate": completed / total if total > 0 else 0
    }
