# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
from typing import Union, List, Optional
from datetime import datetime, timezone

from shared.utils.ui_styles import get_panel_sub_header, PRIMARY_COLOR
from shared.utils.headers import get_system_status_header
from shared.utils.common_views import EphemeralPanelView
from shared.utils.ui_helpers import run_with_animation, DEFAULT_UI_DELAY
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.models.incursion import IncursionType, IncursionStatus

class IncursionPanel:
    """Main panel for displaying active Shadow Incursions"""
    
    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
        """Render the main incursion panel embed"""
        header = get_system_status_header(user)
        sub_header = get_panel_sub_header("incursions")
        
        # Get active incursions
        manager = IncursionManager(bot.db_pool)
        active_incursions = await manager.get_active_incursions()
        user_progress = await manager.get_user_progress(user.id)
        
        # Build content
        if not active_incursions:
            content = (
                "```ansi\n"
                f"{header}\n"
                "🌑 [ SHADOW INCURSIONS MODULE ]\n"
                "System: SHADOW_PACT // Incursion Access [GRANTED]\n"
                "──────────────────────────\n\n"
                "\x1b[2;37m● Status: No active incursions detected\x1b[0m\n"
                "\x1b[2;37m● Shadow Realm: Dormant\x1b[0m\n"
                "\x1b[2;37m● Next Scan: Automated\x1b[0m\n\n"
                "The shadows lie still... for now.\n"
                "──────────────────────────\n"
                "```"
            )
        else:
            content_lines = [
                "```ansi",
                header,
                "🌑 [ SHADOW INCURSIONS MODULE ]",
                "System: SHADOW_PACT // Incursion Access [GRANTED]",
                "──────────────────────────",
                ""
            ]
            
            for i, incursion in enumerate(active_incursions[:3]):  # Show max 3
                # Get user's progress for this incursion
                progress = user_progress.get(incursion.id, 0)
                progress_pct = min(100, (progress / incursion.target_reps) * 100) if incursion.target_reps > 0 else 0
                
                # Progress bar
                filled = int(progress_pct / 10)
                bar = "█" * filled + "░" * (10 - filled)
                
                # Type styling
                type_colors = {
                    IncursionType.SURGE: "\x1b[1;32m",      # Bright green
                    IncursionType.CHALLENGE: "\x1b[1;33m",  # Bright yellow  
                    IncursionType.ANOMALY: "\x1b[1;35m"     # Bright magenta
                }
                color = type_colors.get(incursion.incursion_type, "\x1b[1;37m")
                
                # Time remaining
                time_left = incursion.expires_at - datetime.now(timezone.utc)
                hours_left = int(time_left.total_seconds() / 3600)
                
                content_lines.extend([
                    f"{color}● {incursion.title}\x1b[0m",
                    f"  Type: {incursion.incursion_type.value.upper()} | {hours_left}h remaining",
                    f"  Progress: [{bar}] {progress}/{incursion.target_reps} ({progress_pct:.0f}%)",
                    f"  Reward: {incursion.reward_description}",
                    ""
                ])
            
            if len(active_incursions) > 3:
                content_lines.append(f"\x1b[2;37m... and {len(active_incursions) - 3} more\x1b[0m")
            
            content_lines.extend([
                "──────────────────────────",
                "```"
            ])
            content = "\n".join(content_lines)
        
        embed = discord.Embed(
            description=content,
            color=int(PRIMARY_COLOR.replace("#", ""), 16)
        )
        
        if active_incursions:
            embed.set_footer(text="💡 Use buttons below to interact with incursions")
        
        return embed
    
    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member]) -> discord.ui.View:
        """Build the interactive view for the incursion panel"""
        manager = IncursionManager(bot.db_pool)
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
        
        # Add navigation buttons if there are incursions
        if active_incursions:
            if len(active_incursions) > 1:
                self.add_item(PrevIncursionButton(self))
                self.add_item(NextIncursionButton(self))
            
            self.add_item(ViewDetailsButton(self))
            self.add_item(ParticipateButton(self))
        
        # Add refresh button
        self.add_item(RefreshButton(self))
        
        # Add panel selector (standard across all panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(self.bot, self.user_id))

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
            current_incursion = self.parent_view.active_incursions[self.parent_view.current_page]
            view = IncursionDetailsView(self.parent_view.bot, interaction.user, current_incursion, self.parent_view)
            embed = await view.render_details_embed()
            return embed, view
        
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
            # Refresh the incursions data
            manager = IncursionManager(self.parent_view.bot.db_pool)
            self.parent_view.active_incursions = await manager.get_active_incursions()
            self.parent_view.current_page = 0
            
            embed = await IncursionPanel.render_embed(self.parent_view.bot, interaction.user)
            new_view = await IncursionPanel.build_view(self.parent_view.bot, interaction.user)
            return embed, new_view
        
        await run_with_animation(interaction, do_work())