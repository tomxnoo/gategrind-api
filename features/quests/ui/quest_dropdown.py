from features.quests.ui.daily.daily_quest_panel import DailyQuestSelectorView
# c:\Users\sakko\Downloads\RoFS (1)\RoFS\views\quest_dropdown.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import logging
import asyncio  # Add missing import for loading animation
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

class QuestDropdown(discord.ui.Select):
    """Unified quest dropdown with loading animations and proper error handling."""
    
    def __init__(self, bot, user_id: int, ephemeral: bool = False, with_loading: bool = True):
        self.bot = bot
        self.user_id = user_id
        self.ephemeral = ephemeral
        self.with_loading = with_loading
        
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
        
        # Validate user
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your menu.", ephemeral=True)
            return
        
        value = self.values[0]
        
        # Only defer for actions that don't use loading animations
        if not (self.with_loading and value in ["view_daily", "view_weekly"]):
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=self.ephemeral)
        
        # Add loading animation for quest views if enabled
        loading_task = None
        stop_loading = None
        if self.with_loading and value in ["view_daily", "view_weekly"]:
            # Defer the interaction first for loading animation
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=self.ephemeral)
            from shared.utils.ui_helpers import create_loading_animation
            loading_task, stop_loading = await create_loading_animation(interaction, interaction.user)
        
        try:
            if value == "view_daily":
                await self._handle_view_daily(interaction, loading_task, stop_loading)
            elif value == "view_weekly":
                await self._handle_view_weekly(interaction, loading_task, stop_loading)
            elif value == "reroll_quests":
                await self._handle_reroll_quests(interaction)
            elif value == "abandon_quests":
                await self._handle_abandon_quests(interaction)
            else:
                await self._handle_unknown_action(interaction)
                
        except Exception as e:
            await self._handle_error(interaction, e, loading_task, stop_loading, value)
    
    async def _handle_view_daily(self, interaction: discord.Interaction, loading_task, stop_loading):
        """Handle viewing daily quests."""
        from features.quests.ui.daily.daily_quest_panel import user_quest_pages
        user_quest_pages[interaction.user.id] = 0
        
        view = DailyQuestSelectorView(self.bot, interaction.user.id)
        
        # Stop loading BEFORE UI update to prevent race condition
        if stop_loading:
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            # Add delay to ensure loading animation fully stops
            await asyncio.sleep(0.1)
        
        # Now safely update the UI without conflicts
        await view.refresh_panel(interaction)
        view.message = interaction.message
    
    async def _handle_view_weekly(self, interaction: discord.Interaction, loading_task, stop_loading):
        """Handle viewing weekly quests."""
        from features.quests.ui.weekly.weekly_contract_panel import WeeklyQuestSelectorView, _weekly_pages
        _weekly_pages[interaction.user.id] = 0
        
        view = WeeklyQuestSelectorView(self.bot, interaction.user.id)
        
        # Stop loading BEFORE UI update to prevent race condition
        if stop_loading:
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            # Add delay to ensure loading animation fully stops
            await asyncio.sleep(0.1)
        
        # Now safely update the UI without conflicts
        await view.refresh_panel(interaction)
    
    async def _stop_loading_animation(self, loading_task, stop_loading):
        """Stop the loading animation safely."""
        stop_loading()
        try:
            await asyncio.wait_for(loading_task, timeout=1.0)
        except asyncio.TimeoutError:
            loading_task.cancel()
        
        # Remove this delay since we're stopping before UI updates now
        # await asyncio.sleep(0.35)
    
    async def _handle_reroll_quests(self, interaction: discord.Interaction):
        """Handle quest reroll action."""
        from features.quests.ui.quest_reroll_ui import ConfirmRerollView, build_reroll_confirm_embed
        view = ConfirmRerollView(self.bot, interaction.user)
        embed = build_reroll_confirm_embed(interaction.user)
        await interaction.edit_original_response(embed=embed, view=view)
    
    async def _handle_abandon_quests(self, interaction: discord.Interaction):
        """Handle quest abandon action."""
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
    
    async def _handle_unknown_action(self, interaction: discord.Interaction):
        """Handle unknown action."""
        if self.ephemeral:
            await interaction.response.send_message("Unknown action.", ephemeral=True)
        else:
            await interaction.edit_original_response(content="❌ Unknown action.", embed=None, view=None)
    
    async def _stop_loading_animation(self, loading_task, stop_loading):
        """Stop the loading animation safely."""
        stop_loading()
        try:
            await asyncio.wait_for(loading_task, timeout=1.0)
        except asyncio.TimeoutError:
            loading_task.cancel()
        
        # Add delay to ensure UI transition completes properly
        await asyncio.sleep(0.35)
    
    async def _handle_error(self, interaction: discord.Interaction, error: Exception, loading_task, stop_loading, value: str):
        """Handle errors with proper cleanup."""
        import sentry_sdk
        
        # Stop loading animation on error
        if stop_loading:
            await self._stop_loading_animation(loading_task, stop_loading)
        
        logger.error(f"Quest action failed for user {self.user_id}: {error}", exc_info=True)
        sentry_sdk.capture_exception(error)
        sentry_sdk.capture_message(f"QuestDropdown callback failed: {error}, user_id={self.user_id}, value={value}")
        
        if self.ephemeral:
            await interaction.response.send_message("❌ Could not perform quest action.", ephemeral=True)
        else:
            await interaction.edit_original_response(content="❌ Could not perform quest action.", embed=None, view=None)


# Legacy aliases for backward compatibility
class QuestActionDropdown(QuestDropdown):
    """Legacy alias for QuestDropdown with non-ephemeral responses and loading enabled."""
    
    def __init__(self, bot, user_id: int):
        super().__init__(bot, user_id, ephemeral=False, with_loading=True)