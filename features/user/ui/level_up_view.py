# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Dict, Optional
from features.user.logic.class_evolution import get_class_for_level, get_next_evolution
from shared.utils.headers import get_system_status_header

async def build_level_up_embed(bot, user: discord.abc.User, new_level: int, evolution: Optional[Dict] = None) -> discord.Embed:
    # Centralized RPG embed logic for level up panel
    title = f"🎉 Level Up!"
    description = f"Congratulations, {user.display_name}!\n\nYou reached Level {new_level}."
    color = discord.Color.gold()
    if evolution:
        description += f"\n\n🦋 Evolution: {evolution.get('name', 'Unknown')}\n{evolution.get('description', '')}"
        color = discord.Color.purple()
    embed = discord.Embed(title=title, description=f"```ansi\n{description}\n```", color=color)
    embed.set_footer(text="Shadow Archive • Level Database")
    return embed

async def render_level_up_embed(bot, user: discord.abc.User, new_level: int, evolution: Optional[Dict] = None) -> discord.Embed:
    # Use the centralized RPG embed logic
    return await build_level_up_embed(bot, user, new_level, evolution)