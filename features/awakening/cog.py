import discord
from discord.ext import commands
import sentry_sdk
import logging

from core.api_client import APIClient
from features.awakening.ui.awakening_panel import EnhancedAwakeningPanel

logger = logging.getLogger(__name__)

class AwakeningCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="awakening")
    async def awakening(self, ctx: commands.Context):
        """
        Displays the user's daily awakening panel.
        """
        try:
            user = await APIClient.get_user(ctx.author.id)
            if not user:
                await ctx.send("User not found.", ephemeral=True)
                return

            embed = await EnhancedAwakeningPanel.render_embed(self.bot, user)
            view = EnhancedAwakeningPanel.build_view(self.bot, user)
            await ctx.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in awakening command: {e}", exc_info=True)
            sentry_sdk.capture_exception(e)
            await ctx.send("An unexpected error occurred while displaying the awakening panel.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AwakeningCog(bot))