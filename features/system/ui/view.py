# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from core.api_client import api_client

async def build_hub_embed(bot, user, show_header: bool = True):
    """Build system hub embed using API data"""
    try:
        # Get user profile from API
        user_data = await api_client.get_user_profile(user)
        
        # Get daily quests from API
        quests_data = await api_client.get_daily_quests(user)
        
        # CRITICAL FIX: Handle both list and dict responses
        if isinstance(quests_data, list):
            daily_quests = quests_data
        else:
            daily_quests = quests_data.get("quests", [])
        
        # Build enhanced description with real data
        level = user_data.get("level", 1)
        xp = user_data.get("xp", 0)
        xp_max = user_data.get("xp_max", 100)
        username = user_data.get("username", user.display_name)
        
        # Count active quests
        active_quests = len([q for q in daily_quests if q.get("status") == "active"])
        completed_quests = len([q for q in daily_quests if q.get("status") == "completed"])
        
        desc = (
            f"[ SHADOW NEXUS MAINFRAME ]\n"
            f"──────────────────────────────────────────────\n"
            f"🎭 Operative: {username}\n"
            f"⚡ Level {level} • {xp}/{xp_max} XP\n"
            f"🎯 Active Quests: {active_quests}\n"
            f"✅ Completed Today: {completed_quests}\n"
            f"──────────────────────────────────────────────\n"
            f"🖥️ System Status: ONLINE\n"
            f"🔗 API Connection: ESTABLISHED\n"
            f"──────────────────────────────────────────────\n"
            f'"The nexus responds to your presence..."\n'
        )
        
        embed = discord.Embed(
            title="🖥️ System Hub",
            description=f"```ansi\n{desc}\n```",
            color=discord.Color.dark_teal()
        )
        
        # Add stats as fields
        stats = user_data.get("stats", {})
        if stats:
            stats_text = ""
            for stat_name, stat_data in stats.items():
                stat_level = stat_data.get("level", 1)
                stat_xp = stat_data.get("xp", 0)
                stat_xp_max = stat_data.get("xp_max", 100)
                stats_text += f"{stat_name}: Lv.{stat_level} ({stat_xp}/{stat_xp_max})\n"
            
            embed.add_field(
                name="📊 Combat Statistics",
                value=f"```\n{stats_text}```",
                inline=True
            )
        
        # Add active buffs if any
        active_buffs = user_data.get("active_buffs", {})
        if active_buffs:
            buffs_text = ""
            for buff_name, buff_data in active_buffs.items():
                buffs_text += f"• {buff_data.get('name', buff_name)}\n"
            
            embed.add_field(
                name="✨ Active Buffs",
                value=buffs_text,
                inline=True
            )
        
        embed.set_footer(text="Shadow Archive • System Hub • API-Powered")
        
    except Exception as e:
        print(f"[SYSTEM_HUB] Error fetching API data: {e}")
        # Fallback to basic embed
        desc = (
            f"[ SHADOW NEXUS MAINFRAME ]\n"
            f"──────────────────────────────────────────────\n"
            f"🎭 Operative: {user.display_name}\n"
            f"⚠️ API Connection: OFFLINE\n"
            f"──────────────────────────────────────────────\n"
            f'"Connecting to the nexus..."\n'
        )
        embed = discord.Embed(
            title="🖥️ System Hub",
            description=f"```ansi\n{desc}\n```",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Shadow Archive • System Hub • Offline Mode")
    
    return embed

async def render_hub_embed(bot, user: discord.abc.User, show_header: bool = True) -> discord.Embed:
    """Use the centralized RPG embed logic with API integration"""
    return await build_hub_embed(bot, user, show_header=show_header)