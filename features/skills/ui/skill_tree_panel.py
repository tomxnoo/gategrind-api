"""
Optimized Skill Tree Panel UI
Addresses performance issues and adds unlock button functionality.

PERFORMANCE FIXES:
- Cache library data after first load to prevent redundant API calls
- Reuse cached data for category navigation instead of re-fetching

FUNCTIONALITY FIXES:  
- Add unlock button for locked skill nodes
- Implement skill unlock API integration
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
from shared.utils.ui_components import create_progress_bar
from core.api_client import APIClient
from shared.utils.error_helpers import handle_panel_errors

logger = logging.getLogger(__name__)

# Global cache to prevent redundant API calls
_library_cache: Dict[str, Any] = {}
_cache_timestamp: Optional[datetime] = None
_profile_cache: Dict[int, Dict[str, Any]] = {}  # user_id -> profile_data
_profile_cache_timestamp: Dict[int, datetime] = {}  # user_id -> timestamp
CACHE_TTL_SECONDS = 300  # 5 minutes
PROFILE_CACHE_TTL_SECONDS = 60  # 1 minute for profile data

# --- CACHE MANAGEMENT ---

async def get_cached_library_data(user: discord.User) -> Dict[str, Any]:
    """Get library data from cache or fetch if expired."""
    global _library_cache, _cache_timestamp
    
    # Check if cache is valid
    if _cache_timestamp and _library_cache:
        cache_age = (datetime.now() - _cache_timestamp).total_seconds()
        if cache_age < CACHE_TTL_SECONDS:
            logger.info(f"Using cached library data (age: {cache_age:.1f}s)")
            return _library_cache
    
    # Cache expired or empty, fetch new data
    logger.info("Fetching fresh library data...")
    api_client = APIClient()
    library_data = await asyncio.wait_for(api_client.get_movement_library_v2(user), timeout=10.0)
    
    # Update cache
    _library_cache = library_data
    _cache_timestamp = datetime.now()
    
    return library_data

async def get_cached_profile_data(user: discord.User) -> Dict[str, Any]:
    """Get profile data from cache or fetch if expired."""
    global _profile_cache, _profile_cache_timestamp
    
    user_id = user.id
    
    # Check if cache is valid for this user
    if (user_id in _profile_cache_timestamp and user_id in _profile_cache):
        cache_age = (datetime.now() - _profile_cache_timestamp[user_id]).total_seconds()
        if cache_age < PROFILE_CACHE_TTL_SECONDS:
            logger.info(f"Using cached profile data for user {user_id} (age: {cache_age:.1f}s)")
            return _profile_cache[user_id]
    
    # Cache expired or empty, fetch new data
    logger.info(f"Fetching fresh profile data for user {user_id}...")
    api_client = APIClient()
    profile_data = await api_client.get_user_profile_v2(user)
    
    # Update cache
    _profile_cache[user_id] = profile_data
    _profile_cache_timestamp[user_id] = datetime.now()
    
    return profile_data

def clear_library_cache():
    """Clear the library cache (useful after unlock operations)."""
    global _library_cache, _cache_timestamp
    _library_cache = {}
    _cache_timestamp = None
    logger.info("Library cache cleared")

def clear_profile_cache(user_id: Optional[int] = None):
    """Clear profile cache for a specific user or all users."""
    global _profile_cache, _profile_cache_timestamp
    if user_id:
        _profile_cache.pop(user_id, None)
        _profile_cache_timestamp.pop(user_id, None)
        logger.info(f"Profile cache cleared for user {user_id}")
    else:
        _profile_cache.clear()
        _profile_cache_timestamp.clear()
        logger.info("All profile caches cleared")

# --- FALLBACK EMBED ---

async def _create_fallback_embed(user: discord.User, error_type: str) -> discord.Embed:
    """Create a fallback embed for when the API is unavailable."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_tree")
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● System Alert: Movement Library Offline\x1b[0m\n"
        f"Status: \x1b[1;31m❌ OFFLINE\x1b[0m\n"
        f"Reason: \x1b[1;33m{error_type}\x1b[0m\n\n"
        f"\x1b[1;37mThe Movement Library system is currently unable to\n"
        f"connect to the central archives. Your skill data is\n"
        f"safe, but services are temporarily unavailable.\n\n"
        f"\x1b[1;37mPlease try again shortly.\n"
        f"──────────────────────────\n"
        f"```"
    )
    embed = discord.Embed(description=content, color=discord.Color.red())
    embed.set_footer(text="Shadow Archive • System Alert • Skill Tree")
    return embed

# --- MAIN SKILL TREE PANEL ---

@register
class SkillTreePanel:
    key = "skill_tree"
    label = "Skill Tree"
    emoji = "🌟"

    @staticmethod
    async def render_embed(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        """Render the skill tree panel embed."""
        return await build_skill_tree_embed(bot, user)

    @staticmethod
    async def build_view(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        """Build the skill tree panel view with category navigation."""
        return SkillTreeView(bot, user)

async def build_skill_tree_embed(bot: discord.Client, user: Union[discord.User, discord.Member], category: Optional[str] = None) -> discord.Embed:
    """
    Build the skill tree panel embed showing movement library data.
    
    Args:
        bot: The Discord bot instance
        user: The Discord user to show the panel for
        category: Optional category ID to show specific category details
        
    Returns:
        discord.Embed: The formatted embed for display
    """
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_tree")

    try:
        # Use cached data to improve performance
        library_data = await get_cached_library_data(user)
        
        if not library_data or 'categories' not in library_data:
            raise ValueError("Invalid library data received")
        
        categories = library_data['categories']
        
        # Fetch user's unlocked skills using cached profile data
        try:
            profile_data = await asyncio.wait_for(get_cached_profile_data(user), timeout=5.0)
            unlocked_skills = profile_data.get('unlocked_skills', [])
            unlocked_skill_ids = {skill.get('skill_tree_node_id') for skill in unlocked_skills}
            user_stats = profile_data.get('stats', {})
        except:
            unlocked_skill_ids = set()
            user_stats = {}
        
        # If no category selected, show overview
        if not category:
            # Calculate total skills available
            total_skills = sum(len(cat.get('skill_tree', [])) for cat in categories)
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Movement Library\x1b[0m\n"
                f"Status: \x1b[1;32mONLINE\x1b[0m (cached)\n"
                f"Categories: \x1b[1;33m{len(categories)}\x1b[0m\n"
                f"Skills Unlocked: \x1b[1;32m{len(unlocked_skill_ids)}\x1b[0m / \x1b[1;37m{total_skills}\x1b[0m\n\n"
                f"\x1b[1;37m📚 Library Overview:\x1b[0m\n"
            )
            
            # Group categories by body area
            upper_body = []
            lower_body = []
            core_categories = []
            
            for cat in categories:
                cat_name = cat.get('name', 'Unknown')
                skill_count = len(cat.get('skill_tree', []))
                
                if any(keyword in cat_name.lower() for keyword in ['pull', 'push', 'overhead', 'arm', 'shoulder']):
                    upper_body.append((cat_name, skill_count))
                elif any(keyword in cat_name.lower() for keyword in ['squat', 'lunge', 'leg', 'hip', 'hinge']):
                    lower_body.append((cat_name, skill_count))
                else:
                    core_categories.append((cat_name, skill_count))
            
            # Display categories by group
            if upper_body:
                content += f"\n\x1b[1;31m▸ Upper Body\x1b[0m\n"
                for name, count in upper_body:
                    content += f"  • {name} ({count} levels)\n"
            
            if lower_body:
                content += f"\n\x1b[1;34m▸ Lower Body\x1b[0m\n"
                for name, count in lower_body:
                    content += f"  • {name} ({count} levels)\n"
            
            if core_categories:
                content += f"\n\x1b[1;35m▸ Core & Stability\x1b[0m\n"
                for name, count in core_categories:
                    content += f"  • {name} ({count} levels)\n"
            
            content += (
                f"\n──────────────────────────\n"
                f"\x1b[1;37mSelect a category to view skills\x1b[0m\n"
                f"```"
            )
        else:
            # Show specific category details
            category_data = next((cat for cat in categories if cat.get('id') == category), None)
            if not category_data:
                category_data = categories[0] if categories else None
            
            if category_data:
                cat_name = category_data.get('name', 'Unknown')
                primary_stat = category_data.get('primary_stat', 'STR')
                skill_tree = category_data.get('skill_tree', [])
                
                # Get user's relevant stat
                user_stat_value = user_stats.get(primary_stat.lower() + '_points', 0)
                user_level = user_stats.get('ascendant_level', 1)
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● {cat_name}\x1b[0m\n"
                    f"Primary Stat: \x1b[1;33m{primary_stat}\x1b[0m (You: {user_stat_value})\n"
                    f"Your Level: \x1b[1;33m{user_level}\x1b[0m\n"
                    f"Skill Levels: \x1b[1;33m{len(skill_tree)}\x1b[0m\n\n"
                    f"\x1b[1;37m🎯 Skill Progression:\x1b[0m\n"
                )
                
                # Display skill tree levels
                for node in skill_tree[:5]:  # Show first 5 levels
                    node_id = node.get('id')
                    level = node.get('level', 1)
                    name = node.get('name', 'Unknown')
                    movements = node.get('movements', [])
                    requirements = node.get('requirements', {})
                    
                    # Check if unlocked
                    is_unlocked = node_id in unlocked_skill_ids
                    
                    # Check if can unlock (meets requirements)
                    can_unlock = False
                    if not is_unlocked:
                        req_level = requirements.get('ascendant_level', 0)
                        req_str = requirements.get('str_points', 0)
                        req_end = requirements.get('end_points', 0)
                        req_tech = requirements.get('tech_points', 0)
                        
                        user_str = user_stats.get('str_points', 0)
                        user_end = user_stats.get('end_points', 0)
                        user_tech = user_stats.get('tech_points', 0)
                        
                        can_unlock = (user_level >= req_level and 
                                    user_str >= req_str and 
                                    user_end >= req_end and 
                                    user_tech >= req_tech)
                    
                    # Status indicator
                    if is_unlocked:
                        unlock_indicator = "✅"
                        status_text = ""
                    elif can_unlock:
                        unlock_indicator = "🔓"
                        status_text = " (Can Unlock!)"
                    else:
                        unlock_indicator = "🔒"
                        status_text = ""
                    
                    # Level indicator with color based on level
                    level_color = ["\x1b[1;37m", "\x1b[1;32m", "\x1b[1;34m", "\x1b[1;35m", "\x1b[1;31m"][min(level-1, 4)]
                    content += f"\n{level_color}Level {level}: {name} {unlock_indicator}{status_text}\x1b[0m\n"
                    
                    # Show requirements if not unlocked
                    if not is_unlocked and requirements:
                        req_parts = []
                        req_level = requirements.get('ascendant_level', 0)
                        req_str = requirements.get('str_points', 0)
                        req_end = requirements.get('end_points', 0)
                        req_tech = requirements.get('tech_points', 0)
                        
                        if req_level > 0:
                            req_parts.append(f"Level {req_level}")
                        if req_str > 0:
                            req_parts.append(f"{req_str} STR")
                        if req_end > 0:
                            req_parts.append(f"{req_end} END")
                        if req_tech > 0:
                            req_parts.append(f"{req_tech} TECH")
                        
                        if req_parts:
                            color = "\x1b[1;32m" if can_unlock else "\x1b[1;33m"
                            content += f"  {color}Requires: {', '.join(req_parts)}\x1b[0m\n"
                    
                    # Show movements
                    if movements:
                        for i, mov in enumerate(movements[:3]):  # Limit to 3 movements shown
                            mov_name = mov.get('name', 'Unknown')
                            xp_per_rep = mov.get('xp_per_rep', 1)
                            if i == len(movements[:3]) - 1:
                                content += f"  └─ {mov_name} ({xp_per_rep} XP/rep)\n"
                            else:
                                content += f"  ├─ {mov_name} ({xp_per_rep} XP/rep)\n"
                        if len(movements) > 3:
                            content += f"  └─ ... and {len(movements) - 3} more\n"
                
                content += (
                    f"\n──────────────────────────\n"
                    f"\x1b[1;37mClick 'Unlock Skill' to unlock available nodes\x1b[0m\n"
                    f"```"
                )
            else:
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;31m● Category Not Found\x1b[0m\n"
                    f"```"
                )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(255, 215, 0)  # Gold color for skills
        )
        embed.set_footer(text="Shadow Archive • Movement Library • Skill Tree (Optimized)")
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching skill tree data for user {user.id}")
        return await _create_fallback_embed(user, "CONNECTION TIMEOUT")
    except Exception as e:
        logger.error(f"Error building skill tree embed for user {user.id}: {e}")
        return await _create_fallback_embed(user, "SYSTEM ERROR")
    
    return embed

# --- VIEW IMPLEMENTATION ---

class SkillTreeView(discord.ui.View):
    """View for skill tree panel with category navigation buttons."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.current_category: Optional[str] = None
        
        # Add the panel switch dropdown first
        from shared.utils.common_views import EphemeralPanelSelect
        for item in EphemeralPanelView(bot, user).children:
            self.add_item(item)
        
        # Add category navigation buttons
        self.add_item(UpperBodyButton(bot, user))
        self.add_item(LowerBodyButton(bot, user))
        self.add_item(CoreButton(bot, user))
        self.add_item(BackToOverviewButton(bot, user))
        
        # Add unlock button (only shown when in a category with unlockable skills)
        self.unlock_button = UnlockSkillButton(bot, user)
        self.unlock_button.disabled = True  # Disabled by default
        self.add_item(self.unlock_button)

    def update_unlock_button(self, category: Optional[str], has_unlockable: bool):
        """Update the unlock button state based on current category."""
        self.current_category = category
        # Hide button entirely on overview page, show and enable/disable on category pages
        if category is None:
            self.unlock_button.style = discord.ButtonStyle.secondary
            self.unlock_button.disabled = True
            self.unlock_button.label = "🔒 Select Category"
        else:
            self.unlock_button.disabled = not has_unlockable
            if has_unlockable:
                self.unlock_button.style = discord.ButtonStyle.success
                self.unlock_button.label = "🔓 Unlock Skill"
            else:
                self.unlock_button.style = discord.ButtonStyle.secondary
                self.unlock_button.label = "🔒 No Skills Available"
        self.unlock_button.current_category = category

# --- CATEGORY NAVIGATION BUTTONS ---

class UpperBodyButton(discord.ui.Button):
    """Button for navigating to upper body skills category."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="💪 Upper Body",
            style=discord.ButtonStyle.primary,
            row=1
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            # Use cached data instead of making API call
            library_data = await get_cached_library_data(self.user)
            categories = library_data.get('categories', [])
            
            upper_body_cat = None
            for cat in categories:
                if any(keyword in cat.get('name', '').lower() for keyword in ['pull', 'push', 'overhead']):
                    upper_body_cat = cat.get('id')
                    break
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=upper_body_cat)
            view = SkillTreeView(self.bot, self.user)
            view.current_category = upper_body_cat
            
            # Check if there are unlockable skills
            has_unlockable = await check_has_unlockable_skills(self.user, upper_body_cat, library_data)
            view.update_unlock_button(upper_body_cat, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

class LowerBodyButton(discord.ui.Button):
    """Button for navigating to lower body skills category."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🦵 Lower Body",
            style=discord.ButtonStyle.primary,
            row=1
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            # Use cached data instead of making API call
            library_data = await get_cached_library_data(self.user)
            categories = library_data.get('categories', [])
            
            lower_body_cat = None
            for cat in categories:
                if any(keyword in cat.get('name', '').lower() for keyword in ['squat', 'lunge', 'leg', 'hip']):
                    lower_body_cat = cat.get('id')
                    break
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=lower_body_cat)
            view = SkillTreeView(self.bot, self.user)
            view.current_category = lower_body_cat
            
            # Check if there are unlockable skills
            has_unlockable = await check_has_unlockable_skills(self.user, lower_body_cat, library_data)
            view.update_unlock_button(lower_body_cat, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

class CoreButton(discord.ui.Button):
    """Button for navigating to core and stability skills category."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🎯 Core & Stability",
            style=discord.ButtonStyle.primary,
            row=1
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            # Use cached data instead of making API call
            library_data = await get_cached_library_data(self.user)
            categories = library_data.get('categories', [])
            
            core_cat = None
            for cat in categories:
                cat_name = cat.get('name', '').lower()
                if not any(keyword in cat_name for keyword in ['pull', 'push', 'squat', 'lunge', 'overhead']):
                    core_cat = cat.get('id')
                    break
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=core_cat)
            view = SkillTreeView(self.bot, self.user)
            view.current_category = core_cat
            
            # Check if there are unlockable skills
            has_unlockable = await check_has_unlockable_skills(self.user, core_cat, library_data)
            view.update_unlock_button(core_cat, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

class BackToOverviewButton(discord.ui.Button):
    """Button for returning to skill tree overview."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="📚 Overview",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            embed = await build_skill_tree_embed(self.bot, self.user, category=None)
            view = SkillTreeView(self.bot, self.user)
            view.current_category = None
            view.update_unlock_button(None, False)
            return embed, view
        
        await run_with_animation(interaction, do_work)

# --- NEW UNLOCK FUNCTIONALITY ---

class UnlockSkillButton(discord.ui.Button):
    """Button for unlocking available skill nodes."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🔓 Unlock Skill",
            style=discord.ButtonStyle.success,
            row=2
        )
        self.bot = bot
        self.user = user
        self.current_category: Optional[str] = None

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        if not self.current_category:
            await interaction.response.send_message("No category selected.", ephemeral=True)
            return
        
        # Show skill selection modal instead of auto-unlocking
        try:
            library_data = await get_cached_library_data(self.user)
            profile_data = await get_cached_profile_data(self.user)
            
            # Find all unlockable skills in current category
            categories = library_data.get('categories', [])
            category_data = next((cat for cat in categories if cat.get('id') == self.current_category), None)
            
            if not category_data:
                await interaction.response.send_message("❌ Category not found.", ephemeral=True)
                return
            
            unlocked_skills = profile_data.get('unlocked_skills', [])
            unlocked_skill_ids = {skill.get('skill_tree_node_id') for skill in unlocked_skills}
            user_stats = profile_data.get('stats', {})
            
            # Find all unlockable skills
            skill_tree = category_data.get('skill_tree', [])
            unlockable_skills = []
            
            for node in skill_tree:
                node_id = node.get('id')
                if node_id in unlocked_skill_ids:
                    continue  # Already unlocked
                
                requirements = node.get('requirements', {})
                req_level = requirements.get('ascendant_level', 0)
                req_str = requirements.get('str_points', 0)
                req_end = requirements.get('end_points', 0)
                req_tech = requirements.get('tech_points', 0)
                
                user_level = user_stats.get('ascendant_level', 1)
                user_str = user_stats.get('str_points', 0)
                user_end = user_stats.get('end_points', 0)
                user_tech = user_stats.get('tech_points', 0)
                
                can_unlock = (user_level >= req_level and 
                            user_str >= req_str and 
                            user_end >= req_end and 
                            user_tech >= req_tech)
                
                if can_unlock:
                    unlockable_skills.append(node)
            
            if not unlockable_skills:
                await interaction.response.send_message("❌ No skills available to unlock in this category.", ephemeral=True)
                return
            
            # Show skill selection dropdown
            view = SkillSelectionView(self.bot, self.user, self.current_category, unlockable_skills)
            embed = create_skill_selection_embed(unlockable_skills, user_stats)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error showing skill selection for user {self.user.id}: {e}")
            await interaction.response.send_message(f"❌ Error loading available skills: {str(e)}", ephemeral=True)

# --- SKILL SELECTION SYSTEM ---

def create_skill_selection_embed(unlockable_skills: List[Dict], user_stats: Dict) -> discord.Embed:
    """Create embed showing available skills to unlock."""
    user_level = user_stats.get('ascendant_level', 1)
    user_str = user_stats.get('str_points', 0)
    user_end = user_stats.get('end_points', 0)
    user_tech = user_stats.get('tech_points', 0)
    
    content = (
        f"```ansi\n"
        f"\x1b[1;36m🌟 Available Skills to Unlock\x1b[0m\n"
        f"Your Stats: Lv.{user_level} | STR:{user_str} | END:{user_end} | TECH:{user_tech}\n\n"
        f"\x1b[1;32mYou can unlock {len(unlockable_skills)} skill(s):\x1b[0m\n"
    )
    
    for i, skill in enumerate(unlockable_skills[:10], 1):  # Show first 10
        skill_name = skill.get('name', 'Unknown Skill')
        content += f"{i}. \x1b[1;33m{skill_name}\x1b[0m\n"
    
    if len(unlockable_skills) > 10:
        content += f"\n... and {len(unlockable_skills) - 10} more\n"
    
    content += f"\n\x1b[1;37mSelect a skill from the dropdown below to unlock it.\x1b[0m\n```"
    
    embed = discord.Embed(
        description=content,
        color=discord.Color.gold()
    )
    embed.set_footer(text="Shadow Archive • Skill Selection • Choose Wisely")
    return embed

class SkillSelectionView(discord.ui.View):
    """View containing skill selection dropdown."""
    
    def __init__(self, bot: discord.Client, user: discord.User, category: str, unlockable_skills: List[Dict]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.category = category
        self.unlockable_skills = unlockable_skills
        
        # Add skill selection dropdown
        self.add_item(SkillSelectionDropdown(bot, user, category, unlockable_skills))

class SkillSelectionDropdown(discord.ui.Select):
    """Dropdown for selecting which skill to unlock."""
    
    def __init__(self, bot: discord.Client, user: discord.User, category: str, unlockable_skills: List[Dict]):
        self.bot = bot
        self.user = user
        self.category = category
        self.unlockable_skills = unlockable_skills
        
        # Create options from unlockable skills (max 25 options per Discord limits)
        options = []
        for i, skill in enumerate(unlockable_skills[:25]):  # Discord limit
            skill_name = skill.get('name', f'Skill {skill.get("id", i+1)}')
            skill_desc = skill.get('description', 'No description available')
            
            # Show requirements in description
            requirements = skill.get('requirements', {})
            req_level = requirements.get('ascendant_level', 0)
            req_str = requirements.get('str_points', 0)
            req_end = requirements.get('end_points', 0)
            req_tech = requirements.get('tech_points', 0)
            
            if any([req_level, req_str, req_end, req_tech]):
                req_text = f"Req: Lv.{req_level}"
                if req_str: req_text += f" STR:{req_str}"
                if req_end: req_text += f" END:{req_end}"
                if req_tech: req_text += f" TECH:{req_tech}"
                skill_desc = req_text
            
            # Truncate description to fit Discord limits
            if len(skill_desc) > 100:
                skill_desc = skill_desc[:97] + "..."
            
            options.append(discord.SelectOption(
                label=skill_name[:100],  # Discord limit
                value=str(skill.get('id', i)),
                description=skill_desc,
                emoji="🌟"
            ))
        
        super().__init__(
            placeholder="🌟 Choose a skill to unlock...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle skill selection and unlock the chosen skill."""
        # Check if this is the correct user
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ This is not for you.", ephemeral=True)
            return
            
        selected_skill_id = self.values[0]
        
        # Find the selected skill
        selected_skill = None
        for skill in self.unlockable_skills:
            if str(skill.get('id')) == selected_skill_id:
                selected_skill = skill
                break
        
        if not selected_skill:
            await interaction.response.send_message("❌ Selected skill not found.", ephemeral=True)
            return
        
        # Unlock the selected skill
        try:
            api_client = APIClient()
            unlock_result = await api_client.unlock_skill_v2(self.user, str(selected_skill['id']))
            
            # Clear caches to force refresh
            clear_library_cache()
            clear_profile_cache(self.user.id)
            
            # Show success message
            skill_name = selected_skill.get('name', 'Unknown')
            await interaction.response.send_message(
                f"🎉 **Successfully unlocked: {skill_name}!**\n"
                f"✨ You can now access this skill in your training routines.\n"
                f"🔄 The skill tree panel will refresh automatically.", 
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Failed to unlock skill {selected_skill['id']} for user {self.user.id}: {e}")
            await interaction.response.send_message(f"❌ Failed to unlock skill: {str(e)}", ephemeral=True)

# --- HELPER FUNCTIONS ---

async def check_has_unlockable_skills(user: discord.User, category_id: str, library_data: Optional[Dict] = None) -> bool:
    """Check if the user has any unlockable skills in the given category."""
    try:
        if not library_data:
            library_data = await get_cached_library_data(user)
        
        profile_data = await get_cached_profile_data(user)
        unlocked_skills = profile_data.get('unlocked_skills', [])
        unlocked_skill_ids = {skill.get('skill_tree_node_id') for skill in unlocked_skills}
        user_stats = profile_data.get('stats', {})
        
        # Find category
        categories = library_data.get('categories', [])
        category_data = next((cat for cat in categories if cat.get('id') == category_id), None)
        
        if not category_data:
            return False
        
        # Check each skill node
        skill_tree = category_data.get('skill_tree', [])
        for node in skill_tree:
            node_id = node.get('id')
            if node_id in unlocked_skill_ids:
                continue  # Already unlocked
            
            requirements = node.get('requirements', {})
            req_level = requirements.get('ascendant_level', 0)
            req_str = requirements.get('str_points', 0) 
            req_end = requirements.get('end_points', 0)
            req_tech = requirements.get('tech_points', 0)
            
            user_level = user_stats.get('ascendant_level', 1)
            user_str = user_stats.get('str_points', 0)
            user_end = user_stats.get('end_points', 0)
            user_tech = user_stats.get('tech_points', 0)
            
            can_unlock = (user_level >= req_level and 
                        user_str >= req_str and 
                        user_end >= req_end and 
                        user_tech >= req_tech)
            
            if can_unlock:
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking unlockable skills for user {user.id}: {e}")
        return False