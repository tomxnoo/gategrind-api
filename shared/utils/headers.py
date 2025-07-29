# utils/headers.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Union

def get_system_status_header(user: Union[discord.User, discord.Member]) -> str:
    """
    Returns the status header with dynamic user name and static system info.
    """
    header = (
        "```ansi\n"
        "● Status: \x1b[1;32m● Online\x1b[0m\n"
        f"● User: {user.name} [LINKED]\n"
        "● System: SHADOW_NEXUS // v0.412\n"
        "──────────────────────────\n"
    )
    return header

def create_header_embed(title: str, description: str) -> discord.Embed:
    """
    Creates a Discord embed with the standard header format.
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x2f3136
    )
    return embed

# --- NEW: RPG/Terminal-style animated loading embed ---
def render_loading_embed(user: Union[discord.User, discord.Member], dot_count: int = 1) -> discord.Embed:
    """
    Returns a Discord embed with the universal header and an animated [ SYSTEM LOADING... ] line.
    dot_count cycles from 1 to 3 for animation.
    """
    header = get_system_status_header(user)  # No need to strip the ansi codeblock
    dots = '.' * dot_count
    desc = f"{header}[ SYSTEM LOADING{dots} ]\n───────────────────────────\n```"  # Wrap in ansi codeblock
    embed = discord.Embed(description=desc, color=discord.Color.dark_teal())
    return embed

def render_logging_in_embed(user: Union[discord.User, discord.Member], dot_count: int = 1) -> discord.Embed:
    """
    Returns a Discord embed with the universal header and an animated [ SYSTEM LOGGING IN... ] line.
    dot_count cycles from 1 to 3 for animation.
    Used specifically for the ephemeral menu login process.
    """
    header = get_system_status_header(user)  # No need to strip the ansi codeblock
    dots = '.' * dot_count
    desc = f"{header}[ SYSTEM LOGGING IN{dots} ]\n───────────────────────────\n```"  # Wrap in ansi codeblock
    embed = discord.Embed(description=desc, color=discord.Color.dark_teal())
    return embed