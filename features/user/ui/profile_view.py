# ui/profile_ui.py
"""
Handles the display of the user profile, including stats, history, and progress.
This module is responsible for the presentation layer of the user profile system.
"""
import discord
import asyncio
import sentry_sdk
from typing import Union, Dict, Any, List, Tuple
from core.api_client import api_client
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
    """Builds the main profile embed with modern, mobile-friendly design using API data."""
    try:
        # Get profile data from API
        profile_data = await api_client.get_user_profile(user)
        
        # Build the main embed with universal header
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("profile")
        
        # Get profile data
        level = profile_data.get('level', 1)
        current_xp = profile_data.get('xp', 0)
        max_xp = profile_data.get('xp_max', 100)
        stats = profile_data.get('stats', {})
        username = profile_data.get('username', user.display_name)
        
        # Create XP progress section
        xp_bar = create_xp_bar(current_xp, max_xp)
        
        # Build the main description with ANSI formatting
        desc_content = f"""{header}
{sub_header}

🧑‍💼 OPERATIVE PROFILE
├─ Name: {username}
├─ Level: {level}
└─ {xp_bar}

📊 CORE ATTRIBUTES"""
        
        # Add stats with visual bars
        stat_keys = ["STR", "END", "SPR", "TECH"]
        stat_emojis = {"STR": "💪", "END": "🛡️", "SPR": "✨", "TECH": "🎯"}
        stat_labels = {"STR": "Strength", "END": "Endurance", "SPR": "Spirit", "TECH": "Technique"}
        
        for i, key in enumerate(stat_keys):
            stat_data = stats.get(key, {})
            if isinstance(stat_data, dict):
                val = stat_data.get('level', 1)
                stat_xp = stat_data.get('xp', 0)
                stat_xp_max = stat_data.get('xp_max', 100)
            else:
                val = stat_data or 1
                stat_xp = 0
                stat_xp_max = 100
            
            emoji = stat_emojis.get(key, "•")
            label = stat_labels.get(key, key)
            stat_bar = create_stat_bar(val, 10)  # Assuming max stat level of 10 for visual purposes
            
            if i == len(stat_keys) - 1:  # Last item
                desc_content += f"\n└─ {emoji} {label}: Lv.{val} {stat_bar}"
            else:
                desc_content += f"\n├─ {emoji} {label}: Lv.{val} {stat_bar}"
        
        # Add active buffs if available
        active_buffs = profile_data.get('active_buffs', {})
        if active_buffs:
            desc_content += "\n\n✨ ACTIVE BUFFS"
            buff_items = list(active_buffs.items())
            for i, (buff_key, buff_data) in enumerate(buff_items):
                buff_name = buff_data.get('name', buff_key)
                if i == len(buff_items) - 1:  # Last item
                    desc_content += f"\n└─ 🔮 {buff_name}"
                else:
                    desc_content += f"\n├─ 🔮 {buff_name}"
        else:
            desc_content += "\n\n✨ ACTIVE BUFFS\n└─ 📊 No active buffs"
        
        # Create the embed
        embed = discord.Embed(
            description=f"```ansi\n{desc_content}\n```",
            color=0x9146FF  # Using the primary color from ui_styles
        )
        
        # Set thumbnail
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Add footer with API indicator
        embed.set_footer(text="Shadow Archive • Profile Node • API-Powered", icon_url=user.display_avatar.url)
        
    except Exception as e:
        print(f"[PROFILE] Error fetching API data: {e}")
        # Fallback to error embed
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("profile")
        desc_content = f"""{header}
{sub_header}

❌ ERROR: Profile data unavailable

Connection to API failed.
Please try again later."""
        
        embed = discord.Embed(
            description=f"```ansi\n{desc_content}\n```",
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Profile Node • Offline Mode")
    
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
            try:
                # Get detailed stats from API
                profile_data = await api_client.get_user_profile(self.user)
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("profile")
                
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
                
                for key, stat_data in stats.items():
                    if isinstance(stat_data, dict):
                        level = stat_data.get('level', 1)
                        xp = stat_data.get('xp', 0)
                        xp_max = stat_data.get('xp_max', 100)
                        desc_content += f"\n├─ {key}: Lv.{level} ({xp}/{xp_max} XP)"
                    else:
                        desc_content += f"\n├─ {key}: {stat_data}"
                
                # Fix the last item formatting
                lines = desc_content.split('\n')
                if lines and lines[-1].startswith('├─'):
                    lines[-1] = lines[-1].replace('├─', '└─')
                desc_content = '\n'.join(lines)
                
            except Exception as e:
                print(f"[STATS] Error fetching API data: {e}")
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("profile")
                desc_content = f"""{header}
{sub_header}

❌ No detailed statistics available
API connection failed."""
            
            embed = discord.Embed(
                description=f"```ansi\n{desc_content}\n```",
                color=0x9146FF
            )
            embed.set_footer(text="Shadow Archive • Statistics Division • API-Powered")
            
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
                # Get quest history from API
                quest_history = await api_client.get_quest_history(self.user, limit=10)
                quests = quest_history.get("history", [])
                history_view.total_pages = max(1, len(quests) // 10 + (1 if len(quests) % 10 else 0))
                
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
                print(f"[HISTORY] Error fetching API data: {e}")
                # If data loading fails, show error and return to profile
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                error_embed = discord.Embed(
                    description=f"```ansi\n{header}\n\n❌ ERROR: Failed to load history data\n\nAPI connection failed. Please try again later.\n```",
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
        try:
            self.current_view = "quests"
            quest_history = await api_client.get_quest_history(self.user, limit=10)
            quests = quest_history.get("history", [])
            self.total_pages = max(1, len(quests) // 10 + (1 if len(quests) % 10 else 0))
            embed = self.build_history_embed("Completed Quests", quests)
            await self.update_view(interaction, embed)
        except Exception as e:
            print(f"[QUEST_HISTORY] Error: {e}")
            await self.show_error(interaction, "Failed to load quest history")

    async def show_movement_logs(self, interaction: discord.Interaction):
        try:
            self.current_view = "logs"
            rep_history = await api_client.get_rep_history(self.user, limit=10)
            logs = rep_history.get("history", [])
            self.total_pages = max(1, len(logs) // 10 + (1 if len(logs) % 10 else 0))
            embed = self.build_history_embed("Movement Logs", logs)
            await self.update_view(interaction, embed)
        except Exception as e:
            print(f"[REP_HISTORY] Error: {e}")
            await self.show_error(interaction, "Failed to load movement logs")

    async def show_error(self, interaction: discord.Interaction, message: str):
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        embed = discord.Embed(
            description=f"```ansi\n{header}\n\n❌ ERROR: {message}\n\nAPI connection failed.\n```",
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Error Handler")
        await interaction.edit_original_response(embed=embed, view=self)

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
                    movement = item.get('movement_type', 'Unknown Exercise')
                    reps = item.get('reps', 'N/A')
                    date = item.get('logged_at', 'N/A')
                    embed.add_field(name=movement, value=f"```\nReps: {reps}\nLogged: {date}\n```", inline=False)

        embed.set_footer(text=f"Page {self.page}/{self.total_pages} • API-Powered")
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
            try:
                # Get logging stats from API
                stats_data = await api_client.get_logging_stats(self.parent_view.user)
                
                header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
                embed = discord.Embed(title="📈 Movement Progress (Last 7 Days)", description=f"```ansi\n{header}\n```", color=0x2b2d31)

                # Build chart from API data
                chart_str = self.build_ascii_chart_from_api(stats_data)
                embed.add_field(name="Total Reps per Day", value=f"```\n{chart_str}\n```", inline=False)
                
            except Exception as e:
                print(f"[CHART] Error: {e}")
                header = get_system_status_header(self.parent_view.user).replace('```ansi', '').replace('```', '').strip()
                embed = discord.Embed(title="📈 Movement Progress", description=f"```ansi\n{header}\n\n❌ Chart data unavailable\n```", color=discord.Color.red())
            
            return embed, self.parent_view
        
        await run_with_animation(interaction, do_work())

    def build_ascii_chart_from_api(self, stats_data: Dict[str, Any]) -> str:
        """Build ASCII chart from API stats data"""
        try:
            # Extract daily data from API response
            daily_stats = stats_data.get("daily_breakdown", {})
            if not daily_stats:
                return "No data available for chart"
            
            # Simple ASCII chart
            chart_lines = []
            for day, count in daily_stats.items():
                bar = "█" * min(int(count / 10), 20)  # Scale bars
                chart_lines.append(f"{day}: {bar} ({count})")
            
            return "\n".join(chart_lines) if chart_lines else "No movement data"
        except Exception as e:
            return f"Chart generation failed: {e}"

# Placeholder for reset confirmation view
class ResetConfirmationView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        
    # Implementation would go here for reset confirmation
    # This is a placeholder to prevent errors