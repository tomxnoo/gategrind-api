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
        
        # Get user progress
        manager = IncursionManager(self.bot.db_pool)
        user_progress = await manager.get_user_progress(self.user.id)
        progress = user_progress.get(self.incursion.id, 0)
        progress_pct = min(100, (progress / self.incursion.target_reps) * 100) if self.incursion.target_reps > 0 else 0
        
        # Progress bar
        filled = int(progress_pct / 5)  # 20 segments for detail view
        bar = "█" * filled + "░" * (20 - filled)
        
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
            f"[{bar}] {progress}/{self.incursion.target_reps} ({progress_pct:.1f}%)\n\n"
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
        header = get_system_status_header(self.user)
        
        # Get leaderboard data
        manager = IncursionManager(self.bot.db_pool)
        leaderboard = await manager.get_incursion_leaderboard(self.incursion.id, limit=10)
        
        content_lines = [
            "```ansi",
            header,
            "🏆 [ INCURSION LEADERBOARD ]\n",
            "System: SHADOW_PACT // Leaderboard Access [GRANTED]",
            "──────────────────────────",
            f"\x1b[1;37m{self.incursion.title}\x1b[0m",
            ""
        ]
        
        if not leaderboard:
            content_lines.extend([
                "\x1b[2;37mNo participants yet...\x1b[0m",
                "Be the first to join this incursion!"
            ])
        else:
            for i, (user_id, progress) in enumerate(leaderboard, 1):
                # Get user info
                try:
                    user_obj = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    username = user_obj.display_name if user_obj else f"User {user_id}"
                except:
                    username = f"User {user_id}"
                
                # Medal emojis
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
                
                # Highlight current user
                if user_id == self.user.id:
                    content_lines.append(f"\x1b[1;33m{medal} {i:2d}. {username}: {progress} reps\x1b[0m")
                else:
                    content_lines.append(f"{medal} {i:2d}. {username}: {progress} reps")
        
        content_lines.extend([
            "",
            "──────────────────────────",
            "```"
        ])
        
        embed = discord.Embed(
            description="\n".join(content_lines),
            color=int(PRIMARY_COLOR.replace("#", ""), 16)
        )
        
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
            # Create a minimal previous view for navigation
            manager = IncursionManager(self.bot.db_pool)
            active_incursions = await manager.get_active_incursions()
            previous_view = IncursionPanelView(self.bot, self.user, active_incursions)
            
            view = IncursionDetailsView(self.bot, self.user, self.incursion, previous_view)
            embed = await view.render_details_embed()
            return embed, view
        
        await run_with_animation(interaction, do_work())