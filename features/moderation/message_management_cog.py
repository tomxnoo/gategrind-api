# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands

class MessageManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx: commands.Context, amount: int = None):
        """Clear a specific number of messages from the channel."""
        
        if amount is None:
            await ctx.send("❌ Please specify the number of messages to clear. Usage: `!clear <amount>`", delete_after=5)
            return
        
        if amount <= 0:
            await ctx.send("❌ Amount must be a positive number.", delete_after=5)
            return
        
        if amount > 100:
            await ctx.send("❌ Cannot delete more than 100 messages at once due to Discord limits.", delete_after=5)
            return
        
        try:
            # Delete the command message first
            await ctx.message.delete()
            
            # Delete the specified number of messages
            deleted = await ctx.channel.purge(limit=amount)
            
            # Send confirmation message that will auto-delete
            confirmation = await ctx.send(f"🗑️ Successfully deleted {len(deleted)} messages.", delete_after=3)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages in this channel.", delete_after=5)
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to delete messages: {e}", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", delete_after=5)

    @clear_messages.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need the 'Manage Messages' permission to use this command.", delete_after=5)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please provide a valid number. Usage: `!clear <amount>`", delete_after=5)

async def setup(bot):
    await bot.add_cog(MessageManagement(bot))
