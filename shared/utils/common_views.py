# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
import traceback
from typing import Union

from discord.ui import Select, View

# This import is no longer needed as we will pass the connection pool via the bot object.
# from utils.database.db import get_db
from shared.utils.panel_registry import get_panel_by_key, get_registered_panels
from shared.utils.headers import render_loading_embed

class EphemeralPanelSelect(Select):
    """
    A dropdown for switching between all registered panels.
    """
    def __init__(self, bot, user_id: int):
        self.bot = bot
        self.user_id = user_id
        
        excluded_panels = {"fitness_integration"}

        options = [
            discord.SelectOption(label=p.label, value=p.key, emoji=p.emoji)
            for p in get_registered_panels()
            if p.key not in excluded_panels
        ]
        super().__init__(
            placeholder="Switch Panel…",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"panel_switch:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if not interaction.user or interaction.user.id != self.user_id:
                await interaction.response.send_message("This menu isn't for you.", ephemeral=True)
                return

            key = self.values[0]
            if not isinstance(key, str):
                await interaction.response.send_message("Invalid panel key.", ephemeral=True)
                return
            panel_cls = get_panel_by_key(key)
            if panel_cls is None:
                await interaction.response.send_message("❌ Panel not found.", ephemeral=True)
                return

            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True)

            loading = True
            loading_task = asyncio.create_task(self.animate_loading(interaction))
            embed = None
            view = None
            try:
                embed = await asyncio.wait_for(panel_cls.render_embed(self.bot, interaction.user), timeout=15)
                view = await asyncio.wait_for(panel_cls.build_view(self.bot, interaction.user), timeout=15)
            except asyncio.TimeoutError:
                print(f"[ERROR] Panel render timed out for {key}")
                embed = discord.Embed(
                    title="⚠️ Panel Loading Timeout",
                    description=f"Panel `{key}` took too long to load. Please try again.",
                    color=0xff6b35
                )
                if interaction.user:
                    view = EphemeralPanelView(self.bot, interaction.user)  # Accepts both User and Member
            except Exception as render_error:
                print(f"[ERROR] Panel render failed for {key}: {render_error}")
                traceback.print_exc()
                embed = discord.Embed(
                    title="⚠️ Panel Loading Error",
                    description=f"Could not load `{key}` panel. Please try again.",
                    color=0xff6b35
                )
                if interaction.user:
                    view = EphemeralPanelView(self.bot, interaction.user)  # Accepts both User and Member
            finally:
                loading = False
                loading_task.cancel()
                try:
                    await loading_task
                except asyncio.CancelledError:
                    pass
                if embed and view:
                    await interaction.edit_original_response(embed=embed, view=view)

        except Exception as e:
            print(f"[ERROR] Unexpected error in EphemeralPanelSelect: {e}")
            traceback.print_exc()

    async def animate_loading(self, interaction: discord.Interaction):
        dots = 1
        while True:
            if not interaction.user:
                break
            loading_embed = render_loading_embed(interaction.user, dot_count=dots)
            try:
                await interaction.edit_original_response(embed=loading_embed, view=None)
            except (discord.NotFound, discord.InteractionResponded):
                break # Stop if the message is gone
            dots = dots % 3 + 1
            await asyncio.sleep(0.4)


class EphemeralPanelView(View):
    """
    A view that contains the EphemeralPanelSelect dropdown.
    """
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(EphemeralPanelSelect(self.bot, user.id))