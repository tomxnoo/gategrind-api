# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
import traceback

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_msg = f"❌ Error in command `{ctx.command}`: {error}"
        print(error_msg)
        traceback.print_exception(type(error), error, error.__traceback__)

        try:
            await ctx.send("⚠️ An unexpected error occurred. Check logs or contact The Watcher.", ephemeral=True)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        print(f"❌ Global error in `{event_method}`")
        traceback.print_exc()


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))