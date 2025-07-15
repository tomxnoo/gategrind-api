# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
import sentry_sdk
from typing import Union, List, Optional
from datetime import datetime, timezone

from shared.utils.ui_styles import get_panel_sub_header, PRIMARY_COLOR
from shared.utils.headers import get_system_status_header
from shared.utils.common_views import EphemeralPanelView
from shared.utils.ui_helpers import run_with_animation, DEFAULT_UI_DELAY
from shared.utils.panel_registry import register
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.models.incursion import IncursionType  # Remove IncursionStatus
from features.incursions.ui.participation_modal import ParticipationModal  # Add missing import

@register
class IncursionPanel:
    """Main panel for displaying active Shadow Incursions"""
    
    # Required attributes for panel registration
    key = "incursions"
    label = "Shadow Incursions"
    emoji = "🌑"
    
    @staticmethod
    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
        """Render the main incursion panel embed"""
        # Fix header implementation to match other panels
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("incursions")
        
        # Get active incursions - FIXED: Pass bot object instead of bot.db_pool
        manager = IncursionManager(bot)
        active_incursions = await manager.get_active_incursions()
        
        if not active_incursions:
            content = f"```ansi\n{header}\n{sub_header}\n\n\x1b[1;31mNo active incursions found.\x1b[0m\n\nShadow Incursions are temporary challenges that appear\nperiodically. Check back later for new opportunities.\n```"
        else:
            current_incursion = active_incursions[0]
            # Fix ZeroDivisionError: Add safety check for target_reps
            if current_incursion.target_reps > 0:
                progress_percent = min(100, (current_incursion.current_reps / current_incursion.target_reps) * 100)
            else:
                progress_percent = 0
            
            # Create visual progress bar with custom emojis
            filled_squares = int(progress_percent / 10)  # Each square represents 10%
            empty_squares = 10 - filled_squares
            progress_bar = "🟩" * filled_squares + "⬜️" * empty_squares
            
            # Get participant count
            participant_count = await manager.get_participant_count(current_incursion.incursion_id)
            
            content = f"```ansi\n{header}\n{sub_header}\n\n\x1b[1;35m{current_incursion.title}\x1b[0m\nType: {current_incursion.incursion_type.value.upper()} | {current_incursion.target_exercise}\n\nProgress: [{progress_bar}] {progress_percent:.0f}%\n\nCurrent: {current_incursion.current_reps}/{current_incursion.target_reps} reps\nReward: {current_incursion.reward_description}\nParticipants: {participant_count}\n```"
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.dark_purple()
        )
        # Fix footer to match panel design
        embed.set_footer(text="Shadow Archive • Incursion Command Node")
        return embed
    
    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        """Build the interactive view for the incursion panel"""
        # FIXED: Pass bot object instead of bot.db_pool
        manager = IncursionManager(bot)
        active_incursions = await manager.get_active_incursions()
        
        view = IncursionPanelView(bot, user, active_incursions)
        return view

class IncursionPanelView(discord.ui.View):
    """Interactive view for the incursion panel"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], active_incursions: List):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        self.active_incursions = active_incursions
        self.current_page = 0
        
        # Add dropdown FIRST (above buttons like other panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Then add action buttons
        if active_incursions:
            self.add_item(ViewDetailsButton(self))
            self.add_item(ParticipateButton(self))
            
            if len(active_incursions) > 1:
                self.add_item(PrevIncursionButton(self))
                self.add_item(NextIncursionButton(self))
        
        self.add_item(RefreshButton(self))
        
        # REMOVED: Duplicate EphemeralPanelSelect that was causing the error
        # from shared.utils.common_views import EphemeralPanelSelect
        # self.add_item(EphemeralPanelSelect(self.bot, self.user_id))

class PrevIncursionButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="⬅️ Prev", style=discord.ButtonStyle.primary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        async def do_work():
            self.parent_view.current_page = (self.parent_view.current_page - 1) % len(self.parent_view.active_incursions)
            embed = await IncursionPanel.render_embed(self.parent_view.bot, interaction.user)
            return embed, self.parent_view
        
        await run_with_animation(interaction, do_work())

class NextIncursionButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Next ➡️", style=discord.ButtonStyle.primary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        async def do_work():
            self.parent_view.current_page = (self.parent_view.current_page + 1) % len(self.parent_view.active_incursions)
            embed = await IncursionPanel.render_embed(self.parent_view.bot, interaction.user)
            return embed, self.parent_view
        
        await run_with_animation(interaction, do_work())

class ViewDetailsButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="📋 View Details", style=discord.ButtonStyle.success)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        if not self.parent_view.active_incursions:
            await interaction.response.send_message("❌ No active incursions to view.", ephemeral=True)
            return
        
        async def do_work():
            try:
                current_incursion = self.parent_view.active_incursions[self.parent_view.current_page]
                sentry_sdk.add_breadcrumb(
                    message=f"ViewDetailsButton: Loading details for incursion {current_incursion.incursion_id}",
                    level="info"
                )
                
                from features.incursions.ui.incursion_details import IncursionDetailsView
                view = IncursionDetailsView(self.parent_view.bot, interaction.user, current_incursion, self.parent_view)
                
                sentry_sdk.add_breadcrumb(
                    message="ViewDetailsButton: IncursionDetailsView created, rendering embed",
                    level="info"
                )
                
                embed = await view.render_details_embed()
                
                sentry_sdk.add_breadcrumb(
                    message="ViewDetailsButton: Embed rendered successfully",
                    level="info"
                )
                
                return embed, view
            except Exception as e:
                sentry_sdk.capture_exception(e)
                sentry_sdk.add_breadcrumb(
                    message=f"ViewDetailsButton: Error occurred - {str(e)}",
                    level="error"
                )
                raise
        
        await run_with_animation(interaction, do_work())

class ParticipateButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="⚡ Participate", style=discord.ButtonStyle.success)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        if not self.parent_view.active_incursions:
            await interaction.response.send_message("❌ No active incursions to participate in.", ephemeral=True)
            return
        
        current_incursion = self.parent_view.active_incursions[self.parent_view.current_page]
        
        # Show participation modal
        modal = ParticipationModal(self.parent_view.bot, current_incursion)
        await interaction.response.send_modal(modal)

class RefreshButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        async def do_work():
            # Refresh the incursions data - FIXED: Pass bot object instead of bot.db_pool
            manager = IncursionManager(self.parent_view.bot)
            self.parent_view.active_incursions = await manager.get_active_incursions()
            self.parent_view.current_page = 0
            
            embed = await IncursionPanel.render_embed(self.parent_view.bot, interaction.user)
            new_view = await IncursionPanel.build_view(self.parent_view.bot, interaction.user)
            return embed, new_view
        
        await run_with_animation(interaction, do_work())