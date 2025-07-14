# ui/daily_quest_ansi.py
# Contains render_daily_quest_ansi_block for use in daily_quest_panel.py

def render_daily_quest_ansi_block(quest: dict, user) -> str:
    """Render daily quest in ANSI format similar to weekly contracts"""
    name = quest.get("QuestName", "Unknown Quest")
    flavor = quest.get("Flavor", "")
    tier = quest.get("Tier", 1)
    movements = quest.get("Movements", [])
    targets = quest.get("Targets", {})
    progress = quest.get("Progress", {})
    xp_reward = quest.get("XPReward", 0)
    buff_reward = quest.get("BuffReward")
    is_active = quest.get("Active", False) or quest.get("active", False)
    is_completed = quest.get("Completed", False) or quest.get("_completed_flag", False)
    
    lines = []
    
    # Quest name and tier
    lines.append(f"**T{tier}: {name}** (Tier {tier})")
    
    # Flavor text
    if flavor:
        lines.append(flavor)
    
    # Status
    if is_active:
        lines.append("[ACTIVE]")
        lines.append("You are currently undertaking this quest!")
    elif is_completed:
        lines.append("[COMPLETED]")
        lines.append("This quest is completed.")
    else:
        lines.append("[INACTIVE]")
        lines.append("This quest is not currently active.")
    
    lines.append("")
    
    # Objectives/Movements with proper progress display
    if movements:
        for movement in movements:
            target_reps = targets.get(movement, 0)
            current_progress = progress.get(movement, 0)
            # Format: Movement: {'reps': current, 'sets': current}/target reps
            if isinstance(current_progress, dict):
                reps = current_progress.get('reps', 0)
                sets = current_progress.get('sets', 0)
                lines.append(f"{movement}: {{'reps': {reps}, 'sets': {sets}}}/{target_reps} reps")
            else:
                lines.append(f"{movement}: {current_progress}/{target_reps} reps")
    
    lines.append("")
    
    # Rewards
    lines.append(f"+{xp_reward} XP (Completion)")
    if buff_reward:
        lines.append(f"{buff_reward}")
    
    return "\n".join(lines)
