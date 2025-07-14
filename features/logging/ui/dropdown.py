# views/log_dropdown.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ui import Select, View

from features.user.logic.xp_engine import MOVEMENT_DATA
from shared.utils.common_views import EphemeralPanelSelect
from shared.utils.headers import render_loading_embed
import asyncio

# Modal for logging reps
class LogModal(discord.ui.Modal):
    def __init__(self, movement, user_id):
        super().__init__(title="Log Reps")
        self.movement = movement
        self.user_id = user_id

        self.reps = discord.ui.TextInput(
            label=f"How many {movement} reps?",
            placeholder="Enter number...",
            required=True,
            min_length=1,
            max_length=5,
        )
        self.add_item(self.reps)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            reps = int(self.reps.value)
        except Exception:
            return await interaction.response.send_message(
                "Please enter a valid number.", ephemeral=True
            )
        # Defer and let the MovementLogger cog handle the loading UI and response
        await interaction.response.defer(ephemeral=True)
        bot = interaction.client
        bot.dispatch("log_reps", interaction, self.movement, reps)
        # Do not send another response or run a loading animation here; the cog will handle it.

# Dropdown for selecting movement to log
class LogMovementDropdown(Select):
    def __init__(self, user_id: int):
        self.user_id = user_id

        # Organize movements by tier for better UX
        options = []
        
        # Add Tier I-II movements first
        for move, info in MOVEMENT_DATA.items():
            if info["tier"] <= 2:
                options.append(discord.SelectOption(
                    label=f"{move} (Tier {info['tier']})", 
                    value=move,
                    description=f"{info['xp']} XP per rep"
                ))
        
        # Add Tier III-IV movements
        for move, info in MOVEMENT_DATA.items():
            if info["tier"] >= 3:
                options.append(discord.SelectOption(
                    label=f"{move} (Tier {info['tier']})", 
                    value=move,
                    description=f"{info['xp']} XP per rep"
                ))

        super().__init__(
            placeholder="Select movement to log…",
            min_values=1,
            max_values=1,
            options=options,
            # Remove custom_id to avoid conflicts
            # custom_id=f"log_movement:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message(
                    "This menu isn't for you.", ephemeral=True
                )

            movement = self.values[0]
            modal = LogModal(movement, self.user_id)
            await interaction.response.send_modal(modal)
            
        except discord.InteractionResponded:
            # Interaction was already responded to
            pass
        except discord.NotFound:
            # Interaction token expired
            await interaction.followup.send(
                "❌ This interaction has expired. Please try again.", ephemeral=True
            )
        except Exception as e:
            print(f"[ERROR] LogMovementDropdown callback failed: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Failed to open movement logging modal. Please try again.", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Failed to open movement logging modal. Please try again.", ephemeral=True
                )

# View for Log Panel (dropdown + switcher)
class LogMovementView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.add_item(LogMovementDropdown(user_id))
        self.add_item(EphemeralPanelSelect(user_id))
