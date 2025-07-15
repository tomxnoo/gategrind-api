# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Union
from datetime import datetime, timezone

from shared.utils.ui_styles import PRIMARY_COLOR
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
        color=discord.Color.dark_purple()
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
        
        # Add back button
        self.add_item(BackToIncursionsButton(self.previous_view))
        
        # Add participate button
        self.add_item(ParticipateDetailButton(self.bot, self.incursion))
        
        # Add leaderboard button
        self.add_item(LeaderboardButton(self.bot, self.incursion))
    
    async def render_details_embed(self) -> discord.Embed:
        """Render detailed incursion information"""
        header = get_system_status_header(self.user)
        
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
        
        # Type-specific styling
        type_colors = {
            IncursionType.SURGE: "\x1b[1;32m",      # Bright green
            IncursionType.CHALLENGE: "\x1b[1;33m",  # Bright yellow  
            IncursionType.ANOMALY: "\x1b[1;35m"     # Bright magenta
        }
        color = type_colors.get(self.incursion.incursion_type, "\x1b[1;37m")
        
        # Get participant count
        participant_count = await manager.get_participant_count(self.incursion.id)
        
        content = (
            "```ansi\n"
            f"{header}\n"
            "🌑 [ INCURSION DETAILS MODULE ]\n"
            "System: SHADOW_PACT // Detail Access [GRANTED]\n"
            "──────────────────────────\n\n"
            f"{color}● {self.incursion.title}\x1b[0m\n"
            f"  Type: {self.incursion.incursion_type.value.upper()}\n"
            f"  Exercise: {self.incursion.exercise_type}\n\n"
            f"\x1b[1;37mDescription:\x1b[0m\n"
            f"{self.incursion.description}\n\n"
            f"\x1b[1;37mYour Progress:\x1b[0m\n"
        )
        
        content += f"[{progress_bar}] {progress}/{self.incursion.target_reps} ({progress_pct:.1f}%)\n\n"
        
        content += (
            f"\x1b[1;37mReward:\x1b[0m {self.incursion.reward_description}\n"
            f"\x1b[1;37mParticipants:\x1b[0m {participant_count} warriors\n"
            f"\x1b[1;37mTime Remaining:\x1b[0m {hours_left}h {minutes_left}m\n\n"
        )
        
        # Add special effects for anomalies
        if self.incursion.incursion_type == IncursionType.ANOMALY and self.incursion.special_effects:
            content += (
                f"\x1b[1;35m⚠️ ANOMALY EFFECTS:\x1b[0m\n"
                f"{self.incursion.special_effects}\n\n"
            )
        
        content += (
            "──────────────────────────\n"
            "```"
        )
        
        embed = discord.Embed(
            description=content,
            color=int(PRIMARY_COLOR.replace("#", ""), 16)
        )
        
        embed.set_footer(text="💡 Use buttons below to participate or view leaderboard")
        
        return embed

class BackToIncursionsButton(discord.ui.Button):
    def __init__(self, previous_view):
        super().__init__(label="⬅️ Back", style=discord.ButtonStyle.secondary)
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
            view = LeaderboardView(self.bot, interaction.user, self.incursion)
            embed = await view.render_leaderboard_embed()
            return embed, view
        
        await run_with_animation(interaction, do_work())

class LeaderboardView(discord.ui.View):
    """View for displaying incursion leaderboard"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], incursion):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.incursion = incursion
        
        # Add back button
        self.add_item(BackToDetailsButton(bot, user, incursion))
    
    async def render_leaderboard_embed(self) -> discord.Embed:
        """Render the leaderboard for this incursion"""
        # Fix header implementation
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        
        # Get leaderboard data - FIXED: Pass bot object instead of bot.db_pool
        manager = IncursionManager(self.bot)
        leaderboard = await manager.get_incursion_leaderboard(self.incursion.incursion_id, limit=10)
        
        content_lines = [
            "```ansi",
            header,
            "🏆 [ INCURSION LEADERBOARD ]",
            "System: SHADOW_PACT // Leaderboard Access [GRANTED]",
            "──────────────────────────",
            f"\x1b[1;37m{self.incursion.title}\x1b[0m",
            ""
        ]
        
        if leaderboard:
            for i, entry in enumerate(leaderboard, 1):
                rank_color = "\x1b[1;33m" if i <= 3 else "\x1b[0m"
                content_lines.append(
                    f"{rank_color}{i:2d}. {entry['username']:<15} {entry['total_reps']:>6} reps\x1b[0m"
                )
        else:
            content_lines.append("\x1b[1;31mNo participants yet.\x1b[0m")
        
        content_lines.append("```")
        
        embed = discord.Embed(
            description="\n".join(content_lines),
            color=discord.Color.gold()
        )
        # Fix footer to match panel design
        embed.set_footer(text="Shadow Archive • Incursion Leaderboard")
        return embed

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