# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import sentry_sdk
from typing import Union
from datetime import datetime, timezone

from core.api_client import api_client
from shared.utils.ui_styles import PRIMARY_COLOR, get_panel_sub_header
from shared.utils.headers import get_system_status_header
from shared.utils.ui_helpers import run_with_animation

async def render_details_embed(bot, user: Union[discord.User, discord.Member], incursion) -> discord.Embed:
    """Render detailed embed for a specific incursion"""
    # Fix header implementation to match other panels
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    
    # Get participant count from leaderboard
    try:
        leaderboard_response = await api_client.get_incursion_leaderboard(user, incursion["incursion_id"], limit=100)
        participant_count = len(leaderboard_response.get("participants", []))
    except Exception as e:
        print(f"Error fetching participant count: {e}")
        participant_count = 0
    
    progress_percent = min(100, (incursion.get("current_reps", 0) / incursion.get("target_reps", 1)) * 100)
    
    # Create visual progress bar with custom emojis
    filled_squares = int(progress_percent / 10)  # Each square represents 10%
    empty_squares = 10 - filled_squares
    progress_bar = "🟩" * filled_squares + "⬜️" * empty_squares
    
    expires_at = datetime.fromtimestamp(incursion["expires_at"], tz=timezone.utc)
    time_remaining = expires_at - datetime.now(timezone.utc)
    hours_left = max(0, int(time_remaining.total_seconds() / 3600))
    
    content_lines = [
        "```ansi",
        header,
        "🌑 [ INCURSION DETAILS ]",
        "System: SHADOW_PACT // Incursion Access [GRANTED]",
        "──────────────────────────",
        f"\x1b[1;37m{incursion.get('title', 'Unknown Incursion')}\x1b[0m",
        "",
        f"Type: {incursion.get('incursion_type', 'UNKNOWN').upper()}",
        f"Target: {incursion.get('target_exercise', 'Unknown')}",
        "```",
        f"Progress: [{progress_bar}] {progress_percent:.0f}%",
        "```ansi",
        f"Current: {incursion.get('current_reps', 0)}/{incursion.get('target_reps', 0)} reps",
        f"Participants: {participant_count}",
        f"Time Remaining: {hours_left}h",
        "",
        "\x1b[1;33mReward:\x1b[0m",
        f"{incursion.get('reward_description', 'Unknown reward')}",
        "",
        "\x1b[1;32mDescription:\x1b[0m",
        f"{incursion.get('description', 'No description available.')}",
        "```"
    ]
    
    embed = discord.Embed(
        description="\n".join(content_lines),
        color=_get_incursion_color(incursion.get("incursion_type"))
    )
    # Fix footer to match panel design
    embed.set_footer(text="Shadow Archive • Incursion Details")
    return embed

def _get_incursion_color(incursion_type) -> discord.Color:
    """Get color based on incursion type"""
    color_map = {
        "ANOMALY": discord.Color.from_rgb(255, 20, 147),    # Magenta
        "CHALLENGE": discord.Color.from_rgb(0, 255, 255),   # Cyan  
        "SURGE": discord.Color.from_rgb(255, 140, 0)        # Orange
    }
    return color_map.get(incursion_type, discord.Color.dark_purple())

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
    
    async def render_details_embed(self) -> discord.Embed:
        """Render detailed incursion information"""
        # Use universal header and sub-header pattern
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("incursions")
        
        # Get user progress - For now, we'll use 0 as we don't have user-specific progress in API yet
        progress = 0
        progress_pct = 0
        
        # Create visual progress bar with custom emojis (consistent with main panel)
        filled_squares = int(progress_pct / 5)  # Each square represents 5% for detail view (20 total)
        empty_squares = 20 - filled_squares
        progress_bar = "🟩" * filled_squares + "⬜️" * empty_squares
        
        # Time remaining
        expires_at = datetime.fromtimestamp(self.incursion["expires_at"], tz=timezone.utc)
        time_left = expires_at - datetime.now(timezone.utc)
        hours_left = int(time_left.total_seconds() / 3600)
        minutes_left = int((time_left.total_seconds() % 3600) / 60)
        
        # Type-specific styling (consistent with panel view)
        type_colors = {
            "SURGE": "\x1b[1;33m",      # Bright orange
            "CHALLENGE": "\x1b[1;36m",  # Bright cyan
            "ANOMALY": "\x1b[1;35m"     # Bright magenta
        }
        color = type_colors.get(self.incursion.get("incursion_type"), "\x1b[1;37m")
        
        # Get participant count
        try:
            leaderboard_response = await api_client.get_incursion_leaderboard(self.user, self.incursion["incursion_id"], limit=100)
            participant_count = len(leaderboard_response.get("participants", []))
        except Exception as e:
            print(f"Error fetching participant count: {e}")
            participant_count = 0
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"{color}● {self.incursion.get('title', 'Unknown Incursion')}\x1b[0m\n"
            f"Type: {self.incursion.get('incursion_type', 'UNKNOWN').upper()}\n"
            f"Exercise: {self.incursion.get('target_exercise', 'Unknown')}\n\n"
            f"\x1b[1;37mDescription:\x1b[0m\n"
            f"{self.incursion.get('description', 'No description available.')}\n\n"
            f"\x1b[1;37mYour Progress:\x1b[0m\n"
            f"[{progress_bar}] {progress}/{self.incursion.get('target_reps', 0)} ({progress_pct:.1f}%)\n\n"
            f"\x1b[1;37mReward:\x1b[0m {self.incursion.get('reward_description', 'Unknown reward')}\n"
            f"\x1b[1;37mParticipants:\x1b[0m {participant_count} warriors\n"
            f"\x1b[1;37mTime Remaining:\x1b[0m {hours_left}h {minutes_left}m\n\n"
        )
        
        # Add special effects for anomalies
        if self.incursion.get("incursion_type") == "ANOMALY" and self.incursion.get("metadata", {}).get("special_effects"):
            content += (
                f"\x1b[1;35m⚠️ ANOMALY EFFECTS:\x1b[0m\n"
                f"{self.incursion['metadata']['special_effects']}\n\n"
            )
        
        content += (
            "──────────────────────────\n"
            "```"
        )
        
        embed = discord.Embed(
            description=content,
            color=self._get_incursion_color(self.incursion.get("incursion_type"))
        )
        
        # Fix footer to match panel design
        embed.set_footer(text="Shadow Archive • Incursion Details")
        
        return embed
    
    def _get_incursion_color(self, incursion_type: str) -> discord.Color:
        """Get color based on incursion type"""
        color_map = {
            "ANOMALY": discord.Color.from_rgb(255, 20, 147),    # Magenta
            "CHALLENGE": discord.Color.from_rgb(0, 255, 255),   # Cyan
            "SURGE": discord.Color.from_rgb(255, 140, 0)        # Orange
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
                    message=f"LeaderboardButton: Starting leaderboard load for incursion {self.incursion.get('incursion_id')}",
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
            message=f"LeaderboardView: Initializing for incursion {incursion.get('incursion_id')}",
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
            
            # Get leaderboard data from API
            try:
                leaderboard_response = await api_client.get_incursion_leaderboard(self.user, self.incursion["incursion_id"], limit=10)
                leaderboard = leaderboard_response.get("participants", [])
            except Exception as e:
                print(f"Error fetching leaderboard: {e}")
                leaderboard = []
            
            sentry_sdk.add_breadcrumb(
                message=f"LeaderboardView: Leaderboard fetched, {len(leaderboard)} entries",
                level="info"
            )
            
            # Type-specific ANSI colors for incursion title
            type_colors = {
                "SURGE": "\x1b[1;33m",      # Bright orange
                "CHALLENGE": "\x1b[1;36m",  # Bright cyan
                "ANOMALY": "\x1b[1;35m"     # Bright magenta
            }
            title_color = type_colors.get(self.incursion.get("incursion_type"), "\x1b[1;37m")
            
            content_lines = [
                "```ansi",
                header,
                sub_header,
                "",
                f"{title_color}● {self.incursion.get('title', 'Unknown Incursion')}\x1b[0m",
                f"Type: {self.incursion.get('incursion_type', 'UNKNOWN').upper()}",
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
                        f"{rank_color}{i:2d}. {entry.get('username', 'Unknown'):<15} {entry.get('total_reps', 0):>6} reps\x1b[0m"
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
                color=self._get_incursion_color(self.incursion.get("incursion_type"))
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
    
    def _get_incursion_color(self, incursion_type: str) -> discord.Color:
        """Get color based on incursion type"""
        color_map = {
            "ANOMALY": discord.Color.from_rgb(255, 20, 147),    # Magenta
            "CHALLENGE": discord.Color.from_rgb(0, 255, 255),   # Cyan
            "SURGE": discord.Color.from_rgb(255, 140, 0)        # Orange
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
            # Create a minimal previous view for navigation
            try:
                response = await api_client.get_active_incursions(self.user)
                active_incursions = response.get("incursions", [])
            except Exception as e:
                print(f"Error fetching active incursions: {e}")
                active_incursions = []
            
            previous_view = IncursionPanelView(self.bot, self.user, active_incursions)
            
            view = IncursionDetailsView(self.bot, self.user, self.incursion, previous_view)
            embed = await view.render_details_embed()
            return embed, view
        
        await run_with_animation(interaction, do_work())