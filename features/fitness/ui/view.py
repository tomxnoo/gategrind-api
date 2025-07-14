# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import os
from typing import Union
from features.user.logic.user_data import load_user_data
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from shared.utils import ui_styles
from shared.utils.headers import get_system_status_header

async def build_fitness_integration_embed(bot, user, fitness_data):
    # Centralized RPG embed logic for fitness integration panel
    desc = f"[FITNESS INTEGRATION]\n──────────────────────────\nUser: {user.display_name}\n\n{fitness_data.get('summary', 'No fitness data available.')}\n\nKeep moving!"
    embed = discord.Embed(
        title="🏃 Fitness Integration",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Shadow Archive • Fitness Database")
    return embed

class FitnessIntegrationPanel:
    key   = "fitness_integration"
    label = "Link Accounts"
    emoji = "🔗"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        # Use the centralized RPG embed logic
        fitness_data = kwargs.get('fitness_data', {})
        return await build_fitness_integration_embed(bot, user, fitness_data)

    @staticmethod
    def build_view(bot, user: Union[discord.User, discord.Member]) -> discord.ui.View:
        view = EphemeralPanelView(bot, user)
        #view.add_item(GarminButton(user.id)) #remove
        #view.add_item(SyncAllFitnessButton(user.id)) #remove
        return view


register(FitnessIntegrationPanel)