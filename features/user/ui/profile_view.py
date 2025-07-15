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

def create_xp_bar(current_xp: int, next_level_xp: int, length: int = 12) -> str:
    """Generates a dynamic ASCII progress bar for XP with improved styling."""
    if not next_level_xp or next_level_xp == 0:
        return f"[{'█' * length}] MAX LEVEL"
    progress = min(1.0, current_xp / next_level_xp)
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percentage = int(progress * 100)
    return f"[{bar}] {current_xp}/{next_level_xp} XP ({percentage}%)"

def create_stat_bar(value: int, max_value: int = 100, length: int = 8) -> str:
    """Creates a visual bar for stats."""
    if max_value == 0:
        return "[░░░░░░░░]"
    progress = min(1.0, value / max_value)
    filled_length = int(length * progress)
    bar = '▰' * filled_length + '▱' * (length - filled_length)
    return f"[{bar}]"

async def build_profile_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Builds the main profile embed with modern, mobile-friendly design."""
    profile_data = await data_manager.get_user_profile(bot, user.id)
    if not profile_data:
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("profile")
        desc = f"```ansi\n{header}\n{sub_header}\n\n❌ ERROR: Profile data not found\n\nPlease contact system administrator.\n```"
        embed = discord.Embed(description=desc, color=discord.Color.red())
        embed.set_footer(text="Shadow Archive • Profile Node")
        return embed

    # Build the main embed with universal header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("profile")
    
    # Get profile data
    level = profile_data.get('level', 1)
    current_xp = profile_data.get('xp', 0)
    max_xp = profile_data.get('xp_max', 100)
    stats = profile_data.get('stats', {})
    fitness = profile_data.get('health_fitness', {})
    
    # Create XP progress section
    xp_bar = create_xp_bar(current_xp, max_xp)
    
    # Build the main description with ANSI formatting
    desc_content = f"""{header}
{sub_header}

🧑‍💼 OPERATIVE PROFILE
├─ Level: {level}
└─ {xp_bar}

📊 CORE ATTRIBUTES"""
    
    # Add stats with visual bars
    stat_keys = ["STR", "END", "SPR"]
    stat_emojis = {"STR": "💪", "END": "🛡️", "SPR": "✨"}
    stat_labels = {"STR": "Strength", "END": "Endurance", "SPR": "Spirit"}
    
    for i, key in enumerate(stat_keys):
        val = stats.get(key, 1)
        emoji = stat_emojis.get(key, "•")
        label = stat_labels.get(key, key)
        stat_bar = create_stat_bar(val, 50)  # Assuming max stat of 50 for visual purposes
        
        if i == len(stat_keys) - 1:  # Last item
            desc_content += f"\n└─ {emoji} {label}: {val} {stat_bar}"
        else:
            desc_content += f"\n├─ {emoji} {label}: {val} {stat_bar}"
    
    # Add fitness section if available
    if fitness and any(fitness.values()):
        desc_content += "\n\n💖 HEALTH & FITNESS"
        fitness_items = list(fitness.items())
        for i, (key, value) in enumerate(fitness_items):
            formatted_key = key.replace('_', ' ').title()
            if i == len(fitness_items) - 1:  # Last item
                desc_content += f"\n└─ 🏃‍♂️ {formatted_key}: {value}"
            else:
                desc_content += f"\n├─ 🏃‍♂️ {formatted_key}: {value}"
    else:
        desc_content += "\n\n💖 HEALTH & FITNESS\n└─ 📊 No fitness data recorded"
    
    # Create the embed
    embed = discord.Embed(
        description=f"```ansi\n{desc_content}\n```",
        color=0x9146FF  # Using the primary color from ui_styles
    )
    
    # Set thumbnail
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Add footer
    embed.set_footer(text="Shadow Archive • Profile Node", icon_url=user.display_avatar.url)
    
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
        # Add action buttons in a more organized layout
        view.add_item(HistoryButton(bot, user))
        view.add_item(StatsButton(bot, user))
        view.add_item(ResetDataButton(bot, user))
        return view

# --- Enhanced Action Buttons ---
class StatsButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="Detailed Stats", style=discord.ButtonStyle.primary, emoji="📈")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            # Build detailed stats embed
            profile_data = await data_manager.get_user_profile(self.bot, self.user.id)
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("profile")
            
            if profile_data:
                stats = profile_data.get('stats', {})
                level = profile_data.get('level', 1)
                
                desc_content = f"""{header}
{sub_header}

📊 DETAILED STATISTICS
├─ Operative Level: {level}
├─ Total XP: {profile_data.get('xp', 0)}
├─ XP to Next Level: {profile_data.get('xp_max', 100) - profile_data.get('xp', 0)}
└─ Profile Created: {profile_data.get('created_at', 'Unknown')}

💪 ATTRIBUTE BREAKDOWN"""
                
                for key, value in stats.items():
                    desc_content += f"\n├─ {key}: {value}"
                
                desc_content = desc_content.rstrip('├─').rstrip('\n') + "\n└─ " + desc_content.split('\n')[-1].replace('├─ ', '')
            else:
                desc_content = f"""{header}
{sub_header}

❌ No detailed statistics available"""
            
            embed = discord.Embed(
                description=f"```ansi\n{desc_content}\n```",
                color=0x9146FF
            )
            embed.set_footer(text="Shadow Archive • Statistics Division")
            
            # Add back button
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileButton(self.bot, self.user))
            
            return embed, back_view
        
        await run_with_animation(interaction, do_work())

class HistoryButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="History", style=discord.ButtonStyle.secondary, emoji="📜")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            # Create history view and load data with error handling
            history_view = HistoryPanel(self.bot, self.user)
            
            try:
                quests, history_view.total_pages = await data_manager.get_completed_quests(self.bot, self.user.id, history_view.page)
                embed = history_view.build_history_embed("Completed Quests", quests)
                
                # Build the view components
                history_view.clear_items()
                history_view.add_item(ToggleHistoryViewButton(history_view, "Quests", "quests", True))
                history_view.add_item(ToggleHistoryViewButton(history_view, "Logs", "logs", False))
                history_view.add_item(PaginationButton(history_view, "⬅️ Prev", "prev", history_view.page == 1))
                history_view.add_item(PaginationButton(history_view, "Next ➡️", "next", history_view.page >= history_view.total_pages))
                history_view.add_item(BackToProfileButton(self.bot, self.user))
                
                return embed, history_view
                
            except Exception as e:
                # If data loading fails, show error and return to profile
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                error_embed = discord.Embed(
                    description=f"```ansi\n{header}\n\n❌ ERROR: Failed to load history data\n\nPlease try again later.\n```",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="Shadow Archive • Error Handler")
                
                back_view = discord.ui.View(timeout=120)
                back_view.add_item(BackToProfileButton(self.bot, self.user))
                return error_embed, back_view
        
        await run_with_animation(interaction, do_work())

class ResetDataButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="Reset Data", style=discord.ButtonStyle.danger, emoji="🗑️")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Show confirmation view
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = "[ DATA RESET WARNING ]\nSystem: SHADOW_PACT // Data Reset [CONFIRM]\n──────────────────────────"
        
        desc_content = f"""{header}
{sub_header}

⚠️ WARNING: IRREVERSIBLE ACTION

This will permanently delete:
├─ All profile statistics
├─ Quest completion history
├─ Movement logs
└─ Achievement progress

Are you absolutely certain?"""
        
        embed = discord.Embed(
            description=f"```ansi\n{desc_content}\n```",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Shadow Archive • Data Management")
        
        confirmation_view = ResetConfirmationView(self.bot, self.user)
        await interaction.edit_original_response(embed=embed, view=confirmation_view)

class BackToProfileButton(discord.ui.Button):
    def __init__(self, bot, user):
        super().__init__(label="Back to Profile", style=discord.ButtonStyle.secondary, emoji="🔙")
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            embed = await build_profile_embed(self.bot, self.user)
            view = await ProfilePanel.build_view(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

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

        # Always use edit_original_response since interactions are already deferred
        await interaction.edit_original_response(embed=embed, view=self)

class ToggleHistoryViewButton(discord.ui.Button):
    def __init__(self, parent_view, label, view_type, is_active):
        super().__init__(label=label, style=discord.ButtonStyle.primary if is_active else discord.ButtonStyle.secondary, disabled=is_active)
        self.parent_view = parent_view
        self.view_type = view_type

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            self.parent_view.page = 1
            if self.view_type == "quests":
                await self.parent_view.show_completed_quests(interaction)
            else:
                await self.parent_view.show_movement_logs(interaction)
            return None, None  # show_completed_quests/show_movement_logs handle the update
        
        await run_with_animation(interaction, do_work())

class PaginationButton(discord.ui.Button):
    def __init__(self, parent_view, label, direction, disabled):
        super().__init__(label=label, style=discord.ButtonStyle.grey, disabled=disabled)
        self.parent_view = parent_view
        self.direction = direction

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            if self.direction == "prev":
                self.parent_view.page = max(1, self.parent_view.page - 1)
            else:
                self.parent_view.page += 1

            if self.parent_view.current_view == "quests":
                await self.parent_view.show_completed_quests(interaction)
            else:
                await self.parent_view.show_movement_logs(interaction)
            return None, None  # parent methods handle the update
        
        await run_with_animation(interaction, do_work())

class ViewChartButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="View Progress Chart", style=discord.ButtonStyle.success, emoji="📈")
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            summary = await data_manager.get_movement_summary_last_7_days(self.parent_view.bot, self.parent_view.user.id)

            header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
            embed = discord.Embed(title="📈 Movement Progress (Last 7 Days)", description=f"```ansi\n{header}\n```", color=0x2b2d31)

            chart_str = self.build_ascii_chart(summary)
            embed.add_field(name="Total Reps per Day", value=f"```\n{chart_str}\n```", inline=False)
            
            return embed, self.parent_view
        
        await run_with_animation(interaction, do_work())

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

class ResetConfirmationView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
    
    @discord.ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            await data_manager.reset_user_profile(self.bot, self.user.id)
            
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = "[ DATA RESET COMPLETE ]\nSystem: SHADOW_PACT // Data Reset [SUCCESS]\n──────────────────────────"
            
            desc_content = f"""{header}
{sub_header}

✅ RESET SUCCESSFUL

All profile data has been cleared.
You may now start fresh."""
            
            embed = discord.Embed(
                description=f"```ansi\n{desc_content}\n```",
                color=discord.Color.green()
            )
            embed.set_footer(text="Shadow Archive • Data Management")
            
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileButton(self.bot, self.user))
            
            return embed, back_view
        
        await run_with_animation(interaction, do_work())
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            embed = await build_profile_embed(self.bot, self.user)
            view = await ProfilePanel.build_view(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())