# quest_panel.py
# Unified panel for quest log UI, views, and embeds
from typing import Union

import discord

from core.redis_cache import get_or_cache_user_json_data
from features.quests.ui.daily.daily_quest_panel import build_daily_quest_panel_embed
from shared.utils.ui_styles import get_panel_sub_header
## removed: from ui.embeds.weekly_contract_embed import build_weekly_contract_embed
from shared.utils.headers import get_system_status_header
from shared.utils.panel_registry import register


# --- EMBED LOGIC ---
async def build_quest_panel_embed(bot, user):
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("quests")
    embed = discord.Embed(
        description=f"```ansi\n{header}\n{sub_header}\n```",
        color=discord.Color.dark_teal()
    )
    embed.set_footer(text="Obsidian Archive • Pact Management Node")
    json_data = await get_or_cache_user_json_data(bot, user.id)
    daily_quests = json_data.get("daily_quests", {}).get("quests", [])
    daily_quests = [q for q in daily_quests if isinstance(q, dict)]
    # --- Daily Quest Panel Section ---
    from features.quests.ui.daily.daily_quest_panel import build_daily_quest_panel_embed
    from features.quests.ui.daily.daily_quest_ansi import render_daily_quest_ansi_block
    if daily_quests:
        active_quest = next((q for q in daily_quests if q.get("active")), None)
        if active_quest:
            daily_quest_block = render_daily_quest_ansi_block(active_quest, user)
            dq_value = f"```ansi\n{daily_quest_block}\n```"
            embed.add_field(name="— DAILY QUEST —", value=dq_value, inline=False)
        else:
            dq_value = "```ansi\nNo active quest.\n```"
            embed.add_field(name="— DAILY QUEST —", value=dq_value, inline=False)
    else:
        dq_value = "```ansi\nNo daily quests found.\n```"
        embed.add_field(name="— DAILY QUEST —", value=dq_value, inline=False)
    weekly_contracts_data = json_data.get("weekly_contracts", {})
    weekly_contracts = weekly_contracts_data.get("contracts", []) if isinstance(weekly_contracts_data, dict) else []
    if not weekly_contracts:
        # Generate contracts if none exist
        from features.quests.ui.weekly.weekly_contract_panel import get_weekly_contracts
        weekly_contracts = await get_weekly_contracts(user.id, bot=bot)
        # Refresh json_data in case it was updated
        json_data = await get_or_cache_user_json_data(bot, user.id)
        weekly_contracts_data = json_data.get("weekly_contracts", {})
        weekly_contracts = weekly_contracts_data.get("contracts", []) if isinstance(weekly_contracts_data, dict) else []
    active_contract = next((c for c in weekly_contracts if c.get("active")), None)
    if active_contract:
        from features.quests.ui.weekly.weekly_contract_ansi import render_weekly_contract_ansi_block
        ansi_block = render_weekly_contract_ansi_block(active_contract, user)
        weekly_value = f"```ansi\n{ansi_block}\n```"
        embed.add_field(name="— WEEKLY CONTRACT —", value=weekly_value, inline=False)
    elif weekly_contracts:
        embed.add_field(name="— WEEKLY CONTRACT —", value="```ansi\nYou have weekly contracts available, but none are active. Please accept a contract!\n```", inline=False)
    else:
        embed.add_field(name="— WEEKLY CONTRACT —", value="```ansi\nNo weekly contracts found.\n```", inline=False)
    return embed

# --- VIEW/SELECTOR LOGIC ---
from shared.utils.common_views import EphemeralPanelSelect


@register
class QuestPanel:
    key = "quest_log"
    label = "Quest Panel"
    emoji = "🗺️"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_quest_panel_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        from features.quests.ui.quest_dropdown import QuestActionDropdown
        view = discord.ui.View(timeout=None)
        view.add_item(EphemeralPanelSelect(bot, user.id))
        view.add_item(QuestActionDropdown(bot, user.id))
        return view