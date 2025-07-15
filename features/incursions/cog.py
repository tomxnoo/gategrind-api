# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from typing import Optional, List  # Added List import

from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.scheduler import IncursionScheduler
from features.incursions.ui.incursion_panel import IncursionPanel  # This import triggers @register
from shared.utils.ui_helpers import run_with_animation

class IncursionsCog(commands.Cog):
    """Shadow Incursions - Dynamic world events for fitness challenges"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = IncursionManager(bot)
        self.scheduler = IncursionScheduler(bot)  # Changed from bot.db_pool to bot

    @commands.command(name="incursions", aliases=["inc"])
    async def view_incursions(self, ctx: commands.Context):
        """View active Shadow Incursions"""
        user = ctx.author
        try:
            embed = await IncursionPanel.render_embed(self.bot, user)
            view = await IncursionPanel.build_view(self.bot, user)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            embed = discord.Embed(
                title="❌ INCURSION ERROR",
                description=f"```\n{tb}\n```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="incursion_admin", aliases=["inc_admin"])
    @commands.is_owner()  # Only bot owner can use this command
    async def incursion_admin(self, ctx: commands.Context, action: Optional[str] = None):
        """Admin commands for managing incursions. Usage: !incursion_admin [start|stop|status]"""
        # Delete the user's command message for cleaner chat
        try:
            await ctx.message.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        
        if not action:
            embed = discord.Embed(
                title="🔧 Incursion Admin Commands",
                description="Available actions:\n• `!incursion_admin start` - Start a new incursion\n• `!incursion_admin stop` - Stop current incursion\n• `!incursion_admin status` - Check incursion status",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed, delete_after=10)
            return
        
        action = action.lower()
        
        if action == "start":
            # Start a new incursion using the scheduler's force_spawn_incursion method
            try:
                incursion_id = await self.scheduler.force_spawn_incursion()
                if incursion_id:
                    embed = discord.Embed(
                        title="✅ Incursion Started",
                        description=f"A new Shadow Incursion has been initiated! (ID: {incursion_id})",
                        color=discord.Color.green()
                    )
                else:
                    embed = discord.Embed(
                        title="⚠️ Incursion Not Started",
                        description="Could not start a new incursion.",
                        color=discord.Color.orange()
                    )
                await ctx.send(embed=embed, delete_after=10)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error Starting Incursion",
                    description=f"Error: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
        
        elif action == "stop":
            # Stop current incursion by getting active incursions and completing them
            try:
                active_incursions = await self.manager.get_active_incursions()
                if active_incursions:
                    # Complete the first active incursion
                    result = await self.manager.complete_incursion(active_incursions[0].incursion_id)
                    if result:
                        embed = discord.Embed(
                            title="✅ Incursion Stopped",
                            description=f"The incursion '{active_incursions[0].title}' has been ended.",
                            color=discord.Color.green()
                        )
                    else:
                        embed = discord.Embed(
                            title="⚠️ Error Stopping Incursion",
                            description="Could not stop the incursion.",
                            color=discord.Color.orange()
                        )
                else:
                    embed = discord.Embed(
                        title="⚠️ No Active Incursion",
                        description="There is no active incursion to stop.",
                        color=discord.Color.orange()
                    )
                await ctx.send(embed=embed, delete_after=10)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error Stopping Incursion",
                    description=f"Error: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
        
        elif action == "status":
            # Check incursion status
            try:
                active_incursions = await self.manager.get_active_incursions()
                if active_incursions:
                    incursion = active_incursions[0]  # Show first active incursion
                    embed = discord.Embed(
                        title="📊 Incursion Status",
                        description=f"**Active Incursion:** {incursion.title}\n**Type:** {incursion.incursion_type.value}\n**Progress:** {incursion.current_reps}/{incursion.target_reps}\n**Expires:** <t:{int(incursion.expires_at.timestamp())}:R>",
                        color=discord.Color.blue()
                    )
                else:
                    embed = discord.Embed(
                        title="📊 Incursion Status",
                        description="No active incursions.",
                        color=discord.Color.blue()
                    )
                await ctx.send(embed=embed, delete_after=15)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error Checking Status",
                    description=f"Error: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
        
        else:
            embed = discord.Embed(
                title="❌ Invalid Action",
                description="Valid actions: start, stop, status",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)

    # Remove these problematic subcommand decorators:
    # @incursion_admin.command(name="testing")  # DELETE THIS LINE
    @commands.command(name="incursion_testing")  # Change to regular command
    @commands.is_owner()
    async def toggle_testing_mode(self, ctx, mode: str = None):
        """Toggle testing mode on/off"""
        if mode is None:
            # Show current status
            status = "enabled" if self.scheduler.testing_mode else "disabled"
            await ctx.send(f"Testing mode is currently **{status}**")
            return
        
        mode = mode.lower()
        if mode in ["on", "enable", "true", "1"]:
            self.scheduler.set_testing_mode(True)
            await ctx.send("✅ Testing mode **enabled**\n- 1 minute spawn intervals\n- 100% spawn chance\n- 45 second incursion duration")
        elif mode in ["off", "disable", "false", "0"]:
            self.scheduler.set_testing_mode(False)
            await ctx.send("✅ Testing mode **disabled**\n- 2-3 minute spawn intervals\n- 2-3% spawn chance\n- 30 minutes to 3 hours duration")
        else:
            await ctx.send("❌ Invalid mode. Use: `on`, `off`, `enable`, `disable`, `true`, or `false`")
    
    # @incursion_admin.command(name="status")  # DELETE THIS LINE  
    @commands.command(name="incursion_status")  # Change to regular command
    @commands.is_owner()
    async def scheduler_status(self, ctx):
        """Show detailed scheduler status"""
        status = "Running" if self.scheduler.is_running else "Stopped"
        testing = "Enabled" if self.scheduler.testing_mode else "Disabled"
        
        active_incursions = await self.manager.get_active_incursions()
        
        embed = discord.Embed(
            title="🌑 Incursion Scheduler Status",
            color=0x4B0082
        )
        
        embed.add_field(
            name="Scheduler",
            value=f"**Status:** {status}\n**Testing Mode:** {testing}",
            inline=True
        )
        
        if self.scheduler.testing_mode:
            embed.add_field(
                name="Testing Settings",
                value="**Interval:** 1 minute\n**Spawn Chance:** 100%\n**Duration:** 45 seconds",
                inline=True
            )
        else:
            embed.add_field(
                name="Production Settings",
                value="**Interval:** 2-3 minutes\n**Spawn Chance:** 2-3%\n**Duration:** 30min-3hrs",
                inline=True
            )
        
        embed.add_field(
            name="Active Incursions",
            value=f"{len(active_incursions)} currently active",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(IncursionsCog(bot))
    # Panel registration is handled by the IncursionPanel import above