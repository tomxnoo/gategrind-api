# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
from core.api_client import APIClient
from shared.utils.ui_styles import get_panel_icon, get_panel_sub_header
from shared.utils.headers import get_system_status_header

async def build_hub_embed(bot, user, show_header: bool = True):
    """Build the system hub embed with V2 API integration and universal header pattern"""
    
    # Get universal header and sub-header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("system_hub")
    
    try:
        api_client = APIClient()
        # Fetch V2 profile data (includes quests)
        profile = await asyncio.wait_for(api_client.get_user_profile_v2(user), timeout=10.0)
        
        if not profile:
            raise ValueError("No profile data received from V2 API")
        
        # Extract profile data
        username = profile.get('username', user.display_name)
        level = profile.get('level', 1)
        global_xp = profile.get('global_xp', 0)
        aura = profile.get('aura', 0)
        stats = profile.get('stats', {})
        active_quests = profile.get('active_quests', [])
        dungeon_progress = profile.get('dungeon_progress')
        unlocked_skills = profile.get('unlocked_skills', [])
        
        # Extract stats properly
        strength = stats.get('strength', {}).get('level', 1) if isinstance(stats.get('strength'), dict) else 1
        endurance = stats.get('endurance', {}).get('level', 1) if isinstance(stats.get('endurance'), dict) else 1
        technique = stats.get('technique', {}).get('level', 1) if isinstance(stats.get('technique'), dict) else 1
        
        # Extract quest data
        completed_today = len([q for q in active_quests if q.get('completed', False)])
        
        # Extract progression data
        unlocked_skills = profile.get('unlocked_skills', [])
        
        # Build the embed content with universal pattern (ANSI code block)
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;36m● System Hub Overview\x1b[0m\n"
            f"Operative: \x1b[1;33m{username}\x1b[0m\n"
            f"Rank: \x1b[1;37mLevel {level}\x1b[0m • XP: \x1b[1;33m{global_xp:,}\x1b[0m\n"
            f"Aura: \x1b[1;35m{aura}\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ Combat Statistics:\x1b[0m\n"
            f"├─ 🔴 Strength: Lv.\x1b[1;33m{strength}\x1b[0m\n"
            f"├─ 🔵 Endurance: Lv.\x1b[1;33m{endurance}\x1b[0m\n"
            f"└─ 🟡 Technique: Lv.\x1b[1;33m{technique}\x1b[0m\n\n"
            f"\x1b[1;37m🎯 Mission Status:\x1b[0m\n"
            f"├─ Active Quests: \x1b[1;33m{len(active_quests)}\x1b[0m\n"
            f"└─ Completed Today: \x1b[1;32m{completed_today}\x1b[0m\n\n"
        )
        
        # Add progression summary
        if dungeon_progress or unlocked_skills:
            content += f"\x1b[1;37m🌟 Progression Summary:\x1b[0m\n"
            
            if unlocked_skills:
                content += f"├─ Skills Unlocked: \x1b[1;33m{len(unlocked_skills)}\x1b[0m nodes\n"
            
            if dungeon_progress:
                current_tier = dungeon_progress.get('current_tier', 'Shadow')
                current_level = dungeon_progress.get('current_level', 0)
                content += f"└─ Dungeon Progress: \x1b[1;33m{current_tier}\x1b[0m (Lv.{current_level})\n"
            
            content += "\n"
        
        # System status
        content += (
            f"\x1b[1;37m🖥️ System Status:\x1b[0m\n"
            f"├─ Nexus: \x1b[1;32mONLINE\x1b[0m\n"
            f"└─ API Connection: \x1b[1;32mESTABLISHED (V2)\x1b[0m\n"
            f"──────────────────────────\n"
            f"```"
        )

        embed = discord.Embed(
            description=content,
            color=discord.Color.from_rgb(145, 70, 255)  # Purple theme matching other panels
        )
        embed.set_footer(text="Shadow Nexus • System Hub • V2 API")
        
    except (asyncio.TimeoutError, Exception) as e:
        # Fallback embed with universal header pattern
        content = (
            f"```ansi\n"
            f"{header}\n"
            f"{sub_header}\n\n"
            f"\x1b[1;31m● System Alert: Service Unreachable\x1b[0m\n"
            f"Operative: \x1b[1;33m{user.display_name}\x1b[0m\n"
            f"Rank: \x1b[1;30mLevel ???\x1b[0m • XP: \x1b[1;30m???\x1b[0m\n"
            f"Aura: \x1b[1;30m???\x1b[0m\n\n"
            f"\x1b[1;37m⚔️ Combat Statistics:\x1b[0m\n"
            f"├─ 🔴 Strength: \x1b[1;30mLv.???\x1b[0m\n"
            f"├─ 🔵 Endurance: \x1b[1;30mLv.???\x1b[0m\n"
            f"└─ 🟡 Technique: \x1b[1;30mLv.???\x1b[0m\n\n"
            f"\x1b[1;37m🎯 Mission Status:\x1b[0m\n"
            f"├─ Active Quests: \x1b[1;30m???\x1b[0m\n"
            f"└─ Completed Today: \x1b[1;30m???\x1b[0m\n\n"
            f"\x1b[1;37m🖥️ System Status:\x1b[0m\n"
            f"├─ Nexus: \x1b[1;31mDEGRADED\x1b[0m\n"
            f"└─ API Connection: \x1b[1;31mOFFLINE (V2)\x1b[0m\n\n"
            f"\x1b[1;33m\"Connection to the nexus has been severed...\"\x1b[0m\n"
            f"Error: \x1b[1;31m{str(e)[:50]}...\x1b[0m\n\n"
            f"\x1b[1;37m⚠️ System Alert\x1b[0m\n"
            f"Unable to retrieve data from V2 API. Please check system status.\n"
            f"──────────────────────────\n"
            f"```"
        )
        
        embed = discord.Embed(
            description=content,
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Nexus • System Hub • V2 API (Offline)")
    
    return embed

async def render_hub_embed(bot, user: discord.abc.User, show_header: bool = True) -> discord.Embed:
    """Use the centralized RPG embed logic with API integration"""
    return await build_hub_embed(bot, user, show_header=show_header)