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
from shared.utils.base_views import SimpleFallbackView
from shared.utils.panel_registry import register
# Removed EphemeralPanelView import to avoid circular import
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
    # Use singleton APIClient instance to prevent multiple login attempts
    api_client = APIClient()
    
    try:
        library_data = await asyncio.wait_for(api_client.get_movement_library_v2(user), timeout=10.0)
        
        # Update cache
        _library_cache = library_data
        _cache_timestamp = datetime.now()
        
        return library_data
    except Exception as e:
        logger.error(f"Failed to fetch library data for user {user.id}: {e}")
        # If we have stale cache data, use it as fallback
        if _library_cache:
            logger.info("Using stale cached data as fallback")
            return _library_cache
        # Clear auth cache and retry once
        logger.info("Clearing auth cache and retrying...")
        api_client.clear_auth_cache(user.id)
        try:
            library_data = await asyncio.wait_for(api_client.get_movement_library_v2(user), timeout=10.0)
            _library_cache = library_data
            _cache_timestamp = datetime.now()
            return library_data
        except Exception as retry_error:
            logger.error(f"Retry also failed: {retry_error}")
            raise retry_error

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
    # Use singleton APIClient instance to prevent multiple login attempts
    api_client = APIClient()
    
    try:
        profile_data = await api_client.get_user_profile_v2(user)
        
        # Update cache
        _profile_cache[user_id] = profile_data
        _profile_cache_timestamp[user_id] = datetime.now()
        
        return profile_data
    except Exception as e:
        logger.error(f"Failed to fetch profile data for user {user_id}: {e}")
        # If we have stale cache data, use it as fallback
        if user_id in _profile_cache:
            logger.info(f"Using stale cached profile data for user {user_id} as fallback")
            return _profile_cache[user_id]
        # Clear auth cache and retry once
        logger.info(f"Clearing auth cache for user {user_id} and retrying...")
        api_client.clear_auth_cache(user_id)
        try:
            profile_data = await api_client.get_user_profile_v2(user)
            _profile_cache[user_id] = profile_data
            _profile_cache_timestamp[user_id] = datetime.now()
            return profile_data
        except Exception as retry_error:
            logger.error(f"Profile retry also failed for user {user_id}: {retry_error}")
            raise retry_error

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

# --- MAIN SKILL TREE PANEL ---

@register
class SkillTreePanel:
    key = "skill_tree"
    label = "Skill Tree"
    emoji = "🌟"

    @staticmethod
    async def render_embed(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        """Render the skill tree panel embed with robust error handling."""
        try:
            embed = await build_skill_tree_embed(bot, user, view_mode="overview")
            logger.info(f"Successfully created SkillTreePanel embed for user {user.id}")
            return embed
        except Exception as e:
            logger.error(f"Failed to render skill tree embed for user {user.id}: {e}")
            # Return fallback embed instead of letting exception bubble up
            fallback_embed = await _create_fallback_embed(user, f"API Error: {str(e)[:50]}...")
            return fallback_embed

    @staticmethod
    async def build_view(bot: discord.Client, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        """Build the skill tree panel view with category navigation and error handling."""
        try:
            view = SkillTreeView(bot, user, view_mode="overview")
            logger.info(f"Successfully created SkillTreeView for user {user.id}")
            return view
        except Exception as e:
            logger.error(f"Failed to build skill tree view for user {user.id}: {e}", exc_info=True)
            # Return fallback view to avoid circular import
            logger.info(f"Created minimal fallback view for user {user.id}")
            return SimpleFallbackView(timeout=300)

async def build_skill_tree_embed(bot: discord.Client, user: Union[discord.User, discord.Member], category: Optional[str] = None, current_group: Optional[str] = None, view_mode: str = "overview") -> discord.Embed:
    """Build the skill tree embed with comprehensive error handling."""
    try:
        logger.info(f"build_skill_tree_embed called for user {user.id} with view_mode={view_mode}, category={category}, current_group={current_group}")
        
        # Attempt to get cached data with error handling
        library_data = None
        profile_data = None
        
        try:
            library_data = await get_cached_library_data(user)
            logger.info(f"Successfully retrieved library data for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to get library data for user {user.id}: {e}", exc_info=True)
            
        try:
            profile_data = await get_cached_profile_data(user)
            logger.info(f"Successfully retrieved profile data for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to get profile data for user {user.id}: {e}", exc_info=True)
        
        # If both API calls failed, return fallback embed
        if library_data is None and profile_data is None:
            logger.error(f"Both library and profile data failed for user {user.id}")
            return await _create_fallback_embed(user, "Unable to load skill data - API unavailable")
        
        # If only one failed, create partial embed with available data
        if library_data is None:
            logger.warning(f"Library data unavailable for user {user.id}, creating partial embed")
            return await _create_partial_embed(user, profile_data, "Library data unavailable")
            
        if profile_data is None:
            logger.warning(f"Profile data unavailable for user {user.id}, creating partial embed")
            return await _create_partial_embed(user, library_data, "Profile data unavailable")
        
        # Both data sources available, proceed with normal embed creation
        logger.info(f"Both data sources available for user {user.id}, building full embed with view_mode={view_mode}")
        return await _build_full_skill_tree_embed(bot, user, library_data, profile_data, category, current_group, view_mode)
        
    except Exception as e:
        logger.error(f"Unexpected error in build_skill_tree_embed for user {user.id}: {e}", exc_info=True)
        return await _create_fallback_embed(user, f"Build Error: {str(e)[:50]}...")

async def _build_full_skill_tree_embed(bot: discord.Client, user: Union[discord.User, discord.Member], library_data: dict, profile_data: dict, category: Optional[str] = None, current_group: Optional[str] = None, view_mode: str = "overview") -> discord.Embed:
    """
    Build the skill tree panel embed showing movement library data.
    
    Args:
        bot: The Discord bot instance
        user: The Discord user to show the panel for
        library_data: The cached library data
        profile_data: The cached profile data
        category: Optional category ID to show specific category details
        view_mode: "overview" for category summary, "detailed" for full skill tree
        
    Returns:
        discord.Embed: The formatted embed for display
    """
    logger.info(f"Starting _build_full_skill_tree_embed for user {user.id}, category={category}, view_mode={view_mode}")
    
    try:
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("skill_tree")
        logger.info(f"Generated headers successfully for user {user.id}")

        if not library_data or 'categories' not in library_data:
            logger.error(f"Invalid library data for user {user.id}: {library_data}")
            raise ValueError("Invalid library data received")
        
        categories = library_data['categories']
        logger.info(f"Found {len(categories)} categories for user {user.id}")
        
        # DEBUG: Examine profile data structure
        logger.info(f"Profile data keys for user {user.id}: {list(profile_data.keys())}")
        logger.info(f"Profile data structure for user {user.id}: {profile_data}")
        
        # Get user's unlocked skills and stats from profile data
        unlocked_skills = profile_data.get('unlocked_skills', [])
        logger.info(f"Raw unlocked_skills data for user {user.id}: {unlocked_skills}")
        
        # Check for alternative field names that might contain skill data
        potential_skill_fields = ['skills', 'skill_nodes', 'unlocked_nodes', 'movement_skills', 'completed_skills']
        for field in potential_skill_fields:
            if field in profile_data:
                logger.info(f"Found potential skill field '{field}' for user {user.id}: {profile_data[field]}")
        
        # Debug: Check the type and structure of unlocked_skills
        logger.info(f"Type of unlocked_skills: {type(unlocked_skills)}")
        if unlocked_skills:
            logger.info(f"Type of first skill: {type(unlocked_skills[0])}")
            logger.info(f"First skill data: {unlocked_skills[0]}")
            if hasattr(unlocked_skills[0], 'node_id'):
                logger.info(f"First skill has node_id attribute: {unlocked_skills[0].node_id}")
            if isinstance(unlocked_skills[0], dict):
                logger.info(f"First skill dict keys: {unlocked_skills[0].keys()}")
        
        # Handle both dictionary and object formats
        unlocked_skill_ids = set()
        for skill in unlocked_skills:
            if isinstance(skill, dict):
                node_id = skill.get('node_id')
            else:
                node_id = getattr(skill, 'node_id', None)
            
            if node_id:
                unlocked_skill_ids.add(node_id)
        
        logger.info(f"Processed unlocked_skill_ids for user {user.id}: {unlocked_skill_ids}")
        
        user_stats = profile_data.get('stats', {})
        available_points = profile_data.get('available_points', {})
        logger.info(f"User stats for user {user.id}: {user_stats}")
        logger.info(f"Available points for user {user.id}: {available_points}")
        logger.info(f"User {user.id} has {len(unlocked_skill_ids)} unlocked skills")
        
        # Debug: Log the structure of skill node requirements
        if categories and len(categories) > 0:
            first_category = categories[0]
            if first_category and len(first_category.get('skill_tree', [])) > 0:
                first_node = first_category['skill_tree'][0]
                if 'requirements' in first_node:
                    logger.debug(f"Sample skill node requirements structure: {first_node['requirements']}")
                    logger.debug(f"Sample skill node requirements keys: {list(first_node['requirements'].keys())}")
                    logger.debug(f"Full first node structure: {first_node}")
        
        
        # If overview mode and no category selected, show improved category overview
        if view_mode == "overview" and not category:
            logger.info(f"Processing overview mode for user {user.id}")
            # Calculate total skills available
            total_skills = sum(len(cat.get('skill_tree', [])) for cat in categories)
            
            # Get user's stat and skill points with correct field mappings
            str_skill_points = available_points.get('strength', 0)
            end_skill_points = available_points.get('endurance', 0)
            tech_skill_points = available_points.get('technique', 0)
            user_str = user_stats.get('str_level', 1)
            user_end = user_stats.get('end_level', 1)
            user_tech = user_stats.get('tech_level', 1)
            # Calculate user level as max of all stat levels since ascendant_level doesn't exist
            user_level = max(user_str, user_end, user_tech)
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Movement Library Overview\x1b[0m\n"
                f"Operative: \x1b[1;33m{user.display_name}\x1b[0m\n"
                f"Rank: \x1b[1;37mLevel {user_level}\x1b[0m\n"
                f"Skills Mastered: \x1b[1;32m{len(unlocked_skill_ids)}\x1b[0m / \x1b[1;37m{total_skills}\x1b[0m\n\n"
                f"\x1b[1;37m⚔️ Combat Statistics:\x1b[0m\n"
                f"├─ 🔴 Strength: \x1b[1;33m{user_str}\x1b[0m pts\n"
                f"├─ 🔵 Endurance: \x1b[1;33m{user_end}\x1b[0m pts\n"
                f"└─ 🟡 Technique: \x1b[1;33m{user_tech}\x1b[0m pts\n\n"
                f"\x1b[1;37m✨ Skill Points Available:\x1b[0m\n"
                f"├─ 🔴 Strength SP: \x1b[1;33m{str_skill_points}\x1b[0m\n"
                f"├─ 🔵 Endurance SP: \x1b[1;33m{end_skill_points}\x1b[0m\n"
                f"└─ 🟡 Technique SP: \x1b[1;33m{tech_skill_points}\x1b[0m\n\n"
                f"\x1b[1;37m📚 Training Categories:\x1b[0m\n"
            )
            
            # Group categories and show unlockable skills for each
            category_groups = {
                "Upper Body": [],
                "Lower Body": [],
                "Core & Stability": []
            }
            
            for cat in categories:
                cat_name = cat.get('name', 'Unknown')
                skill_tree = cat.get('skill_tree', [])
                
                # Find unlockable skills (limit to 2 per category for compactness)
                unlockable_skills = []
                for node in skill_tree[:5]:  # Check first 5 nodes only
                    node_id = node.get('id')
                    if node_id in unlocked_skill_ids:
                        continue  # Skip already unlocked
                    
                    requirements = node.get('requirements', {})
                    req_level = requirements.get('ascendant_level', 0)  # Using new V2 API field names
                    req_str = requirements.get('str_level', 0)  # Using new V2 API field names
                    req_end = requirements.get('end_level', 0)  # Changed from end_level to end_level
                    req_tech = requirements.get('tech_level', 0)  # Changed from tech_level to tech_level
                    
                    can_unlock = (user_level >= req_level and 
                                user_str >= req_str and 
                                user_end >= req_end and 
                                user_tech >= req_tech)
                    
                    if can_unlock:
                        unlockable_skills.append(node)
                        if len(unlockable_skills) >= 2:  # Limit to 2 unlockable skills shown
                            break
                
                # Categorize by body area
                if any(keyword in cat_name.lower() for keyword in ['pull', 'push', 'overhead', 'arm', 'shoulder']):
                    category_groups["Upper Body"].append((cat_name, skill_tree, unlockable_skills))
                elif any(keyword in cat_name.lower() for keyword in ['squat', 'lunge', 'leg', 'hip', 'hinge']):
                    category_groups["Lower Body"].append((cat_name, skill_tree, unlockable_skills))
                else:
                    category_groups["Core & Stability"].append((cat_name, skill_tree, unlockable_skills))
            
            # Display categories with MUCH more compact structure - only show totals per group
            for group_name, group_categories in category_groups.items():
                if not group_categories:
                    continue
                    
                # Calculate group totals
                group_unlocked = sum(sum(1 for node in skill_tree if node.get('id') in unlocked_skill_ids) 
                                   for _, skill_tree, _ in group_categories)
                group_total = sum(len(skill_tree) for _, skill_tree, _ in group_categories)
                group_ready = sum(len(unlockable_skills) for _, _, unlockable_skills in group_categories)
                
                # Group header with color coding and totals
                group_colors = {
                    "Upper Body": "\x1b[1;31m",
                    "Lower Body": "\x1b[1;34m", 
                    "Core & Stability": "\x1b[1;35m"
                }
                color = group_colors.get(group_name, "\x1b[1;37m")
                ready_text = f" • \x1b[1;95m{group_ready} Ready!\x1b[0m" if group_ready else ""
                content += f"{color}▸ {group_name}\x1b[0m (\x1b[1;32m{group_unlocked}\x1b[0m/\x1b[1;37m{group_total}\x1b[0m){ready_text}\n"
            
            content += (
                f"\n────────────────────────\n"
                f"\x1b[1;37mUse buttons below to explore\x1b[0m\n"
                f"```"
            )
            
            # Check if content is too long for Discord's 4096 character limit
            if len(content) > 4000:  # Leave some buffer
                logger.warning(f"Overview content too long ({len(content)} chars), truncating for user {user.id}")
                # Find the last complete category group section
                lines = content.split('\n')
                truncated_lines = []
                char_count = 0
                
                for line in lines:
                    if char_count + len(line) + 1 > 3900:  # Leave more buffer for closing
                        truncated_lines.append("\n\x1b[1;33m... (Additional categories truncated)\x1b[0m\n")
                        truncated_lines.append("──────────────────────────\n")
                        truncated_lines.append("\x1b[1;37mUse buttons below to explore or unlock skills\x1b[0m\n")
                        truncated_lines.append("```")
                        break
                    truncated_lines.append(line)
                    char_count += len(line) + 1
                
                content = '\n'.join(truncated_lines)
                logger.info(f"Truncated overview content to {len(content)} chars for user {user.id}")
            
        # Detailed view (old overview) - now becomes detailed view
        elif view_mode == "detailed" and not category:
            logger.info(f"Processing detailed mode for user {user.id}")
            # Calculate total skills available
            total_skills = sum(len(cat.get('skill_tree', [])) for cat in categories)
            
            # Get user's stat and skill points with correct field mappings
            str_skill_points = available_points.get('strength', 0)
            end_skill_points = available_points.get('endurance', 0)
            tech_skill_points = available_points.get('technique', 0)
            user_str = user_stats.get('str_level', 1)
            user_end = user_stats.get('end_level', 1)
            user_tech = user_stats.get('tech_level', 1)
            user_level = max(user_str, user_end, user_tech)
            
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"\x1b[1;36m● Movement Library\x1b[0m\n"
                f"Status: \x1b[1;32mONLINE\x1b[0m (cached)\n"
                f"Categories: \x1b[1;33m{len(categories)}\x1b[0m\n"
                f"Skills Unlocked: \x1b[1;32m{len(unlocked_skill_ids)}\x1b[0m / \x1b[1;37m{total_skills}\x1b[0m\n"
                f"Stat Points: \x1b[1;33mSTR:{user_str} END:{user_end} TECH:{user_tech}\x1b[0m\n"
                f"Skill Points: \x1b[1;33mSTR:{str_skill_points} END:{end_skill_points} TECH:{tech_skill_points}\x1b[0m\n\n"
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
            logger.info(f"Processing category view for user {user.id}, category={category}")
            # Show specific category details
            # Use normalized category IDs for proper matching
            normalized_target = normalize_category_id(category)
            category_data = None
            
            # First try exact match with normalized IDs
            for cat in categories:
                if normalize_category_id(cat.get('id', '')) == normalized_target:
                    category_data = cat
                    break
            
            # If no exact match, try name-based matching as fallback
            if not category_data:
                target_lower = normalized_target.lower()
                for cat in categories:
                    cat_name = cat.get('name', '').lower()
                    if target_lower in cat_name or cat_name in target_lower:
                        category_data = cat
                        break
            
            # Final fallback to first category
            if not category_data:
                category_data = categories[0] if categories else None
            
            if category_data:
                cat_name = category_data.get('name', 'Unknown')
                primary_stat = category_data.get('primary_stat', 'STR')
                skill_tree = category_data.get('skill_tree', [])
                
                # Get user's relevant stat
                user_stat_value = user_stats.get(primary_stat.lower() + '_level', 1)  # Changed from _points to _level
                user_level = max(user_stats.get('str_level', 1), user_stats.get('end_level', 1), user_stats.get('tech_level', 1))
                
                # Get page position info if we have a current group
                page_info = ""
                if current_group:
                    page_info = get_category_position_info(categories, category, current_group)
                
                # Get user's skill points for display with correct field mappings
                str_skill_points = available_points.get('strength', 0)
                end_skill_points = available_points.get('endurance', 0)
                tech_skill_points = available_points.get('technique', 0)
                
                # Get user's stat levels for display
                user_str = user_stats.get('str_level', 1)
                user_end = user_stats.get('end_level', 1)
                user_tech = user_stats.get('tech_level', 1)
                
                content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;36m● {cat_name}{page_info}\x1b[0m\n"
                    f"Operative: \x1b[1;33m{user.display_name}\x1b[0m\n"
                    f"Rank: \x1b[1;37mLevel {user_level}\x1b[0m\n"
                    f"Primary Stat: \x1b[1;33m{primary_stat}\x1b[0m (You: {user_stat_value})\n\n"
                    f"\x1b[1;37m⚔️ Combat Statistics:\x1b[0m\n"
                    f"├─ 🔴 Strength: \x1b[1;33m{user_str}\x1b[0m pts\n"
                    f"├─ 🔵 Endurance: \x1b[1;33m{user_end}\x1b[0m pts\n"
                    f"└─ 🟡 Technique: \x1b[1;33m{user_tech}\x1b[0m pts\n\n"
                    f"\x1b[1;37m✨ Skill Points Available:\x1b[0m\n"
                    f"├─ 🔴 Strength SP: \x1b[1;33m{str_skill_points}\x1b[0m\n"
                    f"├─ 🔵 Endurance SP: \x1b[1;33m{end_skill_points}\x1b[0m\n"
                    f"└─ 🟡 Technique SP: \x1b[1;33m{tech_skill_points}\x1b[0m\n\n"
                    f"\x1b[1;37m🎯 Skill Progression ({len(skill_tree)} levels):\x1b[0m\n"
                )
                
                # Display skill tree levels - sort by level and show all levels
                logger.info(f"Skill tree for {cat_name}: {len(skill_tree)} nodes")
                if skill_tree:
                    logger.info(f"Sample skill node: {skill_tree[0]}")
                    for i, node in enumerate(skill_tree[:3]):
                        logger.info(f"Node {i}: level={node.get('level')}, name={node.get('name')}")
                
                sorted_skills = sorted(skill_tree, key=lambda x: x.get('level', 1))
                logger.info(f"After sorting: levels = {[s.get('level') for s in sorted_skills[:5]]}")
                for node in sorted_skills:  # Show all levels in order
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
                        req_level = requirements.get('ascendant_level', 0)  # Using new V2 API field names
                        req_str = requirements.get('str_level', 0)  # Using new V2 API field names
                        req_end = requirements.get('end_level', 0)  # Changed from end_level to end_level
                        req_tech = requirements.get('tech_level', 0)  # Changed from tech_level to tech_level
                        
                        user_str = user_stats.get('str_level', 1)  # Using new V2 API field names
                        user_end = user_stats.get('end_level', 1)  # Changed from end_level to end_level
                        user_tech = user_stats.get('tech_level', 1)  # Changed from tech_level to tech_level
                        
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
                    level_line = f"\n{level_color}Level {level}: {name} {unlock_indicator}{status_text}\x1b[0m\n"
                    content += level_line
                    logger.info(f"Added level line for Level {level}: content length now {len(content)} chars")
                    
                    # Show requirements if not unlocked
                    if not is_unlocked and requirements:
                        req_parts = []
                        req_level = requirements.get('ascendant_level', 0)  # Using new V2 API field names
                        req_str = requirements.get('str_level', 0)  # Using new V2 API field names
                        req_end = requirements.get('end_level', 0)  # Changed from end_level to end_level
                        req_tech = requirements.get('tech_level', 0)  # Changed from tech_level to tech_level
                        req_str_skill = requirements.get('strength', 0)  # Changed from strength_points to strength
                        req_end_skill = requirements.get('endurance', 0)  # Changed from endurance_points to endurance
                        req_tech_skill = requirements.get('technique', 0)  # Changed from technique_points to technique
                        
                        if req_level > 0:
                            req_parts.append(f"Level {req_level}")
                        if req_str > 0:
                            req_parts.append(f"{req_str} STR")
                        if req_end > 0:
                            req_parts.append(f"{req_end} END")
                        if req_tech > 0:
                            req_parts.append(f"{req_tech} TECH")
                        
                        skill_point_parts = []
                        if req_str_skill > 0:
                            skill_point_parts.append(f"STR SP:{req_str_skill}")
                        if req_end_skill > 0:
                            skill_point_parts.append(f"END SP:{req_end_skill}")
                        if req_tech_skill > 0:
                            skill_point_parts.append(f"TECH SP:{req_tech_skill}")
                        
                        if req_parts:
                            color = "\x1b[1;32m" if can_unlock else "\x1b[1;33m"
                            content += f"  {color}Requires: {', '.join(req_parts)}\x1b[0m\n"
                        
                        if skill_point_parts:
                            color = "\x1b[1;32m" if can_unlock else "\x1b[1;33m"
                            content += f"  {color}Skill Points: {', '.join(skill_point_parts)}\x1b[0m\n"
                        
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
        
        # Final check for Discord's 4096 character limit before creating embed
        logger.info(f"Content length before truncation check: {len(content)} chars")
        if len(content) > 4000:
            logger.warning(f"Content too long ({len(content)} chars), applying smart truncation for user {user.id}")
            
            # Smart truncation - preserve skill levels but reduce detail
            lines = content.split('\n')
            
            # For category views, preserve skill level structure
            if category and lines:
                # Find skill level lines (they start with level indicators)
                new_lines = []
                in_skill_section = False
                current_skill_lines = []
                
                for line in lines:
                    # Keep header lines (before skill progression section)
                    if "🎯 Skill Progression" in line:
                        in_skill_section = True
                        new_lines.append(line)
                        continue
                    
                    if not in_skill_section:
                        new_lines.append(line)
                        continue
                        
                    # In skill section - detect level lines vs detail lines  
                    stripped_line = line.strip()
                    if stripped_line.startswith('Level ') or 'Level ' in stripped_line:
                        # This is a level header - keep it
                        new_lines.append(line)
                    elif 'Requires:' in line or 'Skill Points:' in line:
                        # Keep requirement lines (compact)
                        new_lines.append(line)
                    elif line.strip().startswith('├─') or line.strip().startswith('└─'):
                        # Skip movement detail lines to save space
                        continue
                    elif line.strip().startswith('...'):
                        # Skip movement count lines
                        continue
                    else:
                        # Keep other lines (footer, etc.)
                        new_lines.append(line)
                
                # Rebuild content with preserved structure
                content = '\n'.join(new_lines)
                logger.info(f"Smart truncated category content to {len(content)} chars for user {user.id}")
                
                # If still too long, apply emergency truncation
                if len(content) > 4000:
                    logger.warning(f"Content still too long after smart truncation, applying emergency truncation")
                    lines = content.split('\n')
                    if len(lines) > 10:
                        header_lines = lines[:12]  # Keep more header lines for category views
                        footer_lines = lines[-3:]  # Keep last 3 lines (footer)
                        truncated_content = '\n'.join(header_lines) + '\n\n\x1b[1;33m... (Movement details truncated)\x1b[0m\n\n' + '\n'.join(footer_lines)
                        content = truncated_content
                        logger.info(f"Emergency truncated content to {len(content)} chars for user {user.id}")
            else:
                # Original emergency truncation for overview mode
                if len(lines) > 10:
                    header_lines = lines[:8]  # Keep first 8 lines (header info)
                    footer_lines = lines[-3:]  # Keep last 3 lines (footer)
                    truncated_content = '\n'.join(header_lines) + '\n\n\x1b[1;33m... (Content truncated due to length limit)\x1b[0m\n\n' + '\n'.join(footer_lines)
                    content = truncated_content
                    logger.info(f"Emergency truncated content to {len(content)} chars for user {user.id}")
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(255, 215, 0)  # Gold color for skills
        )
        embed.set_footer(text="Shadow Archive • Movement Library • Skill Tree (Optimized)")
        return embed
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching skill tree data for user {user.id}")
        return await _create_fallback_embed(user, "CONNECTION TIMEOUT")
    except Exception as e:
        logger.error(f"Error building skill tree embed for user {user.id}: {e}", exc_info=True)
        return await _create_fallback_embed(user, "SYSTEM ERROR")

async def _create_fallback_embed(user: Union[discord.User, discord.Member], error_message: str) -> discord.Embed:
    """Create a fallback embed when API calls fail."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_tree")
    
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;31m● Skill Tree Unavailable\x1b[0m\n"
        f"Status: \x1b[1;31mOFFLINE\x1b[0m\n"
        f"Error: {error_message}\n\n"
        f"\x1b[1;33m⚠️ The skill tree system is temporarily unavailable.\x1b[0m\n"
        f"This may be due to:\n"
        f"• API connection issues\n"
        f"• Authentication problems\n"
        f"• Server maintenance\n\n"
        f"\x1b[1;37mPlease try again in a few moments.\x1b[0m\n"
        f"```"
    )
    
    embed = discord.Embed(
        description=content,
        color=discord.Color.red()
    )
    embed.set_footer(text="Shadow Archive • Movement Library • Error State")
    return embed

async def _create_partial_embed(user: Union[discord.User, discord.Member], available_data: dict, missing_info: str) -> discord.Embed:
    """Create a partial embed when only some data is available."""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_tree")
    
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;33m● Skill Tree (Limited Data)\x1b[0m\n"
        f"Status: \x1b[1;33mPARTIAL\x1b[0m\n"
        f"Missing: {missing_info}\n\n"
        f"\x1b[1;37m📚 Available Information:\x1b[0m\n"
    )
    
    # Show what data we have
    if 'categories' in available_data:
        categories = available_data['categories']
        content += f"• Movement Categories: \x1b[1;32m{len(categories)}\x1b[0m\n"
        for cat in categories[:3]:  # Show first 3 categories
            cat_name = cat.get('name', 'Unknown')
            skill_count = len(cat.get('skill_tree', []))
            content += f"  └─ {cat_name} ({skill_count} levels)\n"
        if len(categories) > 3:
            content += f"  └─ ... and {len(categories) - 3} more\n"
    
    if 'stats' in available_data:
        stats = available_data['stats']
        user_level = max(stats.get('str_level', 1), stats.get('end_level', 1), stats.get('tech_level', 1))  # Calculate from stat levels
        content += f"• Your Level: \x1b[1;33m{user_level}\x1b[0m\n"
    
    content += (
        f"\n\x1b[1;33m⚠️ Some features may be limited due to missing data.\x1b[0m\n"
        f"\x1b[1;37mTry refreshing or check your connection.\x1b[0m\n"
        f"```"
    )
    
    embed = discord.Embed(
        description=content,
        color=discord.Color.orange()
    )
    embed.set_footer(text="Shadow Archive • Movement Library • Partial Data")
    return embed

# --- VIEW IMPLEMENTATION ---

class SkillTreeView(discord.ui.View):
    """View for skill tree panel with category navigation buttons."""
    
    def __init__(self, bot: discord.Client, user: discord.User, current_group: Optional[str] = None, current_category: Optional[str] = None, view_mode: str = "overview"):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.current_category: Optional[str] = current_category
        self.current_group: Optional[str] = current_group
        self.view_mode = view_mode
        
        # Add panel dropdown using local import to avoid circular dependency
        try:
            from shared.utils.common_views import EphemeralPanelSelect
            panel_dropdown = EphemeralPanelSelect(bot, user.id)
            panel_dropdown.row = 0
            self.add_item(panel_dropdown)
            logger.info(f"Successfully added panel dropdown for user {user.id}")
        except ImportError as e:
            logger.warning(f"Could not add panel dropdown for user {user.id}: {e}")
            logger.info(f"Creating SkillTreeView for user {user.id} without panel dropdown")
        
        # Add navigation buttons based on state
        if current_group and current_category:
            # Show category dropdown navigation when in a category
            logger.info(f"Adding category dropdown for group={current_group}, category={current_category}")
            
            # Add category selection dropdown - row 1
            self.category_dropdown = CategorySelectionDropdown(bot, user, current_group, current_category)
            self.category_dropdown.row = 1
            self.add_item(self.category_dropdown)
            
            # Add unlock button - row 2
            self.unlock_button = UnlockSkillButton(bot, user)
            self.unlock_button.disabled = True  # Disabled by default
            self.unlock_button.row = 2
            self.add_item(self.unlock_button)
            
            # Add back to overview button - row 2
            back_button = BackToOverviewButton(bot, user)
            back_button.row = 2
            self.add_item(back_button)
        else:
            # Show body group selection when in overview - row 2
            upper_button = UpperBodyButton(bot, user)
            upper_button.row = 2
            self.add_item(upper_button)
            
            lower_button = LowerBodyButton(bot, user)
            lower_button.row = 2
            self.add_item(lower_button)
            
            core_button = CoreButton(bot, user)
            core_button.row = 2
            self.add_item(core_button)
            
            # Add View Skill Tree button for overview mode - row 3
            if view_mode == "overview":
                view_tree_button = ViewSkillTreeButton(bot, user)
                view_tree_button.row = 3
                self.add_item(view_tree_button)
            else:
                # Add Back to Overview button for detailed mode - row 3
                back_overview_button = BackToOverviewButton(bot, user)
                back_overview_button.row = 3
                self.add_item(back_overview_button)
            
            # Don't add unlock button on overview page - it should only appear in category view
            self.unlock_button = None

    async def initialize_dropdown(self):
        """Initialize the category dropdown options after view creation."""
        if hasattr(self, 'category_dropdown'):
            await self.category_dropdown.populate_options()

    def update_unlock_button(self, category: Optional[str], has_unlockable: bool):
        """Update the unlock button state based on current category."""
        self.current_category = category
        # Only update unlock button if it exists (category view only)
        if hasattr(self, 'unlock_button') and self.unlock_button is not None:
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
            style=discord.ButtonStyle.primary
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
            
            # Find upper body categories - prioritize PUSH first
            upper_body_categories = []
            for cat in categories:
                cat_id = cat.get('id', '').upper()
                cat_name = cat.get('name', '').lower()
                if (cat_id in ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC'] or
                    any(keyword in cat_name for keyword in ['push', 'pull', 'overhead', 'upper', 'grip', 'ballistic'])):
                    upper_body_categories.append(cat.get('id'))
            
            # Use PUSH as the primary category
            upper_body_cat = 'PUSH' if 'PUSH' in upper_body_categories else (upper_body_categories[0] if upper_body_categories else None)
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=upper_body_cat, current_group='upper')
            view = SkillTreeView(self.bot, self.user, current_group='upper', current_category=upper_body_cat)
            await view.initialize_dropdown()  # Initialize dropdown options
            
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
            style=discord.ButtonStyle.primary
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
            
            # Find lower body categories - prioritize SQUAT first
            lower_body_categories = []
            for cat in categories:
                cat_id = cat.get('id', '').upper()
                cat_name = cat.get('name', '').lower()
                if (cat_id in ['SQUAT', 'LUNGE', 'HINGE', 'GAIT', 'LOADED_CARRY'] or
                    any(keyword in cat_name for keyword in ['squat', 'lunge', 'hinge', 'leg', 'hip', 'gait', 'carry'])):
                    lower_body_categories.append(cat.get('id'))
            
            # Use SQUAT as the primary category
            lower_body_cat = 'SQUAT' if 'SQUAT' in lower_body_categories else (lower_body_categories[0] if lower_body_categories else None)
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=lower_body_cat, current_group='lower')
            view = SkillTreeView(self.bot, self.user, current_group='lower', current_category=lower_body_cat)
            await view.initialize_dropdown()  # Initialize dropdown options
            
            # Check if there are unlockable skills and update button
            has_unlockable = await check_has_unlockable_skills(self.user, lower_body_cat, library_data)
            view.update_unlock_button(lower_body_cat, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

class CoreButton(discord.ui.Button):
    """Button for navigating to core and stability skills category."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🎯 Core & Stability",
            style=discord.ButtonStyle.primary
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
            
            # Find core and stability categories - prioritize CORE first
            core_categories = []
            for cat in categories:
                cat_id = cat.get('id', '').upper()
                cat_name = cat.get('name', '').lower()
                if (cat_id in ['CORE', 'ROTATION', 'BALANCE', 'FLEXIBILITY', 'MOBILITY_FLOW'] or
                    any(keyword in cat_name for keyword in ['core', 'rotation', 'balance', 'flexibility', 'mobility'])):
                    core_categories.append(cat.get('id'))
            
            # Use CORE as the primary category
            core_cat = 'CORE' if 'CORE' in core_categories else (core_categories[0] if core_categories else None)
            
            embed = await build_skill_tree_embed(self.bot, self.user, category=core_cat, current_group='core')
            view = SkillTreeView(self.bot, self.user, current_group='core', current_category=core_cat)
            await view.initialize_dropdown()  # Initialize dropdown options
            
            # Check if there are unlockable skills
            has_unlockable = await check_has_unlockable_skills(self.user, core_cat, library_data)
            view.update_unlock_button(core_cat, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

class ViewSkillTreeButton(discord.ui.Button):
    """Button to switch from overview to detailed skill tree view."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="🌳 View Skill Tree",
            custom_id="view_skill_tree"
        )
        self.bot = bot
        self.user = user
    
    async def callback(self, interaction: discord.Interaction):
        """Handle view skill tree button click."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This panel is not for you.", ephemeral=True)
            return
        
        try:
            # Defer the response immediately
            await interaction.response.defer()
            
            # Create detailed view showing individual categories
            embed = await build_skill_tree_embed(self.bot, self.user, view_mode="detailed")
            view = SkillTreeView(self.bot, self.user, view_mode="detailed")
            
            # Initialize any dropdown components if they exist
            if hasattr(view, 'initialize_dropdown'):
                await view.initialize_dropdown()
            
            # Edit the original message with the new content
            await interaction.edit_original_response(embed=embed, view=view)
            
            logger.info(f"ViewSkillTreeButton: Successfully created expanded overview for user {self.user.id}")
            
        except Exception as e:
            logger.error(f"ViewSkillTreeButton: Error creating expanded overview for user {self.user.id}: {e}")
            
            # Create fallback response
            fallback_embed = await _create_fallback_embed(self.user, f"View Error: {str(e)[:50]}...")
            fallback_view = SkillTreeView(self.bot, self.user, view_mode="overview")
            
            try:
                await interaction.edit_original_response(embed=fallback_embed, view=fallback_view)
            except Exception as fallback_error:
                logger.error(f"ViewSkillTreeButton: Fallback also failed: {fallback_error}")
                # Last resort - send a simple error message
                try:
                    await interaction.edit_original_response(
                        content=f"Error loading skill tree: {str(e)[:100]}", 
                        embed=None, 
                        view=None
                    )
                except:
                    pass

class BackToOverviewButton(discord.ui.Button):
    """Button for returning to skill tree overview."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🏠 Back to Menu",
            style=discord.ButtonStyle.secondary  # Gray color as requested
        )
        self.bot = bot
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        
        async def do_work():
            try:
                embed = await build_skill_tree_embed(self.bot, self.user, view_mode="overview")
                view = SkillTreeView(self.bot, self.user, view_mode="overview")
                view.current_category = None
                # No need to update unlock button on overview page since it doesn't exist
                
                logger.info(f"BackToOverviewButton: Successfully created overview for user {self.user.id}")
                return embed, view
                
            except Exception as e:
                logger.error(f"BackToOverviewButton: Error creating overview for user {self.user.id}: {e}")
                # Return fallback embed instead of letting exception bubble up
                fallback_embed = await _create_fallback_embed(self.user, f"Overview Error: {str(e)[:50]}...")
                fallback_view = SkillTreeView(self.bot, self.user, view_mode="overview")
                return fallback_embed, fallback_view
        
        await run_with_animation(interaction, do_work)

# --- NEW UNLOCK FUNCTIONALITY ---

class UnlockSkillButton(discord.ui.Button):
    """Button for unlocking available skill nodes."""
    
    def __init__(self, bot: discord.Client, user: discord.User):
        super().__init__(
            label="🔓 Unlock Skill",
            style=discord.ButtonStyle.success
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
            unlocked_skill_ids = {skill.get('node_id') for skill in unlocked_skills}  # Using new V2 API field names
            user_stats = profile_data.get('stats', {})
            
            # Find all unlockable skills
            skill_tree = category_data.get('skill_tree', [])
            unlockable_skills = []
            
            for node in skill_tree:
                node_id = node.get('id')
                if node_id in unlocked_skill_ids:
                    continue  # Already unlocked
                
                requirements = node.get('requirements', {})
                req_level = requirements.get('ascendant_level', 0)  # Using new V2 API field names
                req_str = requirements.get('str_level', 0)  # Using new V2 API field names
                req_end = requirements.get('end_level', 0)  # Fixed: use end_level instead of end_level
                req_tech = requirements.get('tech_level', 0)  # Fixed: use tech_level instead of tech_level
                
                user_level = max(user_stats.get('str_level', 1), user_stats.get('end_level', 1), user_stats.get('tech_level', 1))  # Fixed: calculate from actual levels
                user_str = user_stats.get('str_level', 1)  # Using new V2 API field names
                user_end = user_stats.get('end_level', 1)  # Fixed: use end_level instead of end_level
                user_tech = user_stats.get('tech_level', 1)  # Fixed: use tech_level instead of tech_level
                
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
            embed = create_skill_selection_embed(unlockable_skills, user_stats, self.user)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error showing skill selection for user {self.user.id}: {e}")
            await interaction.response.send_message(f"❌ Error loading available skills: {str(e)}", ephemeral=True)

# --- SKILL SELECTION SYSTEM ---

def create_skill_selection_embed(unlockable_skills: List[Dict], user_stats: Dict, user: discord.User) -> discord.Embed:
    """Create embed showing available skills to unlock with proper headers and navigation."""
    from shared.utils.headers import get_system_status_header
    from shared.utils.ui_styles import get_panel_sub_header
    
    # Get universal header and sub-header to match other interfaces
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("skill_unlock")
    
    user_level = max(user_stats.get('str_level', 1), user_stats.get('end_level', 1), user_stats.get('tech_level', 1))  # Fixed: calculate from actual levels
    user_str = user_stats.get('str_level', 1)  # Using new V2 API field names
    user_end = user_stats.get('end_level', 1)  # Fixed: use end_level instead of end_level
    user_tech = user_stats.get('tech_level', 1)  # Fixed: use tech_level instead of tech_level
    
    content = (
        f"```ansi\n"
        f"{header}\n"
        f"{sub_header}\n\n"
        f"\x1b[1;36m🌟 Available Skills to Unlock\x1b[0m\n"
        f"Your Stats: Lv.{user_level} | STR:{user_str} | END:{user_end} | TECH:{user_tech}\n\n"
        f"\x1b[1;32mYou can unlock {len(unlockable_skills)} skill(s):\x1b[0m\n"
    )
    
    for i, skill in enumerate(unlockable_skills[:10], 1):  # Show first 10
        skill_name = skill.get('name', 'Unknown Skill')
        content += f"{i}. \x1b[1;33m{skill_name}\x1b[0m\n"
    
    if len(unlockable_skills) > 10:
        content += f"\n... and {len(unlockable_skills) - 10} more\n"
    
    content += (
        f"\n\x1b[1;37mSelect a skill from the dropdown below to unlock it.\x1b[0m\n"
        f"──────────────────────────\n"
        f"```"
    )
    
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
        
        # Add back to menu button for proper navigation
        self.add_item(BackToOverviewButton(bot, user))

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
            req_level = requirements.get('ascendant_level', 0)  # Using new V2 API field names
            req_str = requirements.get('str_level', 0)  # Using new V2 API field names
            req_end = requirements.get('end_level', 0)  # Fixed: use end_level instead of end_level
            req_tech = requirements.get('tech_level', 0)  # Fixed: use tech_level instead of tech_level
            req_str_skill = requirements.get('strength_points', 0)
            req_end_skill = requirements.get('endurance_points', 0)
            req_tech_skill = requirements.get('technique_points', 0)
            
            req_parts = []
            if req_level > 0:
                req_parts.append(f"Lv.{req_level}")
            if req_str > 0:
                req_parts.append(f"STR:{req_str}")
            if req_end > 0:
                req_parts.append(f"END:{req_end}")
            if req_tech > 0:
                req_parts.append(f"TECH:{req_tech}")
            
            skill_parts = []
            if req_str_skill > 0:
                skill_parts.append(f"STR SP:{req_str_skill}")
            if req_end_skill > 0:
                skill_parts.append(f"END SP:{req_end_skill}")
            if req_tech_skill > 0:
                skill_parts.append(f"TECH SP:{req_tech_skill}")
            
            req_text = ""
            if req_parts:
                req_text = f"Req: {', '.join(req_parts)}"
            if skill_parts:
                if req_text:
                    req_text += f" | SP: {', '.join(skill_parts)}"
                else:
                    req_text = f"SP: {', '.join(skill_parts)}"
            
            if req_text:
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
        
        # Use run_with_animation pattern to fix Shadow Nexus Error
        async def do_work():
            try:
                # Use singleton APIClient instance - this will reuse existing token cache
                api_client = APIClient()
                unlock_result = await api_client.unlock_skill_v2(self.user, str(selected_skill['id']))
                
                # Clear caches to force refresh
                clear_library_cache()
                clear_profile_cache(self.user.id)
                
                # Show success message with universal formatting
                skill_name = selected_skill.get('name', 'Unknown')
                unlock_message = selected_skill.get('unlock_message', '')
                
                # Create formatted success message using universal headers
                from shared.utils.headers import get_system_status_header
                from shared.utils.ui_styles import get_panel_sub_header
                
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("skill_tree")
                
                success_content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;32m🎉 SKILL MASTERED! 🎉\x1b[0m\n\n"
                    f"\x1b[1;33m⚡ {skill_name}\x1b[0m\n"
                    f"\x1b[0;37m{unlock_message}\x1b[0m\n\n"
                    f"\x1b[1;36m✨ Your training has paid off, Ascendant!\x1b[0m\n"
                    f"\x1b[0;37mThis skill is now available in your movement arsenal.\x1b[0m\n\n"
                    f"\x1b[1;35m🔄 The skill tree will refresh automatically.\x1b[0m\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                success_embed = discord.Embed(
                    description=success_content,
                    color=discord.Color.gold()
                )
                success_embed.set_footer(text="Shadow Archive • Skill Mastery • Well Done!")
                
                # Return to skill tree after successful unlock - ensure proper initialization
                embed = await build_skill_tree_embed(self.bot, self.user)
                view = SkillTreeView(self.bot, self.user, view_mode="overview")
                
                logger.info(f"SkillSelectionDropdown: Successfully unlocked skill and returning to overview for user {self.user.id}")
                return embed, view
                
            except Exception as e:
                logger.error(f"Failed to unlock skill {selected_skill['id']} for user {self.user.id}: {e}")
                # Return error embed and view
                from shared.utils.headers import get_system_status_header
                from shared.utils.ui_styles import get_panel_sub_header
                
                header = get_system_status_header(self.user).replace('```ansi', '').replace('```', '').strip()
                sub_header = get_panel_sub_header("skill_tree")
                
                error_content = (
                    f"```ansi\n"
                    f"{header}\n"
                    f"{sub_header}\n\n"
                    f"\x1b[1;31m❌ SKILL UNLOCK FAILED\x1b[0m\n\n"
                    f"\x1b[0;37mError: {str(e)}\x1b[0m\n\n"
                    f"\x1b[1;33m🔄 Returning to skill tree...\x1b[0m\n"
                    f"──────────────────────────\n"
                    f"```"
                )
                
                error_embed = discord.Embed(
                    description=error_content,
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="Shadow Archive • Error • Try Again")
                
                # Return to skill tree on error - ensure proper initialization
                embed = await build_skill_tree_embed(self.bot, self.user)
                view = SkillTreeView(self.bot, self.user, view_mode="overview")
                
                logger.info(f"SkillSelectionDropdown: Error handled, returning to overview for user {self.user.id}")
                return embed, view
        
        await run_with_animation(interaction, do_work)

# --- ENHANCED RPG NAVIGATION BUTTONS ---

def get_category_position_info(categories: List[Dict], current_category: str, current_group: str) -> str:
    """Get position information for the current category within its group."""
    try:
        # Get categories for the current group
        group_categories = find_categories_for_group(categories, current_group)
        
        if not group_categories:
            return ""
        
        # Find current category position
        normalized_current = normalize_category_id(current_category)
        current_index = -1
        
        for i, cat_id in enumerate(group_categories):
            if normalize_category_id(cat_id) == normalized_current:
                current_index = i
                break
        
        if current_index >= 0:
            return f" ({current_index + 1}/{len(group_categories)})"
        else:
            return f" (1/{len(group_categories)})"  # Fallback
    except Exception as e:
        logger.warning(f"Error getting category position: {e}")
        return ""

def find_categories_for_group(categories: List[Dict], group: str) -> List[str]:
    """Find all category IDs that belong to a specific group."""
    try:
        if not categories:
            logger.info(f"No categories provided for group '{group}'")
            return []
        
        group_mapping = get_category_group_mapping()
        expected_categories = group_mapping.get(group, [])
        
        logger.info(f"Finding categories for group '{group}', expecting: {expected_categories}")
        
        found_categories = []
        
        for cat in categories:
            try:
                cat_id = cat.get('id', '')
                cat_name = cat.get('name', '').lower()
                
                # Normalize the category ID
                normalized_id = normalize_category_id(cat_id)
                
                # Check if this category belongs to the group (exact match only)
                if normalized_id in expected_categories:
                    if normalized_id not in found_categories:  # Avoid duplicates
                        found_categories.append(normalized_id)
                        
            except Exception as cat_error:
                logger.error(f"Error processing category: {cat_error}")
                continue
        
        logger.info(f"Found {len(found_categories)} categories for group '{group}': {found_categories}")
        return found_categories
        
    except Exception as e:
        logger.error(f"Exception in find_categories_for_group: {e}")
        return []

# --- HELPER FUNCTIONS ---

async def check_has_unlockable_skills(user: discord.User, category_id: str, library_data: Optional[Dict] = None) -> bool:
    """Check if the user has any unlockable skills in the given category."""
    try:
        if not library_data:
            library_data = await get_cached_library_data(user)
        
        profile_data = await get_cached_profile_data(user)
        unlocked_skills = profile_data.get('unlocked_skills', [])
        unlocked_skill_ids = {skill.get('node_id') for skill in unlocked_skills}  # Using new V2 API field names
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
            req_str = requirements.get('str_level', 0)
            req_end = requirements.get('end_level', 0)
            req_tech = requirements.get('tech_level', 0)
            
            user_level = max(user_stats.get('str_level', 1), user_stats.get('end_level', 1), user_stats.get('tech_level', 1))
            user_str = user_stats.get('str_level', 1)
            user_end = user_stats.get('end_level', 1)
            user_tech = user_stats.get('tech_level', 1)
            
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

class CategorySelectionDropdown(discord.ui.Select):
    """Dropdown for selecting which category to view within a group."""
    
    def __init__(self, bot: discord.Client, user: discord.User, group: str, current_category: Optional[str] = None):
        self.bot = bot
        self.user = user
        self.group = group
        self.current_category = current_category
        
        # We'll populate options in an async method since we need to fetch library data
        super().__init__(
            placeholder="🗂️ Select a category...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label="Loading...", value="loading")]  # Temporary
        )
    
    async def populate_options(self):
        """Populate dropdown options with categories from the current group."""
        try:
            # Get library data to find available categories
            library_data = await get_cached_library_data(self.user)
            categories = library_data.get('categories', [])
            
            # Get category IDs for this group
            category_ids = find_categories_for_group(categories, self.group)
            
            if not category_ids:
                self.options = [discord.SelectOption(
                    label="No categories found",
                    value="none",
                    description="No categories available for this group"
                )]
                return
            
            # Create options from categories
            options = []
            for cat_id in category_ids:
                # Find the category data to get the display name
                category_data = None
                for cat in categories:
                    if normalize_category_id(cat.get('id', '')) == cat_id:
                        category_data = cat
                        break
                
                if category_data:
                    cat_name = category_data.get('name', cat_id)
                    cat_description = f"View {cat_name} skills"
                    
                    # Truncate name and description to fit Discord limits
                    if len(cat_name) > 100:
                        cat_name = cat_name[:97] + "..."
                    if len(cat_description) > 100:
                        cat_description = cat_description[:97] + "..."
                    
                    # Mark current category
                    emoji = "📍" if normalize_category_id(self.current_category) == cat_id else "📂"
                    
                    options.append(discord.SelectOption(
                        label=cat_name,
                        value=cat_id,
                        description=cat_description,
                        emoji=emoji
                    ))
            
            # Sort options by group mapping order (logical progression) instead of alphabetically
            group_mapping = get_category_group_mapping()
            group_order = group_mapping.get(self.group, [])
            
            def get_sort_key(option):
                """Get sort key based on group mapping order."""
                try:
                    # Find the index in the group mapping
                    return group_order.index(option.value)
                except ValueError:
                    # If not found in mapping, put at end
                    return len(group_order)
            
            options.sort(key=get_sort_key)
            
            # Limit to Discord's 25 option maximum
            self.options = options[:25]
            
        except Exception as e:
            logger.error(f"Error populating category dropdown options: {e}")
            self.options = [discord.SelectOption(
                label="Error loading categories",
                value="error",
                description="Failed to load category list"
            )]
    
    async def callback(self, interaction: discord.Interaction):
        """Handle category selection and navigate to the chosen category."""
        # Check if this is the correct user
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ This is not for you.", ephemeral=True)
            return
        
        selected_category = self.values[0]
        
        # Handle special cases
        if selected_category in ["loading", "none", "error"]:
            await interaction.response.send_message("❌ Cannot navigate to this category.", ephemeral=True)
            return
        
        async def do_work():
            logger.info(f"CategorySelectionDropdown: Navigating to category {selected_category} in group {self.group}")
            
            # Get library data for unlockable skills check
            library_data = await get_cached_library_data(self.user)
            
            # Build embed and view for selected category
            embed = await build_skill_tree_embed(self.bot, self.user, category=selected_category, current_group=self.group)
            view = SkillTreeView(self.bot, self.user, current_group=self.group, current_category=selected_category)
            
            # Initialize the dropdown
            await view.initialize_dropdown()
            
            # Check if there are unlockable skills and update button
            has_unlockable = await check_has_unlockable_skills(self.user, selected_category, library_data)
            view.update_unlock_button(selected_category, has_unlockable)
            
            return embed, view
        
        await run_with_animation(interaction, do_work)

# --- ENHANCED RPG NAVIGATION BUTTONS ---

def get_category_position_info(categories: List[Dict], current_category: str, current_group: str) -> str:
    """Get position information for the current category within its group."""
    try:
        # Get categories for the current group
        group_categories = find_categories_for_group(categories, current_group)
        
        if not group_categories:
            return ""
        
        # Find current category position
        normalized_current = normalize_category_id(current_category)
        current_index = -1
        
        for i, cat_id in enumerate(group_categories):
            if normalize_category_id(cat_id) == normalized_current:
                current_index = i
                break
        
        if current_index >= 0:
            return f" ({current_index + 1}/{len(group_categories)})"
        else:
            return f" (1/{len(group_categories)})"  # Fallback
    except Exception as e:
        logger.warning(f"Error getting category position: {e}")
        return ""


def normalize_category_id(category_id: str) -> str:
    """Normalize category ID to handle different formats from the API."""
    if not category_id:
        return ""
    
    # Convert to uppercase and handle common variations
    normalized = str(category_id).upper().strip()
    
    # Handle numeric to string mapping (legacy database IDs)
    numeric_mapping = {
        "10": "PUSH",
        "11": "PULL", 
        "12": "SQUAT",
        "13": "HINGE",
        "14": "LUNGE",
        "15": "CORE",
        "16": "ROTATION",
        "17": "BALANCE",
        "18": "PULL_VERTICAL",
        "19": "UPPER_DYNAMIC",
        "20": "GRIP",
        "21": "BALLISTIC",
        "22": "GAIT",
        "23": "LOADED_CARRY",
        "24": "FLEXIBILITY",
        "25": "MOBILITY_FLOW"
    }
    
    if normalized in numeric_mapping:
        return numeric_mapping[normalized]
    
    return normalized

def get_category_group_mapping():
    """Get the mapping of category groups to their category IDs."""
    return {
        'upper': ['PUSH', 'PULL', 'PULL_VERTICAL', 'UPPER_DYNAMIC', 'GRIP', 'BALLISTIC'],
        'lower': ['SQUAT', 'LUNGE', 'HINGE', 'GAIT', 'LOADED_CARRY'],
        'core': ['CORE', 'ROTATION', 'BALANCE', 'FLEXIBILITY', 'MOBILITY_FLOW']
    }