"""
Awakening Panel UI - Legacy Version
Handles the daily awakening ritual interface
"""

import discord
import asyncio
import sentry_sdk
import logging
from typing import Union, Dict, Any, Optional
from datetime import date

from shared.utils.ui_helpers import run_with_animation, interaction_handler
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from core.api_client import APIClient

logger = logging.getLogger(__name__)

# --- AWAKENING PANEL EMBED ---
async def build_awakening_panel_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Build the main awakening panel embed"""
    
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
                "total_xp_gained": 0
            }
        
        # Build ANSI-styled content
        if not status["awakening_exists"]:
            # Ready to awaken state
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Ready to Awaken\x1b[0m\n"
                f"Status: \x1b[1;33mPENDING\x1b[0m\n"
                f"Ritual: \x1b[1;33mAWAITING\x1b[0m\n\n"
                f"\x1b[1;37mDaily Awakening:\x1b[0m\n"
                f"Begin your daily ritual to unlock today's quests.\n"
                f"Your energy level selection will determine quest\n"
                f"difficulty and training intensity.\n\n"
                f"\x1b[1;37mNext Steps:\x1b[0m\n"
                f"├─ Choose your current energy level honestly\n"
                f"├─ Complete the awakening ritual\n"
                f"└─ Unlock personalized quest selection\n\n"
                f"\x1b[1;37mAutoregulation Tip:\x1b[0m\n"
                f"Listen to your body and select the energy level\n"
                f"that matches how you feel today.\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            color = discord.Color.blue()
            
        elif status["status"] == "awakened":
            # Awakened state with progress
            completed = status.get("completed_quests", 0)
            total = status.get("quest_count", 0)
            xp_gained = status.get("total_xp_gained", 0)
            readiness = status.get("readiness_level", "unknown")
            
            # Progress bar
            if total > 0:
                progress_percent = (completed / total) * 100
                filled_blocks = int(progress_percent / 10)
                progress_bar = "█" * filled_blocks + "░" * (10 - filled_blocks)
            else:
                progress_bar = "░" * 10
                progress_percent = 0
            
            # Readiness styling
            readiness_info = {
                "low": ("\x1b[1;34m", "🔋", "LOW ENERGY"),
                "standard": ("\x1b[1;33m", "⚖️", "STANDARD ENERGY"), 
                "high": ("\x1b[1;31m", "🔥", "HIGH ENERGY")
            }
            color_code, emoji, level_text = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN"))
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;32m● Awakened\x1b[0m\n"
                f"Status: \x1b[1;32mACTIVE\x1b[0m\n"
                f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n\n"
                f"\x1b[1;37mQuest Progress:\x1b[0m\n"
                f"Completed: \x1b[1;33m{completed}\x1b[0m / \x1b[1;37m{total}\x1b[0m\n"
                f"Progress: [{progress_bar}] \x1b[1;33m{progress_percent:.0f}%\x1b[0m\n"
                f"XP Gained: \x1b[1;33m{xp_gained}\x1b[0m\n\n"
                f"\x1b[1;37mDaily Status:\x1b[0m\n"
            )
            
            if completed >= total and total > 0:
                content += (
                    f"🎉 All quests completed! Excellent work today.\n"
                    f"Your dedication to training is paying off.\n\n"
                    f"\x1b[1;37mNext Steps:\x1b[0m\n"
                    f"├─ Review your progress in History\n"
                    f"├─ Check tomorrow's awakening opportunity\n"
                    f"└─ Continue your consistency streak\n\n"
                )
                color = discord.Color.green()
            else:
                content += (
                    f"Continue working through your quest selection.\n"
                    f"Each completed quest brings valuable XP and\n"
                    f"progress toward your fitness goals.\n\n"
                    f"\x1b[1;37mAvailable Actions:\x1b[0m\n"
                    f"├─ View detailed quest information\n"
                    f"├─ Complete remaining quests\n"
                    f"└─ Check daily briefing for insights\n\n"
                )
                color = discord.Color.orange()
                
            content += "──────────────────────────\n```"
            
        else:
            # Completed state
            xp_gained = status.get("total_xp_gained", 0)
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;32m● Awakening Complete\x1b[0m\n"
                f"Status: \x1b[1;32mFINISHED\x1b[0m\n"
                f"Daily Goal: \x1b[1;32mACHIEVED\x1b[0m\n\n"
                f"\x1b[1;37mToday's Results:\x1b[0m\n"
                f"All quests have been completed successfully!\n"
                f"Total XP earned: \x1b[1;33m{xp_gained}\x1b[0m\n\n"
                f"\x1b[1;37mCongratulations:\x1b[0m\n"
                f"You've demonstrated excellent commitment to\n"
                f"your training regimen. Keep up the momentum!\n\n"
                f"\x1b[1;37mNext Opportunity:\x1b[0m\n"
                f"Return tomorrow for a fresh awakening ritual\n"
                f"and new quest challenges.\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            color = discord.Color.green()
        
        embed = discord.Embed(
            description=content,
            color=color
        )
        
        # Standard footer format matching other panels
        embed.set_footer(text="Shadow Archive • Awakening")
            
    except Exception as e:
        logger.error(f"Error building awakening panel embed: {e}")
        sentry_sdk.capture_exception(e)
        
        # Fallback embed with ANSI styling
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● System Error\x1b[0m\n"
            f"Status: \x1b[1;31mUNAVAILABLE\x1b[0m\n"
            f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
            f"\x1b[1;37mError Details:\x1b[0m\n"
            f"Unable to load awakening status from server.\n"
            f"Please try again in a few moments.\n\n"
            f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
            f"├─ Check your network connection\n"
            f"├─ Verify server status\n"
            f"└─ Contact support if issue persists\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Awakening")
    
    return embed

# --- READINESS SELECTION VIEW ---
class ReadinessSelectionView(discord.ui.View):
    """View for selecting readiness level during awakening"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.user = user
        
        # Add readiness level buttons
        self.add_item(ReadinessButton("low", "🔋 Low Energy", discord.ButtonStyle.secondary))
        self.add_item(ReadinessButton("standard", "⚖️ Standard Energy", discord.ButtonStyle.primary))
        self.add_item(ReadinessButton("high", "🔥 High Energy", discord.ButtonStyle.danger))
        self.add_item(BackToAwakeningButton())

class ReadinessButton(discord.ui.Button):
    """Button for selecting readiness level"""
    
    def __init__(self, readiness_level: str, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.readiness_level = readiness_level
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This awakening ritual isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._perform_awakening)
    
    async def _perform_awakening(self):
        """Perform the awakening ritual"""
        try:
            # Call awakening API
            api_client = APIClient()
            response = await api_client.perform_awakening(self.view.user, self.readiness_level)
            
            if response and "awakening" in response:
                # Show awakening results
                return await self._show_awakening_results(response)
            else:
                # Handle error
                return await self._show_awakening_error("API response invalid")
                
        except Exception as e:
            logger.error(f"Error performing awakening: {e}")
            sentry_sdk.capture_exception(e)
            return await self._show_awakening_error(str(e))
    
    async def _show_awakening_results(self, response: Dict[str, Any]) -> tuple:
        """Show results of the awakening ritual"""
        
        awakening = response["awakening"]
        quests = response.get("quests", [])
        briefing = response.get("daily_briefing", {})
        
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Build quest list
        quest_list = ""
        for i, quest in enumerate(quests):
            title = quest.get('title', 'Unknown Quest')
            if i == len(quests) - 1:  # Last item
                quest_list += f"└─ {title}"
            else:
                quest_list += f"├─ {title}\n"
        
        readiness = awakening.get("readiness_level", "unknown")
        readiness_info = {
            "low": ("\x1b[1;34m", "🔋", "LOW ENERGY"),
            "standard": ("\x1b[1;33m", "⚖️", "STANDARD ENERGY"), 
            "high": ("\x1b[1;31m", "🔥", "HIGH ENERGY")
        }
        color_code, emoji, level_text = readiness_info.get(readiness, ("\x1b[1;37m", "❓", "UNKNOWN"))
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;32m● Awakening Complete\x1b[0m\n"
            f"Status: \x1b[1;32mSUCCESS\x1b[0m\n"
            f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n\n"
            f"\x1b[1;37mGenerated Quests:\x1b[0m\n"
            f"{quest_list}\n\n"
            f"\x1b[1;37mDaily Briefing:\x1b[0m\n"
            f"{briefing.get('awakening_summary', 'Your daily quest selection is ready.')}\n\n"
            f"\x1b[1;37mNext Steps:\x1b[0m\n"
            f"├─ View detailed quest information\n"
            f"├─ Begin completing your quests\n"
            f"└─ Track your progress throughout the day\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.green()
        )
        embed.set_footer(text="Shadow Archive • Awakening")
        
        # Create main view with quest actions
        view = AwakeningMainView(self.view.bot, self.view.user)
        await view.update_buttons_for_awakened_state()
        return embed, view
    
    async def _show_awakening_error(self, error_msg: str) -> tuple:
        """Show error message"""
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● Awakening Failed\x1b[0m\n"
            f"Status: \x1b[1;31mERROR\x1b[0m\n"
            f"Readiness: \x1b[1;33m{self.readiness_level.upper()}\x1b[0m\n\n"
            f"\x1b[1;37mError Details:\x1b[0m\n"
            f"The awakening ritual encountered an issue.\n"
            f"Your readiness selection was recorded.\n\n"
            f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
            f"├─ Check your network connection\n"
            f"├─ Verify server status\n"
            f"├─ Try again in a few moments\n"
            f"└─ Contact support if issue persists\n\n"
            f"\x1b[1;37mTechnical Info:\x1b[0m\n"
            f"{error_msg[:50]}{'...' if len(error_msg) > 50 else ''}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Awakening")
        view = AwakeningMainView(self.view.bot, self.view.user)
        return embed, view

class BackToAwakeningButton(discord.ui.Button):
    """Button to go back to main awakening panel"""
    
    def __init__(self):
        super().__init__(label="⬅️ Back to Awakening", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user.id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._go_back)
    
    async def _go_back(self):
        """Go back to main awakening panel"""
        view = AwakeningMainView(self.view.bot, self.view.user)
        embed = await build_awakening_panel_embed(self.view.bot, self.view.user)
        return embed, view

# --- MAIN AWAKENING VIEW ---
class AwakeningMainView(discord.ui.View):
    """Main view for the awakening panel"""
    
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
        # Always add the Begin Awakening button
        self.add_item(AwakeningButton())
        
        # Other buttons will be added dynamically after awakening is complete
    
    async def update_buttons_for_awakened_state(self):
        """Update view to show all buttons after awakening"""
        # Clear existing buttons (except dropdown and awakening button)
        items_to_keep = []
        for item in self.children:
            if hasattr(item, '__class__') and (
                item.__class__.__name__ == 'EphemeralPanelSelect' or 
                item.__class__.__name__ == 'AwakeningButton'
            ):
                items_to_keep.append(item)
        
        # Clear all items and re-add the ones we want to keep
        self.clear_items()
        for item in items_to_keep:
            self.add_item(item)
        
        # Add the buttons for awakened state
        self.add_item(ViewQuestsButton())
        self.add_item(ViewBriefingButton())
        self.add_item(ViewHistoryButton())

class AwakeningButton(discord.ui.Button):
    """Button to start awakening ritual"""
    
    def __init__(self):
        super().__init__(label="🌅 Begin Awakening", style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This awakening ritual isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._check_awakening_status)
    
    async def _check_awakening_status(self):
        """Check if awakening is possible today"""
        try:
            # Check awakening status
            api_client = APIClient()
            status = await api_client.get_awakening_status(self.view.user)
            
            if status and status.get("awakening_exists"):
                # Already awakened today
                await self.view.update_buttons_for_awakened_state()
                
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                readiness = status.get("readiness_level", "unknown")
                completed = status.get("completed_quests", 0)
                total = status.get("quest_count", 0)
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● Already Awakened\x1b[0m\n"
                    f"Status: \x1b[1;32mACTIVE\x1b[0m\n"
                    f"Readiness: \x1b[1;37m{readiness.upper()}\x1b[0m\n"
                    f"Progress: \x1b[1;33m{completed}/{total}\x1b[0m\n\n"
                    f"\x1b[1;37mDaily Status:\x1b[0m\n"
                    f"Your awakening ritual has been completed for today.\n"
                    f"Your quest selection is active and ready.\n\n"
                    f"\x1b[1;37mAvailable Actions:\x1b[0m\n"
                    f"├─ View your quest details\n"
                    f"├─ Check daily briefing\n"
                    f"├─ Review awakening history\n"
                    f"└─ Complete remaining quests\n\n"
                    f"\x1b[1;37mNext Awakening:\x1b[0m\n"
                    f"Return tomorrow for a fresh ritual.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                return embed, self.view
            else:
                # Show readiness selection
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Readiness Assessment\x1b[0m\n"
                    f"Status: \x1b[1;33mAWAITING SELECTION\x1b[0m\n"
                    f"Date: \x1b[1;37m{date.today().strftime('%A, %B %d')}\x1b[0m\n\n"
                    f"\x1b[1;37mEnergy Level Selection:\x1b[0m\n"
                    f"Choose your current energy level to determine\n"
                    f"today's quest difficulty and training intensity.\n\n"
                    f"\x1b[1;37mOptions:\x1b[0m\n"
                    f"🔋 Low Energy - Recovery focused, gentle movement\n"
                    f"⚖️ Standard Energy - Balanced training approach\n"
                    f"🔥 High Energy - Intense, challenging workouts\n\n"
                    f"\x1b[1;37mAutoregulation:\x1b[0m\n"
                    f"Be honest with your assessment. The system will\n"
                    f"adapt your quest selection accordingly.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                
                view = ReadinessSelectionView(self.view.bot, self.view.user)
                return embed, view
                
        except Exception as e:
            logger.error(f"Error checking awakening status: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Connection Error\x1b[0m\n"
                f"Status: \x1b[1;31mUNAVAILABLE\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to connect to the awakening system.\n"
                f"Please try again in a few moments.\n\n"
                f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
                f"├─ Check your network connection\n"
                f"├─ Verify server status\n"
                f"├─ Try refreshing the panel\n"
                f"└─ Contact support if issue persists\n\n"
                f"\x1b[1;37mTechnical Info:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view

class ViewQuestsButton(discord.ui.Button):
    """Button to view today's awakening quests"""
    
    def __init__(self):
        super().__init__(label="⚔️ View Quests", style=discord.ButtonStyle.success)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This quest list isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_quests)
    
    async def _show_quests(self):
        """Show today's awakening quests"""
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
                    f"\x1b[1;33m● No Quests Available\x1b[0m\n"
                    f"Status: \x1b[1;33mPENDING\x1b[0m\n"
                    f"Quests: \x1b[1;31mNOT GENERATED\x1b[0m\n\n"
                    f"\x1b[1;37mRequired Action:\x1b[0m\n"
                    f"Complete your daily awakening ritual to\n"
                    f"generate today's quest selection.\n\n"
                    f"\x1b[1;37mNext Steps:\x1b[0m\n"
                    f"├─ Return to the main awakening panel\n"
                    f"├─ Begin your awakening ritual\n"
                    f"├─ Select your energy level\n"
                    f"└─ Unlock your personalized quests\n\n"
                    f"\x1b[1;37mNote:\x1b[0m\n"
                    f"Quest generation is tied to your daily\n"
                    f"readiness assessment for optimal training.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                return embed, self.view
            
            # Show quest details view
            view = QuestDetailsView(self.view.bot, self.view.user, quests)
            embed = view.build_quest_embed(0)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching quests: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Quest Fetch Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to retrieve quest data from server.\n"
                f"Please try again in a few moments.\n\n"
                f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
                f"├─ Check your network connection\n"
                f"├─ Verify server status\n"
                f"├─ Ensure awakening is complete\n"
                f"└─ Contact support if issue persists\n\n"
                f"\x1b[1;37mTechnical Info:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view

class ViewBriefingButton(discord.ui.Button):
    """Button to view daily briefing"""
    
    def __init__(self):
        super().__init__(label="📊 Daily Briefing", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This briefing isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_briefing)
    
    async def _show_briefing(self):
        """Show daily briefing"""
        try:
            api_client = APIClient()
            briefing = await api_client.get_daily_briefing(self.view.user)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            if briefing:
                # Extract briefing data
                awakening_summary = briefing.get("awakening_summary", "No summary available")
                quest_overview = briefing.get("quest_overview", "No quest overview")
                progress_highlights = briefing.get("progress_highlights", {})
                readiness_impact = briefing.get("readiness_impact", "No readiness analysis")
                motivation_message = briefing.get("motivation_message", "Stay consistent!")
                
                # Format progress highlights
                weekly_completions = progress_highlights.get("weekly_completions", 0)
                weekly_xp = progress_highlights.get("weekly_xp", 0)
                consistency_streak = progress_highlights.get("consistency_streak", 0)
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Daily Intelligence Briefing\x1b[0m\n"
                    f"Status: \x1b[1;32mACTIVE\x1b[0m\n"
                    f"Date: \x1b[1;37m{date.today().strftime('%A, %B %d')}\x1b[0m\n\n"
                    f"\x1b[1;37mAwakening Summary:\x1b[0m\n"
                    f"{awakening_summary}\n\n"
                    f"\x1b[1;37mQuest Overview:\x1b[0m\n"
                    f"{quest_overview}\n\n"
                    f"\x1b[1;37mProgress Highlights:\x1b[0m\n"
                    f"├─ Weekly Completions: \x1b[1;33m{weekly_completions}\x1b[0m\n"
                    f"├─ Weekly XP: \x1b[1;33m{weekly_xp}\x1b[0m\n"
                    f"└─ Consistency Streak: \x1b[1;33m{consistency_streak} days\x1b[0m\n\n"
                    f"\x1b[1;37mReadiness Impact:\x1b[0m\n"
                    f"{readiness_impact}\n\n"
                    f"\x1b[1;37mMotivation:\x1b[0m\n"
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
                    f"Status: \x1b[1;33mPENDING\x1b[0m\n"
                    f"Data: \x1b[1;31mNOT GENERATED\x1b[0m\n\n"
                    f"\x1b[1;37mRequired Action:\x1b[0m\n"
                    f"Complete your daily awakening ritual to\n"
                    f"generate today's intelligence briefing.\n\n"
                    f"\x1b[1;37mBriefing Contents:\x1b[0m\n"
                    f"├─ Awakening summary and analysis\n"
                    f"├─ Quest overview and recommendations\n"
                    f"├─ Progress highlights and statistics\n"
                    f"├─ Readiness impact assessment\n"
                    f"└─ Personalized motivation message\n\n"
                    f"\x1b[1;37mNext Steps:\x1b[0m\n"
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
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view
            
        except Exception as e:
            logger.error(f"Error fetching briefing: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Briefing Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to retrieve briefing data from server.\n"
                f"Please try again in a few moments.\n\n"
                f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
                f"├─ Check your network connection\n"
                f"├─ Verify server status\n"
                f"├─ Ensure awakening is complete\n"
                f"└─ Contact support if issue persists\n\n"
                f"\x1b[1;37mTechnical Info:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view

class ViewHistoryButton(discord.ui.Button):
    """Button to view awakening history"""
    
    def __init__(self):
        super().__init__(label="📜 History", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This history isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_history)
    
    async def _show_history(self):
        """Show awakening history"""
        try:
            api_client = APIClient()
            history = await api_client.get_awakening_history(self.view.user)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            if history and len(history) > 0:
                # Build history list
                history_list = ""
                for i, entry in enumerate(history[:10]):  # Show last 10 entries
                    date_str = entry.get("date", "Unknown")
                    status = entry.get("status", "unknown")
                    readiness = entry.get("readiness_level", "unknown")
                    
                    # Status styling
                    status_info = {
                        "completed": ("\x1b[1;32m", "✅"),
                        "partial": ("\x1b[1;33m", "⚡"),
                        "pending": ("\x1b[1;31m", "❌")
                    }
                    color_code, emoji = status_info.get(status, ("\x1b[1;37m", "❓"))
                    
                    if i == len(history[:10]) - 1:  # Last item
                        history_list += f"└─ {date_str}: {color_code}{emoji} {readiness.upper()}\x1b[0m"
                    else:
                        history_list += f"├─ {date_str}: {color_code}{emoji} {readiness.upper()}\x1b[0m\n"
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● Awakening History\x1b[0m\n"
                    f"Status: \x1b[1;32mACTIVE\x1b[0m\n"
                    f"Entries: \x1b[1;33m{len(history)}\x1b[0m total\n\n"
                    f"\x1b[1;37mRecent Awakenings:\x1b[0m\n"
                    f"{history_list}\n\n"
                    f"\x1b[1;37mLegend:\x1b[0m\n"
                    f"✅ Completed - All quests finished\n"
                    f"⚡ Partial - Some quests completed\n"
                    f"❌ Pending - Awakening incomplete\n\n"
                    f"\x1b[1;37mConsistency:\x1b[0m\n"
                    f"Your awakening history shows your dedication\n"
                    f"to consistent training and self-awareness.\n\n"
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
                    f"Status: \x1b[1;33mEMPTY\x1b[0m\n"
                    f"Records: \x1b[1;31mNONE FOUND\x1b[0m\n\n"
                    f"\x1b[1;37mGetting Started:\x1b[0m\n"
                    f"Your awakening history will appear here as\n"
                    f"you complete daily rituals and build your\n"
                    f"training consistency.\n\n"
                    f"\x1b[1;37mFirst Steps:\x1b[0m\n"
                    f"├─ Complete your first awakening ritual\n"
                    f"├─ Select your energy level honestly\n"
                    f"├─ Work through your generated quests\n"
                    f"└─ Build your consistency streak\n\n"
                    f"\x1b[1;37mBenefits:\x1b[0m\n"
                    f"Tracking your awakening patterns helps\n"
                    f"optimize training and build awareness.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                color = discord.Color.orange()
            
            embed = discord.Embed(
                description=content,
                color=color
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● History Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to retrieve history data from server.\n"
                f"Please try again in a few moments.\n\n"
                f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
                f"├─ Check your network connection\n"
                f"├─ Verify server status\n"
                f"├─ Try refreshing the panel\n"
                f"└─ Contact support if issue persists\n\n"
                f"\x1b[1;37mTechnical Info:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view

# --- QUEST DETAILS VIEW ---
class QuestDetailsView(discord.ui.View):
    """View for displaying quest details"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], quests: list):
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
            self.add_item(PrevQuestButton())
            self.add_item(NextQuestButton())
        
        self.add_item(CompleteQuestButton())
        self.add_item(BackToAwakeningView())
    
    def build_quest_embed(self, index: int) -> discord.Embed:
        """Build quest embed for the given index"""
        
        if not self.quests or index >= len(self.quests):
            return discord.Embed(
                description="No quest data available.",
                color=discord.Color.red()
            )
        
        quest = self.quests[index]
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Extract quest information
        quest_data = quest.get("quest_data", {})
        title = quest_data.get("title", "Unknown Quest")
        description = quest_data.get("description", "No description available")
        target_reps = quest_data.get("target_reps", 0)
        target_sets = quest_data.get("target_sets", 1)
        xp_reward = quest_data.get("xp_reward", 0)
        
        # Status styling
        status = quest.get("status", "pending")
        status_info = {
            "pending": ("\x1b[1;33m", "⏳", "READY"),
            "completed": ("\x1b[1;32m", "✅", "COMPLETE"),
            "active": ("\x1b[1;36m", "⚡", "ACTIVE")
        }
        status_color, status_emoji, status_text = status_info.get(status, ("\x1b[1;37m", "❓", "UNKNOWN"))
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Quest Details ({index + 1}/{len(self.quests)})\x1b[0m\n"
            f"Status: {status_color}{status_emoji} {status_text}\x1b[0m\n"
            f"Reward: \x1b[1;33m{xp_reward} XP\x1b[0m\n\n"
            f"\x1b[1;37mQuest Title:\x1b[0m\n"
            f"{title}\n\n"
            f"\x1b[1;37mObjective:\x1b[0m\n"
            f"Complete \x1b[1;33m{target_sets}\x1b[0m sets of \x1b[1;33m{target_reps}\x1b[0m reps\n\n"
            f"\x1b[1;37mDescription:\x1b[0m\n"
            f"{description[:150]}{'...' if len(description) > 150 else ''}\n\n"
            f"\x1b[1;37mNavigation:\x1b[0m\n"
            f"Use the buttons below to navigate between\n"
            f"quests and mark them as complete.\n\n"
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
        embed.set_footer(text="Shadow Archive • Awakening")
        
        return embed

class PrevQuestButton(discord.ui.Button):
    """Button to go to previous quest"""
    
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This quest list isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._prev_quest)
    
    async def _prev_quest(self):
        """Go to previous quest"""
        if self.view.current_index > 0:
            self.view.current_index -= 1
        else:
            self.view.current_index = len(self.view.quests) - 1  # Wrap to last
        
        embed = self.view.build_quest_embed(self.view.current_index)
        return embed, self.view

class NextQuestButton(discord.ui.Button):
    """Button to go to next quest"""
    
    def __init__(self):
        super().__init__(label="➡️ Next", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This quest list isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._next_quest)
    
    async def _next_quest(self):
        """Go to next quest"""
        if self.view.current_index < len(self.view.quests) - 1:
            self.view.current_index += 1
        else:
            self.view.current_index = 0  # Wrap to first
        
        embed = self.view.build_quest_embed(self.view.current_index)
        return embed, self.view

class CompleteQuestButton(discord.ui.Button):
    """Button to complete current quest"""
    
    def __init__(self):
        super().__init__(label="✅ Complete Quest", style=discord.ButtonStyle.success)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This quest isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._complete_quest)
    
    async def _complete_quest(self):
        """Complete the current quest"""
        try:
            current_quest = self.view.quests[self.view.current_index]
            quest_id = current_quest.get("id")
            
            if not quest_id:
                raise ValueError("Quest ID not found")
            
            # Call API to complete quest
            api_client = APIClient()
            response = await api_client.complete_awakening_quest(self.view.user, quest_id)
            
            if response and response.get("success"):
                # Update quest status locally
                self.view.quests[self.view.current_index]["status"] = "completed"
                
                # Show success message
                xp_gained = response.get("xp_gained", 0)
                
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;32m● Quest Completed!\x1b[0m\n"
                    f"Status: \x1b[1;32m✅ SUCCESS\x1b[0m\n"
                    f"XP Gained: \x1b[1;33m{xp_gained}\x1b[0m\n\n"
                    f"\x1b[1;37mExcellent Work:\x1b[0m\n"
                    f"You've successfully completed this quest!\n"
                    f"Your dedication to training is paying off.\n\n"
                    f"\x1b[1;37mProgress Update:\x1b[0m\n"
                    f"Quest marked as complete and XP has been\n"
                    f"added to your profile. Keep up the momentum!\n\n"
                    f"\x1b[1;37mNext Steps:\x1b[0m\n"
                    f"├─ Continue with remaining quests\n"
                    f"├─ Check your updated progress\n"
                    f"└─ Maintain your consistency streak\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.green()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                
                # Update the view to show completed quest
                updated_embed = self.view.build_quest_embed(self.view.current_index)
                return updated_embed, self.view
            else:
                raise ValueError("Quest completion failed")
                
        except Exception as e:
            logger.error(f"Error completing quest: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Completion Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to mark quest as complete.\n"
                f"Please try again in a few moments.\n\n"
                f"\x1b[1;37mTroubleshooting:\x1b[0m\n"
                f"├─ Check your network connection\n"
                f"├─ Verify server status\n"
                f"├─ Ensure quest is valid\n"
                f"└─ Contact support if issue persists\n\n"
                f"\x1b[1;37mTechnical Info:\x1b[0m\n"
                f"{str(e)[:50]}{'...' if len(str(e)) > 50 else ''}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            return embed, self.view

class BackToAwakeningView(discord.ui.Button):
    """Button to go back to awakening main view"""
    
    def __init__(self):
        super().__init__(label="⬅️ Back to Awakening", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._go_back)
    
    async def _go_back(self):
        """Go back to main awakening view"""
        view = AwakeningMainView(self.view.bot, self.view.user)
        await view.update_buttons_for_awakened_state()
        embed = await build_awakening_panel_embed(self.view.bot, self.view.user)
        return embed, view

# --- PANEL REGISTRATION ---
# NOTE: This is commented out for legacy version
# @register
class AwakeningPanelLegacy:
    """Awakening Panel for the system hub - Legacy Version"""
    key = "awakening_legacy"
    label = "Awakening (Legacy)"
    emoji = "🌅"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_awakening_panel_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return AwakeningMainView(bot, user)