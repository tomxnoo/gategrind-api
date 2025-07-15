# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Union
from datetime import datetime, timezone

from shared.utils.ui_styles import PRIMARY_COLOR, get_panel_sub_header
from shared.utils.headers import get_system_status_header
from shared.utils.ui_helpers import run_with_animation
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.models.incursion import IncursionType

async def render_details_embed(bot, user: Union[discord.User, discord.Member], incursion) -> discord.Embed:
    """Render detailed embed for a specific incursion"""
    # Fix header implementation to match other panels
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    
    # Get additional data - FIXED: Pass bot object instead of bot.db_pool
    manager = IncursionManager(bot)
    participant_count = await manager.get_participant_count(incursion.incursion_id)
    
    progress_percent = min(100, (incursion.current_reps / incursion.target_reps) * 100)
    
    # Create visual progress bar with custom emojis
    filled_squares = int(progress_percent / 10)  # Each square represents 10%
    empty_squares = 10 - filled_squares
    progress_bar = "🟩" * filled_squares + "⬜️" * empty_squares
    
    time_remaining = incursion.expires_at - datetime.now()
    hours_left = max(0, int(time_remaining.total_seconds() / 3600))
    
    content_lines = [
        "```ansi",
        header,
        "🌑 [ INCURSION DETAILS ]",
        "System: SHADOW_PACT // Incursion Access [GRANTED]",
        "──────────────────────────",
        f"\x1b[1;37m{incursion.title}\x1b[0m",
        "",
        f"Type: {incursion.incursion_type.value.upper()}",
        f"Target: {incursion.target_exercise}",
        "```",
        f"Progress: [{progress_bar}] {progress_percent:.0f}%",
        "```ansi",
        f"Current: {incursion.current_reps}/{incursion.target_reps} reps",
        f"Participants: {participant_count}",
        f"Time Remaining: {hours_left}h",
        "",
        "\x1b[1;33mReward:\x1b[0m",
        f"{incursion.reward_description}",
        "",
        "\x1b[1;32mDescription:\x1b[0m",
        f"{incursion.description}",
        "```"
    ]
    
    embed = discord.Embed(
        description="\n".join(content_lines),
        color=_get_incursion_color(incursion.incursion_type)
    )
    # Fix footer to match panel design
    embed.set_footer(text="Shadow Archive • Incursion Details")
    return embed

class IncursionDetailsView(discord.ui.View):
    """Detailed view for a specific incursion"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], incursion, previous_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        self.incursion = incursion
        self.previous_view = previous_view
        
        # Add participate button first
        self.add_item(ParticipateDetailButton(self.bot, self.incursion))
        
        # Add leaderboard button
        self.add_item(LeaderboardButton(self.bot, self.incursion))
        
        # Add back button last (rightmost position)
        self.add_item(BackToIncursionsButton(self.previous_view))
        
        # REMOVED: All duplicate buttons
    
    async def render_details_embed(self) -> discord.Embed:
        """Render detailed incursion information"""
        # Use universal header and sub-header pattern
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("incursions")
        
        # Get user progress - FIXED: Pass bot object instead of bot.db_pool
        manager = IncursionManager(self.bot)
        user_progress = await manager.get_user_progress(self.user.id)
        progress = user_progress.get(self.incursion.id, 0)
        progress_pct = min(100, (progress / self.incursion.target_reps) * 100) if self.incursion.target_reps > 0 else 0
        
        # Create visual progress bar with custom emojis (consistent with main panel)
        filled_squares = int(progress_pct / 5)  # Each square represents 5% for detail view (20 total)
        empty_squares = 20 - filled_squares
        progress_bar = "🟩" * filled_squares + "⬜️" * empty_squares
        
        # Time remaining
        time_left = self.incursion.expires_at - datetime.now(timezone.utc)
        hours_left = int(time_left.total_seconds() / 3600)
        minutes_left = int((time_left.total_seconds() % 3600) / 60)
        
        # Type-specific styling (consistent with panel view)
        type_colors = {
            IncursionType.SURGE: "\x1b[1;33m",      # Bright orange (changed from green)
            IncursionType.CHALLENGE: "\x1b[1;36m",  # Bright cyan
            IncursionType.ANOMALY: "\x1b[1;35m"     # Bright magenta
        }
        color = type_colors.get(self.incursion.incursion_type, "\x1b[1;37m")
        
        # Get participant count
        participant_count = await manager.get_participant_count(self.incursion.incursion_id)
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"{color}● {self.incursion.title}\x1b[0m\n"
            f"Type: {self.incursion.incursion_type.value.upper()}\n"
            f"Exercise: {self.incursion.target_exercise}\n\n"
            f"\x1b[1;37mDescription:\x1b[0m\n"
            f"{self.incursion.description}\n\n"
            f"\x1b[1;37mYour Progress:\x1b[0m\n"
            f"[{progress_bar}] {progress}/{self.incursion.target_reps} ({progress_pct:.1f}%)\n\n"
            f"\x1b[1;37mReward:\x1b[0m {self.incursion.reward_description}\n"
            f"\x1b[1;37mParticipants:\x1b[0m {participant_count} warriors\n"
            f"\x1b[1;37mTime Remaining:\x1b[0m {hours_left}h {minutes_left}m\n\n"
        )
        
        # Add special effects for anomalies
        if self.incursion.incursion_type == IncursionType.ANOMALY and self.incursion.metadata.get('special_effects'):
            content += (
                f"\x1b[1;35m⚠️ ANOMALY EFFECTS:\x1b[0m\n"
                f"{self.incursion.metadata['special_effects']}\n\n"
            )
        
        content += (
            "──────────────────────────\n"
            "```"
        )
        
        embed = discord.Embed(
            description=content,
            color=self._get_incursion_color(self.incursion.incursion_type)
        )
        
        # Fix footer to match panel design
        embed.set_footer(text="Shadow Archive • Incursion Details")
        
        return embed
        # REMOVED: Duplicate footer and return statement
        embed.set_footer(text="💡 Use buttons below to participate or view leaderboard")
        
        return embed
    
    def _get_incursion_color(self, incursion_type: 'IncursionType') -> discord.Color:
        """Get color based on incursion type"""
        from features.incursions.models.incursion import IncursionType
        
        color_map = {
            IncursionType.ANOMALY: discord.Color.from_rgb(255, 20, 147),    # Magenta
            IncursionType.CHALLENGE: discord.Color.from_rgb(0, 255, 255),   # Cyan
            IncursionType.SURGE: discord.Color.from_rgb(255, 140, 0)        # Orange
        }
        return color_map.get(incursion_type, discord.Color.dark_purple())

class BackToIncursionsButton(discord.ui.Button):
    def __init__(self, previous_view):
        super().__init__(label="⬅️ Back to menu", style=discord.ButtonStyle.secondary)
        self.previous_view = previous_view
    
    async def callback(self, interaction: discord.Interaction):
        async def do_work():
            from features.incursions.ui.incursion_panel import IncursionPanel
            embed = await IncursionPanel.render_embed(self.previous_view.bot, interaction.user)
            return embed, self.previous_view
        
        await run_with_animation(interaction, do_work())

class ParticipateDetailButton(discord.ui.Button):
    def __init__(self, bot, incursion):
        super().__init__(label="⚡ Participate", style=discord.ButtonStyle.success)
        self.bot = bot
        self.incursion = incursion
    
    async def callback(self, interaction: discord.Interaction):
        from features.incursions.ui.participation_modal import ParticipationModal
        modal = ParticipationModal(self.bot, self.incursion)
        await interaction.response.send_modal(modal)

class LeaderboardButton(discord.ui.Button):
    def __init__(self, bot, incursion):
        super().__init__(label="🏆 Leaderboard", style=discord.ButtonStyle.primary)
        self.bot = bot
        self.incursion = incursion
    
    async def callback(self, interaction: discord.Interaction):
        async def do_work():
            try:
                sentry_sdk.add_breadcrumb(
                    message=f"LeaderboardButton: Starting leaderboard load for incursion {self.incursion.incursion_id}",
                    level="info"
                )
                
                view = LeaderboardView(self.bot, interaction.user, self.incursion)
                
                sentry_sdk.add_breadcrumb(
                    message="LeaderboardButton: LeaderboardView created, rendering embed",
                    level="info"
                )
                
                embed = await view.render_leaderboard_embed()
                
                sentry_sdk.add_breadcrumb(
                    message="LeaderboardButton: Embed rendered successfully",
                    level="info"
                )
                
                return embed, view
            except Exception as e:
                sentry_sdk.capture_exception(e)
                sentry_sdk.add_breadcrumb(
                    message=f"LeaderboardButton: Error occurred - {str(e)}",
                    level="error"
                )
                raise
        
        await run_with_animation(interaction, do_work())

class LeaderboardView(discord.ui.View):
    """View for displaying incursion leaderboard"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], incursion):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.incursion = incursion
        
        sentry_sdk.add_breadcrumb(
            message=f"LeaderboardView: Initializing for incursion {incursion.incursion_id}",
            level="info"
        )
        
        # Add back button
        self.add_item(BackToDetailsButton(bot, user, incursion))
    
    async def render_leaderboard_embed(self) -> discord.Embed:
        """Render the leaderboard for this incursion"""
        try:
            sentry_sdk.add_breadcrumb(
                message="LeaderboardView: Starting render_leaderboard_embed",
                level="info"
            )
            
            # Use universal header and sub-header pattern
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("incursions")
            
            sentry_sdk.add_breadcrumb(
                message="LeaderboardView: Headers generated",
                level="info"
            )
            
            # Get leaderboard data - FIXED: Pass bot object instead of bot.db_pool
            manager = IncursionManager(self.bot)
            
            sentry_sdk.add_breadcrumb(
                message=f"LeaderboardView: IncursionManager created, fetching leaderboard for {self.incursion.incursion_id}",
                level="info"
            )
            
            leaderboard = await manager.get_incursion_leaderboard(self.incursion.incursion_id, limit=10)
            
            sentry_sdk.add_breadcrumb(
                message=f"LeaderboardView: Leaderboard fetched, {len(leaderboard) if leaderboard else 0} entries",
                level="info"
            )
            
            # Type-specific ANSI colors for incursion title
            type_colors = {
                IncursionType.SURGE: "\x1b[1;33m",      # Bright orange
                IncursionType.CHALLENGE: "\x1b[1;36m",  # Bright cyan
                IncursionType.ANOMALY: "\x1b[1;35m"     # Bright magenta
            }
            title_color = type_colors.get(self.incursion.incursion_type, "\x1b[1;37m")
            
            content_lines = [
                "```ansi",
                header,
                sub_header,
                "",
                f"{title_color}● {self.incursion.title}\x1b[0m",
                f"Type: {self.incursion.incursion_type.value.upper()}",
                "",
                "\x1b[1;37m🏆 LEADERBOARD:\x1b[0m"
            ]
            
            if leaderboard:
                for i, entry in enumerate(leaderboard, 1):
                    # Enhanced rank coloring with ANSI
                    if i == 1:
                        rank_color = "\x1b[1;33m"  # Gold for 1st place
                    elif i == 2:
                        rank_color = "\x1b[1;37m"  # Silver for 2nd place
                    elif i == 3:
                        rank_color = "\x1b[1;31m"  # Bronze/Red for 3rd place
                    else:
                        rank_color = "\x1b[0m"     # Default for others
                        
                    content_lines.append(
                        f"{rank_color}{i:2d}. {entry['username']:<15} {entry['total_reps']:>6} reps\x1b[0m"
                    )
            else:
                content_lines.append("\x1b[1;31mNo participants yet.\x1b[0m")
            
            content_lines.extend([
                "",
                "──────────────────────────",
                "```"
            ])
            
            sentry_sdk.add_breadcrumb(
                message="LeaderboardView: Content lines generated, creating embed",
                level="info"
            )
            
            embed = discord.Embed(
                description="\n".join(content_lines),
                color=self._get_incursion_color(self.incursion.incursion_type)
            )
            # Fix footer to match panel design
            embed.set_footer(text="Shadow Archive • Incursion Leaderboard")
            
            sentry_sdk.add_breadcrumb(
                message="LeaderboardView: Embed created successfully",
                level="info"
            )
            
            return embed
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.add_breadcrumb(
                message=f"LeaderboardView: Error in render_leaderboard_embed - {str(e)}",
                level="error"
            )
            raise
    
    def _get_incursion_color(self, incursion_type: 'IncursionType') -> discord.Color:
        """Get color based on incursion type"""
        from features.incursions.models.incursion import IncursionType
        
        color_map = {
            IncursionType.ANOMALY: discord.Color.from_rgb(255, 20, 147),    # Magenta
            IncursionType.CHALLENGE: discord.Color.from_rgb(0, 255, 255),   # Cyan
            IncursionType.SURGE: discord.Color.from_rgb(255, 140, 0)        # Orange
        }
        return color_map.get(incursion_type, discord.Color.dark_purple())

class BackToDetailsButton(discord.ui.Button):
    def __init__(self, bot, user, incursion):
        super().__init__(label="⬅️ Back to Details", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.user = user
        self.incursion = incursion
    
    async def callback(self, interaction: discord.Interaction):
        async def do_work():
            from features.incursions.ui.incursion_panel import IncursionPanelView
            # Create a minimal previous view for navigation - FIXED: Pass bot object
            manager = IncursionManager(self.bot)
            active_incursions = await manager.get_active_incursions()
            previous_view = IncursionPanelView(self.bot, self.user, active_incursions)
            
            view = IncursionDetailsView(self.bot, self.user, self.incursion, previous_view)
            embed = await view.render_details_embed()
            return embed, view
        
        await run_with_animation(interaction, do_work())