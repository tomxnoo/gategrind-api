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
        
        # Only defer for actions that don't use run_with_animation
        if value not in ["view_daily", "view_weekly"]:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=self.ephemeral)
        
        try:
            if value == "view_daily":
                await self._handle_view_daily(interaction, None, None)
            elif value == "view_weekly":
                await self._handle_view_weekly(interaction, None, None)
            elif value == "reroll_quests":
                await self._handle_reroll_quests(interaction)
            elif value == "abandon_quests":
                await self._handle_abandon_quests(interaction)
            else:
                await self._handle_unknown_action(interaction)
                
        except Exception as e:
            await self._handle_error(interaction, e, None, None, value)
    
    async def _handle_view_daily(self, interaction: discord.Interaction, loading_task, stop_loading):
        """Handle viewing daily quests with run_with_animation."""
        from features.quests.ui.daily.daily_quest_panel import _daily_pages
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            _daily_pages[interaction.user.id] = 0
            view = DailyQuestSelectorView(self.bot, interaction.user.id)
            
            # Get the current quest data to build the embed
            from features.quests.logic.daily_quests.daily_quest_logic import get_today_quests
            quests = await get_today_quests(interaction.user.id, self.bot)
            
            if not quests:
                no_quests_embed = discord.Embed(
                    description="❌ No daily quests found in the shadow realm.", 
                    color=discord.Color.red()
                )
                return no_quests_embed, view
            
            # Get the current quest and build the embed
            current_quest = quests[0]  # Default to first quest
            embed = await view.build_embed(self.bot, current_quest, interaction.user)
            
            # Update button states
            is_completed = bool(current_quest.get("_completed_flag") or current_quest.get("Completed"))
            is_current_active = bool(current_quest.get("active"))
            
            if is_completed:
                view.details_btn.disabled = True
                view.details_btn.label = "Completed"
                view.details_btn.style = discord.ButtonStyle.success
            elif is_current_active:
                view.details_btn.disabled = True
                view.details_btn.label = "Active Quest"
                view.details_btn.style = discord.ButtonStyle.secondary
            else:
                view.details_btn.disabled = False
                view.details_btn.label = "View Details"
                view.details_btn.style = discord.ButtonStyle.primary
            
            view.message = interaction.message
            return embed, view
        
        await run_with_animation(interaction, do_work)

    async def _handle_view_weekly(self, interaction: discord.Interaction, loading_task, stop_loading):
        """Handle viewing weekly quests with run_with_animation."""
        from features.quests.ui.weekly.weekly_contract_panel import WeeklyQuestSelectorView, _weekly_pages
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            _weekly_pages[interaction.user.id] = 0
            view = WeeklyQuestSelectorView(self.bot, interaction.user.id)
            
            # Get the current weekly contracts to build the embed
            from features.quests.ui.weekly.weekly_contract_panel import get_weekly_contracts
            contracts = await get_weekly_contracts(interaction.user.id, self.bot)
            
            if not contracts:
                no_contracts_embed = discord.Embed(
                    description="❌ No weekly contracts found in the shadow realm.", 
                    color=discord.Color.red()
                )
                return no_contracts_embed, view
            
            # Get the current contract and build the embed
            current_contract = contracts[0]  # Default to first contract
            embed = await view.build_embed(self.bot, current_contract, interaction.user)
            
            # Update button states
            is_completed = bool(current_contract.get("_completed_flag") or current_contract.get("Completed"))
            is_current_active = bool(current_contract.get("active"))
            
            if is_completed:
                view.details_btn.disabled = True
                view.details_btn.label = "Completed"
                view.details_btn.style = discord.ButtonStyle.success
            elif is_current_active:
                view.details_btn.disabled = True
                view.details_btn.label = "Active Quest"
                view.details_btn.style = discord.ButtonStyle.secondary
            else:
                view.details_btn.disabled = False
                view.details_btn.label = "View Details"
                view.details_btn.style = discord.ButtonStyle.primary
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

    # Remove the duplicate _stop_loading_animation method (lines 119-126)
    # Keep only the one at lines 155-162
    
    async def _handle_error(self, interaction: discord.Interaction, error: Exception, loading_task, stop_loading, value: str):
        """Handle errors with proper cleanup."""
        import sentry_sdk
        
        # Stop loading animation on error
        if stop_loading:
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
        
        # Remove the cleanup_loading_state call since it doesn't exist
        
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