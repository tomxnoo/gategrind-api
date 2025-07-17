# ui/weekly_contract_ansi.py
# Contains render_weekly_contract_ansi_block, moved to break circular imports

def render_weekly_contract_ansi_block(contract: dict, user) -> str:
    name = contract.get("ContractName", "Unknown Contract")
    flavor = contract.get("Flavor", "")
    objectives = contract.get("Objectives", [])
    progress = contract.get("Progress", {}) or {}
    xp = contract.get("XPReward", 0)
    buff = contract.get("BuffReward")
    is_completed = contract.get("_completed_flag", False)
    is_active = contract.get("active", False)
    lines = []
    # No duplicate header
    lines.append(name)
    if flavor:
        lines.append(flavor)
    if is_active:
        lines.append("[ACTIVE]")
        lines.append("You are currently undertaking this contract!")
    elif is_completed:
        lines.append("[COMPLETED]")
        lines.append("This contract is completed.")
    else:
        lines.append("[INACTIVE]")
        lines.append("This contract is not currently active.")
    # Objectives
    lines.append("")
    for obj in objectives:
        obj_type = obj.get("type")
        target = obj.get("target", 0)
        if obj_type == "reps":
            prog = progress.get(obj.get("movement", "unknown_reps"), 0)
            lines.append(f"{obj.get('movement')}: {prog}/{target} reps")
        elif obj_type == "complete_dailies":
            prog = progress.get("complete_dailies", 0)
            lines.append(f"Complete Daily Quests: {prog}/{target}")
        elif obj_type == "training_days":
            prog = len(progress.get("training_dates", []))
            lines.append(f"Train on Different Days: {prog}/{target} days")
        else:
            lines.append(f"Objective: {obj.get('type')} - {obj.get('target')}")
    lines.append("")
    # Rewards
    lines.append(f"+{xp} XP (Completion)")
    if buff:
        lines.append(f"{buff}")
    return "\n".join(lines)
