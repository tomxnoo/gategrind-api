# Adding anime icon to level up embeds
# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import os
from typing import Optional

async def send_embed_with_icon(interaction: discord.Interaction, embed: discord.Embed, ephemeral: bool = True):
    """Send an embed (no icon attachment support)"""
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

def create_enhanced_embed(title: str, description: str, color: discord.Color, icon_theme: Optional[str] = None) -> discord.Embed:
    """Create an embed (no icon attachment support)"""
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

def create_level_up_embed(user: discord.User, old_level: int, new_level: int, new_title: Optional[str] = None) -> discord.Embed:
    """Create a level up notification embed"""
    from shared.utils.visual_assets import get_level_up_icon

    title = "🎉 LEVEL UP!"
    description = f"**{user.display_name}** has reached **Level {new_level}**!"

    if new_title:
        description += f"\n🏆 New Title: **{new_title}**"

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.gold()
    )

    # Use anime icon for level up
    try:
        icon_url = get_level_up_icon()
        embed.set_thumbnail(url=icon_url)
    except:
        # Fallback to user avatar
        embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(name="Previous Level", value=f"Level {old_level}", inline=True)
    embed.add_field(name="Current Level", value=f"Level {new_level}", inline=True)

    return embed

def create_quest_completion_embed(user: discord.User, quest_name: str, xp_reward: int, bonus_info: Optional[str] = None) -> discord.Embed:
    """Create a quest completion notification embed"""
    from shared.utils.visual_assets import get_quest_icon

    title = "✅ QUEST COMPLETED!"
    description = f"**{user.display_name}** completed: **{quest_name}**"

    if bonus_info:
        description += f"\n{bonus_info}"

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )

    # Use anime icon for quest completion
    try:
        icon_url = get_quest_icon()
        embed.set_thumbnail(url=icon_url)
    except:
        # Fallback to user avatar
        embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(name="XP Reward", value=f"+{xp_reward} XP", inline=True)

    return embed

def set_anime_thumbnail(embed: discord.Embed, anime_name: str):
    """Set anime thumbnail on an embed"""
    try:
        from shared.utils.visual_assets import get_anime_icon_url
        icon_url = get_anime_icon_url(anime_name)
        if icon_url:  # Only set if URL is valid
            # Convert to full URL
            full_url = f"http://0.0.0.0:8080{icon_url}"
            embed.set_thumbnail(url=full_url)
    except Exception as e:
        print(f"Failed to set anime thumbnail: {e}")
        pass