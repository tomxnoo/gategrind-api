# cogs/system/system_hub.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
import asyncio

from features.system.ui.dropdown import SystemHubPublicView
from shared.utils.headers import render_loading_embed, get_system_status_header


class SystemHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hub")
    async def hub(self, ctx: commands.Context):
        print(f"[DEBUG] !hub command called by {ctx.author} in {ctx.channel}")
        user = ctx.author

        # --- UNIVERSAL PANEL STYLE ---
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        desc = (
            f"```ansi\n{header}\n[ SHADOW NEXUS MAINFRAME ]\n"
            "──────────────────────────────────────────────\n"
            "😈 Open System Hub    → Begin your journey\n"
            "🔁 Reopen System Hub  → Return to the nexus\n"
            "──────────────────────────────────────────────\n"
            '\"You place your hand upon the terminal.\"\n'
            "```"
        )
        embed = discord.Embed(
            description=desc,
            color=discord.Color.dark_teal()
        )
        embed.set_footer(text="Watcher Console Uplink • Stable")
        # Pass the bot instance to the view so it can be used for database operations
        view = SystemHubPublicView(bot=self.bot, user=None)
        try:
            message = await ctx.send(embed=embed, view=view)
            print(f"[DEBUG] Message sent successfully - Message ID: {message.id}")
        except Exception as e:
            print(f"[DEBUG] Error sending message: {e}")
        print(f"[DEBUG] !hub command completed")


async def setup(bot: commands.Bot):
    await bot.add_cog(SystemHub(bot))