"""
Awakening Panel UI
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
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._perform_awakening)
    
    async def _perform_awakening(self):
        """Perform the awakening ritual"""
        try:
            # Call awakening API
            api_client = APIClient()
            
            response = await api_client.perform_awakening(
                self.view.user,
                self.readiness_level
            )
            
            if response and "awakening" in response:
                # Show awakening results
                return await self._show_awakening_results(response)
            else:
                # Handle error
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;31m● Awakening Failed\x1b[0m\n"
                    f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                    f"Ritual: \x1b[1;31mUNCOMPLETE\x1b[0m\n\n"
                    f"\x1b[1;37mError Details:\x1b[0m\n"
                    f"Unable to perform awakening ritual.\n"
                    f"Please try again in a few moments.\n\n"
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
                
        except Exception as e:
            logger.error(f"Error performing awakening: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Awakening Error\x1b[0m\n"
                f"Status: \x1b[1;31mERROR\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"An error occurred: {str(e)}\n"
                f"Please try again in a few moments.\n\n"
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
    
    async def _show_awakening_results(self, response: Dict[str, Any]):
        """Show the results of the awakening ritual"""
        
        awakening = response["awakening"]
        quests = response["quests"]
        briefing = response["daily_briefing"]
        
        header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Build quest list
        quest_list = ""
        for i, quest in enumerate(quests):
            if i == len(quests) - 1:  # Last item
                quest_list += f"└─ {quest['title']}"
            else:
                quest_list += f"├─ {quest['title']}\n"
        
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
            f"Readiness: {color_code}{emoji} {level_text}\x1b[0m\n"
            f"Quest Count: \x1b[1;33m{len(quests)}\x1b[0m\n\n"
            f"\x1b[1;37mGenerated Quests:\x1b[0m\n"
            f"{quest_list}\n\n"
            f"\x1b[1;37mDaily Briefing:\x1b[0m\n"
            f"{briefing['awakening_summary']}\n\n"
            f"\x1b[1;37mReadiness Impact:\x1b[0m\n"
            f"{briefing['readiness_impact']}\n\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.green()
        )
        embed.set_footer(text="Shadow Archive • Awakening")
        
        # Create view with quest actions and update buttons
        view = AwakeningMainView(self.view.bot, self.view.user)
        await view.update_buttons_for_awakened_state()
        return embed, view

class BackToAwakeningButton(discord.ui.Button):
    """Button to go back to main awakening panel"""
    
    def __init__(self):
        super().__init__(label="⬅️ Back", style=discord.ButtonStyle.secondary)
    
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
        
        # Add the additional buttons for awakened state
        self.add_item(ViewQuestsButton())
        self.add_item(ViewBriefingButton())
        self.add_item(ViewHistoryButton())

class AwakeningButton(discord.ui.Button):
    """Button to start awakening ritual"""
    
    def __init__(self):
        super().__init__(label="🌅 Begin Awakening", style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._check_awakening_status)
    
    async def _check_awakening_status(self):
        """Check if awakening is possible today"""
        try:
            # Check awakening status
            api_client = APIClient()
            status = await api_client.get_awakening_status(self.view.user)
            
            if status and status.get("awakening_exists"):
                # Already awakened today - show all buttons
                await self.view.update_buttons_for_awakened_state()
                
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● Already Awakened\x1b[0m\n"
                    f"Status: \x1b[1;32mCOMPLETE\x1b[0m\n"
                    f"Today's Ritual: \x1b[1;32mFINISHED\x1b[0m\n\n"
                    f"\x1b[1;37mDaily Status:\x1b[0m\n"
                    f"You have already completed your awakening ritual\n"
                    f"for today. Your quests are ready and waiting.\n\n"
                    f"\x1b[1;37mNext Awakening:\x1b[0m\n"
                    f"Return tomorrow for a new awakening opportunity\n"
                    f"and fresh quest generation.\n\n"
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
                    f"\x1b[1;36m● Daily Awakening Ritual\x1b[0m\n"
                    f"Status: \x1b[1;33mREADY\x1b[0m\n"
                    f"Ritual: \x1b[1;33mPENDING\x1b[0m\n\n"
                    f"\x1b[1;37mEnergy Level Selection:\x1b[0m\n"
                    f"Choose your current energy level honestly for\n"
                    f"optimal quest generation and training intensity.\n\n"
                    f"\x1b[1;37mAvailable Options:\x1b[0m\n"
                    f"🔋 Low Energy - Recovery focused, gentle movement\n"
                    f"⚖️ Standard Energy - Balanced training approach\n"
                    f"🔥 High Energy - Intense challenges, push limits\n\n"
                    f"\x1b[1;37mAutoregulation:\x1b[0m\n"
                    f"Your selection affects quest difficulty, XP rewards,\n"
                    f"and exercise types. Listen to your body.\n\n"
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
                f"Unable to check awakening status.\n"
                f"Please try again in a few moments.\n\n"
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
        super().__init__(label="📋 View Quests", style=discord.ButtonStyle.success)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
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
                    f"Complete your awakening ritual first to generate\n"
                    f"today's personalized quest selection.\n\n"
                    f"\x1b[1;37mNext Steps:\x1b[0m\n"
                    f"Use 'Begin Awakening' to start your daily ritual\n"
                    f"and unlock today's training opportunities.\n\n"
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
                f"Unable to fetch quest data from server.\n"
                f"Please try again in a few moments.\n\n"
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
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_briefing)
    
    async def _show_briefing(self):
        """Show daily briefing"""
        try:
            api_client = APIClient()
            briefing = await api_client.get_awakening_briefing(self.view.user)
            
            if not briefing:
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● No Briefing Available\x1b[0m\n"
                    f"Status: \x1b[1;33mPENDING\x1b[0m\n"
                    f"Briefing: \x1b[1;31mNOT GENERATED\x1b[0m\n\n"
                    f"\x1b[1;37mRequired Action:\x1b[0m\n"
                    f"Complete your awakening ritual first to generate\n"
                    f"today's personalized daily briefing.\n\n"
                    f"\x1b[1;37mBriefing Contents:\x1b[0m\n"
                    f"• Awakening summary and analysis\n"
                    f"• Quest overview and recommendations\n"
                    f"• Progress highlights and statistics\n"
                    f"• Readiness impact assessment\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                return embed, self.view
            
            # Build briefing embed with consistent styling
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            # Build quest overview list
            quest_overview = ""
            quest_list = briefing.get("quest_overview", [])
            for i, quest in enumerate(quest_list):
                if i == len(quest_list) - 1:  # Last item
                    quest_overview += f"└─ {quest}"
                else:
                    quest_overview += f"├─ {quest}\n"
            
            # Get progress highlights
            highlights = briefing.get("progress_highlights", {})
            weekly_completions = highlights.get('weekly_completions', 0)
            weekly_xp = highlights.get('weekly_xp', 0)
            consistency_streak = highlights.get('consistency_streak', 0)
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Daily Briefing\x1b[0m\n"
                f"Status: \x1b[1;32mGENERATED\x1b[0m\n"
                f"Analysis: \x1b[1;32mCOMPLETE\x1b[0m\n\n"
                f"\x1b[1;37mAwakening Summary:\x1b[0m\n"
                f"{briefing.get('awakening_summary', 'No summary available.')}\n\n"
                f"\x1b[1;37mQuest Overview:\x1b[0m\n"
                f"{quest_overview}\n\n"
                f"\x1b[1;37mReadiness Impact:\x1b[0m\n"
                f"{briefing.get('readiness_impact', 'No impact data available.')}\n\n"
                f"\x1b[1;37mProgress Highlights:\x1b[0m\n"
                f"├─ Weekly Completions: \x1b[1;33m{weekly_completions}\x1b[0m\n"
                f"├─ Weekly XP: \x1b[1;33m{weekly_xp}\x1b[0m\n"
                f"└─ Consistency Streak: \x1b[1;33m{consistency_streak}\x1b[0m\n\n"
                f"\x1b[1;37mMotivation:\x1b[0m\n"
                f"{briefing.get('motivation_message', 'Stay strong, warrior!')}\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            
            view = BackToAwakeningView(self.view.bot, self.view.user)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching briefing: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● Briefing Fetch Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to fetch briefing data from server.\n"
                f"Please try again in a few moments.\n\n"
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
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._show_history())
    
    async def _show_history(self):
        """Show awakening history"""
        try:
            api_client = APIClient()
            history = await api_client.get_awakening_history(self.view.user)
            
            if not history:
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;33m● No History Available\x1b[0m\n"
                    f"Status: \x1b[1;33mEMPTY\x1b[0m\n"
                    f"Records: \x1b[1;31mNONE FOUND\x1b[0m\n\n"
                    f"\x1b[1;37mHistory Building:\x1b[0m\n"
                    f"Complete some awakening rituals to build your\n"
                    f"personal training history and progress tracking.\n\n"
                    f"\x1b[1;37mTracked Data:\x1b[0m\n"
                    f"• Daily awakening completions\n"
                    f"• Readiness level selections\n"
                    f"• Quest completion rates\n"
                    f"• XP progression over time\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.orange()
                )
                embed.set_footer(text="Shadow Archive • Awakening")
                return embed, self.view
            
            # Build history embed with consistent styling
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            # Build history entries
            history_entries = ""
            recent_history = history[:7]  # Show last 7 days
            for i, entry in enumerate(recent_history):
                status_emoji = {
                    "completed": "✅",
                    "awakened": "⚡",
                    "pending": "⏳"
                }.get(entry.get("status", "unknown"), "❓")
                
                readiness_emoji = {
                    "low": "🔋",
                    "standard": "⚖️", 
                    "high": "🔥"
                }.get(entry.get("readiness_level", "unknown"), "❓")
                
                completed = entry.get('completed_quests', 0)
                total = entry.get('quest_count', 0)
                xp = entry.get('total_xp_gained', 0)
                date_str = entry.get("date", "Unknown")
                
                if i == len(recent_history) - 1:  # Last item
                    history_entries += f"└─ {date_str}: {status_emoji} {readiness_emoji} ({completed}/{total}) XP:{xp}"
                else:
                    history_entries += f"├─ {date_str}: {status_emoji} {readiness_emoji} ({completed}/{total}) XP:{xp}\n"
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Awakening History\x1b[0m\n"
                f"Status: \x1b[1;32mLOADED\x1b[0m\n"
                f"Records: \x1b[1;33m{len(history)}\x1b[0m entries\n\n"
                f"\x1b[1;37mRecent Sessions (Last 7 Days):\x1b[0m\n"
                f"{history_entries}\n\n"
                f"\x1b[1;37mLegend:\x1b[0m\n"
                f"✅ Completed  ⚡ Awakened  ⏳ Pending\n"
                f"🔋 Low  ⚖️ Standard  🔥 High Energy\n\n"
                f"──────────────────────────\n"
                f"```"
            )
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Shadow Archive • Awakening")
            
            view = BackToAwakeningView(self.view.bot, self.view.user)
            return embed, view
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            sentry_sdk.capture_exception(e)
            
            header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("awakening")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;31m● History Fetch Error\x1b[0m\n"
                f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                f"API: \x1b[1;31mUNREACHABLE\x1b[0m\n\n"
                f"\x1b[1;37mError Details:\x1b[0m\n"
                f"Unable to fetch history data from server.\n"
                f"Please try again in a few moments.\n\n"
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
    """View for displaying quest details with navigation"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member], quests: list):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.quests = quests
        self.current_index = 0
        
        # Add dropdown FIRST (above buttons like other panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        # Add navigation buttons
        if len(quests) > 1:
            self.add_item(PrevQuestButton())
            self.add_item(NextQuestButton())
        
        self.add_item(CompleteQuestButton())
        self.add_item(BackToAwakeningButton())
    
    def build_quest_embed(self, index: int) -> discord.Embed:
        """Build embed for quest at given index"""
        quest = self.quests[index]
        
        header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("awakening")
        
        # Status colors and info
        status_info = {
            "available": ("\x1b[1;34m", "AVAILABLE", discord.Color.blue()),
            "active": ("\x1b[1;33m", "ACTIVE", discord.Color.orange()),
            "completed": ("\x1b[1;32m", "COMPLETED", discord.Color.green())
        }
        color_code, status_text, embed_color = status_info.get(quest.get("status", "available"), ("\x1b[1;37m", "UNKNOWN", discord.Color.blue()))
        
        # Build progress info
        progress_info = ""
        if "progress" in quest and quest["progress"]:
            progress = quest["progress"]
            current_sets = progress.get('current_sets', 0)
            current_reps = progress.get('current_reps', 0)
            target_sets = quest.get('target_sets', 0)
            target_reps = quest.get('target_reps', 0)
            
            # Create progress bars
            if target_sets > 0:
                set_progress = min(100, (current_sets / target_sets) * 100)
                set_filled = int(set_progress / 25)  # Each square represents 25%
                set_empty = 4 - set_filled
                set_bar = "🟩" * set_filled + "⬜️" * set_empty
            else:
                set_bar = "⬜️⬜️⬜️⬜️"
            
            if target_reps > 0:
                rep_progress = min(100, (current_reps / target_reps) * 100)
                rep_filled = int(rep_progress / 25)  # Each square represents 25%
                rep_empty = 4 - rep_filled
                rep_bar = "🟩" * rep_filled + "⬜️" * rep_empty
            else:
                rep_bar = "⬜️⬜️⬜️⬜️"
            
            progress_info = (
                f"\x1b[1;37mProgress Tracking:\x1b[0m\n"
                f"Sets: [{set_bar}] {current_sets}/{target_sets}\n"
                f"Reps: [{rep_bar}] {current_reps}/{target_reps}\n\n"
            )
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"{color_code}● {quest.get('title', 'Unknown Quest')}\x1b[0m\n"
            f"Status: {color_code}{status_text}\x1b[0m\n"
            f"Type: \x1b[1;36mAWAKENING QUEST\x1b[0m\n\n"
            f"\x1b[1;37mDescription:\x1b[0m\n"
            f"{quest.get('description', 'No description available.')}\n\n"
            f"\x1b[1;37mObjective:\x1b[0m\n"
            f"Exercise: {quest.get('movement', 'Unknown')}\n"
            f"Target: {quest.get('target_sets', 0)} sets × {quest.get('target_reps', 0)} reps\n"
            f"XP Reward: \x1b[1;33m{quest.get('xp_reward', 0)}\x1b[0m points\n\n"
            f"{progress_info}"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=embed_color
        )
        
        # Add footer with navigation info
        if len(self.quests) > 1:
            embed.set_footer(text=f"Quest {index + 1} of {len(self.quests)} • Shadow Archive")
        else:
            embed.set_footer(text="Shadow Archive • Quest Details")
        
        return embed

class PrevQuestButton(discord.ui.Button):
    """Button to navigate to previous quest"""
    
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        self.view.current_index = (self.view.current_index - 1) % len(self.view.quests)
        embed = self.view.build_quest_embed(self.view.current_index)
        await interaction.response.edit_message(embed=embed, view=self.view)

class NextQuestButton(discord.ui.Button):
    """Button to navigate to next quest"""
    
    def __init__(self):
        super().__init__(label="Next ➡️", style=discord.ButtonStyle.secondary)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        self.view.current_index = (self.view.current_index + 1) % len(self.view.quests)
        embed = self.view.build_quest_embed(self.view.current_index)
        await interaction.response.edit_message(embed=embed, view=self.view)

class CompleteQuestButton(discord.ui.Button):
    """Button to mark quest as completed"""
    
    def __init__(self):
        super().__init__(label="✅ Complete Quest", style=discord.ButtonStyle.success)
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This panel isn't for you.", ephemeral=True)
            return
            
        await run_with_animation(interaction, self._complete_quest())
    
    async def _complete_quest(self):
        """Complete the quest"""
        async def do_work():
            try:
                current_quest = self.view.quests[self.view.current_index]
                
                if current_quest.get("status") == "completed":
                    header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                    sub_header = get_panel_sub_header("awakening")
                    
                    content = (
                        f"```ansi\n"
                        f"{header}\n"
                        f"{sub_header}\n\n"
                        f"\x1b[1;33m● Already Completed\x1b[0m\n"
                        f"Status: \x1b[1;32mCOMPLETED\x1b[0m\n"
                        f"Quest: \x1b[1;32mFINISHED\x1b[0m\n\n"
                        f"\x1b[1;37mQuest Status:\x1b[0m\n"
                        f"This quest has already been completed and\n"
                        f"XP rewards have been distributed.\n\n"
                        f"\x1b[1;37mNext Steps:\x1b[0m\n"
                        f"Check other available quests or return\n"
                        f"tomorrow for new challenges.\n\n"
                        f"──────────────────────────\n"
                        f"```"
                    )
                    
                    embed = discord.Embed(
                        description=content,
                        color=discord.Color.orange()
                    )
                    return embed, self.view
                
                # Complete quest via API
                api_client = APIClient()
                result = await api_client.complete_awakening_quest(
                    self.view.user,
                    current_quest.get('id')
                )
                
                if result and "xp_gained" in result:
                    # Update quest status
                    current_quest["status"] = "completed"
                    
                    # Show completion message with consistent styling
                    header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                    sub_header = get_panel_sub_header("awakening")
                    
                    awakening_complete = result.get("awakening_completed", False)
                    xp_gained = result.get("xp_gained", 0)
                    
                    content = (
                        f"```ansi\n"
                        f"{header}\n"
                        f"{sub_header}\n\n"
                        f"\x1b[1;32m● Quest Completed!\x1b[0m\n"
                        f"Status: \x1b[1;32mSUCCESS\x1b[0m\n"
                        f"Reward: \x1b[1;33m{xp_gained} XP\x1b[0m\n\n"
                        f"\x1b[1;37mCompleted Quest:\x1b[0m\n"
                        f"{current_quest.get('title', 'Unknown Quest')}\n\n"
                        f"\x1b[1;37mRewards Distributed:\x1b[0m\n"
                        f"├─ Experience Points: \x1b[1;33m{xp_gained}\x1b[0m\n"
                        f"└─ Progress Updated: \x1b[1;32mYES\x1b[0m\n\n"
                    )
                    
                    if awakening_complete:
                        content += (
                            f"\x1b[1;37m🏆 Awakening Complete!\x1b[0m\n"
                            f"All daily quests have been finished.\n"
                            f"Excellent work, warrior!\n\n"
                        )
                    
                    content += "──────────────────────────\n```"
                    
                    embed = discord.Embed(
                        description=content,
                        color=discord.Color.green()
                    )
                    
                    # Update the view with new quest status
                    embed_updated = self.view.build_quest_embed(self.view.current_index)
                    
                    # Show completion notification briefly, then update
                    await asyncio.sleep(2)
                    return embed_updated, self.view
                    
                else:
                    header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                    sub_header = get_panel_sub_header("awakening")
                    
                    content = (
                        f"```ansi\n"
                        f"{header}\n"
                        f"{sub_header}\n\n"
                        f"\x1b[1;31m● Completion Failed\x1b[0m\n"
                        f"Status: \x1b[1;31mERROR\x1b[0m\n"
                        f"API: \x1b[1;31mREJECTED\x1b[0m\n\n"
                        f"\x1b[1;37mError Details:\x1b[0m\n"
                        f"Unable to complete quest at this time.\n"
                        f"Please try again in a few moments.\n\n"
                        f"──────────────────────────\n"
                        f"```"
                    )
                    
                    embed = discord.Embed(
                        description=content,
                        color=discord.Color.red()
                    )
                    return embed, self.view
                    
            except Exception as e:
                logger.error(f"Error completing quest: {e}")
                sentry_sdk.capture_exception(e)
                
                header = get_system_status_header(self.view.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("awakening")
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;31m● System Error\x1b[0m\n"
                    f"Status: \x1b[1;31mFAILED\x1b[0m\n"
                    f"Error: \x1b[1;31m{str(e)[:50]}...\x1b[0m\n\n"
                    f"\x1b[1;37mError Details:\x1b[0m\n"
                    f"An unexpected error occurred during quest "
                    f"completion. Please try again or contact support.\n\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                embed = discord.Embed(
                    description=content,
                    color=discord.Color.red()
                )
                return embed, self.view
        
        return do_work

# --- BACK TO AWAKENING VIEW ---
class BackToAwakeningView(discord.ui.View):
    """Simple view with just a back button"""
    
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        
        # Add dropdown FIRST (above buttons like other panels)
        from shared.utils.common_views import EphemeralPanelSelect
        self.add_item(EphemeralPanelSelect(bot, user.id))
        
        self.add_item(BackToAwakeningButton())

# --- PANEL REGISTRATION ---
@register
class AwakeningPanel:
    """Awakening Panel for the system hub"""
    key = "awakening"
    label = "Awakening"
    emoji = "🌅"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_awakening_panel_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return AwakeningMainView(bot, user)