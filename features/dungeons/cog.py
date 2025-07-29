"""
Dungeons Cog - Discord commands for the dungeon system.
"""
import discord
from discord.ext import commands
from discord import app_commands
from core.api_client import api_client
from features.dungeons.ui.dungeon_panel import DungeonPanel
from shared.utils.common_views import EphemeralPanelView
import asyncio

class DungeonsCog(commands.Cog):
    """Discord commands for the dungeon system."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="dungeon",
        description="Access the Shadow Dungeons"
    )
    async def dungeon(self, interaction: discord.Interaction):
        """Open the dungeon panel."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Build the dungeon panel
            panel = DungeonPanel()
            embed = await panel.render_embed(self.bot, interaction.user)
            view = await panel.build_view(self.bot, interaction.user)
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="⚠️ Dungeon System Error",
                description=f"Failed to access the dungeons: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    @app_commands.command(
        name="dungeon_info",
        description="Get information about the dungeon system"
    )
    async def dungeon_info(self, interaction: discord.Interaction):
        """Show information about dungeons."""
        info_embed = discord.Embed(
            title="🏰 Shadow Dungeons",
            description=(
                "**Welcome to the Shadow Dungeons!**\n\n"
                "Shadow Dungeons are infinite procedurally-generated challenges "
                "that test your combat prowess and strategic thinking.\n\n"
                "**Features:**\n"
                "• 🎯 Progressive difficulty scaling\n"
                "• 🗝️ Shadow Key economy system\n"
                "• 💀 Boss encounters every 5 levels\n"
                "• 🎁 Exclusive rewards and loot\n"
                "• 📊 Leaderboard competition\n\n"
                "**How to Play:**\n"
                "1. Use `/dungeon` to enter\n"
                "2. Complete trials to progress\n"
                "3. Defeat bosses for major rewards\n"
                "4. Use Shadow Keys to continue after failure\n\n"
                "Good luck, Shadow Walker!"
            ),
            color=discord.Color.dark_purple()
        )
        info_embed.set_footer(text="Shadow Dungeons • V2 System")
        
        await interaction.response.send_message(embed=info_embed, ephemeral=True)

async def setup(bot):
    """Setup function for Discord.py extension."""
    await bot.add_cog(DungeonsCog(bot))