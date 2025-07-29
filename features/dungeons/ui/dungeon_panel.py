"""
Dungeon Panel UI
Displays available dungeons, user progress, shadow key balance, 
and provides dungeon entry/trial functionality using V2 endpoints.
"""

import discord
import asyncio
import logging
from typing import Union, Dict, Any, Optional, List
from datetime import datetime

from shared.utils.ui_helpers import run_with_animation
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from shared.utils.ui_components import create_progress_bar, format_tier_name
from core.api_client import APIClient
from shared.utils.error_helpers import handle_panel_errors

logger = logging.getLogger(__name__)

# --- FALLBACK EMBED ---

async def _create_fallback_embed(user: discord.User, error_type: str) -> discord.Embed:
    """Create a fallback embed for when the API is unavailable."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("dungeons")
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● System Alert: Dungeon System Offline\x1b[0m\n"
        f"Status: \x1b[1;31m❌ OFFLINE\x1b[0m\n"
        f"Reason: \x1b[1;33m{error_type}\x1b[0m\n\n"
        f"\x1b[1;37mThe Dungeon system is currently unable to\n"
        f"connect to the central archives. Your progress is\n"
        f"safe, but services are temporarily unavailable.\n\n"
        f"\x1b[1;37mPlease try again shortly.\n"
        f"──────────────────────────\n"
        f"```"
    )
    embed = discord.Embed(description=content, color=discord.Color.red())
    embed.set_footer(text="Shadow Archive • System Alert • Dungeons")
    return embed

# --- MAIN DUNGEON PANEL ---

@register
class DungeonPanel:
    key = "dungeons"
    label = "Dungeons"
    emoji = "🏰"

    @staticmethod
    async def render_embed(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        """Render the dungeon panel embed."""
        return await build_dungeon_embed(bot, user)

    @staticmethod
    async def build_view(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        """Build the dungeon panel view with action buttons."""
        return DungeonView(bot, user)

async def build_dungeon_embed(bot: discord.Client, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """
    Build the dungeon panel embed showing available dungeons and progress.
    
    Args:
        bot: The Discord bot instance  
        user: The Discord user to show the panel for
        
    Returns:
        discord.Embed: The formatted embed for display
    """
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("dungeons")

    try:
        api_client = APIClient()
        
        # Fetch dungeon data and user profile for shadow keys
        dungeons_task = api_client.get_available_dungeons_v2(user)
        profile_task = api_client.get_user_profile_v2(user)
        session_task = api_client.get_dungeon_session_v2(user)
        
        # Run all requests concurrently
        results = await asyncio.gather(
            dungeons_task,
            profile_task,
            session_task,
            return_exceptions=True
        )
        
        dungeons_data = results[0] if not isinstance(results[0], Exception) else None
        profile_data = results[1] if not isinstance(results[1], Exception) else None
        session_data = results[2] if not isinstance(results[2], Exception) else None
        
        if not dungeons_data:
            raise ValueError("Failed to fetch dungeon data")
        
        dungeons = dungeons_data.get('dungeons', [])
        shadow_keys = profile_data.get('shadow_keys', 0) if profile_data else 0
        
        # Check for active session
        has_active_session = bool(session_data and not isinstance(session_data, Exception))
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Dungeon System\x1b[0m\n"
            f"Status: \x1b[1;32mONLINE\x1b[0m\n"
            f"Shadow Keys: \x1b[1;35m{shadow_keys}\x1b[0m\n"
        )
        
        if has_active_session:
            content += f"Active Session: \x1b[1;33mLevel {session_data.get('dungeon_level', 1)}\x1b[0m\n"
        
        content += f"\n\x1b[1;37m🏰 Available Dungeons:\x1b[0m\n"
        
        # Display dungeons by tier
        for dungeon in dungeons:
            tier = dungeon.get('tier', 'shadow')
            tier_display = format_tier_name(tier)
            min_level = dungeon.get('min_level', 1)
            key_cost = dungeon.get('shadow_key_cost', 1)
            
            # Get user's progress for this dungeon
            user_progress = dungeon.get('user_progress', {})
            current_level = user_progress.get('current_level', 0)
            highest_level = user_progress.get('highest_level', 0)
            
            content += f"\n{tier_display} Dungeon\n"
            content += f"  • Entry Cost: \x1b[1;35m{key_cost}\x1b[0m Shadow Key{'s' if key_cost > 1 else ''}\n"
            content += f"  • Min Level: \x1b[1;33m{min_level}\x1b[0m\n"
            
            if current_level > 0:
                content += f"  • Progress: Level \x1b[1;32m{current_level}\x1b[0m (Best: \x1b[1;37m{highest_level}\x1b[0m)\n"
            else:
                content += f"  • Progress: \x1b[1;30mNot Started\x1b[0m\n"
        
        content += (
            f"\n──────────────────────────\n"
            f"\x1b[1;37mUse buttons below to enter dungeons\x1b[0m\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(138, 43, 226)  # Purple color for dungeons
        )
        embed.set_footer(text="Shadow Archive • Dungeon System • Endgame Content")
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching dungeon data for user {user.id}")
        return await _create_fallback_embed(user, "CONNECTION TIMEOUT")
    except Exception as e:
        logger.error(f"Error building dungeon embed for user {user.id}: {e}")
        return await _create_fallback_embed(user, "SYSTEM ERROR")
    
    return embed

# --- VIEW IMPLEMENTATION ---

class DungeonView(discord.ui.View):
    """View for dungeon panel with action buttons."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        
        # Add the panel switch dropdown first
        from shared.utils.common_views import EphemeralPanelSelect
        for item in EphemeralPanelView(bot, user).children:
            self.add_item(item)
        
        # Add dungeon action buttons
        self.add_item(EnterDungeonButton(bot, user, "shadow"))
        self.add_item(EnterDungeonButton(bot, user, "warrior"))
        self.add_item(EnterDungeonButton(bot, user, "ascendant"))
        self.add_item(SessionRecoveryButton(bot, user))

# --- DUNGEON ACTION BUTTONS ---

class EnterDungeonButton(discord.ui.Button):
    """Button for entering a specific dungeon tier."""
    
    def __init__(self, bot: discord.Client, user: discord.User, tier: str):
        tier_labels = {
            "shadow": "🌑 Shadow Dungeon",
            "warrior": "⚔️ Warrior Dungeon",
            "ascendant": "✨ Ascendant Dungeon"
        }
        
        tier_styles = {
            "shadow": discord.ButtonStyle.secondary,
            "warrior": discord.ButtonStyle.primary,
            "ascendant": discord.ButtonStyle.danger
        }
        
        super().__init__(
            label=tier_labels.get(tier, f"{tier.title()} Dungeon"),
            style=tier_styles.get(tier, discord.ButtonStyle.primary),
            row=1
        )
        self.bot = bot
        self.user = user
        self.tier = tier

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            api_client = APIClient()
            
            try:
                # Check for active session first
                session_data = await api_client.get_dungeon_session_v2(self.user)
                if session_data:
                    # Show trial modal for active session
                    modal = DungeonTrialModal(self.bot, self.user, session_data)
                    await interaction.response.send_modal(modal)
                    return None, None
                
                # Enter new dungeon
                # Map tier to level (for now, using tier as level 1)
                tier_to_level = {
                    "shadow": 1,
                    "warrior": 2, 
                    "ascendant": 3
                }
                
                response = await api_client.enter_dungeon_v2(
                    self.user,
                    tier_to_level.get(self.tier, 1)
                )
                
                if response.get('success'):
                    embed = await build_dungeon_embed(self.bot, self.user)
                    view = DungeonView(self.bot, self.user)
                    
                    # Add success message to embed
                    embed.add_field(
                        name="✅ Dungeon Entered",
                        value=f"You've entered the {self.tier.title()} Dungeon! Complete trials to progress.",
                        inline=False
                    )
                    
                    return embed, view
                else:
                    error_msg = response.get('detail', 'Failed to enter dungeon')
                    embed = discord.Embed(
                        title="❌ Cannot Enter Dungeon",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    return embed, None
                    
            except Exception as e:
                logger.error(f"Error entering dungeon: {e}")
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Failed to enter dungeon: {str(e)}",
                    color=discord.Color.red()
                )
                return embed, None
        
        # Only run with animation if not showing modal
        api_client = APIClient()
        session_check = await api_client.get_dungeon_session_v2(self.user)
        if session_check:
            # Show modal directly without animation
            modal = DungeonTrialModal(self.bot, self.user, session_check)
            await interaction.response.send_modal(modal)
        else:
            await run_with_animation(interaction, do_work)

class SessionRecoveryButton(discord.ui.Button):
    """Button for recovering interrupted dungeon sessions."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🔄 Recover Session",
            style=discord.ButtonStyle.success,
            row=2
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            api_client = APIClient()
            
            try:
                # Check for recoverable session
                session_data = await api_client.get_dungeon_session_v2(self.user)
                
                if session_data:
                    embed = discord.Embed(
                        title="✅ Session Recovered",
                        description=(
                            f"Found active session at Level {session_data.get('dungeon_level', 1)}\n\n"
                            f"Click on the dungeon button again to continue your trial!"
                        ),
                        color=discord.Color.green()
                    )
                else:
                    embed = discord.Embed(
                        title="ℹ️ No Active Session",
                        description="You don't have any active dungeon session to recover.",
                        color=discord.Color.blue()
                    )
                
                view = DungeonView(self.bot, self.user)
                return embed, view
                
            except Exception as e:
                logger.error(f"Error recovering session: {e}")
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Failed to recover session: {str(e)}",
                    color=discord.Color.red()
                )
                return embed, None
        
        await run_with_animation(interaction, do_work)

# --- DUNGEON TRIAL MODAL ---

class DungeonTrialModal(discord.ui.Modal):
    """Modal for answering dungeon trial questions."""
    
    def __init__(self, bot: discord.Client, user: discord.User, session: Dict[str, Any]):
        self.bot = bot
        self.user = user
        self.session = session
        
        super().__init__(
            title=f"Dungeon - Level {session.get('dungeon_level', 1)}"
        )
        
        # Add input field for trial answer
        self.answer = discord.ui.TextInput(
            label=f"Trial {session.get('trials_completed', 0) + 1} of {session.get('total_trials', 5)}",
            placeholder="Enter your answer...",
            required=True,
            max_length=100
        )
        self.add_item(self.answer)
    
    async def on_submit(self, interaction: discord.Interaction):
        api_client = APIClient()
        
        try:
            # Submit trial answer
            # Get trial_id from current session
            trial_id = self.session.get('current_trial', {}).get('id', 0)
            response = await api_client.complete_dungeon_trial_v2(
                self.user,
                trial_id,
                {"answer": self.answer.value}
            )
            
            if response.get('success'):
                result = response.get('result', {})
                
                # Build result embed
                if result.get('completed_dungeon'):
                    embed = discord.Embed(
                        title="🎉 Dungeon Complete!",
                        description=(
                            f"Congratulations! You've completed the {self.session.get('dungeon_tier', 'Unknown').title()} Dungeon!\n\n"
                            f"**Rewards:**\n"
                            f"• XP: +{result.get('rewards', {}).get('xp', 0)}\n"
                            f"• Shadow Keys: +{result.get('rewards', {}).get('shadow_keys', 0)}"
                        ),
                        color=discord.Color.gold()
                    )
                else:
                    next_level = result.get('next_level', 1)
                    embed = discord.Embed(
                        title="✅ Trial Complete!",
                        description=(
                            f"Well done! You've advanced to Level {next_level}.\n\n"
                            f"**Level Rewards:**\n"
                            f"• XP: +{result.get('rewards', {}).get('xp', 0)}"
                        ),
                        color=discord.Color.green()
                    )
                
                # Refresh the panel
                dungeon_embed = await build_dungeon_embed(self.bot, self.user)
                view = DungeonView(self.bot, self.user)
                
                await interaction.response.edit_message(embeds=[embed, dungeon_embed], view=view)
            else:
                error_msg = response.get('detail', 'Incorrect answer. Try again!')
                embed = discord.Embed(
                    title="❌ Trial Failed",
                    description=error_msg,
                    color=discord.Color.red()
                )
                
                # Still refresh the panel
                dungeon_embed = await build_dungeon_embed(self.bot, self.user)
                view = DungeonView(self.bot, self.user)
                
                await interaction.response.edit_message(embeds=[embed, dungeon_embed], view=view)
                
        except Exception as e:
            logger.error(f"Error completing trial: {e}")
            await interaction.response.send_message(
                f"An error occurred: {str(e)}",
                ephemeral=True
            )