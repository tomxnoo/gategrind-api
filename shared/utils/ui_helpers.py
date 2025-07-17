import asyncio
import discord
import sentry_sdk
import time  # Add this import for time tracking
from typing import Union, Callable, Coroutine, Any, Tuple
from shared.utils.headers import render_loading_embed

# DEFAULT UI TRANSITION DELAY: 0.35 seconds
# This is the standard delay used throughout the codebase for UI transitions
# to prevent loading animation race conditions and ensure smooth UI updates.
# Use this value or higher for any asyncio.sleep() calls in UI components.
DEFAULT_UI_DELAY = 0.35

# Animation speed for loading dots (how fast they cycle)
DEFAULT_ANIMATION_SPEED = 0.35  

class LoadingState:
    """Coordinates loading animation with UI updates to prevent race conditions."""
    def __init__(self):
        self.ui_update_in_progress = False
        self.lock = asyncio.Lock()
        self.should_stop = False

# Global loading states per interaction ID
loading_states = {}

# Add this constant
MIN_DURATION = 1.5  # Minimum seconds to show loading animation, increased for testing

async def run_with_animation(
    interaction: discord.Interaction,
    work_function_or_coroutine,
    ephemeral: bool = False
):
    """
    Handles a full interaction lifecycle with a safe, animated loading screen.
    
    This function supports both calling patterns for backward compatibility:
    1. run_with_animation(interaction, async_function) - function will be called
    2. run_with_animation(interaction, coroutine_object) - coroutine will be awaited
    
    Args:
        interaction: The discord interaction from the component.
        work_function_or_coroutine: Either an async function or a coroutine object that returns (embed, view) tuple.
        ephemeral: Whether the response should be ephemeral (for backward compatibility).
    """
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("function", "run_with_animation")
        scope.set_context("interaction", {
            "user_id": interaction.user.id,
            "guild_id": interaction.guild_id if interaction.guild else None,
            "channel_id": interaction.channel_id,
            "command": getattr(interaction.command, 'name', 'unknown') if hasattr(interaction, 'command') else 'unknown'
        })
        
        sentry_sdk.add_breadcrumb(
            message="Starting run_with_animation",
            level="info",
            data={
                "work_type": "callable" if callable(work_function_or_coroutine) else "coroutine",
                "ephemeral": ephemeral,
                "response_done": interaction.response.is_done()
            }
        )
    
    # Dynamically determine ephemeral status
    is_ephemeral = ephemeral
    if interaction.message and interaction.message.flags.ephemeral:
        is_ephemeral = True

    # Defer immediately if not already done
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(ephemeral=is_ephemeral)
            await asyncio.sleep(DEFAULT_UI_DELAY)  # Add delay to prevent race condition
            sentry_sdk.add_breadcrumb(message="Successfully deferred interaction with delay", level="info")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.add_breadcrumb(message=f"Failed to defer interaction: {e}", level="error")
            return
    else:
        sentry_sdk.add_breadcrumb(message="Interaction already deferred", level="info")
    
    # Handle both callable functions and coroutine objects
    try:
        if callable(work_function_or_coroutine):
            # Old pattern: function passed, we need to call it
            sentry_sdk.add_breadcrumb(message="Calling work function", level="info")
            work_coroutine = work_function_or_coroutine()
        else:
            # New pattern: coroutine object passed directly
            sentry_sdk.add_breadcrumb(message="Using work coroutine directly", level="info")
            work_coroutine = work_function_or_coroutine
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.add_breadcrumb(message=f"Failed to prepare work coroutine: {e}", level="error")
        return
    
    try:
        work_task = asyncio.create_task(work_coroutine)
        sentry_sdk.add_breadcrumb(message="Created work task", level="info")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.add_breadcrumb(message=f"Failed to create work task: {e}", level="error")
        return
    
    # Initialize timing
    start_time = time.time()
    dots = 1

    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        if work_task.done() and elapsed >= MIN_DURATION:
            break

        try:
            loading_embed = render_loading_embed(interaction.user, dot_count=dots)
            sentry_sdk.add_breadcrumb(message="Rendered loading embed", level="debug")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            sentry_sdk.add_breadcrumb(message=f"Failed to render loading embed: {e}", level="error")
            break
        
        try:
            await interaction.edit_original_response(content="\u200b", embed=loading_embed, view=None)
            sentry_sdk.add_breadcrumb(message="Updated interaction with loading embed", level="debug")
            print(f"[DEBUG] Edited loading embed with {dots} dots at {elapsed:.2f} seconds")  # Added debug print
        except discord.NotFound:
            sentry_sdk.add_breadcrumb(message="Interaction not found - user dismissed", level="warning")
            work_task.cancel()
            return
        except Exception as e:
            sentry_sdk.add_breadcrumb(message=f"Failed to update interaction: {e}", level="warning")
            print(f"[DEBUG] Failed to edit loading embed: {e}")  # Added debug print for errors
        
        dots = (dots % 3) + 1
        
        # Consistent sleep for animation speed
        await asyncio.sleep(DEFAULT_ANIMATION_SPEED)
    
    print(f"[DEBUG] Animation loop completed after {elapsed:.2f} seconds")  # Added final debug print
    
    sentry_sdk.add_breadcrumb(
        message=f"Animation loop ended after {elapsed:.2f} seconds",
        level="info",
        data={"task_done": work_task.done()}
    )
    
    # Work is complete! Get the result and display it
    try:
        final_embed, final_view = await work_task
        sentry_sdk.add_breadcrumb(
            message="Got work task result", 
            level="info",
            data={
                "embed_is_none": final_embed is None,
                "view_is_none": final_view is None
            }
        )
        
        # CRITICAL FIX: Handle None, None returns (when work function handles response internally)
        if final_embed is None and final_view is None:
            sentry_sdk.add_breadcrumb(message="Work function handled response internally - no update needed", level="info")
            return
        
        # Ensure we have at least an embed or view to send
        if final_embed is None and final_view is None:
            sentry_sdk.add_breadcrumb(message="Both embed and view are None - creating fallback", level="warning")
            final_embed = discord.Embed(
                title="✅ Operation Complete",
                description="The operation completed successfully.",
                color=discord.Color.green()
            )
        
        await interaction.edit_original_response(content="\u200b" if final_embed and not final_view else None, embed=final_embed, view=final_view)
        sentry_sdk.add_breadcrumb(message="Successfully updated with final result", level="info")
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.add_breadcrumb(message=f"Failed to get or display final result: {e}", level="error")
        
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