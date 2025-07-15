# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from typing import Optional

from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.incursion_scheduler import IncursionScheduler
from features.incursions.ui.incursion_panel import IncursionPanel
from shared.utils.ui_helpers import run_with_animation

class IncursionsCog(commands.Cog):
    """Shadow Incursions - Dynamic world events for fitness challenges"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = IncursionManager(bot.db_pool)
        self.scheduler = IncursionScheduler(bot.db_pool)
    
    @discord.slash_command(
        name="incursions",
        description="View active Shadow Incursions and participate in dynamic events"
    )
    async def incursions_command(self, ctx: discord.ApplicationContext):
        """Main command to access the Shadow Incursions panel"""
        
        async def do_work():
            embed = await IncursionPanel.render_embed(self.bot, ctx.author)
            view = await IncursionPanel.build_view(self.bot, ctx.author)
            return embed, view
        
        await run_with_animation(ctx.interaction, do_work())
    
    @discord.slash_command(
        name="incursion_admin",
        description="Admin commands for managing Shadow Incursions"
    )
    @commands.has_permissions(administrator=True)
    async def incursion_admin(self, ctx: discord.ApplicationContext, 
                            action: discord.Option(str, choices=["spawn", "cleanup", "status"]),
                            incursion_type: discord.Option(str, choices=["surge", "challenge", "anomaly"], required=False)):
        """Admin commands for incursion management"""
        
        if action == "spawn":
            if not incursion_type:
                await ctx.respond("❌ Please specify an incursion type for spawning.", ephemeral=True)
                return
            
            success = await self.scheduler.spawn_incursion(incursion_type)
            if success:
                await ctx.respond(f"✅ {incursion_type.title()} incursion spawned successfully!", ephemeral=True)
            else:
                await ctx.respond(f"❌ Failed to spawn {incursion_type} incursion.", ephemeral=True)
        
        elif action == "cleanup":
            cleaned = await self.scheduler.cleanup_expired_incursions()
            await ctx.respond(f"🧹 Cleaned up {cleaned} expired incursions.", ephemeral=True)
        
        elif action == "status":
            active_count = len(await self.manager.get_active_incursions())
            await ctx.respond(f"📊 Currently {active_count} active incursions.", ephemeral=True)

def setup(bot):
    bot.add_cog(IncursionsCog(bot))
    
    # Register the panel
    from features.incursions.ui.panel_registration import *