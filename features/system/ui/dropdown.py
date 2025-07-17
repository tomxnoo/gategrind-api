# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from features.system.ui.view import render_hub_embed
from shared.utils.common_views import EphemeralPanelView

class SystemHubPublicDropdown(discord.ui.Select):
    def __init__(self, bot, user=None):
        self.bot = bot
        self.user = user
        options = [
            discord.SelectOption(label="Open System Hub", value="open_hub", emoji="😈"),
            discord.SelectOption(label="Reopen System Hub", value="reopen_hub", emoji="🔁"),
        ]
        custom_id = f"system_public:{user.id}" if user else "system_public"
        super().__init__(
            placeholder="Initialize Shadow Nexus…",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=custom_id
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user:
            await interaction.response.send_message("No user found for this interaction.", ephemeral=True)
            return

        if self.user and interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your menu.", ephemeral=True)
            return

        # Send ephemeral response directly instead of using run_with_animation
        try:
            embed = await render_hub_embed(self.bot, interaction.user)
            view = EphemeralPanelView(self.bot, interaction.user)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                "❌ Failed to open System Hub. Please try again.", 
                ephemeral=True
            )

class SystemHubPublicView(discord.ui.View):
    def __init__(self, bot, user=None):
        super().__init__(timeout=None)
        # Pass the bot instance down to the dropdown
        self.add_item(SystemHubPublicDropdown(bot, user))
