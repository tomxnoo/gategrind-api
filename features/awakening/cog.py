"""
Awakening System Cog
Handles awakening commands and panel registration
"""

import discord
from discord.ext import commands
from features.awakening.ui.awakening_panel import AwakeningPanel  # This import triggers the @register decorator

class AwakeningCog(commands.Cog):
    """Cog for the Awakening System"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="awakening", aliases=["awaken", "ritual"])
    async def awakening_panel(self, ctx: commands.Context):
        """Display the awakening panel"""
        user = ctx.author
        try:
            embed = await AwakeningPanel.render_embed(self.bot, user)
            view = await AwakeningPanel.build_view(self.bot, user)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            embed = discord.Embed(
                title="❌ AWAKENING ERROR",
                description=f"```\n{tb}\n```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    """Setup function to load the AwakeningCog"""
    await bot.add_cog(AwakeningCog(bot))