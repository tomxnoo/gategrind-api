# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)

async def build_hub_embed(bot, user, show_header: bool = True):
    # Centralized RPG embed logic for system hub panel
    desc = f"[SYSTEM HUB]\n──────────────────────────\nUser: {user.display_name}\n\nWelcome to the Shadow Nexus.\n\nAccess your quests, profile, and more from here."
    embed = discord.Embed(
        title="🖥️ System Hub",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.dark_teal()
    )
    embed.set_footer(text="Shadow Archive • System Hub")
    return embed

async def render_hub_embed(bot, user: discord.abc.User, show_header: bool = True) -> discord.Embed:
    # Use the centralized RPG embed logic
    return await build_hub_embed(bot, user, show_header=show_header)