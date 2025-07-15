# c:\Users\sakko\Downloads\RoFS (1)\RoFS\ui\log_panel_ui.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import logging
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from core.database import db as db_utils
from features.user.logic.xp_engine import add_xp, calculate_xp_for_movement
from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress
from features.user.logic.user_data import add_recent_activity
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
from discord.abc import User as DiscordABCUser
from typing import Union
from shared.utils.ui_helpers import run_with_animation

logger = logging.getLogger(__name__)

async def build_log_complete_embed(bot, user, log_data):
    # Centralized RPG embed logic for log completion panel
    desc = f"[LOG COMPLETE]\n──────────────────────────\nUser: {user.display_name}\n\n{log_data.get('summary', 'No summary available.')}\n\nTotal Reps: {log_data.get('total_reps', 0)}\nTotal Sets: {log_data.get('total_sets', 0)}\n\nGreat job!"
    embed = discord.Embed(
        title="✅ Log Complete!",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.dark_green()
    )
    embed.set_footer(text="Shadow Archive • Log Database")
    return embed

async def build_log_panel_embed(bot, user, log_data):
    # Centralized RPG embed logic for log panel
    desc = f"[LOG PANEL]\n──────────────────────────\nUser: {user.display_name}\n\n{log_data.get('summary', 'No log data available.')}\n\nTotal Reps: {log_data.get('total_reps', 0)}\nTotal Sets: {log_data.get('total_sets', 0)}"
    embed = discord.Embed(
        title="✍️ Log Reps",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.dark_green()
    )
    embed.set_footer(text="Shadow Archive • Log Database")
    return embed

@register
class LogRepsPanel:
    key = "log_reps"
    label = "Log Reps"
    emoji = "✍️"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        # Use the centralized RPG embed logic
        log_data = await get_or_cache_user_json_data(bot, user.id)
        return await build_log_panel_embed(bot, user, log_data)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        # The main view contains the dropdown and the standard panel switcher.
        view = EphemeralPanelView(bot, user)
        view.add_item(LogMovementDropdown(bot, user))
        return view

class LogMovementDropdown(discord.ui.Select):
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        self.bot = bot
        self.user = user
        # In a real scenario, you might fetch these from a config or database
        options = [
            discord.SelectOption(label="Pushups", value="Pushups", emoji="💪"),
            discord.SelectOption(label="Squats", value="Squats", emoji="🦵"),
            discord.SelectOption(label="Meditation", value="Meditation", emoji="🧘"),
            # Add other movements here
        ]
        super().__init__(placeholder="Choose a movement to log...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        movement = str(self.values[0])  # Ensure type is str
        # Open a modal to ask for the number of reps
        await interaction.response.send_modal(LogRepsModal(self.bot, self.user, movement))

class LogRepsModal(discord.ui.Modal):
    def __init__(self, bot, user: Union[discord.User, discord.Member], movement: str):
        super().__init__(title=f"Log {movement}")
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

                # Handle XP and quest logic (these functions also need to be refactored)
                xp_earned = calculate_xp_for_movement(self.movement, reps)
                # The add_xp function and others will need to be refactored to use the bot.db_pool
                # For now, we assume they are and that they work.
                # await add_xp(self.bot, self.user.id, xp_earned)
                # await update_quest_progress(self.bot, self.user.id, self.movement, reps)
                # await update_weekly_contract_progress(self.bot, self.user.id, self.movement, reps)
                # await add_recent_activity(self.bot, self.user.id, f"Logged {reps} {self.movement} for {xp_earned} XP.")

                embed = discord.Embed(
                    title="✅ Reps Logged",
                    description=f"Successfully logged **{reps} {self.movement}** and earned **{xp_earned} XP**!",
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

async def render_log_complete_embed(user, movement, reps, xp_earned, user_data=None, daily_quests=None, weekly_contracts=None):
    # Basic RPG-style log complete embed. Expand as needed for your RPG UX!
    log_data = user_data or {}
    log_data['summary'] = f"Logged {reps} {movement} (+{xp_earned} XP)"
    return await build_log_complete_embed(None, user, log_data), None