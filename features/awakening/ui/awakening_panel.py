"""
Enhanced Awakening Panel UI - V2
Integrates with the new API-first architecture and backend services.
"""

import discord
import asyncio
import sentry_sdk
import logging
import httpx
from typing import Union, Dict, Any, Optional, List
from datetime import date

from shared.utils.ui_helpers import run_with_animation
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from core.api_client import APIClient
from shared.utils.error_helpers import handle_panel_errors

logger = logging.getLogger(__name__)

# --- UTILITY FUNCTIONS ---

def _map_tier_to_name(tier_value):
    """Map numeric tier values to tier names"""
    if isinstance(tier_value, int):
        tier_mapping = {1: "shadow", 2: "warrior", 3: "ascendant"}
        return tier_mapping.get(tier_value, "shadow")
    elif isinstance(tier_value, str):
        return tier_value.lower()
    return "shadow"

# --- FALLBACK AND ERROR EMBEDS ---

async def _create_fallback_embed(user: discord.User, error_type: str) -> discord.Embed:
    """Create a fallback embed for when the API is unavailable."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("awakening")
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● System Alert: Service Unreachable\x1b[0m\n"
        f"Status: \x1b[1;31m❌ OFFLINE\x1b[0m\n"
        f"Reason: \x1b[1;33m{error_type}\x1b[0m\n\n"
        f"\x1b[1;37mThe Awakening system is currently unable to\n"
        f"connect to the central archives. Your data is\n"
        f"safe, but services are temporarily unavailable.\n\n"
        f"\x1b[1;37mPlease try again shortly.\n"
        f"──────────────────────────\n"
        f"```"
    )
    embed = discord.Embed(description=content, color=discord.Color.red())
    embed.set_footer(text="Shadow Archive • System Alert")
    return embed

async def _build_quest_sync_pending_embed(header: str, sub_header: str) -> discord.Embed:
    """Build an embed for when quest data is still synchronizing."""
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;33m● Awakening Data Synchronization\x1b[0m\n"
        f"Status: \x1b[1;33m🔄 PENDING\x1b[0m\n\n"
        f"\x1b[1;37mYour awakening session is active, but quest\n"
        f"data is still being synchronized from the\n"
        f"archives. This may take a few moments.\n\n"
        f"\x1b[1;37mPlease wait for synchronization to complete.\n"
        f"──────────────────────────\n"
        f"```"
    )
    embed = discord.Embed(description=content, color=discord.Color.orange())
    embed.set_footer(text="Shadow Archive • Data Synchronization")
    return embed

# --- MAIN AWAKENING PANEL --- 

@register
class EnhancedAwakeningPanel:
    key = "awakening"
    label = "Awakening"
    emoji = "🌅"

    @staticmethod
    async def render_embed(bot, user: discord.User, **kwargs) -> discord.Embed:
        return await build_enhanced_awakening_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: discord.User, **kwargs) -> discord.ui.View:
        api_client = APIClient()
        try:
            status = await api_client.get_awakening_status(user)
            if status and status.get("awakened"):
                if status.get("status") == "active" and not status.get("quests"):
                    return RecoveryView(bot, user)
                return EnhancedAwakeningMainView(bot, user)
            else:
                return EnhancedAwakeningInitialView(bot, user)
        except (httpx.RequestError, asyncio.TimeoutError):
            return await _create_fallback_view(bot, user)

async def build_enhanced_awakening_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Build the enhanced awakening panel embed with comprehensive error handling"""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("awakening")

    try:
        api_client = APIClient()
        status = await asyncio.wait_for(api_client.get_awakening_status(user, include_quests=True), timeout=10.0)

        if not status:
            status = {"awakened": False}

        if status.get("awakened"):
            if status.get("status") == "active" and not status.get("quests"):
                return await _build_quest_sync_pending_embed(header, sub_header)
            
            if status.get("status") == "completed":
                # Completed state
                xp_gained = status.get("total_xp_gained", 0)
                session_theme = status.get("session_theme", "Shadow Training")
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;32m● {session_theme} Complete\x1b[0m\n"
                    f"Status: \x1b[1;32m🏆 MASTERY ACHIEVED\x1b[0m\n\n"
                    f"\x1b[1;37mAll awakening quests completed. Total XP earned: \x1b[1;33m{xp_gained}\x1b[0m.\n"
                    f"Return at dawn for a new ritual.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.green()
            else:
                # Awakened state
                completed = status.get("completed_quests", 0)
                total = status.get("quest_count", 0)
                xp_gained = status.get("total_xp_gained", 0)
                readiness = status.get("readiness_level", "unknown")
                session_theme = status.get("session_theme", "Shadow Training")
                progress_percent = (completed / total * 100) if total > 0 else 0
                progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
                readiness_info = {
                    "low": ("\x1b[1;34m", "🔋", "RECOVERY"),
                    "standard": ("\x1b[1;33m", "⚖️", "BALANCED"), 
                    "high": ("\x1b[1;31m", "🔥", "PEAK")
                }
                color_code, emoji, level_text = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN"))
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;32m● {session_theme}\x1b[0m\n"
                    f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n\n"
                    f"\x1b[1;37m📊 Progress: [{progress_bar}] {progress_percent:.0f}%\x1b[0m\n"
                    f"Completed: \x1b[1;33m{completed}/{total}\x1b[0m | XP: \x1b[1;33m{xp_gained}\x1b[0m\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.orange()
        else:
            # Ready to awaken state
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Shadow Awakening Ritual\x1b[0m\n"
                f"Status: \x1b[1;33mREADY TO BEGIN\x1b[0m\n\n"
                f"\x1b[1;37mBegin your daily training ritual to unlock\n"
                f"today's personalized quest selection.\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            color = discord.Color.blue()

        embed = discord.Embed(description=content, color=color)
        embed.set_footer(text="Shadow Archive • Awakening V2")

    except (asyncio.TimeoutError, httpx.RequestError) as e:
        logger.error(f"Awakening API call failed: {e}")
        sentry_sdk.capture_exception(e)
        return await _create_fallback_embed(user, "Service Unavailable")
    except Exception as e:
        logger.error(f"Error building awakening embed: {e}")
        sentry_sdk.capture_exception(e)
        return await _create_fallback_embed(user, "System Error")

    return embed

# --- VIEWS AND BUTTONS ---

class EnhancedAwakeningInitialView(discord.ui.View):
    """View for when the user has not yet awakened."""
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.add_item(EnhancedAwakeningButton())

class EnhancedAwakeningMainView(discord.ui.View):
    """Main view for an awakened user."""
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.add_item(ViewQuestsButton())
        self.add_item(ViewBriefingButton())
        self.add_item(ViewHistoryButton())

class EnhancedReadinessSelectionView(discord.ui.View):
    """View for selecting readiness level."""
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.add_item(EnhancedReadinessButton("low", "🔋 Recovery", discord.ButtonStyle.secondary))
        self.add_item(EnhancedReadinessButton("standard", "⚖️ Balanced", discord.ButtonStyle.primary))
        self.add_item(EnhancedReadinessButton("high", "🔥 Peak", discord.ButtonStyle.danger))
        self.add_item(BackToAwakeningButton())

class EnhancedAwakeningButton(discord.ui.Button):
    """Button to start the awakening process."""
    def __init__(self):
        super().__init__(label="🌅 Begin Awakening", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        view = EnhancedReadinessSelectionView(self.view.bot, self.view.user)
        await interaction.response.edit_message(view=view)

class EnhancedReadinessButton(discord.ui.Button):
    """Button for selecting a readiness level and performing the awakening."""
    def __init__(self, readiness_level: str, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.readiness_level = readiness_level

    @handle_panel_errors("awakening", "api")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._perform_awakening)

    async def _perform_awakening(self):
        api_client = APIClient()
        response = await api_client.perform_awakening(self.view.user, self.readiness_level)
        if not response or not response.get("awakening"):
            raise ValueError("Invalid API response during awakening.")
        
        embed = await build_enhanced_awakening_embed(self.view.bot, self.view.user)
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        return embed, view

class ViewQuestsButton(discord.ui.Button):
    """Button to view the current quests."""
    def __init__(self):
        super().__init__(label="⚔️ View Quests", style=discord.ButtonStyle.primary)

    @handle_panel_errors("awakening", "quest_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_quests)

    @handle_panel_errors("awakening", "quest_view")
    async def _show_quests(self):
        """Show enhanced quest details with full functionality"""
        try:
            api_client = APIClient()
            # Single API call to get both status and quests
            response = await api_client.get_awakening_status(self.view.user, include_quests=True)
            
            # If no awakening exists, show the "not initiated" message
            if not response or not response.get("awakened", False):
                return await self._show_no_quests_available()

            # Check if quests are available
            quests = response.get("quests", [])
            if not quests:
                # Active session but no quests - this is a sync issue
                return await self._show_session_quest_error()

            # Build quest view with the quests
            view = EnhancedQuestView(self.view.bot, self.view.user, quests, response)
            embed = await view.build_quest_overview_embed()
            return embed, view

        except Exception as e:
            logger.exception(f"Error showing quests: {e}")
            return await self._show_no_quests_available()

    async def _show_no_quests_available(self):
        embed = discord.Embed(title="No Quests Available", description="Quest data is currently unavailable. Please try again later.", color=discord.Color.orange())
        return embed, self.view

    async def _show_session_quest_error(self):
        embed = discord.Embed(
            title="Quest Sync Issue", 
            description="There appears to be an active session but no quests are available. This may be a temporary sync issue. Please try again in a moment.", 
            color=discord.Color.red()
        )
        return embed, self.view
class ViewBriefingButton(discord.ui.Button):
    """Button to view the daily briefing."""
    def __init__(self):
        super().__init__(label="📜 View Briefing", style=discord.ButtonStyle.secondary)

    @handle_panel_errors("awakening", "briefing_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_briefing)

    async def _show_briefing(self):
        api_client = APIClient()
        briefing = await api_client.get_daily_briefing(self.view.user)
        if not briefing:
            embed = discord.Embed(title="Briefing Unavailable", description="Could not retrieve the daily briefing.", color=discord.Color.red())
            return embed, self.view

        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Daily Briefing\x1b[0m\n"
            f"{briefing.get('awakening_summary', '')}\n\n"
            f"\x1b[1;37m⚔️ Quest Overview:\x1b[0m\n{briefing.get('quest_summary', '')}\n\n"
            f"\x1b[1;37m💡 Readiness Impact:\x1b[0m\n{briefing.get('readiness_impact', '')}\n\n"
            f"\x1b[1;37m🔥 Motivation:\x1b[0m\n{briefing.get('motivation_message', '')}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        embed = discord.Embed(description=content, color=discord.Color.purple())
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        return embed, view

class ViewHistoryButton(discord.ui.Button):
    """Button to view awakening history."""
    def __init__(self):
        super().__init__(label="📊 View History", style=discord.ButtonStyle.secondary)

    @handle_panel_errors("awakening", "history_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_history)

    async def _show_history(self):
        api_client = APIClient()
        history = await api_client.get_awakening_history(self.view.user)
        if not history or not history.get('recent_sessions'):
            embed = discord.Embed(title="History Unavailable", description="Could not retrieve awakening history.", color=discord.Color.red())
            return embed, self.view

        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        stats = history.get('stats', {})
        sessions_list = ""
        for session in history.get('recent_sessions', [])[:5]:
            dt = datetime.fromisoformat(session['date'])
            date_str = dt.strftime("%b %d")
            readiness_map = {"low": "L", "standard": "S", "high": "H"}
            readiness = readiness_map.get(session['readiness_level'], '?')
            sessions_list += f"├─ {date_str} | {session['total_xp']} XP | Readiness: {readiness}\n"

        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Shadow Archive: Awakening History\x1b[0m\n"
            f"Total Sessions: \x1b[1;33m{stats.get('total_sessions', 0)}\x1b[0m | Avg XP: \x1b[1;33m{stats.get('average_xp', 0):.0f}\x1b[0m\n\n"
            f"\x1b[1;37m📊 Recent Sessions:\x1b[0m\n{sessions_list}\n"
            f"──────────────────────────\n"
            f"```"
        )
        embed = discord.Embed(description=content, color=discord.Color.dark_gold())
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        return embed, view

class BackToAwakeningButton(discord.ui.Button):
    """Button to return to the main awakening panel."""
    def __init__(self):
        super().__init__(label="🔙 Back", style=discord.ButtonStyle.grey)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._go_back)

    async def _go_back(self):
        embed = await build_enhanced_awakening_embed(self.view.bot, self.view.user)
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view

# --- QUEST VIEWS AND BUTTONS ---

class EnhancedQuestView(discord.ui.View):
    """View for displaying the quest overview."""
    def __init__(self, bot, user, quests, awakening_data):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.quests = quests
        self.awakening_data = awakening_data
        self.current_quest_index = 0

        self.add_item(PreviousQuestButton())
        self.add_item(NextQuestButton())
        self.add_item(QuestDetailsButton())
        self.add_item(CompleteQuestButton())
        self.add_item(BackToAwakeningButton())

    def get_current_quest(self):
        return self.quests[self.current_quest_index]

    async def build_quest_overview_embed(self):
        quest = self.get_current_quest()
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        completed = self.awakening_data.get("completed_quests", 0)
        total = self.awakening_data.get("quest_count", 0)
        progress_percent = (completed / total * 100) if total > 0 else 0
        progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))

        quest_title = quest.get('title', 'Unknown Quest')
        quest_status = "✅" if quest.get('completed') else "❌"

        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Quest Overview ({self.current_quest_index + 1}/{total})\x1b[0m\n"
            f"Progress: [{progress_bar}] {progress_percent:.0f}%\n\n"
            f"\x1b[1;37mCurrent Quest: {quest_status} {quest_title}\x1b[0m\n"
            f"{quest.get('description', '')}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        embed = discord.Embed(description=content, color=discord.Color.blue())
        return embed

class EnhancedQuestDetailView(discord.ui.View):
    """View for displaying detailed information about a single quest."""
    def __init__(self, bot, user, quests, awakening_data, current_quest_index):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.quests = quests
        self.awakening_data = awakening_data
        self.current_quest_index = current_quest_index

        self.add_item(PreviousQuestDetailButton())
        self.add_item(NextQuestDetailButton())
        # TODO: Re-implement logging when API supports it
        # self.add_item(LogRepsButton())
        # self.add_item(LogSetsButton())
        self.add_item(BackToQuestOverviewButton())

    def get_current_quest(self):
        return self.quests[self.current_quest_index]

    async def build_quest_detail_embed(self):
        quest = self.get_current_quest()
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")

        title = quest.get("title", "Unknown Quest")
        description = quest.get("description", "No description")
        movement = quest.get("movement_name", "N/A")
        target_reps = quest.get("target_reps", 0)
        target_sets = quest.get("target_sets", 1)
        xp_reward = quest.get("xp_reward", 0)
        completed = quest.get("completed", False)
        status_text = "\x1b[1;32m✅ COMPLETED\x1b[0m" if completed else "\x1b[1;31m❌ PENDING\x1b[0m"

        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Quest Details ({self.current_quest_index + 1}/{len(self.quests)})\x1b[0m\n"
            f"Status: {status_text}\n\n"
            f"\x1b[1;37m⚔️ {title}\x1b[0m\n"
            f"{description}\n\n"
            f"\x1b[1;37m🎯 Parameters:\x1b[0m\n"
            f"├─ Movement: \x1b[1;33m{movement}\x1b[0m\n"
            f"├─ Target: \x1b[1;33m{target_sets} sets x {target_reps} reps\x1b[0m\n"
            f"└─ Reward: \x1b[1;33m{xp_reward} XP\x1b[0m\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        embed = discord.Embed(description=content, color=discord.Color.green() if completed else discord.Color.dark_orange())
        return embed

class PreviousQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀️ Previous", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.view.current_quest_index > 0:
            self.view.current_quest_index -= 1
        else:
            self.view.current_quest_index = len(self.view.quests) - 1
        embed = await self.view.build_quest_overview_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class NextQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next ▶️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.view.current_quest_index < len(self.view.quests) - 1:
            self.view.current_quest_index += 1
        else:
            self.view.current_quest_index = 0
        embed = await self.view.build_quest_overview_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class QuestDetailsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📋 Details", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = EnhancedQuestDetailView(self.view.bot, self.view.user, self.view.quests, self.view.awakening_data, self.view.current_quest_index)
        embed = await view.build_quest_detail_embed()
        await interaction.response.edit_message(embed=embed, view=view)

class CompleteQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✅ Complete", style=discord.ButtonStyle.success)

    @handle_panel_errors("awakening", "quest_completion")
    async def callback(self, interaction: discord.Interaction):
        await run_with_animation(interaction, self._complete_quest)

    async def _complete_quest(self):
        quest = self.view.get_current_quest()
        api_client = APIClient()
        response = await api_client.complete_awakening_quest(self.view.user, quest['id'])
        if not response or not response.get('success'):
            raise ValueError("Failed to complete quest.")
        
        # Refresh data
        awakening_data = await api_client.get_awakening_quests(self.view.user)
        quests = awakening_data.get("quests", [])
        self.view.quests = quests
        self.view.awakening_data = awakening_data

        embed = await self.view.build_quest_overview_embed()
        return embed, self.view

class PreviousQuestDetailButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀️ Previous", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.view.current_quest_index > 0:
            self.view.current_quest_index -= 1
        else:
            self.view.current_quest_index = len(self.view.quests) - 1
        embed = await self.view.build_quest_detail_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class NextQuestDetailButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next ▶️", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        if self.view.current_quest_index < len(self.view.quests) - 1:
            self.view.current_quest_index += 1
        else:
            self.view.current_quest_index = 0
        embed = await self.view.build_quest_detail_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class BackToQuestOverviewButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔙 Overview", style=discord.ButtonStyle.grey)

    async def callback(self, interaction: discord.Interaction):
        view = EnhancedQuestView(self.view.bot, self.view.user, self.view.quests, self.view.awakening_data)
        embed = await view.build_quest_overview_embed()
        await interaction.response.edit_message(embed=embed, view=view)

# --- RECOVERY VIEW ---

class RecoveryView(discord.ui.View):
    """Recovery view for handling stuck awakening sessions"""
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.add_item(RecoveryButton())
        self.add_item(BackToAwakeningButton())

class RecoveryButton(discord.ui.Button):
    """Button to recover from stuck sessions"""
    def __init__(self):
        super().__init__(label="🔄 Recover", style=discord.ButtonStyle.danger)

    @handle_panel_errors("awakening", "session_recovery")
    async def callback(self, interaction: discord.Interaction):
        await run_with_animation(interaction, self._attempt_recovery)

    async def _attempt_recovery(self):
        api_client = APIClient()
        response = await api_client.get_awakening_quests(self.view.user)
        if response and response.get("quests"):
            embed = await build_enhanced_awakening_embed(self.view.bot, self.view.user)
            view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
            return embed, view
        else:
            raise ValueError("Recovery failed, quests still not available.")

async def _create_fallback_view(bot, user):
    """Creates a fallback view for when the API is down."""
    view = discord.ui.View(timeout=300)
    view.add_item(BackToAwakeningButton())
    return view