# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from core.config import BUFF_DEFINITIONS
from features.buffs.ui.view import build_buff_details_embed
from shared.utils.ui_helpers import run_with_animation

# --- Local BackButton for returning to previous view (no global BackButton found) ---
class BackButton(discord.ui.Button):
    def __init__(self, previous_view: discord.ui.View):
        super().__init__(label="⬅️ Back", style=discord.ButtonStyle.secondary)
        self.previous_view = previous_view

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user:
            await interaction.response.send_message("No user found for this interaction.", ephemeral=True)
            return
        
        async def do_work():
            if self.previous_view:
                # Return the previous view to be displayed
                return None, self.previous_view
            else:
                # Return a message indicating no previous view
                embed = discord.Embed(
                    title="❌ Error",
                    description="No previous view to return to.",
                    color=discord.Color.red()
                )
                return embed, None
        
        await run_with_animation(interaction, do_work)

class BuffDetailsView(discord.ui.View):
    """A view to show the details of a specific buff and a back button."""
    def __init__(self, bot, original_interaction: discord.Interaction, buff_id: int, previous_view: discord.ui.View):
        super().__init__(timeout=180)
        self.bot = bot
        self.original_interaction = original_interaction
        self.buff_id = buff_id
        self.previous_view = previous_view
        self.add_item(BackButton(self.previous_view))

async def show_buff_details(interaction: discord.Interaction, bot, buff_id: int, previous_view: discord.ui.View):
    if not interaction.user:
        await interaction.response.send_message("No user found for this interaction.", ephemeral=True)
        return
    # Fetch buff details from BUFF_DEFINITIONS, not the DB
    buff = BUFF_DEFINITIONS.get(str(buff_id))
    if not buff:
        await interaction.response.send_message("Could not find details for this buff.", ephemeral=True)
        return
    embed = await build_buff_details_embed(bot, interaction.user, buff)
    await interaction.response.send_message(embed=embed, view=BuffDetailsView(bot, interaction, buff_id, previous_view), ephemeral=True)