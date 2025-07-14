# ui/profile_ui.py
"""
Handles the display of the user profile, including stats, history, and progress.
This module is responsible for the presentation layer of the user profile system.
"""
import discord
import asyncio
import sentry_sdk
from typing import Union, Dict, Any, List, Tuple
from core.database.data_manager import *
import core.database.data_manager as data_manager
from shared.utils.headers import get_system_status_header, render_loading_embed
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView

def create_xp_bar(current_xp: int, next_level_xp: int, length: int = 10) -> str:
    """Generates a dynamic ASCII progress bar for XP."""
    if not next_level_xp or next_level_xp == 0:
        return f"[{'█' * length}]"
    progress = min(1.0, current_xp / next_level_xp)
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"[{bar}] {current_xp}/{next_level_xp} XP"

async def build_profile_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Builds the main profile embed with unified information."""
    profile_data = await data_manager.get_user_profile(bot, user.id)
    if not profile_data:
        embed = discord.Embed(description="Could not load profile. User data might not be initialized.", color=discord.Color.red())
        embed.set_footer(text="Shadow Archive • Profile Node")
        return embed

    # Identity Section (no class, only level)
    sub_header = get_panel_sub_header("profile")
    embed = discord.Embed(
        description=f"```ansi\n{sub_header}\n```",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    level = profile_data.get('level', 0)
    embed.add_field(
        name="🧑‍💼 Identity",
        value=f"**Level:** `{level}`",
        inline=True
    )

    # XP Progress Bar
    xp_bar = create_xp_bar(profile_data.get('xp', 0), profile_data.get('xp_max', 100))
    embed.add_field(
        name="🌟 XP Progress",
        value=f"{xp_bar}",
        inline=True
    )

    sub_header = get_panel_sub_header("profile")
    embed = discord.Embed(
        description=f"```ansi\n{sub_header}\n```",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    # Core Info
    # XP Progress
    # Identity and XP Progress will be added below

    # Stats
    stats = profile_data.get('stats', {})
    # Core Stats (only STR, END, SPR)
    stat_keys = ["STR", "END", "SPR"]
    stat_emojis = {"STR": "💪", "END": "🛡️", "SPR": "✨"}
    stat_labels = {"STR": "Strength", "END": "Endurance", "SPR": "Spirit"}
    stats_lines = []
    for key in stat_keys:
        val = stats.get(key, 1)
        emoji = stat_emojis.get(key, "•")
        label = stat_labels.get(key, key)
        stats_lines.append(f"{emoji} **{label}:** `{val}`")
    stats_str = "\n".join(stats_lines)
    embed.add_field(
        name="📊 Core Stats",
        value=stats_str,
        inline=False
    )

    # Health & Fitness
    fitness = profile_data.get('health_fitness', {})
    if fitness:
        fitness_lines = [f"🏃‍♂️ **{key.replace('_', ' ').title()}:** `{value}`" for key, value in fitness.items()]
        fitness_str = "\n".join(fitness_lines)
    else:
        fitness_str = "No health data."
    embed.add_field(
        name="💖 Health & Fitness",
        value=fitness_str,
        inline=False
    )

    embed.set_footer(text="Shadow Archive • Profile Node")
    return embed

@register
class ProfilePanel:
    key = "profile"
    label = "Profile"
    emoji = "🛡️"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_profile_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        view = discord.ui.View(timeout=None)
        # Add the panel switch dropdown
        for item in EphemeralPanelView(bot, user).children:
            view.add_item(item)
        # Add the Reset Data button
        view.add_item(HistoryButton(bot, user))
        view.add_item(ResetDataButton(bot, user))
        return view

# --- Reset Data Button ---
class ResetDataButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="Reset Data", style=discord.ButtonStyle.danger, emoji="♻️")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        # You may want to add a confirmation step here in production
        await data_manager.reset_user_profile(self.bot, self.user.id)
        embed = discord.Embed(description="✅ Your profile data has been reset.", color=discord.Color.green())
        await interaction.edit_original_response(embed=embed, view=None)

class HistoryButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="History", style=discord.ButtonStyle.secondary, emoji="📜")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        loading_embed = render_loading_embed(self.user)
        await interaction.edit_original_response(embed=loading_embed, view=None)

        history_view = HistoryPanel(self.bot, self.user)
        await history_view.show_completed_quests(interaction)

class HistoryPanel(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=120)
        self.bot = bot
        self.user = user
        self.current_view = "quests"
        self.page = 1
        self.total_pages = 1

    async def show_completed_quests(self, interaction: discord.Interaction):
        self.current_view = "quests"
        quests, self.total_pages = await data_manager.get_completed_quests(self.bot, self.user.id, self.page)
        embed = self.build_history_embed("Completed Quests", quests)
        await self.update_view(interaction, embed)

    async def show_movement_logs(self, interaction: discord.Interaction):
        self.current_view = "logs"
        logs, self.total_pages = await data_manager.get_movement_logs(self.bot, self.user.id, self.page)
        embed = self.build_history_embed("Movement Logs", logs)
        await self.update_view(interaction, embed)

    def build_history_embed(self, title: str, items: List[Dict[str, Any]]) -> discord.Embed:
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        embed = discord.Embed(title=f"📜 {title}", description=f"```ansi\n{header}\n```", color=0x2b2d31)

        if not items:
            embed.add_field(name="No Data", value="```\nNo records found for this period.\n```", inline=False)
        else:
            for item in items:
                if self.current_view == "quests":
                    name = item.get('name', 'Unknown Quest')
                    date = item.get('completed_at', 'N/A')
                    reward = item.get('reward', 'N/A')
                    embed.add_field(name=name, value=f"```\nCompleted: {date}\nReward: {reward}\n```", inline=False)
                else:
                    name = item.get('exercise', 'Unknown Exercise')
                    reps = item.get('reps', 'N/A')
                    date = item.get('logged_at', 'N/A')
                    embed.add_field(name=name, value=f"```\nReps: {reps}\nLogged: {date}\n```", inline=False)

        embed.set_footer(text=f"Page {self.page}/{self.total_pages}")
        return embed

    async def update_view(self, interaction: discord.Interaction, embed: discord.Embed):
        self.clear_items()
        self.add_item(ToggleHistoryViewButton(self, "Quests", "quests", self.current_view == "quests"))
        self.add_item(ToggleHistoryViewButton(self, "Logs", "logs", self.current_view == "logs"))
        if self.current_view == "logs":
            self.add_item(ViewChartButton(self))
        self.add_item(PaginationButton(self, "⬅️ Prev", "prev", self.page == 1))
        self.add_item(PaginationButton(self, "Next ➡️", "next", self.page >= self.total_pages))
        self.add_item(BackToProfileButton(self.bot, self.user))

        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

class ToggleHistoryViewButton(discord.ui.Button):
    def __init__(self, parent_view, label, view_type, is_active):
        super().__init__(label=label, style=discord.ButtonStyle.primary if is_active else discord.ButtonStyle.secondary, disabled=is_active)
        self.parent_view = parent_view
        self.view_type = view_type

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.parent_view.page = 1
        if self.view_type == "quests":
            await self.parent_view.show_completed_quests(interaction)
        else:
            await self.parent_view.show_movement_logs(interaction)

class PaginationButton(discord.ui.Button):
    def __init__(self, parent_view, label, direction, disabled):
        super().__init__(label=label, style=discord.ButtonStyle.grey, disabled=disabled)
        self.parent_view = parent_view
        self.direction = direction

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.direction == "prev":
            self.parent_view.page = max(1, self.parent_view.page - 1)
        else:
            self.parent_view.page += 1

        if self.parent_view.current_view == "quests":
            await self.parent_view.show_completed_quests(interaction)
        else:
            await self.parent_view.show_movement_logs(interaction)

class ViewChartButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="View Progress Chart", style=discord.ButtonStyle.success, emoji="📈")
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        summary = await data_manager.get_movement_summary_last_7_days(self.parent_view.bot, self.parent_view.user.id)

        header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
        embed = discord.Embed(title="📈 Movement Progress (Last 7 Days)", description=f"```ansi\n{header}\n```", color=0x2b2d31)

        chart_str = self.build_ascii_chart(summary)
        embed.add_field(name="Total Reps per Day", value=f"```\n{chart_str}\n```", inline=False)

        # We only update the embed, keeping the view the same
        await interaction.edit_original_response(embed=embed)

    def build_ascii_chart(self, summary: Dict[str, int], max_width=20) -> str:
        if not any(summary.values()):
            return "No reps logged in the last 7 days."

        max_reps = max(summary.values()) if any(summary.values()) else 1
        chart = []
        for day, reps in sorted(summary.items()):
            bar_length = int((reps / max_reps) * max_width) if max_reps > 0 else 0
            bar = '█' * bar_length
            chart.append(f"{day[-5:]}: {bar} ({reps})")
        return "\n".join(chart)

class BackToProfileButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="Back to Profile", style=discord.ButtonStyle.danger)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        loading_embed = render_loading_embed(self.user)
        await interaction.edit_original_response(embed=loading_embed, view=None)

        embed = await build_profile_embed(self.bot, self.user)
        view = ProfilePanel.build_view(self.bot, self.user)
        await interaction.edit_original_response(embed=embed, view=await view)
