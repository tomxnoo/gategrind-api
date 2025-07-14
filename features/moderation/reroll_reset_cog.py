# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from discord.ui import Button, View, Select
from typing import Optional

from features.user.logic.user_data import load_user_data, save_user_data


class RerollResetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rr")
    @commands.is_owner()  # Only the bot owner can use this command
    async def reset_reroll(self, ctx, user: Optional[discord.User] = None):
        print(f"[DEBUG] reset_reroll called by {ctx.author.id} for user {user.id if user else ctx.author.id}")
        """Reset the daily reroll for yourself or another user (admin/test only)."""
        user_id = user.id if user else ctx.author.id
        from features.user.logic.user_data import load_user_data, save_user_data
        data = await load_user_data(user_id, bot=self.bot)
        print(f"[DEBUG] Loaded user data: {data}")
        if "daily_quests" in data and isinstance(data["daily_quests"], dict):
            import datetime
            now = datetime.datetime.utcnow()
            today = now.strftime("%Y-%m-%d")
            print(f"[DEBUG] System UTC now: {now.isoformat()} | Setting daily_quests['date'] to {today} and rerolled to None")
            data["daily_quests"]["date"] = today
            data["daily_quests"]["rerolled"] = None
            # Deactivate all quests
            quests = data["daily_quests"].get("quests", [])
            for quest in quests:
                quest["Active"] = False
                quest["active"] = False
            data["daily_quests"]["quests"] = quests
            await save_user_data(user_id, data, bot=self.bot)
            # Write-through: Invalidate cache after DB write
            from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
            await invalidate_user_json_cache(self.bot, user_id)
            await get_or_cache_user_json_data(self.bot, user_id)
            # Reload and print new date for confirmation
            new_data = await load_user_data(user_id, bot=self.bot)
            print(f"[DEBUG] After reset: daily_quests['date'] = {new_data.get('daily_quests', {}).get('date')}, rerolled = {new_data.get('daily_quests', {}).get('rerolled')}")
            await ctx.send(f"✅ Daily reroll reset for user {user_id}.")
            print(f"[DEBUG] Reroll reset for user {user_id}")
        else:
            await ctx.send("No daily quest data found for this user.")
            print(f"[DEBUG] No daily quest data found for user {user_id}")

async def setup(bot):
    await bot.add_cog(RerollResetCog(bot))
