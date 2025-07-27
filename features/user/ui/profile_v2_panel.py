"""
Enhanced V2 Profile Panel UI
Displays comprehensive V2 profile data including ascendant stats, skill progress, 
dungeon progress, and awakening information using V2 endpoints.
"""

import discord
import asyncio
import sentry_sdk
import logging
import httpx
from typing import Union, Dict, Any, Optional, List
from datetime import datetime

from shared.utils.ui_helpers import run_with_animation
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from core.api_client import APIClient
from shared.utils.error_helpers import handle_panel_errors

logger = logging.getLogger(__name__)

# --- UTILITY FUNCTIONS ---

def create_stat_bar(value: int, max_value: int = 100, length: int = 8) -> str:
    """Creates a visual bar for stats."""
    if max_value == 0:
        return "[░░░░░░░░]"
    progress = min(1.0, value / max_value)
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"[{bar}]"

def create_xp_bar(current_xp: int, next_level_xp: int, length: int = 10) -> str:
    """Generates a dynamic ASCII progress bar for XP."""
    if not next_level_xp or next_level_xp == 0:
        return f"[{'█' * length}] MAX"
    progress = min(1.0, current_xp / next_level_xp)
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percentage = int(progress * 100)
    return f"[{bar}] {percentage}%"

# --- FALLBACK EMBED ---

async def _create_fallback_embed(user: discord.User, error_type: str) -> discord.Embed:
    """Create a fallback embed for when the API is unavailable."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("profile_v2")
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● System Alert: Service Unreachable\x1b[0m\n"
        f"Status: \x1b[1;31m❌ OFFLINE\x1b[0m\n"
        f"Reason: \x1b[1;33m{error_type}\x1b[0m\n\n"
        f"\x1b[1;37mThe V2 Profile system is currently unable to\n"
        f"connect to the central archives. Your data is\n"
        f"safe, but services are temporarily unavailable.\n\n"
        f"\x1b[1;37mPlease try again shortly.\n"
        f"──────────────────────────\n"
        f"```"
    )
    embed = discord.Embed(description=content, color=discord.Color.red())
    embed.set_footer(text="Shadow Archive • System Alert • V2 Profile")
    return embed

# --- MAIN V2 PROFILE PANEL ---

@register
class ProfileV2Panel:
    key = "profile_v2"
    label = "Profile V2"
    emoji = "⚡"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        return await build_profile_v2_embed(bot, user)

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        return ProfileV2View(bot, user)

async def build_profile_v2_embed(bot, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Build the enhanced V2 profile panel embed with comprehensive data"""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("profile_v2")

    try:
        api_client = APIClient()
        profile = await asyncio.wait_for(api_client.get_user_profile_v2(user), timeout=10.0)

        if not profile:
            raise ValueError("No profile data received")

        # Extract data from comprehensive profile
        username = profile.get('username', user.display_name)
        level = profile.get('level', 1)
        current_xp = profile.get('xp', 0)
        xp_to_next_level = profile.get('xp_to_next_level', 100)
        aura = profile.get('aura', 0)
        
        # Stats breakdown
        stats = profile.get('stats', {})
        strength = stats.get('strength', {})
        endurance = stats.get('endurance', {})
        technique = stats.get('technique', {})
        
        # Progress data
        dungeon_progress = profile.get('dungeon_progress', {})
        unlocked_skills = profile.get('unlocked_skills', [])
        active_quests = profile.get('active_quests', [])
        
        # Build XP progress bar
        xp_bar = create_xp_bar(current_xp, xp_to_next_level)
        
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● Ascendant Profile V2\x1b[0m\n"
            f"Operative: \x1b[1;33m{username}\x1b[0m\n"
            f"Rank: \x1b[1;37mLevel {level}\x1b[0m | Aura: \x1b[1;35m{aura}\x1b[0m\n"
            f"Status: \x1b[1;32mACTIVE DUTY\x1b[0m\n\n"
            f"\x1b[1;37m⚡ Experience Progress:\x1b[0m\n"
            f"Progress: {xp_bar}\n"
            f"Current XP: \x1b[1;33m{current_xp:,}\x1b[0m / \x1b[1;37m{xp_to_next_level:,}\x1b[0m\n\n"
            f"\x1b[1;37m💪 Core Attributes:\x1b[0m\n"
        )
        
        # Add stats with mini progress bars
        stat_data = [
            ("Strength", strength, "🔴"),
            ("Endurance", endurance, "🔵"), 
            ("Technique", technique, "🟡")
        ]
        
        for i, (name, stat, emoji) in enumerate(stat_data):
            stat_level = stat.get('level', 1) if isinstance(stat, dict) else 1
            stat_xp = stat.get('xp', 0) if isinstance(stat, dict) else 0
            stat_xp_max = stat.get('xp_to_next_level', 100) if isinstance(stat, dict) else 100
            
            # Create mini progress bar for stat
            if stat_xp_max > 0:
                stat_progress = int((stat_xp / stat_xp_max) * 5)  # 5-char mini bar
                stat_bar = "█" * stat_progress + "░" * (5 - stat_progress)
            else:
                stat_bar = "█" * 5
            
            if i == len(stat_data) - 1:  # Last item
                content += f"└─ {emoji} {name}: Lv.\x1b[1;33m{stat_level}\x1b[0m [{stat_bar}]\n"
            else:
                content += f"├─ {emoji} {name}: Lv.\x1b[1;33m{stat_level}\x1b[0m [{stat_bar}]\n"
        
        # Add progression summary
        content += f"\n\x1b[1;37m🎯 Progression Status:\x1b[0m\n"
        
        # Skills
        skill_count = len(unlocked_skills)
        content += f"├─ 🌟 Skills Unlocked: \x1b[1;33m{skill_count}\x1b[0m nodes\n"
        
        # Dungeons
        if dungeon_progress:
            current_tier = dungeon_progress.get('current_tier', 'Shadow')
            current_level = dungeon_progress.get('current_level', 0)
            content += f"├─ 🏰 Dungeon Progress: \x1b[1;33m{current_tier} Tier\x1b[0m (Lv.{current_level})\n"
        else:
            content += f"├─ 🏰 Dungeon Progress: \x1b[1;30mNot Started\x1b[0m\n"
        
        # Quests
        quest_count = len(active_quests)
        if quest_count > 0:
            content += f"└─ ⚔️ Active Quests: \x1b[1;33m{quest_count}\x1b[0m in progress\n"
        else:
            content += f"└─ ⚔️ Active Quests: \x1b[1;30mNone\x1b[0m\n"
        
        content += f"\n──────────────────────────\n"
        content += f"```"
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(145, 70, 255)  # Purple theme
        )
        embed.set_footer(text="Shadow Archive • Profile V2 • Ascendant Database")

    except (asyncio.TimeoutError, httpx.RequestError) as e:
        logger.error(f"Profile V2 API call failed: {e}")
        sentry_sdk.capture_exception(e)
        return await _create_fallback_embed(user, "Service Unavailable")
    except Exception as e:
        logger.error(f"Error building profile V2 embed: {e}")
        sentry_sdk.capture_exception(e)
        return await _create_fallback_embed(user, "System Error")

    return embed

# --- VIEWS AND BUTTONS ---

class ProfileV2View(discord.ui.View):
    """Main view for the V2 profile panel."""
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        
        # Add panel switching dropdown first
        from shared.utils.common_views import EphemeralPanelSelect
        for item in EphemeralPanelView(bot, user).children:
            self.add_item(item)
        
        # Add action buttons
        self.add_item(ViewStatsButton(bot, user))
        self.add_item(ViewSkillsButton(bot, user))
        self.add_item(ViewDungeonButton(bot, user))
        self.add_item(ViewQuestsButton(bot, user))

class ViewStatsButton(discord.ui.Button):
    """Button to view detailed stats breakdown."""
    def __init__(self, bot, user):
        super().__init__(label="📊 Detailed Stats", style=discord.ButtonStyle.primary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_stats)

    async def _show_stats(self):
        api_client = APIClient()
        try:
            profile = await api_client.get_user_profile_v2(self.user)
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("profile_v2")
            
            stats = profile.get('stats', {})
            level = profile.get('level', 1)
            aura = profile.get('aura', 0)
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Detailed Statistics Analysis\x1b[0m\n"
                f"Global Level: \x1b[1;33m{level}\x1b[0m\n"
                f"Total Aura: \x1b[1;35m{aura}\x1b[0m\n"
                f"Total XP: \x1b[1;33m{profile.get('xp', 0):,}\x1b[0m\n\n"
                f"\x1b[1;37m💪 Attribute Breakdown:\x1b[0m\n"
            )
            
            stat_names = ['strength', 'endurance', 'technique']
            stat_colors = {"strength": "\x1b[1;31m", "endurance": "\x1b[1;34m", "technique": "\x1b[1;35m"}
            
            for i, stat_name in enumerate(stat_names):
                stat_data = stats.get(stat_name, {})
                if isinstance(stat_data, dict):
                    level = stat_data.get('level', 1)
                    xp = stat_data.get('xp', 0)
                    xp_max = stat_data.get('xp_to_next_level', 100)
                    total_xp = stat_data.get('total_xp', 0)
                    color = stat_colors.get(stat_name, "\x1b[1;37m")
                    
                    if i == len(stat_names) - 1:  # Last item
                        content += (
                            f"└─ {color}{stat_name.capitalize()}\x1b[0m\n"
                            f"   ├─ Level: \x1b[1;33m{level}\x1b[0m\n"
                            f"   ├─ Progress: \x1b[1;37m{xp}/{xp_max}\x1b[0m XP\n"
                            f"   └─ Total XP: \x1b[1;33m{total_xp:,}\x1b[0m\n"
                        )
                    else:
                        content += (
                            f"├─ {color}{stat_name.capitalize()}\x1b[0m\n"
                            f"│  ├─ Level: \x1b[1;33m{level}\x1b[0m\n"
                            f"│  ├─ Progress: \x1b[1;37m{xp}/{xp_max}\x1b[0m XP\n"
                            f"│  └─ Total XP: \x1b[1;33m{total_xp:,}\x1b[0m\n"
                        )
            
            content += f"\n──────────────────────────\n```"
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.from_rgb(145, 70, 255)
            )
            embed.set_footer(text="Shadow Archive • Statistics Division • V2 API")
            
            # Add back button
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileV2Button(self.bot, self.user))
            
            return embed, back_view
            
        except Exception as e:
            logger.error(f"Error showing detailed stats: {e}")
            embed = discord.Embed(
                title="Stats Unavailable",
                description="Could not retrieve detailed statistics.",
                color=discord.Color.red()
            )
            view = ProfileV2View(self.bot, self.user)
            return embed, view

class ViewSkillsButton(discord.ui.Button):
    """Button to view unlocked skills."""
    def __init__(self, bot, user):
        super().__init__(label="🌟 Skills", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_skills)

    async def _show_skills(self):
        api_client = APIClient()
        try:
            profile = await api_client.get_user_profile_v2(self.user)
            unlocked_skills = profile.get('unlocked_skills', [])
            
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("profile_v2")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Unlocked Skills Overview\x1b[0m\n"
                f"Total Skills: \x1b[1;33m{len(unlocked_skills)}\x1b[0m nodes\n\n"
            )
            
            if unlocked_skills:
                # Group skills by category
                skills_by_category = {}
                for skill in unlocked_skills:
                    category = skill.get('category', 'Unknown')
                    if category not in skills_by_category:
                        skills_by_category[category] = []
                    skills_by_category[category].append(skill)
                
                content += f"\x1b[1;37m🌟 Skills by Category:\x1b[0m\n"
                categories = list(skills_by_category.keys())
                for i, category in enumerate(categories):
                    skills = skills_by_category[category]
                    if i == len(categories) - 1:  # Last category
                        content += f"└─ \x1b[1;33m{category}\x1b[0m: {len(skills)} skills\n"
                    else:
                        content += f"├─ \x1b[1;33m{category}\x1b[0m: {len(skills)} skills\n"
            else:
                content += f"\x1b[1;30mNo skills unlocked yet.\x1b[0m\n"
                content += f"Visit the Skill Tree panel to begin your journey.\n"
            
            content += f"\n──────────────────────────\n```"
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.from_rgb(145, 70, 255)
            )
            embed.set_footer(text="Shadow Archive • Skill Registry • V2 System")
            
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileV2Button(self.bot, self.user))
            
            return embed, back_view
            
        except Exception as e:
            logger.error(f"Error showing skills: {e}")
            embed = discord.Embed(
                title="Skills Unavailable",
                description="Could not retrieve skill information.",
                color=discord.Color.red()
            )
            view = ProfileV2View(self.bot, self.user)
            return embed, view

class ViewDungeonButton(discord.ui.Button):
    """Button to view dungeon progress."""
    def __init__(self, bot, user):
        super().__init__(label="🏰 Dungeons", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_dungeons)

    async def _show_dungeons(self):
        api_client = APIClient()
        try:
            profile = await api_client.get_user_profile_v2(self.user)
            dungeon_progress = profile.get('dungeon_progress', {})
            dungeon_keys = profile.get('dungeon_keys', [])
            
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("profile_v2")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Dungeon Progress Summary\x1b[0m\n"
            )
            
            if dungeon_progress:
                current_tier = dungeon_progress.get('current_tier', 'Shadow')
                current_level = dungeon_progress.get('current_level', 0)
                best_level = dungeon_progress.get('best_level', 0)
                total_trials = dungeon_progress.get('total_trials_completed', 0)
                
                content += (
                    f"Current Tier: \x1b[1;33m{current_tier}\x1b[0m\n"
                    f"Current Level: \x1b[1;37m{current_level}\x1b[0m\n"
                    f"Best Level: \x1b[1;32m{best_level}\x1b[0m\n"
                    f"Trials Completed: \x1b[1;33m{total_trials}\x1b[0m\n\n"
                )
                
                # Show shadow keys
                content += f"\x1b[1;37m🔑 Shadow Keys:\x1b[0m\n"
                total_keys = sum(key.get('quantity', 0) for key in dungeon_keys)
                content += f"└─ Total Keys: \x1b[1;33m{total_keys}\x1b[0m\n"
            else:
                content += (
                    f"Status: \x1b[1;30mNot Started\x1b[0m\n\n"
                    f"Begin your dungeon journey through the\n"
                    f"Dungeons panel to test your might!\n"
                )
            
            content += f"\n──────────────────────────\n```"
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.from_rgb(145, 70, 255)
            )
            embed.set_footer(text="Shadow Archive • Dungeon Records • V2 System")
            
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileV2Button(self.bot, self.user))
            
            return embed, back_view
            
        except Exception as e:
            logger.error(f"Error showing dungeons: {e}")
            embed = discord.Embed(
                title="Dungeon Data Unavailable",
                description="Could not retrieve dungeon information.",
                color=discord.Color.red()
            )
            view = ProfileV2View(self.bot, self.user)
            return embed, view

class ViewQuestsButton(discord.ui.Button):
    """Button to view active quests."""
    def __init__(self, bot, user):
        super().__init__(label="⚔️ Quests", style=discord.ButtonStyle.secondary)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._show_quests)

    async def _show_quests(self):
        api_client = APIClient()
        try:
            profile = await api_client.get_user_profile_v2(self.user)
            active_quests = profile.get('active_quests', [])
            
            header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("profile_v2")
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Active Quest Overview\x1b[0m\n"
                f"Active Quests: \x1b[1;33m{len(active_quests)}\x1b[0m\n\n"
            )
            
            if active_quests:
                content += f"\x1b[1;37m⚔️ Current Quests:\x1b[0m\n"
                for i, quest in enumerate(active_quests[:5]):  # Show max 5
                    quest_name = quest.get('name', 'Unknown Quest')
                    quest_type = quest.get('quest_type', 'daily')
                    completed = quest.get('completed', False)
                    status = "\x1b[1;32m✓\x1b[0m" if completed else "\x1b[1;33m◉\x1b[0m"
                    
                    if i == len(active_quests) - 1 or i == 4:  # Last item or max
                        content += f"└─ {status} {quest_name} ({quest_type})\n"
                    else:
                        content += f"├─ {status} {quest_name} ({quest_type})\n"
                
                if len(active_quests) > 5:
                    content += f"\n... and {len(active_quests) - 5} more quests\n"
            else:
                content += (
                    f"\x1b[1;30mNo active quests.\x1b[0m\n"
                    f"Begin your awakening to receive daily quests!\n"
                )
            
            content += f"\n──────────────────────────\n```"
            
            embed = discord.Embed(
                description=content,
                color=discord.Color.from_rgb(145, 70, 255)
            )
            embed.set_footer(text="Shadow Archive • Quest Log • V2 System")
            
            back_view = discord.ui.View(timeout=120)
            back_view.add_item(BackToProfileV2Button(self.bot, self.user))
            
            return embed, back_view
            
        except Exception as e:
            logger.error(f"Error showing quests: {e}")
            embed = discord.Embed(
                title="Quest Data Unavailable",
                description="Could not retrieve quest information.",
                color=discord.Color.red()
            )
            view = ProfileV2View(self.bot, self.user)
            return embed, view

class BackToProfileV2Button(discord.ui.Button):
    """Button to return to the main profile V2 panel."""
    def __init__(self, bot, user):
        super().__init__(label="🔙 Back to Profile", style=discord.ButtonStyle.grey)
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        await run_with_animation(interaction, self._go_back)

    async def _go_back(self):
        embed = await build_profile_v2_embed(self.bot, self.user)
        view = ProfileV2View(self.bot, self.user)
        return embed, view