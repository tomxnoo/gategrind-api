import discord
from discord.ext import commands
from features.quests.ui.quest_panel import QuestPanel

class QuestPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quests")
    async def quest_panel(self, ctx: commands.Context):
        user = ctx.author
        try:
            embed = await QuestPanel.render_embed(self.bot, user)
            view = await QuestPanel.build_view(self.bot, user)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            embed = discord.Embed(
                title="❌ QUEST LOG ERROR",
                description=f"```\n{tb}\n```",
                color=discord.Color.red()
            )
            view = None
        if view is not None:
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(QuestPanelCog(bot))