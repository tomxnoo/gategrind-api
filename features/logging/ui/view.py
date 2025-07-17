import logging
import discord
from discord.ext import commands
from typing import Union

from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress
from features.user.logic.user_data import add_recent_activity
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
from discord.abc import User as DiscordABCUser
from shared.utils.ui_helpers import run_with_animation
from shared.utils.panel_registry import register
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header

logger = logging.getLogger(__name__)

@register
class LogRepsPanel:
    """Panel for logging exercise repetitions"""
    key = "log_reps"
    label = "Log Reps"
    emoji = "📝"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("log_reps")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Rep Logging System\x1b[0m\n"
            f"Status: \x1b[1;32mREADY\x1b[0m\n"
            f"Mode: \x1b[1;33mQUICK LOG\x1b[0m\n\n"
            f"\x1b[1;37m📝 Log Your Training:\x1b[0m\n"
            f"Select a movement from the dropdown below\n"
            f"to quickly log your completed repetitions.\n\n"
            f"\x1b[1;37m⚡ Features:\x1b[0m\n"
            f"├─ Instant XP calculation\n"
            f"├─ Quest progress tracking\n"
            f"├─ Weekly contract updates\n"
            f"└─ Activity history logging\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Shadow Archive • Rep Logging • Quick Entry")
        return embed

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return LogRepsView(bot, user)

class LogRepsView(discord.ui.View):
    """View for the rep logging panel"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        
        # Add dropdown for panel navigation
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add movement selection dropdown
        self.add_item(MovementSelectDropdown())

class MovementSelectDropdown(discord.ui.Select):
    """Dropdown for selecting movement to log"""
    
    def __init__(self):
        options = [
            discord.SelectOption(label="Push-ups", value="pushups", emoji="💪"),
            discord.SelectOption(label="Pull-ups", value="pullups", emoji="🔗"),
            discord.SelectOption(label="Squats", value="squats", emoji="🦵"),
            discord.SelectOption(label="Pike Push-ups", value="pike_pushups", emoji="⬆️"),
            discord.SelectOption(label="Lateral Raises", value="lateral_raises", emoji="🔺"),
        ]
        
        super().__init__(
            placeholder="Select a movement to log...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        movement = self.values[0]
        modal = LogRepsModal(self.view.bot, self.view.user, movement)
        await interaction.response.send_modal(modal)

class LogRepsModal(discord.ui.Modal):
    def __init__(self, bot, user: Union[discord.User, discord.Member], movement: str):
        super().__init__(title=f"Log {movement.replace('_', ' ').title()}")
        self.bot = bot
        self.user = user
        self.movement = movement

        self.reps_input = discord.ui.InputText(
            label="How many reps did you complete?",
            style=discord.InputTextStyle.short,
            placeholder="e.g., 10",
            required=True,
            max_length=5,
        )
        self.add_item(self.reps_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            reps_str = self.reps_input.value or "0"
            reps = int(reps_str)
            if reps <= 0:
                raise ValueError("Reps must be a positive number.")
        except ValueError:
            return await interaction.response.send_message("Invalid number of reps. Please enter a positive integer.", ephemeral=True)

        async def do_work():
            try:
                # Use a single connection for all database operations
                async with self.bot.db_pool.acquire() as connection:
                    async with connection.transaction():
                        await connection.execute(
                            "INSERT INTO activity_log (user_id, activity, reps) VALUES ($1, $2, $3)",
                            self.user.id, self.movement, reps
                        )
                
                # Write-through: Invalidate cache after DB write
                await invalidate_user_json_cache(self.bot, self.user.id)
                # Pre-warm cache for best UX
                await get_or_cache_user_json_data(self.bot, self.user.id)

                # Handle XP and quest logic
                xp_earned = calculate_xp_for_movement(self.movement, reps)
                
                embed = discord.Embed(
                    title="✅ Reps Logged",
                    description=f"Successfully logged **{reps} {self.movement.replace('_', ' ').title()}** and earned **{xp_earned} XP**!",
                    color=discord.Color.green()
                )
                return embed, None

            except Exception as e:
                logger.error(f"Error logging reps for {self.user.id}: {e}", exc_info=True)
                error_embed = discord.Embed(
                    title="❌ Error",
                    description="An error occurred while logging your reps. Please try again later.",
                    color=discord.Color.red()
                )
                return error_embed, None

        await run_with_animation(interaction, do_work, ephemeral=True)

def calculate_xp_for_movement(movement: str, reps: int) -> int:
    """Calculate XP earned for a movement"""
    # Basic XP calculation - can be enhanced later
    base_xp = {
        "pushups": 2, "pullups": 3, "squats": 2, 
        "pike_pushups": 3, "lateral_raises": 1
    }
    return base_xp.get(movement, 1) * reps

async def render_log_complete_embed(user, movement: str, reps: int, xp_gained: int, 
                                  user_data: dict = None, daily_quests: list = None, 
                                  weekly_contracts: list = None) -> tuple[discord.Embed, discord.ui.View]:
    """Render the completion embed after logging reps"""
    
    # Create completion embed
    embed = discord.Embed(
        title="✅ Training Logged",
        color=discord.Color.green()
    )
    
    # Main completion message
    movement_display = movement.replace('_', ' ').title()
    embed.add_field(
        name="🎯 Movement Completed",
        value=f"**{movement_display}** × {reps} reps",
        inline=False
    )
    
    # XP gained
    embed.add_field(
        name="⚡ Experience Gained",
        value=f"+{xp_gained} XP",
        inline=True
    )
    
    # User stats if available
    if user_data:
        current_xp = user_data.get('total_xp', 0)
        level = user_data.get('level', 1)
        embed.add_field(
            name="📊 Current Stats",
            value=f"Level {level} • {current_xp:,} XP",
            inline=True
        )
    
    # Quest progress if available
    if daily_quests:
        active_quests = [q for q in daily_quests if q.get('status') == 'active']
        if active_quests:
            quest_progress = []
            for quest in active_quests[:3]:  # Show up to 3 quests
                progress = quest.get('progress', 0)
                target = quest.get('target', 1)
                percentage = min(100, int((progress / target) * 100)) if target > 0 else 0
                quest_progress.append(f"• {quest.get('title', 'Quest')}: {percentage}%")
            
            if quest_progress:
                embed.add_field(
                    name="🎯 Quest Progress",
                    value="\n".join(quest_progress),
                    inline=False
                )
    
    embed.set_footer(text="Shadow Archive • Training Complete")
    embed.timestamp = discord.utils.utcnow()
    
    # Return embed with no view for now
    return embed, None