"""
Enhanced Awakening Panel UI - V2
Integrates with the new quest generation engine for improved user experience
"""

import discord
import asyncio
import sentry_sdk
import logging
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

logger = logging.getLogger(__name__)

# --- ENHANCED AWAKENING PANEL EMBED ---
async def build_enhanced_awakening_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Build the enhanced awakening panel embed with new quest engine integration"""
    
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("awakening")
    
    try:
        # Get awakening status from API
        api_client = APIClient()
        status_response = await api_client.get_awakening_status(user)
        
        if status_response and "awakening_exists" in status_response:
            status = status_response
        else:
            # Fallback status
            status = {
                "awakening_exists": False,
                "status": "pending",
                "readiness_level": None,
                "quest_count": 0,
                "completed_quests": 0,
                "total_xp_gained": 0,
                "session_theme": None
            }
        
        # Build ANSI-styled content with enhanced visuals
        if not status["awakening_exists"]:
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
            
    except Exception as e:
        logger.error(f"Error building enhanced awakening panel embed: {e}")
        sentry_sdk.capture_exception(e)
        
        # Enhanced fallback embed
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● System Disruption\x1b[0m\n"
            f"Status: \x1b[1;31m⚠️ TEMPORARILY OFFLINE\x1b[0m\n"
            f"Engine: \x1b[1;31m🔧 MAINTENANCE MODE\x1b[0m\n"
            f"API: \x1b[1;31m📡 CONNECTION LOST\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Technical Details:\x1b[0m\n"
            f"The awakening system is temporarily unavailable.\n"
            f"Our technicians are working to restore service.\n\n"
            f"\x1b[1;37m🔄 Recovery Actions:\x1b[0m\n"
            f"├─ Verify network connectivity\n"
            f"├─ Check system status updates\n"
            f"├─ Retry in a few moments\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Error Code:\x1b[0m\n"
            f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Error Recovery")
    
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
    
    async def _perform_enhanced_awakening(self):
        """Perform the enhanced awakening ritual with new quest engine"""
        try:
            # Get user data for quest generation
            api_client = APIClient()
            user_data = await api_client.get_user_data(self.view.user)
            user_level = user_data.get("level", 1) if user_data else 1
            
            # Generate awakening session using new quest engine
            quest_session = generate_awakening_for_user(
                user_id=self.view.user.id,
                user_level=user_level,
                readiness_level=self.readiness_level,
                preferences=user_data.get("preferences") if user_data else None
            )
            
            # Call awakening API with generated session
            response = await api_client.perform_enhanced_awakening(
                self.view.user,
                self.readiness_level,
                quest_session
            )
            
            if response and "awakening" in response:
                # Show enhanced awakening results
                return await self._show_enhanced_awakening_results(response, quest_session)
            else:
                # Handle error with enhanced styling
                return await self._show_awakening_error("API response invalid")
                
        except Exception as e:
            logger.error(f"Error performing enhanced awakening: {e}")
            sentry_sdk.capture_exception(e)
            return await self._show_awakening_error(str(e))
    
    async def _show_enhanced_awakening_results(self, response: Dict[str, Any], quest_session) -> tuple:
        """Show enhanced results of the awakening ritual"""
        
        awakening = response["awakening"]
        quests = response.get("quests", quest_session.quests)
        briefing = response.get("daily_briefing", {})
        
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
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.green()
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Quest Engine Powered")
        
        # Create enhanced view with quest actions
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        await view.update_buttons_for_awakened_state()
        return embed, view
    
    async def _show_awakening_error(self, error_msg: str) -> tuple:
        """Show enhanced error message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Awakening Disrupted\x1b[0m\n"
            f"Status: \x1b[1;31m⚠️ RITUAL FAILED\x1b[0m\n"
            f"Engine: \x1b[1;31m🔧 ERROR STATE\x1b[0m\n"
            f"Readiness: \x1b[1;33m{self.readiness_level.upper()}\x1b[0m\n\n"
            f"\x1b[1;37m🛠️ Technical Details:\x1b[0m\n"
            f"The awakening ritual encountered an issue.\n"
            f"Your readiness selection was recorded.\n\n"
            f"\x1b[1;37m🔄 Recovery Options:\x1b[0m\n"
            f"├─ Retry the awakening process\n"
            f"├─ Check system connectivity\n"
            f"├─ Wait a moment and try again\n"
            f"└─ Contact support if persistent\n\n"
            f"\x1b[1;37m💡 Error Details:\x1b[0m\n"
            f"{error_msg[:50]}{'...' if len(error_msg) > 50 else ''}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Awakening V2 • Error Recovery")
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        return embed, view

class BackToAwakeningButton(discord.ui.Button):
    """Enhanced button to go back to main awakening panel"""
    
    def __init__(self):
        super().__init__(label="⬅️ Return to Awakening", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._go_back)
    
    async def _go_back(self):
        """Go back to enhanced main awakening panel"""
        view = EnhancedAwakeningMainView(self.view.bot, self.view.user)
        embed = await build_enhanced_awakening_embed(self.view.bot, self.view.user)
        return embed, view

# --- ENHANCED MAIN AWAKENING VIEW ---
class EnhancedAwakeningMainView(discord.ui.View):
    """Enhanced main view for the awakening panel with new quest engine integration"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        
        # Add dropdown FIRST (above buttons like other panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add buttons conditionally based on awakening status
        self._add_conditional_buttons()
    
    def _add_conditional_buttons(self):
        """Add buttons based on awakening status"""
        # Always add the enhanced Begin Awakening button
        self.add_item(EnhancedAwakeningButton())
        
        # Other buttons will be added dynamically after awakening is complete
    
    async def update_buttons_for_awakened_state(self):
        """Update view to show all enhanced buttons after awakening"""
        # Clear existing buttons (except dropdown and awakening button)
        items_to_keep = []
        for item in self.children:
            if hasattr(item, '__class__') and (
                item.__class__.__name__ == 'EphemeralPanelSelect' or 
                item.__class__.__name__ == 'EnhancedAwakeningButton'
            ):
                items_to_keep.append(item)
        
        # Clear all items and re-add the ones we want to keep
        self.clear_items()
        for item in items_to_keep:
            self.add_item(item)
        
        # Add the enhanced buttons for awakened state
        self.add_item(EnhancedViewQuestsButton())
        self.add_item(EnhancedViewBriefingButton())
        self.add_item(EnhancedViewHistoryButton())

class EnhancedAwakeningButton(discord.ui.Button):
    """Enhanced button to start awakening ritual"""
    
    def __init__(self):
        super().__init__(label="🌅 Begin Shadow Awakening", style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This awakening ritual isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._check_enhanced_awakening_status)
    
    async def _check_enhanced_awakening_status(self):
        """Check if awakening is possible today with enhanced feedback"""
        try:
            # Check awakening status
            api_client = APIClient()
            status = await api_client.get_awakening_status(self.view.user)
            
            if status and status.get("awakening_exists"):
                # Already awakened today - show enhanced status
                await self.view.update_buttons_for_awakened_state()
                
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                readiness = status.get("readiness_level", "unknown")
                session_theme = status.get("session_theme", "Shadow Training")
                completed = status.get("completed_quests", 0)
                total = status.get("quest_count", 0)
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● Awakening Already Complete\x1b[0m\n"
                    f"Session: \x1b[1;36m{session_theme}\x1b[0m\n"
                    f"Status: \x1b[1;32m✅ ACTIVE\x1b[0m\n"
                    f"Progress: \x1b[1;33m{completed}/{total}\x1b[0m quests\n\n"
                    f"\x1b[1;37m🎯 Current Session:\x1b[0m\n"
                    f"Your daily awakening ritual has been completed.\n"
                    f"Your personalized quest selection is active and\n"
                    f"ready for execution.\n\n"
                    f"\x1b[1;37m⚔️ Available Actions:\x1b[0m\n"
                    f"├─ View detailed quest information\n"
                    f"├─ Access daily briefing insights\n"
                    f"├─ Complete remaining challenges\n"
                    f"└─ Review awakening history\n\n"
                    f"\x1b[1;37m🔄 Next Awakening:\x1b[0m\n"
                    f"Return tomorrow for a fresh ritual and new\n"
                    f"quest generation opportunities.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening V2 • Session Active")
                return embed, self.view
            else:
                # Show enhanced readiness selection
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Shadow Awakening Ritual\x1b[0m\n"
                    f"Status: \x1b[1;33m🌅 READY TO BEGIN\x1b[0m\n"
                    f"Engine: \x1b[1;32m⚡ V2 QUEST SYSTEM\x1b[0m\n"
                    f"Date: \x1b[1;37m{date.today().strftime('%A, %B %d')}\x1b[0m\n\n"
                    f"\x1b[1;37m🎯 Energy Assessment Protocol:\x1b[0m\n"
                    f"Select your current energy level for optimal\n"
                    f"quest generation and training personalization.\n\n"
                    f"\x1b[1;37m⚡ Enhanced Readiness Options:\x1b[0m\n"
                    f"🔋 Recovery Mode - Gentle movement, form focus\n"
                    f"⚖️ Balanced Training - Steady progression\n"
                    f"🔥 Peak Intensity - Maximum challenge\n\n"
                    f"\x1b[1;37m🧠 Smart Autoregulation:\x1b[0m\n"
                    f"Your selection influences quest difficulty,\n"
                    f"movement categories, XP scaling, and session\n"
                    f"duration for optimal training adaptation.\n\n"
                    f"\x1b[1;37m💡 V-Taper Focus:\x1b[0m\n"
                    f"Quest generation prioritizes movements that\n"
                    f"build shoulder width and back development.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Shadow Archive • Awakening V2 • Quest Engine Ready")
                
                view = EnhancedReadinessSelectionView(self.view.bot, self.view.user)
                return embed, view
                
        except Exception as e:
            logger.error(f"Error checking enhanced awakening status: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● System Disruption\x1b[0m\n"
                f"Status: \x1b[1;31m⚠️ CONNECTION LOST\x1b[0m\n"
                f"Engine: \x1b[1;31m🔧 OFFLINE\x1b[0m\n"
                f"API: \x1b[1;31m📡 UNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37m🛠️ Technical Analysis:\x1b[0m\n"
                f"Unable to establish connection with the\n"
                f"awakening system. Service temporarily\n"
                f"unavailable.\n\n"
                f"\x1b[1;37m🔄 Recovery Protocol:\x1b[0m\n"
                f"├─ Verify network connectivity\n"
                f"├─ Check system status updates\n"
                f"├─ Retry in a few moments\n"
                f"└─ Contact support if persistent\n\n"
                f"\x1b[1;37m💡 Error Details:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening V2 • Error Recovery")
            return embed, self.view

class EnhancedViewQuestsButton(discord.ui.Button):
    """Enhanced button to view today's awakening quests"""
    
    def __init__(self):
        super().__init__(label="⚔️ View Quest Selection", style=discord.ButtonStyle.success)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This quest selection isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_enhanced_quests)
    
    async def _show_enhanced_quests(self):
        """Show today's awakening quests with enhanced display"""
        try:
            api_client = APIClient()
            quests = await api_client.get_awakening_quests(self.view.user)
            
            if not quests:
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● Quest Selection Unavailable\x1b[0m\n"
                    f"Status: \x1b[1;33m⏳ PENDING GENERATION\x1b[0m\n"
                    f"Engine: \x1b[1;31m🔧 AWAITING RITUAL\x1b[0m\n"
                    f"Quests: \x1b[1;31m❌ NOT GENERATED\x1b[0m\n\n"
                    f"\x1b[1;37m🌅 Required Action:\x1b[0m\n"
                    f"Complete your daily awakening ritual to\n"
                    f"generate today's personalized quest selection\n"
                    f"using the enhanced V2 quest engine.\n\n"
                    f"\x1b[1;37m⚡ Quest Generation Features:\x1b[0m\n"
                    f"├─ Smart autoregulation based on readiness\n"
                    f"├─ V-taper focused movement selection\n"
                    f"├─ Dynamic difficulty scaling\n"
                    f"├─ Thematic quest descriptions\n"
                    f"└─ Progressive XP and stat rewards\n\n"
                    f"\x1b[1;37m🎯 Next Steps:\x1b[0m\n"
                    f"Use 'Begin Shadow Awakening' to start your\n"
                    f"daily ritual and unlock training opportunities.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening V2 • Quest Generation Pending")
                return embed, self.view
            
            # Show enhanced quest details view
            view = EnhancedQuestDetailsView(self.view.bot, self.view.user, quests)
            embed = view.build_enhanced_quest_embed(0)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching enhanced quests: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Quest Retrieval Failed\x1b[0m\n"
                f"Status: \x1b[1;31m⚠️ FETCH ERROR\x1b[0m\n"
                f"Engine: \x1b[1;31m🔧 DATA UNAVAILABLE\x1b[0m\n"
                f"API: \x1b[1;31m📡 CONNECTION LOST\x1b[0m\n\n"
                f"\x1b[1;37m🛠️ Technical Details:\x1b[0m\n"
                f"Unable to retrieve quest data from the\n"
                f"awakening system. Service temporarily\n"
                f"disrupted.\n\n"
                f"\x1b[1;37m🔄 Recovery Options:\x1b[0m\n"
                f"├─ Retry quest data retrieval\n"
                f"├─ Check network connectivity\n"
                f"├─ Verify awakening completion\n"
                f"└─ Contact support if persistent\n\n"
                f"\x1b[1;37m💡 Error Code:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening V2 • Error Recovery")
            return embed, self.view

class EnhancedViewBriefingButton(discord.ui.Button):
    """Enhanced button to view daily briefing"""
    
    def __init__(self):
        super().__init__(label="📊 Daily Intelligence", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This briefing isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_enhanced_briefing)
    
    async def _show_enhanced_briefing(self):
        """Show enhanced daily briefing"""
        # Implementation similar to original but with enhanced styling
        # This would be implemented with the same pattern as above
        pass

class EnhancedViewHistoryButton(discord.ui.Button):
    """Enhanced button to view awakening history"""
    
    def __init__(self):
        super().__init__(label="📜 Shadow Archive", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This archive isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_enhanced_history)
    
    async def _show_enhanced_history(self):
        """Show enhanced awakening history"""
        # Implementation similar to original but with enhanced styling
        # This would be implemented with the same pattern as above
        pass

# --- ENHANCED QUEST DETAILS VIEW ---
class EnhancedQuestDetailsView(discord.ui.View):
    """Enhanced view for displaying quest details with new quest engine data"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], quests: List[Dict]):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        self.quests = quests
        self.current_index = 0
        
        # Add dropdown FIRST
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add navigation and action buttons
        if len(quests) > 1:
            self.add_item(PreviousQuestButton())
            self.add_item(NextQuestButton())
        
        self.add_item(CompleteQuestButton())
        self.add_item(BackToAwakeningButton())
    
    def build_enhanced_quest_embed(self, index: int) -> discord.Embed:
        """Build enhanced quest embed with new quest engine data"""
        
        if not self.quests or index >= len(self.quests):
            return discord.Embed(
                description="No quest data available.",
                color=discord.Color.red()
            )
        
        quest = self.quests[index]
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Enhanced quest information display
        quest_data = quest.get("quest_data", {})
        title = quest_data.get("title", "Unknown Quest")
        description = quest_data.get("description", "No description available")
        target_reps = quest_data.get("target_reps", 0)
        target_sets = quest_data.get("target_sets", 1)
        xp_reward = quest_data.get("xp_reward", 0)
        tier = quest_data.get("tier", "shadow")
        movement_category = quest_data.get("movement_category", "unknown")
        estimated_duration = quest_data.get("estimated_duration_minutes", 5)
        
        # Status styling
        status = quest.get("status", "pending")
        status_info = {
            "pending": ("\x1b[1;33m", "⏳", "READY TO START"),
            "completed": ("\x1b[1;32m", "✅", "COMPLETED"),
            "active": ("\x1b[1;36m", "⚡", "IN PROGRESS")
        }
        status_color, status_emoji, status_text = status_info.get(status, ("\x1b[1;37m", "❓", "UNKNOWN"))
        
        # Tier styling
        tier_info = {
            "shadow": ("\x1b[1;34m", "🌑", "SHADOW PRACTICE"),
            "warrior": ("\x1b[1;33m", "⚔️", "WARRIOR'S TRIAL"),
            "ascendant": ("\x1b[1;31m", "⭐", "ASCENDANT'S CHALLENGE")
        }
        tier_color, tier_emoji, tier_text = tier_info.get(tier.lower(), ("\x1b[1;37m", "📋", "STANDARD"))
        
        # Category styling
        category_emojis = {
            "pull": "🔗", "push_h": "👐", "push_v": "⬆️",
            "legs": "🦵", "core": "💪", "accessory_shoulders": "🔺"
        }
        category_emoji = category_emojis.get(movement_category.lower(), "⚔️")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Quest Details ({index + 1}/{len(self.quests)})\x1b[0m\n"
            f"Status: {status_color}{status_emoji} {status_text}\x1b[0m\n"
            f"Tier: {tier_color}{tier_emoji} {tier_text}\x1b[0m\n"
            f"Category: \x1b[1;37m{category_emoji} {movement_category.upper()}\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ Quest Title:\x1b[0m\n"
            f"{title}\n\n"
            f"\x1b[1;37m📋 Objective:\x1b[0m\n"
            f"Execute \x1b[1;33m{target_sets}\x1b[0m sets × \x1b[1;33m{target_reps}\x1b[0m reps\n\n"
            f"\x1b[1;37m📊 Quest Parameters:\x1b[0m\n"
            f"├─ XP Reward: \x1b[1;33m{xp_reward}\x1b[0m points\n"
            f"├─ Duration: \x1b[1;33m~{estimated_duration}\x1b[0m minutes\n"
            f"├─ Difficulty: {tier_color}{tier_text}\x1b[0m\n"
            f"└─ Focus: \x1b[1;37m{category_emoji} {movement_category.title()}\x1b[0m\n\n"
            f"\x1b[1;37m📖 Description:\x1b[0m\n"
            f"{description[:200]}{'...' if len(description) > 200 else ''}\n\n"
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
        
        return embed

# Reuse navigation buttons from original (PreviousQuestButton, NextQuestButton, CompleteQuestButton)
# with enhanced styling...

# --- ENHANCED PANEL REGISTRATION ---
@register
class EnhancedAwakeningPanel:
    """Enhanced Awakening Panel V2 for the system hub"""
    key = "awakening_v2"
    label = "Awakening V2"
    emoji = "🌅"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_enhanced_awakening_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return EnhancedAwakeningMainView(bot, user)