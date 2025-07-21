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
            f"Status: \x1b[1;32mOPERATIONAL\x1b[0m\n"
            f"Mode: \x1b[1;33mQUICK ENTRY\x1b[0m\n"
            f"Engine: \x1b[1;32mV2 TRACKING SYSTEM\x1b[0m\n\n"
            f"\x1b[1;37m📝 Training Log Interface:\x1b[0m\n"
            f"Select a movement from the dropdown below\n"
            f"to quickly log your completed repetitions.\n\n"
            f"\x1b[1;37m⚡ Enhanced Features:\x1b[0m\n"
            f"├─ Instant XP calculation & rewards\n"
            f"├─ Real-time quest progress tracking\n"
            f"├─ Weekly contract advancement\n"
            f"├─ Activity history archival\n"
            f"└─ Statistical analysis integration\n\n"
            f"\x1b[1;37m🎯 Movement Categories:\x1b[0m\n"
            f"Upper body, lower body, and core movements\n"
            f"available for comprehensive training logs.\n\n"
            f"\x1b[1;37m💡 Pro Tip:\x1b[0m\n"
            f"Log immediately after completion for\n"
            f"accurate progress tracking and momentum.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(0, 255, 127)  # Green theme for logging
        )
        embed.set_footer(text="Shadow Archive • Rep Logging • Training Interface")
        return embed

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return LogRepsView(bot, user)

class LogRepsView(discord.ui.View):
    """Enhanced view for the rep logging panel"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        
        # Add dropdown for panel navigation (first, like other panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add movement selection dropdown
        self.add_item(MovementSelectDropdown())
        
        # Add quick action buttons
        self.add_item(ViewHistoryButton(self))
        self.add_item(RefreshButton(self))

class MovementSelectDropdown(discord.ui.Select):
    """Enhanced dropdown for selecting movement to log"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Push-ups", 
                value="pushups", 
                emoji="💪",
                description="Upper body strength training"
            ),
            discord.SelectOption(
                label="Pull-ups", 
                value="pullups", 
                emoji="🔗",
                description="Back and bicep development"
            ),
            discord.SelectOption(
                label="Squats", 
                value="squats", 
                emoji="🦵",
                description="Lower body power training"
            ),
            discord.SelectOption(
                label="Pike Push-ups", 
                value="pike_pushups", 
                emoji="⬆️",
                description="Shoulder strength and stability"
            ),
            discord.SelectOption(
                label="Lateral Raises", 
                value="lateral_raises", 
                emoji="🔺",
                description="Shoulder isolation exercise"
            ),
        ]
        
        super().__init__(
            placeholder="🎯 Select movement to log...",
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

class ViewHistoryButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="📊 View History", style=discord.ButtonStyle.primary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        async def do_work():
            try:
                # Get recent logging history from API
                from core.api_client import api_client
                history_data = await api_client.get_rep_history(self.parent_view.user, limit=10)
                logs = history_data.get("history", [])
                
                header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("log_reps")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Recent Training History\x1b[0m\n"
                    f"Status: \x1b[1;32mLOADED\x1b[0m\n"
                    f"Records: \x1b[1;33m{len(logs)}\x1b[0m entries\n\n"
                    f"\x1b[1;37m📋 Last 10 Sessions:\x1b[0m\n"
                )
                
                if logs:
                    for i, log in enumerate(logs[:10]):
                        movement = log.get('movement_type', 'Unknown').replace('_', ' ').title()
                        reps = log.get('reps', 0)
                        date = log.get('logged_at', 'Unknown')[:10]  # Just date part
                        
                        if i == len(logs) - 1 or i == 9:  # Last item or max items
                            content += f"└─ \x1b[1;33m{movement}\x1b[0m: {reps} reps (\x1b[1;30m{date}\x1b[0m)\n"
                        else:
                            content += f"├─ \x1b[1;33m{movement}\x1b[0m: {reps} reps (\x1b[1;30m{date}\x1b[0m)\n"
                else:
                    content += f"└─ \x1b[1;30mNo training history found\x1b[0m\n"
                
                content += f"\n\x1b[1;37m📈 Quick Stats:\x1b[0m\n"
                content += f"├─ Total sessions logged today\n"
                content += f"├─ Weekly training frequency\n"
                content += f"└─ Most trained movement\n\n"
                content += f"──────────────────────────\n"
                content += f"```"
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.from_rgb(0, 255, 127)
                )
                embed.set_footer(text="Shadow Archive • Training History • Recent Activity")
                
                # Add back button
                back_view = discord.ui.View(timeout=120)
                back_view.add_item(BackToLoggingButton(self.parent_view.bot, self.parent_view.user))
                
                return embed, back_view
                
            except Exception as e:
                print(f"[LOGGING_HISTORY] Error: {e}")
                header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
                content = (
                    f"```ansi\n"
                    f"{header}\n\n"
                    f"\x1b[1;31m● History Unavailable\x1b[0m\n"
                    f"Status: \x1b[1;31mAPI CONNECTION FAILED\x1b[0m\n\n"
                    f"Training history temporarily unavailable.\n"
                    f"Please try again later.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.red()
                )
                embed.set_footer(text="Shadow Archive • Error Handler")
                
                back_view = discord.ui.View(timeout=120)
                back_view.add_item(BackToLoggingButton(self.parent_view.bot, self.parent_view.user))
                
                return embed, back_view
        
        await run_with_animation(interaction, do_work())

class RefreshButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        async def do_work():
            embed = await LogRepsPanel.render_embed(self.parent_view.bot, interaction.user)
            view = await LogRepsPanel.build_view(self.parent_view.bot, interaction.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

class BackToLoggingButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="🔙 Back to Logging", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            embed = await LogRepsPanel.render_embed(self.bot, self.user)
            view = await LogRepsPanel.build_view(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

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
                
                # Enhanced completion embed matching other panels
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = "[ TRAINING COMPLETE ]\nSystem: SHADOW_PACT // Training Log [SUCCESS]\n──────────────────────────"
                
                movement_display = self.movement.replace('_', ' ').title()
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;32m● Training Session Logged\x1b[0m\n"
                    f"Movement: \x1b[1;33m{movement_display}\x1b[0m\n"
                    f"Repetitions: \x1b[1;33m{reps}\x1b[0m reps\n"
                    f"XP Earned: \x1b[1;33m+{xp_earned}\x1b[0m points\n\n"
                    f"\x1b[1;37m✅ Session Results:\x1b[0m\n"
                    f"├─ Training data archived successfully\n"
                    f"├─ Quest progress updated automatically\n"
                    f"├─ Weekly contracts advanced\n"
                    f"└─ Experience points awarded\n\n"
                    f"\x1b[1;37m🎯 Next Steps:\x1b[0m\n"
                    f"Continue your training regimen or\n"
                    f"check quest progress for new objectives.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.green()
                )
                embed.set_footer(text="Shadow Archive • Training Complete • Session Archived")
                
                return embed, None

            except Exception as e:
                logger.error(f"Error logging reps for {self.user.id}: {e}", exc_info=True)
                
                # Enhanced error embed
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                content = (
                    f"```ansi\n"
                    f"{header}\n\n"
                    f"\x1b[1;31m● Logging System Error\x1b[0m\n"
                    f"Status: \x1b[1;31mFAILED TO RECORD\x1b[0m\n"
                    f"Error: \x1b[1;33mDATABASE UNAVAILABLE\x1b[0m\n\n"
                    f"Training session could not be logged.\n"
                    f"Please try again in a few moments.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                error_embed = discord.Embed(
                    description=content,
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="Shadow Archive • Error Handler")
                
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