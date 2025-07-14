# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from features.buffs.logic.engine import (
    get_active_buffs,
    grant_random_buff,
    use_consumable_buff,
    add_consumable_buff,
    BUFF_DEFINITIONS
)
from core.database import data_manager
from features.buffs.ui.view import render_buff_panel
# Import moved to method to avoid circular imports

class BuffTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="buffs")
    async def buff_panel(self, ctx: commands.Context):
        """Display user's active buffs and inventory"""
        from features.buffs.ui.management_view import create_buff_management_view
        user = ctx.author
        user_data = await data_manager.get_user_profile(self.bot, user.id)
        embed, _ = await render_buff_panel(user, user_data)
        view = create_buff_management_view(user.id)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="testbuff")
    @commands.is_owner()
    async def test_buff(self, ctx: commands.Context, buff_id: str):
        """Test command to grant buffs (owner only)"""
        user = ctx.author
        
        if buff_id and buff_id in BUFF_DEFINITIONS:
            from features.buffs.logic.engine import apply_buff
            result = await apply_buff(self.bot, user.id, buff_id)
            if result["success"]:
                await ctx.send(f"✅ Applied buff: {result['buff']['name']}")
            else:
                await ctx.send(f"❌ Failed to apply buff: {result.get('error', 'Unknown error')}")
        else:
            # Grant random buff
            result = grant_random_buff(user.id)
            if result:
                await ctx.send(f"🎁 Granted random {result['rarity']} buff: {result['buff']['name']}")
            else:
                await ctx.send("❌ Failed to grant random buff")

    @commands.command(name="giveconsumable")
    @commands.is_owner()
    async def give_consumable(self, ctx: commands.Context, buff_id: str, quantity: int = 1):
        """Give consumable buffs to user (owner only)"""
        user = ctx.author
        
        if await add_consumable_buff(user.id, buff_id, quantity):
            buff_def = BUFF_DEFINITIONS.get(buff_id, {})
            await ctx.send(f"✅ Added {quantity}x {buff_def.get('name', buff_id)} to inventory")
        else:
            await ctx.send(f"❌ Invalid consumable buff ID: {buff_id}")


# For discord.py v2.x and above, use async setup and await add_cog
async def setup(bot):
    await bot.add_cog(BuffTracker(bot))
