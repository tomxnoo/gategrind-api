import asyncio
import discord
import sentry_sdk
from typing import Union, Callable, Coroutine, Any, Tuple
from shared.utils.headers import render_loading_embed

# DEFAULT UI TRANSITION DELAY: 0.35 seconds
# This is the standard delay used throughout the codebase for UI transitions
# to prevent loading animation race conditions and ensure smooth UI updates.
# Use this value or higher for any asyncio.sleep() calls in UI components.
DEFAULT_UI_DELAY = 0.35

# Animation speed for loading dots (how fast they cycle)
DEFAULT_ANIMATION_SPEED = 0.8

class LoadingState:
    """Coordinates loading animation with UI updates to prevent race conditions."""
    def __init__(self):
        self.ui_update_in_progress = False
        self.lock = asyncio.Lock()
        self.should_stop = False

# Global loading states per interaction ID
loading_states = {}

async def run_with_animation(
    interaction: discord.Interaction,
    work_coroutine: Coroutine[Any, Any, Tuple[discord.Embed, discord.ui.View]]
):
    """
    Handles a full interaction lifecycle with a safe, animated loading screen.
    
    This is the bulletproof animation pattern that eliminates race conditions
    by having a single task control both animation and work completion.
    
    Args:
        interaction: The discord interaction from the component.
        work_coroutine: The slow coroutine that returns the final (embed, view) tuple.
    """
    # Defer immediately if not already done
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=False)
    
    # Create a task for the actual work - starts running in background
    work_task = asyncio.create_task(work_coroutine)
    dots = 1
    
    # Loop and animate ONLY while the work task is still running
    while not work_task.done():
        loading_embed = render_loading_embed(interaction.user, dot_count=dots)
        try:
            await interaction.edit_original_response(embed=loading_embed, view=None)
        except discord.NotFound:
            # User dismissed the message, stop everything
            work_task.cancel()
            return
        except Exception:
            # Other errors, continue trying
            pass
        
        dots = dots % 3 + 1
        
        # Wait for animation speed, but check frequently if work is done
        try:
            await asyncio.wait_for(asyncio.shield(work_task), timeout=DEFAULT_ANIMATION_SPEED)
        except asyncio.TimeoutError:
            # Expected - work isn't done yet, continue animation
            pass
    
    # Work is complete! Get the result and display it
    try:
        final_embed, final_view = await work_task
        await interaction.edit_original_response(embed=final_embed, view=final_view)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        error_embed = discord.Embed(
            title="❌ Shadow Nexus Error",
            description="The shadows have encountered an unexpected disturbance.",
            color=discord.Color.red()
        )
        try:
            await interaction.edit_original_response(embed=error_embed, view=None)
        except discord.NotFound:
            pass  # Message was dismissed

# Legacy function for backward compatibility - will be phased out
async def create_loading_animation(interaction: discord.Interaction, user: Union[discord.User, discord.Member]):
    """Legacy function - use run_with_animation instead for new code."""
    # Implementation kept for existing code that hasn't been migrated yet
    pass

# Keep the interaction_handler decorator for other use cases
import functools

def interaction_handler(ephemeral=True, with_loading=True):
    """Decorator for interaction handlers that adds standard defer and error handling."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            try:
                await interaction.response.defer(ephemeral=ephemeral)
            except Exception:
                pass
            
            try:
                result = await func(self, interaction, *args, **kwargs)
                return result
            except Exception as e:
                sentry_sdk.capture_exception(e)
                await interaction.edit_original_response(
                    content=f"Error: {e}", embed=None, view=None
                )
        return wrapper
    return decorator