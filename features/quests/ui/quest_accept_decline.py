# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ui import View
from typing import Optional
import logging
import asyncio

class QuestAcceptDeclineView(View):
    def __init__(self, user_id: int, on_accept, on_decline, quest_type: str = "daily", quest_data=None, timeout: Optional[float] = None, bot=None):
        # quest_type: "daily" or "weekly"; quest_data: dict for quest/contract
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.on_accept = on_accept
        self.on_decline = on_decline
        self.quest_type = quest_type
        self.quest_data = quest_data
        self.bot = bot
        self.accept_button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.success, custom_id=f"{quest_type}_accept")
        self.accept_button.callback = self.accept
        self.add_item(self.accept_button)
        self.decline_button = discord.ui.Button(label="Decline", style=discord.ButtonStyle.danger, custom_id=f"{quest_type}_decline")
        self.decline_button.callback = self.decline
        self.add_item(self.decline_button)
        
        # Add quest action dropdown for abandon access
        if bot:
            from features.quests.ui.quest_dropdown import QuestActionDropdown
            self.add_item(QuestActionDropdown(bot, user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return bool(interaction.user) and interaction.user.id == self.user_id

    @interaction_handler(ephemeral=True, with_loading=True)
    async def accept(self, interaction: discord.Interaction):
        try:
            # Universal header/sub-header for accept panel
            from shared.utils.headers import get_system_status_header
            header = get_system_status_header(interaction.user) if interaction.user else ""
            sub_header = f"Accept {self.quest_type.capitalize()} {'Contract' if self.quest_type=='weekly' else 'Quest'}"
            embed = discord.Embed(
                title=f"Accept {self.quest_type.capitalize()} {'Contract' if self.quest_type=='weekly' else 'Quest'}",
                description=f"{header}\n{sub_header}\n\nAre you sure you want to accept this {self.quest_type}?",
                color=discord.Color.green() if self.quest_type == 'weekly' else discord.Color.blue()
            )
            embed.set_footer(text="Shadow Archive • Contract Database")
            await interaction.edit_original_response(embed=embed, view=self)
            await self.on_accept(interaction)
        except Exception as e:
            logging.exception("Error in accept handler:")
            raise e

    @interaction_handler(ephemeral=True, with_loading=True)
    async def decline(self, interaction: discord.Interaction):
        try:
            # Universal header/sub-header for decline panel
            from shared.utils.headers import get_system_status_header
            header = get_system_status_header(interaction.user) if interaction.user else ""
            sub_header = f"Decline {self.quest_type.capitalize()} {'Contract' if self.quest_type=='weekly' else 'Quest'}"
            embed = discord.Embed(
                title=f"Decline {self.quest_type.capitalize()} {'Contract' if self.quest_type=='weekly' else 'Quest'}",
                description=f"{header}\n{sub_header}\n\nAre you sure you want to decline this {self.quest_type}?",
                color=discord.Color.red()
            )
            embed.set_footer(text="Shadow Archive • Contract Database")
            await interaction.edit_original_response(embed=embed, view=self)
            await self.on_decline(interaction)
        except Exception as e:
            logging.exception("Error in decline handler:")
            raise e
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
        except Exception as inner_e:
            logging.exception("Failed to send error message in decline handler:")
        finally:
            self.stop()
