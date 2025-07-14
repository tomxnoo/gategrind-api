
import datetime

# This is a stub for future Google Sheets or DB updates
# It manages XP gain, multipliers, rep caps, and evolution

XP_PER_REP = 1  # Base XP per rep

# Mock user XP state
user_data = {
    "xp": 0,
    "level": 1,
    "buffs": [],
    "debuffs": [],
    "rep_log": {},  # e.g. {"pushups": 180, "squats": 50}
}

def get_level_threshold(level):
    return 100 + (level - 1) * 20  # Scaling XP needed per level

def add_xp(user_id, exercise, reps):
    global user_data

    # Update today's rep log for this exercise
    today = datetime.date.today().isoformat()
    key = f"{exercise}_{today}"
    prev_reps = user_data["rep_log"].get(key, 0)
    total_reps_today = prev_reps + reps
    user_data["rep_log"][key] = total_reps_today

    # Check for rep cap debuff (e.g. over 500 reps)
    debuffed = total_reps_today > 500
    if debuffed and "rep_cap" not in user_data["debuffs"]:
        user_data["debuffs"].append("rep_cap")

    # Check Bloodhowl Berserker trigger
    if total_reps_today > 100 and "bloodhowl" not in user_data["buffs"]:
        user_data["buffs"].append("bloodhowl")

    # Calculate XP
    base_xp = reps * XP_PER_REP
    xp = base_xp

    # Apply buffs
    if "bloodhowl" in user_data["buffs"]:
        xp *= 1.12
    if "emberlock" in user_data["buffs"]:
        xp *= 1.10

    # Apply debuffs
    if "rep_cap" in user_data["debuffs"]:
        xp *= 0.2  # -80% XP penalty

    # Update user XP and check level-up
    user_data["xp"] += int(xp)
    old_level = user_data["level"]
    threshold = get_level_threshold(old_level)
    leveled_up = False

    while user_data["xp"] >= threshold:
        user_data["xp"] -= threshold
        user_data["level"] += 1
        threshold = get_level_threshold(user_data["level"])
        leveled_up = True

    return {
        "xp_gained": int(xp),
        "total_xp": user_data["xp"],
        "level": user_data["level"],
        "leveled_up": leveled_up,
        "buffs": user_data["buffs"],
        "debuffs": user_data["debuffs"],
        "rep_log": user_data["rep_log"]
    }
