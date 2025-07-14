from features.quests.ui.daily.daily_quest_panel import DailyQuestSelectorView
# c:\Users\sakko\Downloads\RoFS (1)\RoFS\views\quest_dropdown.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import logging
from features.quests.ui.quest_reroll_ui import ConfirmRerollView
from features.quests.ui.quest_abandon_ui import AbandonQuestsView
## removed: from ui.embeds.weekly_contract_embed import build_weekly_contract_embed
from features.quests.ui.quest_panel import build_quest_panel_embed
from core.redis_cache import invalidate_user_json_cache
from discord.ui import Select, View
# Change line 14 from:
# from shared.utils.database import db as db_utils
# To:
from core.database import db as db_utils
from typing import Union

logger = logging.getLogger(__name__)

class QuestActionDropdown(discord.ui.Select):
    def __init__(self, bot, user_id: int):
        self.bot = bot
        self.user_id = user_id
        options = [
            discord.SelectOption(label="View Daily Quests", value="view_daily", emoji="<:scrollquill:1392885868397723738>"),
            discord.SelectOption(label="View Weekly Quests", value="view_weekly", emoji="<:hourglass:1392884696505122927>"),
            discord.SelectOption(label="Reroll Quests (Daily/Weekly)", value="reroll_quests", emoji="<:recycle:1392885233183100928>"),
            discord.SelectOption(label="Abandon Quests (Daily/Weekly)", value="abandon_quests", emoji="<:hazardsign:1392885089515602061>"),
        ]
        super().__init__(
            placeholder="Select a quest action...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"quest_action:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        import sentry_sdk
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu.", ephemeral=True)
            return
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        value = self.values[0]
        try:
            if value == "view_daily":
                # Reset page index to show active quest first
                from features.quests.ui.daily.daily_quest_panel import user_quest_pages
                user_quest_pages[interaction.user.id] = 0
                
                view = DailyQuestSelectorView(self.bot, interaction.user.id)
                await view.refresh_panel(interaction)
                view.message = interaction.message
            elif value == "view_weekly":
                from features.quests.ui.weekly.weekly_contract_panel import WeeklyQuestSelectorView, get_weekly_contracts, _weekly_pages
                
                # Reset page index to show active quest first
                _weekly_pages[interaction.user.id] = 0
                
                view = WeeklyQuestSelectorView(self.bot, interaction.user.id)
                await view.refresh_panel(interaction)
            elif value == "reroll_quests":
                # Show confirm reroll UI (combined for daily/weekly) with RPG/terminal style
                from features.quests.ui.quest_reroll_ui import ConfirmRerollView, build_reroll_confirm_embed
                view = ConfirmRerollView(self.bot, interaction.user)
                embed = build_reroll_confirm_embed(interaction.user)
                await interaction.edit_original_response(embed=embed, view=view)
            elif value == "abandon_quests":
                # Show abandon UI (combined for daily/weekly) with RPG-style embed
                async with self.bot.db_pool.acquire() as conn:
                    json_data = await db_utils.get_user_json_data(conn, self.user_id)
                daily_quests = json_data.get("daily_quests", {}).get("quests", [])
                has_daily = any(isinstance(q, dict) and q.get("active") for q in daily_quests)
                weekly_contracts_data = json_data.get("weekly_contracts", {})
                weekly_contracts = weekly_contracts_data.get("contracts", []) if isinstance(weekly_contracts_data, dict) else []
                has_weekly = any(isinstance(c, dict) and c.get("active") for c in weekly_contracts)
                view = AbandonQuestsView(self.bot, interaction.user, has_daily=has_daily, has_weekly=has_weekly)
                from features.quests.ui.quest_abandon_ui import build_abandon_quests_embed
                embed = build_abandon_quests_embed(interaction.user)
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.send_message("Unknown action.", ephemeral=True)
        except Exception as e:
            logger.error(f"Quest action failed for user {self.user_id}: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(f"QuestActionDropdown callback failed: {e}, user_id={self.user_id}, value={value}")
            await interaction.response.send_message("❌ Could not perform quest action.", ephemeral=True)

# The rest of the file can be extended with additional views/buttons as needed for more granular quest actions.
class QuestDropdown(Select):
    def __init__(self, bot, user_id: int):
        self.bot = bot
        self.user_id = user_id
        options = [
            discord.SelectOption(label="View Daily Quests", value="view_daily", emoji="<:scrollquill:1392885868397723738>"),
            discord.SelectOption(label="View Weekly Quests", value="view_weekly", emoji="<:hourglass:1392884696505122927>"),
            discord.SelectOption(label="Reroll Quests (Daily/Weekly)", value="reroll_quests", emoji="<:recycle:1392885233183100928>"),
            discord.SelectOption(label="Abandon Quests (Daily/Weekly)", value="abandon_quests", emoji="<:hazardsign:1392885089515602061>"),
        ]
        super().__init__(
            placeholder="Select a quest action...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"quest_action:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        import sentry_sdk
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu.", ephemeral=True)
            return
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        value = self.values[0]
        try:
            if value == "view_daily":
                # Reset page index to show active quest first
                from features.quests.ui.daily.daily_quest_panel import user_quest_pages
                user_quest_pages[interaction.user.id] = 0
                
                view = DailyQuestSelectorView(self.bot, interaction.user.id)
                await view.refresh_panel(interaction)
                view.message = interaction.message
            elif value == "view_weekly":
                from features.quests.ui.weekly.weekly_contract_panel import WeeklyQuestSelectorView, get_weekly_contracts, _weekly_pages
                
                # Reset page index to show active quest first
                _weekly_pages[interaction.user.id] = 0
                
                view = WeeklyQuestSelectorView(self.bot, interaction.user.id)
                await view.refresh_panel(interaction)
            elif value == "reroll_quests":
                # Show confirm reroll UI (combined for daily/weekly) with RPG/terminal style
                from features.quests.ui.quest_reroll_ui import ConfirmRerollView, build_reroll_confirm_embed
                view = ConfirmRerollView(self.bot, interaction.user)
                embed = build_reroll_confirm_embed(interaction.user)
                await interaction.edit_original_response(embed=embed, view=view)
            elif value == "abandon_quests":
                # Show abandon UI (combined for daily/weekly) with RPG-style embed
                async with self.bot.db_pool.acquire() as conn:
                    json_data = await db_utils.get_user_json_data(conn, self.user_id)
                daily_quests = json_data.get("daily_quests", {}).get("quests", [])
                has_daily = any(isinstance(q, dict) and q.get("active") for q in daily_quests)
                weekly_contracts_data = json_data.get("weekly_contracts", {})
                weekly_contracts = weekly_contracts_data.get("contracts", []) if isinstance(weekly_contracts_data, dict) else []
                has_weekly = any(isinstance(c, dict) and c.get("active") for c in weekly_contracts)
                view = AbandonQuestsView(self.bot, interaction.user, has_daily=has_daily, has_weekly=has_weekly)
                from features.quests.ui.quest_abandon_ui import build_abandon_quests_embed
                embed = build_abandon_quests_embed(interaction.user)
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.send_message("Unknown action.", ephemeral=True)
        except Exception as e:
            logger.error(f"Quest action failed for user {self.user_id}: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            sentry_sdk.capture_message(f"QuestDropdown callback failed: {e}, user_id={self.user_id}, value={value}")
            await interaction.response.send_message("❌ Could not perform quest action.", ephemeral=True)