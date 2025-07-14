import asyncio
import discord
import sentry_sdk
from typing import Union, Callable
from shared.utils.headers import render_loading_embed

# DEFAULT UI TRANSITION DELAY: 0.35 seconds
# This is the standard delay used throughout the codebase for UI transitions
# to prevent loading animation race conditions and ensure smooth UI updates.
# Use this value or higher for any asyncio.sleep() calls in UI components.
DEFAULT_UI_DELAY = 0.35

async def create_loading_animation(interaction: discord.Interaction, user: Union[discord.User, discord.Member]):
    """Creates and returns a loading animation task that can be started and stopped."""
    loading = True
    
    async def animate_loading():
        dots = 1
        while loading:
            loading_embed = render_loading_embed(user, dot_count=dots)
            try:
                # Only update if still loading to prevent race conditions
                if loading:
                    await interaction.edit_original_response(embed=loading_embed, view=None)
            except Exception:
                pass
            dots = dots % 3 + 1
            # Check loading status before sleeping to exit faster
            if loading:
                await asyncio.sleep(DEFAULT_UI_DELAY)  # Use the standard delay
    
    task = asyncio.create_task(animate_loading())
    
    def stop_loading():
        nonlocal loading
        loading = False
    
    return task, stop_loading

import functools

def interaction_handler(ephemeral=True, with_loading=True):
    """Decorator for interaction handlers that adds standard defer, loading, and error handling."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            try:
                await interaction.response.defer(ephemeral=ephemeral)
            except Exception:
                pass
                
            if with_loading:
                loading_task, stop_loading = await create_loading_animation(interaction, self.user)
            
            try:
                result = await func(self, interaction, *args, **kwargs)
                if with_loading:
                    stop_loading()
                    # Wait for the loading task to finish
                    try:
                        await asyncio.wait_for(loading_task, timeout=1.0)
                    except asyncio.TimeoutError:
                        loading_task.cancel()
                return result
            except Exception as e:
                sentry_sdk.capture_exception(e)
                if with_loading:
                    stop_loading()
                    try:
                        await asyncio.wait_for(loading_task, timeout=1.0)
                    except asyncio.TimeoutError:
                        loading_task.cancel()
                await interaction.edit_original_response(
                    content=f"Error: {e}", embed=None, view=None
                )
                
        return wrapper
    return decorator