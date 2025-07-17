"""
Quests System Cog
Handles quest commands and panel registration
"""

import discord
from discord.ext import commands

class QuestsCog(commands.Cog):
    """Cog for the Quests System"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quests", aliases=["quest", "q"])
    async def quests_panel(self, ctx: commands.Context):
        """Display the quests panel"""
        embed = discord.Embed(
            title="🎯 Quest System",
            description="Quest system is under development. Please use the System Hub for quest access.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function to load the QuestsCog"""
    await bot.add_cog(QuestsCog(bot))