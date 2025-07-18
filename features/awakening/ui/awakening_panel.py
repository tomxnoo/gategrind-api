"""
Enhanced Awakening Panel UI - V2
Integrates with the new quest generation engine for improved user experience
"""

import discord
import asyncio
import sentry_sdk
import logging
import httpx
from typing import Union, Dict, Any, Optional, List
from datetime import date, datetime

from shared.utils.ui_helpers import run_with_animation, interaction_handler
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from core.api_client import APIClient
from core.game_data.quest_engine import (
    QuestGenerationEngine, ReadinessLevel, QuestType,
    generate_awakening_for_user, create_quest_engine
)
from shared.utils.error_helpers import handle_panel_errors

logger = logging.getLogger(__name__)

# --- ENHANCED AWAKENING PANEL EMBED ---
async def build_enhanced_awakening_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Build the enhanced awakening panel embed with comprehensive error handling"""
    
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("awakening")
    
    try:
        # Get awakening status from API with timeout
        api_client = APIClient()
        status_response = await asyncio.wait_for(
            api_client.get_awakening_status(user), 
            timeout=10.0  # 10 second timeout
        )
        
        if status_response and status_response.get("awakened", False):
            status = status_response
        else:
            # Fallback status
            status = {
                "awakened": False,
                "status": "pending",
                "readiness_level": None,
                "quest_count": 0,
                "completed_quests": 0,
                "total_xp_gained": 0,
                "session_theme": None
            }
        
        # Build ANSI-styled content with enhanced visuals
        if not status.get("awakened", False):
            # Ready to awaken state - Enhanced with quest engine preview
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Shadow Awakening Ritual\x1b[0m\n"
                f"Status: \x1b[1;33mREADY TO BEGIN\x1b[0m\n"
                f"Engine: \x1b[1;32mV2 QUEST SYSTEM\x1b[0m\n"
                f"Today: \x1b[1;37m{date.today().strftime('%A, %B %d')}\x1b[0m\n\n"
                f"\x1b[1;37m🌅 Daily Awakening Protocol:\x1b[0m\n"
                f"Begin your personalized training ritual to unlock\n"
                f"today's intelligently generated quest selection.\n\n"
                f"\x1b[1;37m⚡ Enhanced Features:\x1b[0m\n"
                f"├─ Smart autoregulation based on energy levels\n"
                f"├─ V-taper focused movement selection\n"
                f"├─ Dynamic difficulty scaling\n"
                f"├─ Thematic quest generation\n"
                f"└─ Progressive XP and stat rewards\n\n"
                f"\x1b[1;37m🎯 Energy Level Selection:\x1b[0m\n"
                f"Your honest assessment determines quest intensity,\n"
                f"movement selection, and reward scaling.\n\n"
                f"\x1b[1;37m💡 Autoregulation Tip:\x1b[0m\n"
                f"Listen to your body. The system adapts to your\n"
                f"current state for optimal training outcomes.\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            color = discord.Color.blue()
            
        elif status["status"] == "awakened":
            # Awakened state with enhanced progress display
            completed = status.get("completed_quests", 0)
            total = status.get("quest_count", 0)
            xp_gained = status.get("total_xp_gained", 0)
            readiness = status.get("readiness_level", "unknown")
            session_theme = status.get("session_theme", "Shadow Training")
            
            # Enhanced progress bar with visual flair
            if total > 0:
                progress_percent = (completed / total) * 100
                filled_blocks = int(progress_percent / 10)
                progress_bar = "█" * filled_blocks + "▓" * max(0, min(1, (progress_percent % 10) // 5)) + "░" * (10 - filled_blocks - max(0, min(1, (progress_percent % 10) // 5)))
            else:
                progress_bar = "░" * 10
                progress_percent = 0
            
            # Enhanced readiness styling with more visual elements
            readiness_info = {
                "low": ("\x1b[1;34m", "🔋", "RECOVERY MODE", "Gentle movement, form focus"),
                "standard": ("\x1b[1;33m", "⚖️", "BALANCED TRAINING", "Steady progression, consistent effort"), 
                "high": ("\x1b[1;31m", "🔥", "PEAK INTENSITY", "Maximum challenge, push limits")
            }
            color_code, emoji, level_text, description = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN", "Standard protocol"))
            
            # Quest completion status with visual indicators
            completion_status = ""
            if completed >= total and total > 0:
                completion_status = "\x1b[1;32m🏆 ALL QUESTS COMPLETE\x1b[0m"
                color = discord.Color.green()
            elif completed > 0:
                completion_status = f"\x1b[1;33m⚡ {completed}/{total} QUESTS ACTIVE\x1b[0m"
                color = discord.Color.orange()
            else:
                completion_status = f"\x1b[1;37m📋 {total} QUESTS AWAITING\x1b[0m"
                color = discord.Color.blue()
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;32m● {session_theme}\x1b[0m\n"
                f"Status: \x1b[1;32mACTIVE SESSION\x1b[0m\n"
                f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n"
                f"Protocol: \x1b[1;37m{description}\x1b[0m\n\n"
                f"\x1b[1;37m📊 Session Progress:\x1b[0m\n"
                f"Progress: [{progress_bar}] \x1b[1;33m{progress_percent:.0f}%\x1b[0m\n"
                f"Completed: \x1b[1;33m{completed}\x1b[0m / \x1b[1;37m{total}\x1b[0m quests\n"
                f"XP Earned: \x1b[1;33m{xp_gained}\x1b[0m points\n"
                f"Status: {completion_status}\n\n"
            )
            
            if completed >= total and total > 0:
                content += (
                    f"\x1b[1;37m🎉 Awakening Complete!\x1b[0m\n"
                    f"Outstanding dedication to your training regimen.\n"
                    f"Your consistency builds the foundation of mastery.\n\n"
                    f"\x1b[1;37m🔮 Next Opportunities:\x1b[0m\n"
                    f"├─ Review progress in Shadow Archive\n"
                    f"├─ Check weekly challenge status\n"
                    f"├─ Prepare for tomorrow's awakening\n"
                    f"└─ Monitor consistency streak\n\n"
                )
            else:
                content += (
                    f"\x1b[1;37m⚔️ Active Training Session:\x1b[0m\n"
                    f"Your personalized quest selection awaits.\n"
                    f"Each completed quest advances your journey.\n\n"
                    f"\x1b[1;37m🎯 Available Actions:\x1b[0m\n"
                    f"├─ View detailed quest information\n"
                    f"├─ Access daily briefing insights\n"
                    f"├─ Complete remaining challenges\n"
                    f"└─ Track real-time progress\n\n"
                )
                
            content += "──────────────────────────\n```"
            
        else:
            # Completed state with enhanced celebration
            xp_gained = status.get("total_xp_gained", 0)
            session_theme = status.get("session_theme", "Shadow Training")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;32m● {session_theme} Complete\x1b[0m\n"
                f"Status: \x1b[1;32m🏆 MASTERY ACHIEVED\x1b[0m\n"
                f"Daily Goal: \x1b[1;32m✅ ACCOMPLISHED\x1b[0m\n"
                f"Dedication: \x1b[1;33m⭐ EXEMPLARY\x1b[0m\n\n"
                f"\x1b[1;37m🎊 Today's Achievements:\x1b[0m\n"
                f"All awakening quests completed with precision!\n"
                f"Total XP earned: \x1b[1;33m{xp_gained}\x1b[0m points\n\n"
                f"\x1b[1;37m🌟 Warrior's Recognition:\x1b[0m\n"
                f"Your commitment to consistent training shapes\n"
                f"the path to mastery. Excellence recognized.\n\n"
                f"\x1b[1;37m🔄 Tomorrow's Opportunity:\x1b[0m\n"
                f"Return at dawn for a fresh awakening ritual\n"
                f"and new challenges tailored to your growth.\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            color = discord.Color.green()
        
        embed = discord.Embed(
            description=content,
            color=color
        )
        
        # Enhanced footer with version info
        embed.set_footer(text="Shadow Archive • Awakening V2 • Quest Engine Powered")
            
    except asyncio.TimeoutError:
        print(f"[AWAKENING] API timeout for user {user.id}")
        logger.error("Awakening status API call timed out")
        sentry_sdk.capture_message(f"Awakening API timeout for user {user.id}", level="warning")
        return await _create_fallback_embed(user, "API Request Timeout")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"[AWAKENING] API endpoint not found (404) - checking if API server is running")
            sentry_sdk.capture_message(f"Awakening API 404 error - possible server issue", level="error")
            return await _create_fallback_embed(user, "Service Unavailable")
        else:
            print(f"[AWAKENING] API HTTP error {e.response.status_code}: {e.response.text}")
            sentry_sdk.capture_exception(e)
            return await _create_fallback_embed(user, f"Service Error (HTTP {e.response.status_code})")
    except Exception as e:
        print(f"[AWAKENING] Unexpected error in build_enhanced_awakening_embed: {e}")
        logger.error(f"Error building enhanced awakening panel embed: {e}")
        sentry_sdk.capture_exception(e)
        return await _create_fallback_embed(user, "System Error")
    
    return embed

# --- ENHANCED READINESS SELECTION VIEW ---
class EnhancedReadinessSelectionView(discord.ui.View):
    """Enhanced view for selecting readiness level with detailed descriptions"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.user = user
        
        # Add enhanced readiness level buttons with better descriptions
        self.add_item(EnhancedReadinessButton("low", "🔋 Recovery Mode", discord.ButtonStyle.secondary, 
                                            "Gentle movement, form focus, recovery-oriented"))
        self.add_item(EnhancedReadinessButton("standard", "⚖️ Balanced Training", discord.ButtonStyle.primary,
                                            "Steady progression, consistent effort, optimal balance"))
        self.add_item(EnhancedReadinessButton("high", "🔥 Peak Intensity", discord.ButtonStyle.danger,
                                            "Maximum challenge, push limits, elite performance"))
        self.add_item(BackToAwakeningButton())

class EnhancedReadinessButton(discord.ui.Button):
    """Enhanced button for selecting readiness level with detailed feedback"""
    
    def __init__(self, readiness_level: str, label: str, style: discord.ButtonStyle, description: str):
        super().__init__(label=label, style=style)
        self.readiness_level = readiness_level
        self.description = description
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This awakening ritual isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._perform_enhanced_awakening)
    
    @handle_panel_errors("awakening", "api")
    async def _perform_enhanced_awakening(self):
        """Perform enhanced awakening with quest generation"""
        # Initialize user_data with default values
        user_data = None
        user_level = 1
        
        # Create API client instance
        api_client = APIClient()
        
        try:
            # First check if awakening is already completed
            awakening_status = await api_client.get_awakening_status(self.view.user)
            if awakening_status and awakening_status.get("awakening_exists", False):
                # Awakening already exists - show the appropriate status message
                return await self._show_already_awakened_message(awakening_status)
            
            # Get user data for quest generation
            user_data = await api_client.get_user_profile(self.view.user)
            user_level = user_data.get("level", 1)
        except Exception:
            # user_data remains None, user_level remains 1
            pass
        
        try:
            # Generate awakening session using new quest engine
            quest_session = generate_awakening_for_user(
                user_id=self.view.user.id,
                user_level=user_level,
                readiness_level=self.readiness_level,
                preferences=user_data.get("preferences") if user_data else None
            )
            
            # Call awakening API with correct method name and parameters
            response = await api_client.perform_awakening(
                self.view.user,
                self.readiness_level.value if hasattr(self.readiness_level, 'value') else str(self.readiness_level)
            )
            
            if response and "awakening" in response:
                # Show enhanced awakening results
                return await self._show_enhanced_awakening_results(response, quest_session)
            else:
                # This will automatically trigger the error recovery UI
                raise ValueError("API response invalid or incomplete")
                
        except Exception as e:
            # Check if this is the "already completed" error
            if "already completed" in str(e).lower() or "400" in str(e):
                # Try to get current status and show appropriate message
                try:
                    awakening_status = await api_client.get_awakening_status(self.view.user)
                    if awakening_status:
                        return await self._show_already_awakened_message(awakening_status)
                except:
                    pass
            # Re-raise the exception to be handled by the decorator
            raise e
    

    
    async def _show_enhanced_awakening_results(self, response: Dict[str, Any], quest_session) -> tuple:
        """Show enhanced results of the awakening ritual"""
        
        awakening = response["awakening"]
        quests = response.get("quests", quest_session.quests)
        briefing = response.get("daily_briefing", {})
        
        # Get the status from the awakening response
        status = awakening.get("status", "active")  # Default to "active" for new awakenings
        
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Enhanced quest list with categories and difficulty indicators
        quest_list = ""
        for i, quest in enumerate(quests):
            # Get quest data from session if available
            if hasattr(quest, 'title'):
                title = quest.title
                tier_emoji = {"shadow": "🌑", "warrior": "⚔️", "ascendant": "⭐"}.get(quest.tier.value.lower(), "📋")
            else:
                title = quest.get('title', 'Unknown Quest')
                tier_emoji = "📋"
            
            if i == len(quests) - 1:  # Last item
                quest_list += f"└─ {tier_emoji} {title}"
            else:
                quest_list += f"├─ {tier_emoji} {title}\n"
        
        readiness = awakening.get("readiness_level", "unknown")
        readiness_info = {
            "low": ("\x1b[1;34m", "🔋", "RECOVERY MODE", "Gentle movement, form focus"),
            "standard": ("\x1b[1;33m", "⚖️", "BALANCED TRAINING", "Steady progression, consistent effort"), 
            "high": ("\x1b[1;31m", "🔥", "PEAK INTENSITY", "Maximum challenge, push limits")
        }
        color_code, emoji, level_text, description = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN", "Standard protocol"))
        
        # Enhanced session information
        session_theme = quest_session.session_theme if hasattr(quest_session, 'session_theme') else "Shadow Training"
        estimated_duration = quest_session.total_estimated_duration if hasattr(quest_session, 'total_estimated_duration') else 25
        total_xp_potential = quest_session.total_xp_potential if hasattr(quest_session, 'total_xp_potential') else 0
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;32m● Awakening Ritual Complete\x1b[0m\n"
            f"Session: \x1b[1;36m{session_theme}\x1b[0m\n"
            f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n"
            f"Protocol: \x1b[1;37m{description}\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ Generated Quest Selection:\x1b[0m\n"
            f"{quest_list}\n\n"
            f"\x1b[1;37m📊 Session Parameters:\x1b[0m\n"
            f"├─ Quest Count: \x1b[1;33m{len(quests)}\x1b[0m\n"
            f"├─ Est. Duration: \x1b[1;33m{estimated_duration} min\x1b[0m\n"
            f"├─ XP Potential: \x1b[1;33m{total_xp_potential}\x1b[0m\n"
            f"└─ Difficulty: {color_code}{level_text}\x1b[0m\n\n"
            f"\x1b[1;37m🎯 Daily Briefing:\x1b[0m\n"
            f"{briefing.get('awakening_summary', quest_session.session_description if hasattr(quest_session, 'session_description') else 'Your personalized training session is ready.')}\n\n"
            f"\x1b[1;37m💡 Autoregulation Impact:\x1b[0m\n"
            f"{briefing.get('readiness_impact', 'Training intensity optimized for your current state.')}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        # Color based on status
        color_map = {
            "pending": discord.Color.blue(),
            "completed": discord.Color.green(),
            "active": discord.Color.orange()
        }
        
        embed = discord.Embed(
            description=content,
            color=color_map.get(status, discord.Color.blue())
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Quest Details")
        
        # Create the view with awakened state buttons
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        await view.update_buttons_for_awakened_state()
        
        return embed

# Reuse navigation buttons from original (PreviousQuestButton, NextQuestButton, CompleteQuestButton)
# with enhanced styling...

# --- ENHANCED PANEL REGISTRATION ---
@register
class EnhancedAwakeningPanel:
    """Enhanced Awakening Panel V2 for the system hub"""
    key = "awakening"
    label = "Awakening"
    emoji = "🌅"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        try:
            return await build_enhanced_awakening_embed(bot, user)
        except Exception as e:
            logger.error(f"Failed to render awakening embed: {e}")
            sentry_sdk.capture_exception(e)
            # Return a fallback embed
            return await _create_fallback_embed(user, str(e))

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        # Get awakening status to determine which buttons to show
        awakening_status = None
        try:
            api_client = APIClient()
            awakening_status = await asyncio.wait_for(
                api_client.get_awakening_status(user),
                timeout=10.0  # 10 second timeout
            )
        except asyncio.TimeoutError:
            print(f"[AWAKENING] API timeout in build_view for user {user.id}")
            logger.error("Awakening status API call timed out in build_view")
            sentry_sdk.capture_message(f"Awakening build_view API timeout for user {user.id}", level="warning")
            awakening_status = None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"[AWAKENING] API endpoint not found (404) in build_view - checking if API server is running")
                sentry_sdk.capture_message(f"Awakening build_view API 404 error - possible server issue", level="error")
                awakening_status = None
            else:
                print(f"[AWAKENING] API HTTP error in build_view {e.response.status_code}: {e.response.text}")
                sentry_sdk.capture_exception(e)
                awakening_status = None
        except Exception as e:
            # Log the error but don't let it break the panel
            print(f"[AWAKENING] Unexpected error in build_view: {e}")
            logger.error(f"Failed to get awakening status in build_view: {e}")
            sentry_sdk.capture_exception(e)
            awakening_status = None
            
        try:
            return EnhancedAwakeningMainView(bot, user, awakening_status)
        except Exception as e:
            print(f"[AWAKENING] Failed to create awakening view: {e}")
            logger.error(f"Failed to create awakening view: {e}")
            sentry_sdk.capture_exception(e)
            # Return a minimal fallback view
            return _create_fallback_view(bot, user)

# Alias for backward compatibility
AwakeningPanel = EnhancedAwakeningPanel

# --- FALLBACK FUNCTIONS ---
async def _create_fallback_embed(user: Union[discord.User, discord.Member], error_msg: str) -> discord.Embed:
    """Create a fallback embed when the main embed fails to load"""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("awakening")
    
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● System Temporarily Unavailable\x1b[0m\n"
        f"Status: \x1b[1;31m⚠️ CONNECTION ISSUE\x1b[0m\n"
        f"Mode: \x1b[1;33m🔧 FALLBACK ACTIVE\x1b[0m\n\n"
        f"\x1b[1;37m🛠️ Current Situation:\x1b[0m\n"
        f"The awakening system is experiencing connectivity\n"
        f"issues. You can still attempt to begin awakening.\n\n"
        f"\x1b[1;37m🔄 Available Actions:\x1b[0m\n"
        f"├─ Try beginning awakening (may work)\n"
        f"├─ Refresh the panel in a moment\n"
        f"├─ Check your network connection\n"
        f"└─ Contact support if persistent\n\n"
        f"\x1b[1;37m💡 Technical Note:\x1b[0m\n"
        f"The system will attempt to recover automatically.\n"
        f"Your progress and data remain safe.\n\n"
        f"──────────────────────────\n"
        f"```"
    )
    
    embed = discord.Embed(
        description=content,
        color=discord.Color.orange()
    )
    embed.set_footer(text="Shadow Archive • Awakening V2 • Fallback Mode")
    return embed

def _create_fallback_view(bot, user: Union[discord.User, discord.Member]) -> discord.ui.View:
    """Create a minimal fallback view when the main view fails"""
    view = discord.ui.View(timeout=None)
    
    # Add dropdown
    try:
        from shared.utils.common_views import EphemeralPanelSelect
        view.add_item(EphemeralPanelSelect(bot, user.id))
    except Exception:
        pass  # If even the dropdown fails, continue without it
    
    # Add a simple awakening button
    view.add_item(FallbackAwakeningButton(bot, user))
    
    return view

class FallbackAwakeningButton(discord.ui.Button):
    """Fallback awakening button when the main system is unavailable"""
    
    def __init__(self, bot, user):
        super().__init__(label="🌅 Try Awakening", style=discord.ButtonStyle.primary)
        self.bot = bot
        self.user = user
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
        
        try:
            await interaction.response.defer()
            
            # Try to create a readiness selection view
            try:
                view = EnhancedReadinessSelectionView(self.bot, self.user)
                
                embed = discord.Embed(
                    title="🌅 Begin Awakening",
                    description="Select your current energy level to begin today's awakening ritual.",
                    color=discord.Color.blue()
                )
                
                await interaction.followup.edit_message(
                    interaction.message.id,
                    embed=embed,
                    view=view
                )
            except Exception:
                # If readiness selection fails, show a simple message
                embed = discord.Embed(
                    title="❌ System Unavailable",
                    description="The awakening system is currently experiencing issues. Please try again later.",
                    color=discord.Color.red()
                )
                
                await interaction.followup.edit_message(
                    interaction.message.id,
                    embed=embed,
                    view=None
                )
            
        except Exception as e:
            logger.error(f"Fallback awakening button failed: {e}")
            try:
                await interaction.followup.send(
                    "❌ The awakening system is currently unavailable. Please try again later.",
                    ephemeral=True
                )
            except Exception:
                pass  # If even this fails, give up gracefully


# --- ENHANCED MAIN VIEW ---
class EnhancedAwakeningMainView(discord.ui.View):
    """Enhanced main view for the awakening panel with improved UI"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], awakening_status=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        
        # Add dropdown FIRST (above buttons like other panels)
        try:
            from shared.utils.common_views import EphemeralPanelSelect
            self.add_item(EphemeralPanelSelect(bot, user.id))
        except Exception as e:
            logger.error(f"Failed to add panel select dropdown: {e}")
        
        # Add buttons conditionally based on awakening status
        self._add_conditional_buttons(awakening_status)
    
    def _add_conditional_buttons(self, awakening_status=None):
        """Add buttons based on awakening status"""
        try:
            if awakening_status and awakening_status.get("awakened", False):
                # Awakening exists - show quest management buttons
                self.add_item(ViewQuestsButton())
                self.add_item(ViewBriefingButton())
                self.add_item(ViewHistoryButton())
            else:
                # No awakening - show begin awakening button
                self.add_item(EnhancedAwakeningButton())
        except Exception as e:
            logger.error(f"Failed to add conditional buttons: {e}")
            # Add a fallback button
            try:
                self.add_item(FallbackAwakeningButton(self.bot, self.user))
            except Exception:
                pass  # If even this fails, continue without buttons
    
    async def update_buttons_for_awakened_state(self):
        """Update view to show all buttons after awakening"""
        # Clear existing buttons (except dropdown)
        items_to_keep = []
        for item in self.children:
            if hasattr(item, '__class__') and item.__class__.__name__ == 'EphemeralPanelSelect':
                items_to_keep.append(item)
        
        # Clear all items and re-add the ones we want to keep
        self.clear_items()
        for item in items_to_keep:
            self.add_item(item)
        
        # Add the buttons for awakened state
        self.add_item(ViewQuestsButton())
        self.add_item(ViewBriefingButton())
        self.add_item(ViewHistoryButton())

class EnhancedAwakeningButton(discord.ui.Button):
    """Enhanced button to start awakening ritual"""
    
    def __init__(self):
        super().__init__(label="🌅 Begin Awakening", style=discord.ButtonStyle.primary)
    
    @handle_panel_errors("awakening", "navigation")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This awakening ritual isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._check_and_start_awakening)
    
    async def _check_and_start_awakening(self):
        """Check awakening status before starting"""
        # Create API client instance
        api_client = APIClient()
        
        try:
            # Check current awakening status
            status_response = await api_client.get_awakening_status(self.view.user)
            
            if status_response and status_response.get("awakened", False):
                # Awakening already exists - show appropriate message
                return await self._show_already_awakened_message(status_response)
            else:
                # No awakening exists - proceed with readiness selection
                return await self._show_readiness_selection()
                
        except Exception as e:
            # If status check fails, still allow awakening attempt
            # The API will handle the validation
            return await self._show_readiness_selection()
    
    async def _show_already_awakened_message(self, status_response):
        """Show message when awakening already exists for today"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        status = status_response.get("status", "unknown")
        readiness_level = status_response.get("readiness_level", "unknown")
        quest_count = status_response.get("quest_count", 0)
        completed_quests = status_response.get("completed_quests", 0)
        
        if status == "completed":
            status_text = "\x1b[1;32m🏆 COMPLETED\x1b[0m"
            message = "Today's awakening ritual has been completed with excellence!"
        elif completed_quests > 0:
            status_text = f"\x1b[1;33m⚡ IN PROGRESS\x1b[0m"
            message = f"Your awakening is active with {completed_quests}/{quest_count} quests completed."
        else:
            status_text = "\x1b[1;36m📋 ACTIVE\x1b[0m"
            message = "Your awakening ritual is ready with quests awaiting completion."
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Today's Awakening Status\x1b[0m\n"
            f"Status: {status_text}\n"
            f"Readiness: \x1b[1;37m{readiness_level.upper()}\x1b[0m\n"
            f"Quests: \x1b[1;33m{completed_quests}/{quest_count}\x1b[0m\n\n"
            f"\x1b[1;37m📋 Current Situation:\x1b[0m\n"
            f"{message}\n\n"
            f"\x1b[1;37m🎯 Available Actions:\x1b[0m\n"
            f"├─ View your active quests\n"
            f"├─ Check daily briefing\n"
            f"├─ Review progress details\n"
            f"└─ Plan tomorrow's session\n\n"
            f"\x1b[1;37m🔄 Next Awakening:\x1b[0m\n"
            f"Return tomorrow for a fresh awakening ritual\n"
            f"and new challenges tailored to your growth.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.green() if status == "completed" else discord.Color.orange()
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Status Check")
        
        # Use the proper panel method to ensure consistency with main panel
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view

    async def _show_readiness_selection(self):
        """Show enhanced readiness selection view"""
        view = EnhancedReadinessSelectionView(self.view.bot, self.view.user)
        
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Energy Assessment Protocol\x1b[0m\n"
            f"Status: \x1b[1;33mAWAITING INPUT\x1b[0m\n"
            f"System: \x1b[1;32mAUTOREGULATION ACTIVE\x1b[0m\n"
            f"Engine: \x1b[1;32mV2 QUEST SYSTEM\x1b[0m\n\n"
            f"\x1b[1;37m🎯 Honest Self-Assessment:\x1b[0m\n"
            f"Select your current energy and readiness level.\n"
            f"This determines quest intensity and movement selection.\n\n"
            f"\x1b[1;37m⚡ Autoregulation Benefits:\x1b[0m\n"
            f"├─ Optimized training load for your current state\n"
            f"├─ Reduced injury risk through smart scaling\n"
            f"├─ Enhanced long-term progress consistency\n"
            f"└─ Personalized movement recommendations\n\n"
            f"\x1b[1;37m🔋 Energy Level Guide:\x1b[0m\n"
            f"Recovery: Low energy, prioritize form and mobility\n"
            f"Balanced: Standard energy, steady progression\n"
            f"Peak: High energy, maximum challenge intensity\n\n"
            f"\x1b[1;37m💡 Training Wisdom:\x1b[0m\n"
            f"Listen to your body. Consistency over intensity.\n"
            f"Smart training today enables tomorrow's gains.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Energy Assessment")
        
        return embed, view

class BackToAwakeningButton(discord.ui.Button):
    """Enhanced button to go back to main awakening panel"""
    
    def __init__(self):
        super().__init__(label="⬅️ Back to Awakening", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "navigation")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._go_back)
    
    async def _go_back(self):
        """Go back to main awakening panel using the proper panel method"""
        # Use the registered panel's build_view method to ensure consistency
        embed = await EnhancedAwakeningPanel.render_embed(self.view.bot, self.view.user)
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view

# Placeholder classes for the other buttons (these would need to be implemented)
class ViewQuestsButton(discord.ui.Button):
    """Button to view today's awakening quests"""
    
    def __init__(self):
        super().__init__(label="⚔️ View Quests", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "quest_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ These quests aren't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_quests)
    
    async def _show_quests(self):
        """Show enhanced quest details with full functionality"""
        try:
            # First check awakening status to determine if there's an active session
            api_client = APIClient()
            awakening_status = await api_client.get_awakening_status(self.view.user)
            
            # If no awakening exists, show the "not initiated" message
            if not awakening_status.get("awakening_exists", False):
                return await self._show_no_quests_available()
            
            # If awakening exists, try to get quests
            try:
                quests_response = await api_client.get_awakening_quests(self.view.user)
                
                if not quests_response:
                    # Awakening exists but no quest data - show session error
                    return await self._show_session_quest_error()
                
                # Handle different response formats
                if isinstance(quests_response, list):
                    # Direct list of quests
                    quests = quests_response
                    awakening_data = {
                        "readiness_level": awakening_status.get("readiness_level", "standard"),
                        "session_theme": awakening_status.get("session_theme", "Shadow Training")
                    }
                else:
                    # Response with quests and awakening data
                    quests = quests_response.get("quests", [])
                    awakening_data = quests_response.get("awakening", {})
                
                if not quests:
                    # Awakening exists but no quests generated yet - show session error
                    return await self._show_session_quest_error()
                
                # Create enhanced quest view
                view = EnhancedQuestView(self.view.bot, self.view.user, quests, awakening_data)
                embed = await self._build_quest_overview_embed(quests, awakening_data)
                
                return embed, view
                
            except Exception as quest_error:
                logger.error(f"Error fetching quests for active session: {quest_error}")
                # Awakening exists but quest retrieval failed - show session error
                return await self._show_session_quest_error()
            
        except Exception as e:
            logger.error(f"Error checking awakening status: {e}")
            return await self._show_quest_error()
    
    async def _show_no_quests_available(self):
        """Show message when no quests are available"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;33m● No Active Quests\x1b[0m\n"
            f"Status: \x1b[1;37m📋 AWAITING AWAKENING\x1b[0m\n"
            f"Session: \x1b[1;31m❌ NOT INITIATED\x1b[0m\n"
            f"Quests: \x1b[1;37m0 AVAILABLE\x1b[0m\n\n"
            f"\x1b[1;37m🌅 Begin Your Journey:\x1b[0m\n"
            f"Start today's awakening ritual to unlock\n"
            f"your personalized quest selection.\n\n"
            f"\x1b[1;37m⚡ What Awaits:\x1b[0m\n"
            f"├─ Intelligently generated challenges\n"
            f"├─ V-taper focused movements\n"
            f"├─ Autoregulated difficulty scaling\n"
            f"└─ Progressive XP rewards\n\n"
            f"\x1b[1;37m🎯 Next Steps:\x1b[0m\n"
            f"Return to the awakening panel and begin\n"
            f"your daily ritual to access quests.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Shadow Archive • Quest View • No Active Session")
        
        # Use the proper panel method instead of creating a new view directly
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view
    
    async def _show_quest_error(self):
        """Show error message when quest fetching fails"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Quest System Disruption\x1b[0m\n"
            f"Status: \x1b[1;31m⚠️ CONNECTION ERROR\x1b[0m\n"
            f"API: \x1b[1;31m📡 TEMPORARILY OFFLINE\x1b[0m\n"
            f"Data: \x1b[1;31m❌ UNAVAILABLE\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Technical Issue:\x1b[0m\n"
            f"Unable to retrieve quest data from the\n"
            f"Shadow Archive. Connection interrupted.\n\n"
            f"\x1b[1;37m🔄 Recovery Actions:\x1b[0m\n"
            f"├─ Verify network connectivity\n"
            f"├─ Check system status\n"
            f"├─ Retry in a few moments\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Alternative:\x1b[0m\n"
            f"Return to the main awakening panel\n"
            f"and try accessing quests again.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Quest View • Error Recovery")
        
        # Use the proper panel method instead of creating a new view directly
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view
    
    async def _show_session_quest_error(self):
        """Show error message when there's an active session but quest data is unavailable"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;33m● Active Session - Quest Data Sync Issue\x1b[0m\n"
            f"Status: \x1b[1;32m✅ AWAKENING ACTIVE\x1b[0m\n"
            f"Session: \x1b[1;33m⚠️ QUEST SYNC PENDING\x1b[0m\n"
            f"Data: \x1b[1;31m❌ TEMPORARILY UNAVAILABLE\x1b[0m\n\n"
            f"\x1b[1;37m🔄 Synchronization Issue:\x1b[0m\n"
            f"Your awakening session is active, but quest\n"
            f"data is temporarily unavailable. This usually\n"
            f"resolves automatically within moments.\n\n"
            f"\x1b[1;37m🛠️ Quick Fixes:\x1b[0m\n"
            f"├─ Wait 30 seconds and try again\n"
            f"├─ Return to awakening panel and refresh\n"
            f"├─ Check if quest generation completed\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Note:\x1b[0m\n"
            f"Your awakening progress is preserved.\n"
            f"Quest data will sync automatically.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.orange()
        )
        embed.set_footer(text="Shadow Archive • Quest View • Session Sync Issue")
        
        # Use the proper panel method instead of creating a new view directly
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view
    
    async def _build_quest_overview_embed(self, quests, awakening_data):
        """Build the main quest overview embed"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Calculate quest statistics
        total_quests = len(quests)
        completed_quests = sum(1 for q in quests if q.get("completed", False))
        pending_quests = total_quests - completed_quests
        
        # Calculate total XP
        total_xp_earned = sum(q.get("xp_reward", 0) for q in quests if q.get("completed", False))
        total_xp_potential = sum(q.get("xp_reward", 0) for q in quests)
        
        # Progress calculation
        progress_percent = (completed_quests / total_quests * 100) if total_quests > 0 else 0
        filled_blocks = int(progress_percent / 10)
        progress_bar = "█" * filled_blocks + "▓" * max(0, min(1, (progress_percent % 10) // 5)) + "░" * (10 - filled_blocks - max(0, min(1, (progress_percent % 10) // 5)))
        
        # Session info
        readiness = awakening_data.get("readiness_level", "unknown")
        session_theme = awakening_data.get("session_theme", "Shadow Training")
        
        # Readiness styling
        readiness_info = {
            "low": ("\x1b[1;34m", "🔋", "RECOVERY MODE"),
            "standard": ("\x1b[1;33m", "⚖️", "BALANCED TRAINING"), 
            "high": ("\x1b[1;31m", "🔥", "PEAK INTENSITY")
        }
        color_code, emoji, level_text = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN"))
        
        # Quest list preview (first 3 quests)
        quest_preview = ""
        for i, quest in enumerate(quests[:3]):
            status_icon = "✅" if quest.get("completed", False) else "⏳"
            tier_emoji = {"shadow": "🌑", "warrior": "⚔️", "ascendant": "⭐"}.get(quest.get("tier", "shadow"), "📋")
            title = quest.get("title", "Unknown Quest")
            
            if i == min(2, len(quests) - 1):  # Last item in preview
                quest_preview += f"└─ {status_icon} {tier_emoji} {title}"
            else:
                quest_preview += f"├─ {status_icon} {tier_emoji} {title}\n"
        
        if len(quests) > 3:
            quest_preview += f"\n└─ ⋯ +{len(quests) - 3} more quests"
        
        # Status determination
        if completed_quests >= total_quests:
            session_status = "\x1b[1;32m🏆 ALL COMPLETE\x1b[0m"
            color = discord.Color.green()
        elif completed_quests > 0:
            session_status = f"\x1b[1;33m⚡ IN PROGRESS\x1b[0m"
            color = discord.Color.orange()
        else:
            session_status = "\x1b[1;36m📋 READY TO START\x1b[0m"
            color = discord.Color.blue()
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;32m● {session_theme}\x1b[0m\n"
            f"Status: {session_status}\n"
            f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n"
            f"Progress: [{progress_bar}] \x1b[1;33m{progress_percent:.0f}%\x1b[0m\n\n"
            f"\x1b[1;37m📊 Session Overview:\x1b[0m\n"
            f"├─ Total Quests: \x1b[1;33m{total_quests}\x1b[0m\n"
            f"├─ Completed: \x1b[1;32m{completed_quests}\x1b[0m\n"
            f"├─ Remaining: \x1b[1;37m{pending_quests}\x1b[0m\n"
            f"└─ XP Earned: \x1b[1;33m{total_xp_earned}\x1b[0m / \x1b[1;37m{total_xp_potential}\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ Quest Preview:\x1b[0m\n"
            f"{quest_preview}\n\n"
            f"\x1b[1;37m🎯 Navigation:\x1b[0m\n"
            f"Use the buttons below to view detailed quest\n"
            f"information, complete challenges, or navigate\n"
            f"through your personalized training session.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=color
        )
        embed.set_footer(text="Shadow Archive • Quest View • Session Overview")
        
        return embed

# Enhanced Quest View System
class EnhancedQuestView(discord.ui.View):
    """Enhanced view for quest management with navigation and completion"""
    
    def __init__(self, bot, user, quests, awakening_data):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.quests = quests
        self.awakening_data = awakening_data
        self.current_quest_index = 0
        
        # Add dropdown for panel navigation
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add quest navigation and management buttons
        if len(quests) > 1:
            self.add_item(PreviousQuestButton())
            self.add_item(NextQuestButton())
        
        self.add_item(QuestDetailsButton())
        self.add_item(CompleteQuestButton())
        self.add_item(BackToAwakeningButton())
    
    def get_current_quest(self):
        """Get the currently selected quest"""
        if 0 <= self.current_quest_index < len(self.quests):
            return self.quests[self.current_quest_index]
        return None

class PreviousQuestButton(discord.ui.Button):
    """Button to navigate to previous quest"""
    
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "quest_navigation")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ These quests aren't for you.", ephemeral=True)
            return
        
        await run_with_animation(interaction, self._navigate_previous)
    
    async def _navigate_previous(self):
        """Navigate to previous quest"""
        if self.view.current_quest_index > 0:
            self.view.current_quest_index -= 1
        else:
            self.view.current_quest_index = len(self.view.quests) - 1  # Wrap to last
        
        embed = await self._build_quest_detail_embed()
        return embed, self.view
    


# Missing Button Classes - Adding ViewBriefingButton and ViewHistoryButton

class ViewBriefingButton(discord.ui.Button):
    """Button to view daily briefing"""
    
    def __init__(self):
        super().__init__(label="📊 Daily Briefing", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "briefing_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This briefing isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_briefing)
    
    async def _show_briefing(self):
        """Show enhanced daily briefing"""
        try:
            api_client = APIClient()
            briefing_response = await api_client.get_daily_briefing(self.view.user)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            if briefing_response and "briefing" in briefing_response:
                briefing = briefing_response["briefing"]
                
                # Extract briefing data with enhanced formatting
                awakening_summary = briefing.get("awakening_summary", "No summary available")
                quest_overview = briefing.get("quest_overview", "No quest overview")
                progress_highlights = briefing.get("progress_highlights", {})
                readiness_impact = briefing.get("readiness_impact", "No readiness analysis")
                motivation_message = briefing.get("motivation_message", "Stay consistent!")
                
                # Format progress highlights with enhanced visuals
                weekly_completions = progress_highlights.get("weekly_completions", 0)
                weekly_xp = progress_highlights.get("weekly_xp", 0)
                consistency_streak = progress_highlights.get("consistency_streak", 0)
                
                # Enhanced streak display
                streak_status = ""
                if consistency_streak >= 7:
                    streak_status = "\x1b[1;32m🔥 EXCELLENT\x1b[0m"
                elif consistency_streak >= 3:
                    streak_status = "\x1b[1;33m⚡ BUILDING\x1b[0m"
                else:
                    streak_status = "\x1b[1;37m📈 STARTING\x1b[0m"
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Daily Intelligence Briefing\x1b[0m\n"
                    f"Status: \x1b[1;32m📊 ACTIVE ANALYSIS\x1b[0m\n"
                    f"Date: \x1b[1;37m{date.today().strftime('%A, %B %d')}\x1b[0m\n"
                    f"Engine: \x1b[1;32mV2 ANALYTICS\x1b[0m\n\n"
                    f"\x1b[1;37m🌅 Awakening Summary:\x1b[0m\n"
                    f"{awakening_summary}\n\n"
                    f"\x1b[1;37m⚔️ Quest Overview:\x1b[0m\n"
                    f"{quest_overview}\n\n"
                    f"\x1b[1;37m📈 Progress Highlights:\x1b[0m\n"
                    f"├─ Weekly Completions: \x1b[1;33m{weekly_completions}\x1b[0m\n"
                    f"├─ Weekly XP Earned: \x1b[1;33m{weekly_xp}\x1b[0m\n"
                    f"├─ Consistency Streak: \x1b[1;33m{consistency_streak} days\x1b[0m\n"
                    f"└─ Streak Status: {streak_status}\n\n"
                    f"\x1b[1;37m🎯 Readiness Impact:\x1b[0m\n"
                    f"{readiness_impact}\n\n"
                    f"\x1b[1;37m💪 Motivation Message:\x1b[0m\n"
                    f"{motivation_message}\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.blue()
            else:
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● Briefing Unavailable\x1b[0m\n"
                    f"Status: \x1b[1;33m⏳ PENDING GENERATION\x1b[0m\n"
                    f"Data: \x1b[1;31m❌ NOT AVAILABLE\x1b[0m\n"
                    f"Requirement: \x1b[1;37m🌅 AWAKENING NEEDED\x1b[0m\n\n"
                    f"\x1b[1;37m📋 Required Action:\x1b[0m\n"
                    f"Complete your daily awakening ritual to\n"
                    f"generate today's intelligence briefing.\n\n"
                    f"\x1b[1;37m📊 Briefing Contents:\x1b[0m\n"
                    f"├─ Awakening summary and analysis\n"
                    f"├─ Quest overview and recommendations\n"
                    f"├─ Progress highlights and statistics\n"
                    f"├─ Readiness impact assessment\n"
                    f"└─ Personalized motivation message\n\n"
                    f"\x1b[1;37m🎯 Next Steps:\x1b[0m\n"
                    f"Begin your awakening ritual to unlock\n"
                    f"today's personalized briefing.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.orange()
            
            embed = discord.Embed(
                description=content,
                color=color
            )
            embed.set_footer(text="Shadow Archive • Daily Briefing • Intelligence Report")
            
            # Return to main awakening view
            view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching briefing: {e}")
            return await self._show_briefing_error(str(e))
    
    async def _show_briefing_error(self, error_msg):
        """Show briefing error message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Briefing System Error\x1b[0m\n"
            f"Status: \x1b[1;31m❌ CONNECTION FAILED\x1b[0m\n"
            f"API: \x1b[1;31m🚫 UNREACHABLE\x1b[0m\n"
            f"Service: \x1b[1;31m⚠️ TEMPORARILY DOWN\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Error Details:\x1b[0m\n"
            f"Unable to retrieve briefing data from server.\n"
            f"The intelligence system is temporarily offline.\n\n"
            f"\x1b[1;37m🔄 Recovery Actions:\x1b[0m\n"
            f"├─ Check your network connection\n"
            f"├─ Verify server status\n"
            f"├─ Ensure awakening is complete\n"
            f"└─ Contact support if issue persists\n\n"
            f"\x1b[1;37m💡 Technical Info:\x1b[0m\n"
            f"{error_msg[:50]}{'...' if len(error_msg) > 50 else ''}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Daily Briefing • Error Recovery")
        
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view

class ViewHistoryButton(discord.ui.Button):
    """Button to view awakening history"""
    
    def __init__(self):
        super().__init__(label="📜 History", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "history_view")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This history isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_history)
    
    async def _show_history(self):
        """Show enhanced awakening history"""
        try:
            api_client = APIClient()
            history_response = await api_client.get_awakening_history(self.view.user)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            if history_response and "history" in history_response and len(history_response["history"]) > 0:
                history = history_response["history"]
                
                # Calculate statistics
                total_sessions = len(history)
                completed_sessions = sum(1 for entry in history if entry.get("status") == "completed")
                completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
                
                # Build enhanced history list
                history_list = ""
                for i, entry in enumerate(history[:10]):  # Show last 10 entries
                    date_str = entry.get("date", "Unknown")
                    status = entry.get("status", "unknown")
                    readiness = entry.get("readiness_level", "unknown")
                    quest_count = entry.get("quest_count", 0)
                    completed_quests = entry.get("completed_quests", 0)
                    
                    # Enhanced status styling
                    status_info = {
                        "completed": ("\x1b[1;32m", "✅", "COMPLETE"),
                        "partial": ("\x1b[1;33m", "⚡", "PARTIAL"),
                        "pending": ("\x1b[1;31m", "❌", "PENDING"),
                        "active": ("\x1b[1;36m", "🔄", "ACTIVE")
                    }
                    color_code, emoji, status_text = status_info.get(status, ("\x1b[1;37m", "❓", "UNKNOWN"))
                    
                    # Format entry with quest progress
                    entry_text = f"{date_str}: {color_code}{emoji} {readiness.upper()}\x1b[0m"
                    if quest_count > 0:
                        entry_text += f" ({completed_quests}/{quest_count})"
                    
                    if i == len(history[:10]) - 1:  # Last item
                        history_list += f"└─ {entry_text}"
                    else:
                        history_list += f"├─ {entry_text}\n"
                
                # Determine overall performance
                if completion_rate >= 80:
                    performance_status = "\x1b[1;32m🏆 EXCELLENT\x1b[0m"
                elif completion_rate >= 60:
                    performance_status = "\x1b[1;33m⚡ GOOD\x1b[0m"
                else:
                    performance_status = "\x1b[1;37m📈 BUILDING\x1b[0m"
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Awakening History Archive\x1b[0m\n"
                    f"Status: \x1b[1;32m📜 ACTIVE RECORDS\x1b[0m\n"
                    f"Total Sessions: \x1b[1;33m{total_sessions}\x1b[0m\n"
                    f"Completion Rate: \x1b[1;33m{completion_rate:.1f}%\x1b[0m\n"
                    f"Performance: {performance_status}\n\n"
                    f"\x1b[1;37m📊 Session Statistics:\x1b[0m\n"
                    f"├─ Completed: \x1b[1;32m{completed_sessions}\x1b[0m sessions\n"
                    f"├─ Partial: \x1b[1;33m{sum(1 for e in history if e.get('status') == 'partial')}\x1b[0m sessions\n"
                    f"└─ Pending: \x1b[1;31m{sum(1 for e in history if e.get('status') == 'pending')}\x1b[0m sessions\n\n"
                    f"\x1b[1;37m🗓️ Recent Awakenings:\x1b[0m\n"
                    f"{history_list}\n\n"
                    f"\x1b[1;37m📋 Legend:\x1b[0m\n"
                    f"✅ Complete - All quests finished\n"
                    f"⚡ Partial - Some quests completed\n"
                    f"❌ Pending - Awakening incomplete\n"
                    f"🔄 Active - Session in progress\n\n"
                    f"\x1b[1;37m💪 Consistency Impact:\x1b[0m\n"
                    f"Your awakening history demonstrates your\n"
                    f"commitment to consistent training and growth.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.blue()
            else:
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● No History Available\x1b[0m\n"
                    f"Status: \x1b[1;33m📋 EMPTY ARCHIVE\x1b[0m\n"
                    f"Records: \x1b[1;31m❌ NONE FOUND\x1b[0m\n"
                    f"Journey: \x1b[1;37m🌅 JUST BEGINNING\x1b[0m\n\n"
                    f"\x1b[1;37m🚀 Getting Started:\x1b[0m\n"
                    f"Your awakening history will appear here as\n"
                    f"you complete daily rituals and build your\n"
                    f"training consistency over time.\n\n"
                    f"\x1b[1;37m📈 What Gets Tracked:\x1b[0m\n"
                    f"├─ Daily awakening completion status\n"
                    f"├─ Readiness level selections\n"
                    f"├─ Quest completion progress\n"
                    f"├─ XP earned and milestones\n"
                    f"└─ Consistency streaks and patterns\n\n"
                    f"\x1b[1;37m🎯 Build Your Legacy:\x1b[0m\n"
                    f"Start your first awakening ritual today\n"
                    f"to begin building your training history.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.orange()
            
            embed = discord.Embed(
                description=content,
                color=color
            )
            embed.set_footer(text="Shadow Archive • Awakening History • Training Records")
            
            # Return to main awakening view
            view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return await self._show_history_error(str(e))
    
    async def _show_history_error(self, error_msg):
        """Show history error message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● History System Error\x1b[0m\n"
            f"Status: \x1b[1;31m❌ ARCHIVE OFFLINE\x1b[0m\n"
            f"API: \x1b[1;31m🚫 CONNECTION FAILED\x1b[0m\n"
            f"Records: \x1b[1;31m⚠️ TEMPORARILY UNAVAILABLE\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Error Details:\x1b[0m\n"
            f"Unable to retrieve history data from the\n"
            f"Shadow Archive. Connection interrupted.\n\n"
            f"\x1b[1;37m🔄 Recovery Actions:\x1b[0m\n"
            f"├─ Check your network connectivity\n"
            f"├─ Verify server status\n"
            f"├─ Retry in a few moments\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Technical Info:\x1b[0m\n"
            f"{error_msg[:50]}{'...' if len(error_msg) > 50 else ''}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Awakening History • Error Recovery")
        
        view = await EnhancedAwakeningPanel.build_view(self.view.bot, self.view.user)
        return embed, view
    
    async def _build_quest_detail_embed(self):
        """Build detailed view of current quest"""
        quest = self.view.get_current_quest()
        if not quest:
            return await self._build_error_embed()
        
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Quest details
        title = quest.get("title", "Unknown Quest")
        description = quest.get("description", "No description available")
        movement = quest.get("movement_name", "Unknown Movement")
        target_reps = quest.get("target_reps", 0)
        target_sets = quest.get("target_sets", 1)
        rest_seconds = quest.get("rest_seconds", 60)
        xp_reward = quest.get("xp_reward", 0)
        tier = quest.get("tier", "shadow")
        completed = quest.get("completed", False)
        
        # Tier styling
        tier_info = {
            "shadow": ("\x1b[1;34m", "🌑", "SHADOW TIER", "Practice & Volume"),
            "warrior": ("\x1b[1;33m", "⚔️", "WARRIOR TIER", "Technique & Endurance"),
            "ascendant": ("\x1b[1;31m", "⭐", "ASCENDANT TIER", "Intensity & Hypertrophy")
        }
        tier_color, tier_emoji, tier_name, tier_desc = tier_info.get(tier, ("\x1b[1;37m", "📋", "UNKNOWN TIER", "Standard Protocol"))
        
        # Status styling
        if completed:
            status_text = "\x1b[1;32m✅ COMPLETED\x1b[0m"
            color = discord.Color.green()
        else:
            status_text = "\x1b[1;33m⏳ PENDING\x1b[0m"
            color = discord.Color.orange()
        
        # Quest position
        quest_position = f"{self.view.current_quest_index + 1}/{len(self.view.quests)}"
        
        # Format rest time
        rest_minutes = rest_seconds // 60
        rest_display = f"{rest_minutes}m {rest_seconds % 60}s" if rest_minutes > 0 else f"{rest_seconds}s"
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Quest Details ({quest_position})\x1b[0m\n"
            f"Status: {status_text}\n"
            f"Tier: {tier_color}{tier_emoji} {tier_name}\x1b[0m\n"
            f"Focus: \x1b[1;37m{tier_desc}\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ {title}\x1b[0m\n"
            f"{description}\n\n"
            f"\x1b[1;37m🎯 Quest Parameters:\x1b[0m\n"
            f"├─ Movement: \x1b[1;33m{movement}\x1b[0m\n"
            f"├─ Target Sets: \x1b[1;33m{target_sets}\x1b[0m\n"
            f"├─ Target Reps: \x1b[1;33m{target_reps}\x1b[0m per set\n"
            f"├─ Rest Period: \x1b[1;33m{rest_display}\x1b[0m\n"
            f"└─ XP Reward: \x1b[1;33m{xp_reward}\x1b[0m points\n\n"
        )
        
        if completed:
            content += (
                f"\x1b[1;37m🏆 Quest Completed!\x1b[0m\n"
                f"Excellent work! This challenge has been\n"
                f"conquered with skill and determination.\n\n"
                f"\x1b[1;37m📈 Progress Impact:\x1b[0m\n"
                f"XP gained contributes to your overall\n"
                f"advancement and skill development.\n\n"
            )
        else:
            content += (
                f"\x1b[1;37m🚀 Ready to Begin:\x1b[0m\n"
                f"This quest awaits your dedication.\n"
                f"Complete the challenge to earn rewards.\n\n"
                f"\x1b[1;37m💡 Training Tips:\x1b[0m\n"
                f"├─ Focus on proper form over speed\n"
                f"├─ Rest fully between sets\n"
                f"├─ Listen to your body's signals\n"
                f"└─ Maintain consistent breathing\n\n"
            )
        
        content += "──────────────────────────\n```"
        
        embed = discord.Embed(
            description=content,
            color=color
        )
        embed.set_footer(text=f"Shadow Archive • Quest Details • {tier_name}")
        
        return embed
    
    async def _build_error_embed(self):
        """Build error embed when quest data is invalid"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Quest Data Error\x1b[0m\n"
            f"Status: \x1b[1;31m❌ INVALID DATA\x1b[0m\n"
            f"Quest: \x1b[1;31m🚫 NOT FOUND\x1b[0m\n"
            f"Index: \x1b[1;31m{self.view.current_quest_index}\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Data Issue:\x1b[0m\n"
            f"The selected quest data appears to be\n"
            f"corrupted or missing from the archive.\n\n"
            f"\x1b[1;37m🔄 Recovery Options:\x1b[0m\n"
            f"├─ Return to quest overview\n"
            f"├─ Refresh the quest list\n"
            f"├─ Navigate to different quest\n"
            f"└─ Contact support if persistent\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Quest Details • Error")
        
        return embed

class NextQuestButton(discord.ui.Button):
    """Button to navigate to next quest"""
    
    def __init__(self):
        super().__init__(label="Next ➡️", style=discord.ButtonStyle.secondary)
    
    @handle_panel_errors("awakening", "quest_navigation")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ These quests aren't for you.", ephemeral=True)
            return
        
        await run_with_animation(interaction, self._navigate_next)
    
    async def _navigate_next(self):
        """Navigate to next quest"""
        if self.view.current_quest_index < len(self.view.quests) - 1:
            self.view.current_quest_index += 1
        else:
            self.view.current_quest_index = 0  # Wrap to first
        
        embed = await self._build_quest_detail_embed()
        return embed, self.view
    
    async def _build_quest_detail_embed(self):
        """Build detailed view of current quest"""
        # Reuse the same method from PreviousQuestButton
        previous_button = PreviousQuestButton()
        previous_button.view = self.view
        return await previous_button._build_quest_detail_embed()

class QuestDetailsButton(discord.ui.Button):
    """Button to view detailed quest information"""
    
    def __init__(self):
        super().__init__(label="📋 Quest Details", style=discord.ButtonStyle.primary)
    
    @handle_panel_errors("awakening", "quest_details")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ These quests aren't for you.", ephemeral=True)
            return
        
        await run_with_animation(interaction, self._show_quest_details)
    
    async def _show_quest_details(self):
        """Show detailed quest information"""
        # Reuse the detail building method
        previous_button = PreviousQuestButton()
        previous_button.view = self.view
        embed = await previous_button._build_quest_detail_embed()
        return embed, self.view

class CompleteQuestButton(discord.ui.Button):
    """Button to complete the current quest"""
    
    def __init__(self):
        super().__init__(label="✅ Complete Quest", style=discord.ButtonStyle.success)
    
    @handle_panel_errors("awakening", "quest_completion")
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ These quests aren't for you.", ephemeral=True)
            return
        
        await run_with_animation(interaction, self._complete_quest)
    
    async def _complete_quest(self):
        """Complete the current quest"""
        quest = self.view.get_current_quest()
        if not quest:
            return await self._show_completion_error("Quest not found")
        
        if quest.get("completed", False):
            return await self._show_already_completed()
        
        try:
            # Complete quest via API
            api_client = APIClient()
            quest_id = quest.get("id")
            if not quest_id:
                return await self._show_completion_error("Quest ID missing")
            
            response = await api_client.complete_awakening_quest(self.view.user, quest_id)
            
            if response and response.get("success", False):
                # Mark quest as completed in local data
                quest["completed"] = True
                
                # Show completion success
                return await self._show_completion_success(quest, response)
            else:
                error_msg = response.get("message", "Unknown error") if response else "No response"
                return await self._show_completion_error(error_msg)
                
        except Exception as e:
            logger.error(f"Error completing quest: {e}")
            return await self._show_completion_error(str(e))
    
    async def _show_completion_success(self, quest, response):
        """Show quest completion success message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        title = quest.get("title", "Unknown Quest")
        xp_reward = quest.get("xp_reward", 0)
        tier = quest.get("tier", "shadow")
        
        # Tier styling
        tier_info = {
            "shadow": ("\x1b[1;34m", "🌑", "SHADOW TIER"),
            "warrior": ("\x1b[1;33m", "⚔️", "WARRIOR TIER"),
            "ascendant": ("\x1b[1;31m", "⭐", "ASCENDANT TIER")
        }
        tier_color, tier_emoji, tier_name = tier_info.get(tier, ("\x1b[1;37m", "📋", "UNKNOWN TIER"))
        
        # Additional rewards from response
        total_xp = response.get("xp_gained", xp_reward)
        bonus_xp = total_xp - xp_reward if total_xp > xp_reward else 0
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;32m● Quest Completed Successfully!\x1b[0m\n"
            f"Status: \x1b[1;32m✅ VICTORY ACHIEVED\x1b[0m\n"
            f"Quest: {tier_color}{tier_emoji} {tier_name}\x1b[0m\n"
            f"Challenge: \x1b[1;37m{title}\x1b[0m\n\n"
            f"\x1b[1;37m🏆 Rewards Earned:\x1b[0m\n"
            f"├─ Base XP: \x1b[1;33m{xp_reward}\x1b[0m points\n"
        )
        
        if bonus_xp > 0:
            content += f"├─ Bonus XP: \x1b[1;33m+{bonus_xp}\x1b[0m points\n"
        
        content += (
            f"└─ Total XP: \x1b[1;32m{total_xp}\x1b[0m points\n\n"
            f"\x1b[1;37m⭐ Achievement Recognition:\x1b[0m\n"
            f"Outstanding dedication to your training!\n"
            f"Your commitment to excellence drives\n"
            f"continuous progress and mastery.\n\n"
            f"\x1b[1;37m📈 Progress Impact:\x1b[0m\n"
            f"This completion contributes to your\n"
            f"overall advancement and skill development.\n\n"
            f"\x1b[1;37m🎯 Next Steps:\x1b[0m\n"
            f"Continue with remaining quests or\n"
            f"review your session progress.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.green()
        )
        embed.set_footer(text="Shadow Archive • Quest Completion • Victory!")
        
        return embed, self.view
    
    async def _show_already_completed(self):
        """Show message when quest is already completed"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        quest = self.view.get_current_quest()
        title = quest.get("title", "Unknown Quest") if quest else "Unknown Quest"
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;33m● Quest Already Completed\x1b[0m\n"
            f"Status: \x1b[1;32m✅ PREVIOUSLY CONQUERED\x1b[0m\n"
            f"Quest: \x1b[1;37m{title}\x1b[0m\n"
            f"Action: \x1b[1;33m⚠️ DUPLICATE ATTEMPT\x1b[0m\n\n"
            f"\x1b[1;37m🏆 Already Achieved:\x1b[0m\n"
            f"This quest has already been completed\n"
            f"with excellence. Rewards have been\n"
            f"distributed and progress recorded.\n\n"
            f"\x1b[1;37m🎯 Available Actions:\x1b[0m\n"
            f"├─ Navigate to pending quests\n"
            f"├─ Review session progress\n"
            f"├─ Check remaining challenges\n"
            f"└─ Return to awakening overview\n\n"
            f"\x1b[1;37m💡 Training Wisdom:\x1b[0m\n"
            f"Focus your energy on the challenges\n"
            f"that still await your dedication.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Shadow Archive • Quest Completion • Already Complete")
        
        return embed, self.view
    
    async def _show_completion_error(self, error_msg):
        """Show quest completion error message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Quest Completion Failed\x1b[0m\n"
            f"Status: \x1b[1;31m❌ COMPLETION ERROR\x1b[0m\n"
            f"API: \x1b[1;31m🚫 REQUEST FAILED\x1b[0m\n"
            f"Error: \x1b[1;31m⚠️ SYSTEM ISSUE\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Technical Details:\x1b[0m\n"
            f"Unable to complete quest due to a\n"
            f"system error or connectivity issue.\n\n"
            f"\x1b[1;37m📋 Error Information:\x1b[0m\n"
            f"{error_msg[:100]}{'...' if len(error_msg) > 100 else ''}\n\n"
            f"\x1b[1;37m🔄 Recovery Actions:\x1b[0m\n"
            f"├─ Verify network connectivity\n"
            f"├─ Try completing quest again\n"
            f"├─ Check system status\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Alternative:\x1b[0m\n"
            f"Return to the quest overview and\n"
            f"attempt completion again later.\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Quest Completion • Error")
        
        return embed, self.view