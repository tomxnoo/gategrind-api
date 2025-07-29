# cogs/system/system_hub.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
import asyncio
import os
import sys

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

    @commands.command(name="restart", aliases=["reboot"])
    @commands.is_owner()  # Only bot owner can use this command
    async def restart_bot(self, ctx: commands.Context):
        """Restart the bot (Owner only)"""
        print(f"[ADMIN] Restart command called by {ctx.author} ({ctx.author.id})")
        
        # Delete the command message for cleaner chat
        try:
            await ctx.message.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        
        # Send confirmation embed
        embed = discord.Embed(
            title="🔄 System Restart Initiated",
            description=(
                "```ansi\n"
                "\u001b[1;31m[ SHADOW NEXUS MAINFRAME ]\u001b[0m\n"
                "──────────────────────────────────────────────\n"
                "\u001b[1;33m⚠️  SYSTEM RESTART IN PROGRESS\u001b[0m\n"
                "\u001b[0;37m• Closing database connections...\u001b[0m\n"
                "\u001b[0;37m• Terminating Redis cache...\u001b[0m\n"
                "\u001b[0;37m• Shutting down bot processes...\u001b[0m\n"
                "\u001b[0;37m• Restarting application...\u001b[0m\n"
                "──────────────────────────────────────────────\n"
                "\u001b[1;32mBot will be back online shortly.\u001b[0m\n"
                "```"
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="System Administrator • Restart Protocol")
        
        restart_message = await ctx.send(embed=embed)
        
        # Wait a moment for the message to send
        await asyncio.sleep(2)
        
        # Create restart signal file for the wrapper script
        import pathlib
        restart_signal = pathlib.Path("restart_signal")
        restart_signal.touch()
        
        print("[ADMIN] Initiating bot restart...")
        
        # Close database connections gracefully
        if hasattr(self.bot, 'db_pool') and self.bot.db_pool:
            try:
                await self.bot.db_pool.close()
                print("[ADMIN] Database pool closed")
            except Exception as e:
                print(f"[ADMIN] Error closing database pool: {e}")
        
        # Close Redis connections gracefully
        if hasattr(self.bot, 'redis') and self.bot.redis:
            try:
                await self.bot.redis.close()
                print("[ADMIN] Redis connection closed")
            except Exception as e:
                print(f"[ADMIN] Error closing Redis connection: {e}")
        
        # Close the bot
        await self.bot.close()
        
        # Exit the process - the wrapper will restart it
        print("[ADMIN] Exiting process for restart...")
        sys.exit(0)


async def setup(bot: commands.Bot):
    await bot.add_cog(SystemHub(bot))