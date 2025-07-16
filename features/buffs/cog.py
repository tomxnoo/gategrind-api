# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from core.api_client import api_client
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
        
        try:
            # Get buff inventory from API
            buff_data = await api_client.get_buff_inventory(user)
            
            # Get user profile for rendering
            user_profile = await api_client.get_user_profile(user)
            
            embed, _ = await render_buff_panel(user, user_profile, buff_data)
            view = create_buff_management_view(user.id)
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"[BUFF_COG] Error getting buff inventory: {e}")
            await ctx.send("❌ Failed to retrieve buff information. Please try again later.")

    @commands.command(name="testbuff")
    @commands.is_owner()
    async def test_buff(self, ctx: commands.Context, buff_id: str = None):
        """Test command to grant buffs (owner only)"""
        user = ctx.author
        
        try:
            if buff_id:
                # Apply specific buff
                result = await api_client.apply_buff(user, int(buff_id))
                if result.get("success"):
                    buff_info = result.get("buff", {})
                    await ctx.send(f"✅ Applied buff: {buff_info.get('name', 'Unknown')}")
                else:
                    await ctx.send(f"❌ Failed to apply buff: {result.get('error', 'Unknown error')}")
            else:
                # Grant random buff
                result = await api_client.grant_random_buff(user)
                if result.get("success"):
                    buff_info = result.get("buff", {})
                    rarity = result.get("rarity", "unknown")
                    await ctx.send(f"🎁 Granted random {rarity} buff: {buff_info.get('name', 'Unknown')}")
                else:
                    await ctx.send(f"❌ Failed to grant random buff: {result.get('error', 'Unknown error')}")
                    
        except Exception as e:
            print(f"[BUFF_COG] Error in test buff command: {e}")
            await ctx.send("❌ Failed to process buff command. Please try again later.")

    @commands.command(name="giveconsumable")
    @commands.is_owner()
    async def give_consumable(self, ctx: commands.Context, buff_id: str, quantity: int = 1):
        """Give consumable buffs to user (owner only)"""
        user = ctx.author
        
        try:
            result = await api_client.add_consumable_buff(user, int(buff_id), quantity)
            
            if result.get("success"):
                buff_info = result.get("buff", {})
                await ctx.send(f"✅ Added {quantity}x {buff_info.get('name', 'Unknown')} to inventory")
            else:
                await ctx.send(f"❌ Failed to add consumable: {result.get('error', 'Unknown error')}")
                
        except ValueError:
            await ctx.send("❌ Invalid buff ID. Please provide a numeric buff ID.")
        except Exception as e:
            print(f"[BUFF_COG] Error in give consumable command: {e}")
            await ctx.send("❌ Failed to add consumable buff. Please try again later.")


# For discord.py v2.x and above, use async setup and await add_cog
async def setup(bot):
    await bot.add_cog(BuffTracker(bot))
