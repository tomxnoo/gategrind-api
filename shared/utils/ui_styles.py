PRIMARY_COLOR = "#9146FF"  # <--- Add this line

PANEL_ICONS = {
    "profile": "📋",
    "quests": "🏆",
    "buffs": "🧬",
    "log": "📈",
    "system_hub": "💻",
    "daily_quest": "📜",
    "weekly_contract": "📅",
    "default": "◼️",
}

PANEL_SUB_HEADERS = {
    "profile": "[ PROFILE MODULE ]\nSystem: SHADOW_PACT // Profile Access [GRANTED]\n──────────────────────────",
    "quests": "[ QUEST LOG MODULE ]\nSystem: SHADOW_PACT // Quest Log Access [GRANTED]\n──────────────────────────",
    "buffs": "[ BUFFS MODULE ]\nSystem: SHADOW_PACT // Buffs Access [GRANTED]\n──────────────────────────",
    "log": "[ LOG MODULE ]\nSystem: SHADOW_PACT // Log Access [GRANTED]\n──────────────────────────",
    "system_hub": "[ SYSTEM HUB MODULE ]\nSystem: SHADOW_PACT // System Hub Access [GRANTED]\n──────────────────────────",
    "daily_quest": "[ DAILY QUEST MODULE ]\nSystem: SHADOW_PACT // Daily Quest Access [GRANTED]\n──────────────────────────",
    "weekly_contract": "[ WEEKLY CONTRACT MODULE ]\nSystem: SHADOW_PACT // Weekly Contract Access [GRANTED]\n──────────────────────────",
    "log_complete": "[ LOG COMPLETE MODULE ]\nSystem: SHADOW_PACT // Log Complete Access [GRANTED]\n──────────────────────────",
    "quest_accept": "[ QUEST ACCEPT MODULE ]\nSystem: SHADOW_PACT // Quest Accept Access [GRANTED]\n──────────────────────────",
    "quest_abandon": "[ QUEST ABANDON MODULE ]\nSystem: SHADOW_PACT // Quest Abandon Access [GRANTED]\n──────────────────────────",
    "quest_abandon_confirm": "[ QUEST ABANDON CONFIRMATION ]\nSystem: SHADOW_PACT // Quest Abandon Confirm [GRANTED]\n──────────────────────────",
    "level_up": "[ LEVEL UP MODULE ]\nSystem: SHADOW_PACT // Level Up Access [GRANTED]\n──────────────────────────",
    "incursions": "[ INCURSION DETAILS MODULE ]\nSystem: SHADOW_PACT // Incursion Details Access [GRANTED]\n──────────────────────────",
    # Add more panels as needed
}

def get_panel_icon(panel_key):
    return PANEL_ICONS.get(panel_key, PANEL_ICONS["default"])

def get_panel_sub_header(panel_key):
    return PANEL_SUB_HEADERS.get(panel_key, f"[ {panel_key.upper()} MODULE ]\nSystem: SHADOW_PACT // Access [GRANTED]\n──────────────────────────")

def render_panel_template(header, panel_key, panel_title, body_content):
    icon = get_panel_icon(panel_key)
    sep = "──────────────────────────"
    # Compose a unified string description for the embed or message
    return f"{header}\n{icon} {panel_title}\n{body_content}\n{sep}"
