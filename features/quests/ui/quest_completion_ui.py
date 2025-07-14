# ui/quest_completion_ui.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import random
from shared.utils.headers import get_system_status_header
import os
from typing import Union

# Flavor pool for quest completions
COMPLETION_FLAVOR_LINES = [
    "The pact is sealed. Shadows stir.",
    "You bow before no fate.",
    "A burden lifted, a soul sharpened.",
    "The ink dries. The contract ends.",
    "You are forged, not found.",
    "Ashes whisper your name.",
    "From shadow, resolve.",
    "Only ghosts remain behind your steps.",
    "You reap what others fear to sow.",
    "Not all who kneel are broken."
]

async def build_quest_completion_embed(bot, user: Union[discord.User, discord.Member], quest: dict) -> discord.Embed:
    """Build embed for quest completion notification"""
    quest_name = quest.get("QuestName") or quest.get("name") or "Unknown Quest"
    flavor = random.choice(COMPLETION_FLAVOR_LINES)
    
    embed = discord.Embed(
        title="✅ Quest Complete!",
        description=f"**{quest_name}**\n\n*{flavor}*",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Completed by {user.display_name}")
    return embed

def render_quest_completion_panel(quest: dict, user: Union[discord.User, discord.Member]) -> discord.Embed:
    """Render quest completion panel (sync version for compatibility)"""
    quest_name = quest.get("QuestName") or quest.get("name") or "Unknown Quest"
    flavor = random.choice(COMPLETION_FLAVOR_LINES)
    
    embed = discord.Embed(
        title="✅ Quest Complete!",
        description=f"**{quest_name}**\n\n*{flavor}*",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Completed by {user.display_name}")
    return embed
