import discord
from discord.ext import commands
from features.user.ui.profile_view import ProfilePanel  # This import triggers the @register decorator

class UserProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile_panel(self, ctx: commands.Context):
        """Display user profile panel"""
        user = ctx.author
        try:
            embed = await ProfilePanel.render_embed(self.bot, user)
            view = await ProfilePanel.build_view(self.bot, user)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            embed = discord.Embed(
                title="❌ PROFILE ERROR",
                description=f"```\n{tb}\n```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserProfile(bot))