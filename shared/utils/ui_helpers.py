import asyncio
import discord
import sentry_sdk
from typing import Union, Callable
from shared.utils.headers import render_loading_embed

async def create_loading_animation(interaction: discord.Interaction, user: Union[discord.User, discord.Member]):
    """Creates and returns a loading animation task that can be started and stopped."""
    loading = True
    
    async def animate_loading():
        dots = 1
        while loading:
            loading_embed = render_loading_embed(user, dot_count=dots)
            try:
                await interaction.edit_original_response(embed=loading_embed, view=None)
            except Exception:
                pass
            dots = dots % 3 + 1
            await asyncio.sleep(0.35)
    
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