# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
import time
from features.system.ui.view import render_hub_embed
from shared.utils.common_views import EphemeralPanelView
from shared.utils.headers import render_logging_in_embed

# Removed optimized skill tree panel - enhanced features added to main skill tree

async def run_with_login_animation(interaction: discord.Interaction, work_coroutine):
    """
    Custom animation function that shows 'LOGGING IN...' instead of 'LOADING...'
    Used specifically for the ephemeral menu initialization.
    Creates a new ephemeral message instead of editing the original public message.
    """
    MIN_DURATION = 1.5  # Minimum seconds to show animation
    
    # Send initial ephemeral login message immediately
    login_embed = render_logging_in_embed(interaction.user, dot_count=1)
    login_message = await interaction.followup.send(embed=login_embed, ephemeral=True)
    
    # Start the work task
    work_task = asyncio.create_task(work_coroutine)
    
    # Initialize timing
    start_time = time.time()
    dots = 1

    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        if work_task.done() and elapsed >= MIN_DURATION:
            break

        try:
            login_embed = render_logging_in_embed(interaction.user, dot_count=dots)
            await login_message.edit(embed=login_embed)
            print(f"[DEBUG] Edited ephemeral login embed with {dots} dots at {elapsed:.2f} seconds")
        except Exception as e:
            print(f"[ERROR] Failed to update login animation: {e}")
            break
        
        # Update dots (1 -> 2 -> 3 -> 1)
        dots = dots % 3 + 1
        
        # Wait before next animation frame
        await asyncio.sleep(0.5)
    
    # Get the work result
    try:
        result = await work_task
        return result, login_message
    except Exception as e:
        print(f"[ERROR] Work task failed: {e}")
        raise

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

        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        # Create work coroutine that includes caching
        async def login_work():
            embed = await render_hub_embed(self.bot, interaction.user)
            view = EphemeralPanelView(self.bot, interaction.user)
            
            # Pre-cache skill tree data for faster loading when user switches to skill tree
            try:
                from features.skills.ui.skill_tree_panel import get_cached_library_data, get_cached_profile_data
                await get_cached_library_data(interaction.user)
                await get_cached_profile_data(interaction.user)
            except Exception as cache_error:
                # Don't fail the main operation if caching fails
                print(f"[DEBUG] Pre-caching failed: {cache_error}")
            
            return embed, view
        
        # Use custom login animation
        try:
            (embed, view), login_message = await run_with_login_animation(interaction, login_work())
            # Update the existing ephemeral login message with the final result
            await login_message.edit(embed=embed, view=view)
        except Exception as e:
            # Since we deferred, always use followup
            await interaction.followup.send(
                "❌ Failed to open System Hub. Please try again.", 
                ephemeral=True
            )

class SystemHubPublicView(discord.ui.View):
    def __init__(self, bot, user=None):
        super().__init__(timeout=None)
        # Pass the bot instance down to the dropdown
        self.add_item(SystemHubPublicDropdown(bot, user))
