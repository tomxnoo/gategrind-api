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
    
    Enhanced with robust webhook error handling to prevent caching system failures.
    """
    MIN_DURATION = 1.5  # Minimum seconds to show animation
    login_message = None
    
    # Try to send initial ephemeral login message with retry logic
    for attempt in range(3):
        try:
            login_embed = render_logging_in_embed(interaction.user, dot_count=1)
            login_message = await interaction.followup.send(embed=login_embed, ephemeral=True)
            print(f"[DEBUG] Successfully sent login message on attempt {attempt + 1}")
            break
        except discord.errors.NotFound as e:
            print(f"[ERROR] Webhook not found on attempt {attempt + 1}: {e}")
            if attempt == 2:  # Last attempt
                print("[ERROR] All webhook attempts failed, proceeding without animation")
                break
            await asyncio.sleep(0.5)  # Brief delay before retry
        except Exception as e:
            print(f"[ERROR] Unexpected error sending login message on attempt {attempt + 1}: {e}")
            if attempt == 2:
                break
            await asyncio.sleep(0.5)
    
    # Start the work task regardless of animation success
    work_task = asyncio.create_task(work_coroutine)
    
    # Only run animation if we successfully created the login message
    if login_message:
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
            except discord.errors.NotFound:
                print("[ERROR] Login message webhook expired during animation, stopping animation")
                break
            except Exception as e:
                print(f"[ERROR] Failed to update login animation: {e}")
                break
            
            # Update dots (1 -> 2 -> 3 -> 1)
            dots = dots % 3 + 1
            
            # Wait before next animation frame
            await asyncio.sleep(0.5)
    else:
        # No animation, just wait for minimum duration
        print("[DEBUG] Running without animation, waiting for work completion")
        await asyncio.sleep(MIN_DURATION)
    
    # Get the work result - this is critical for caching system
    try:
        result = await work_task
        print("[DEBUG] Work task completed successfully")
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
        """Handle dropdown selection with robust error handling for webhook issues."""
        if not interaction.user:
            await interaction.response.send_message("No user found for this interaction.", ephemeral=True)
            return

        if self.user and interaction.user.id != self.user.id:
            await interaction.response.send_message("This is not your menu.", ephemeral=True)
            return

        try:
            # Defer the response to avoid timeout
            await interaction.response.defer(ephemeral=True)
            
            # Define the work coroutine that includes caching
            async def login_work():
                """
                Perform the actual work including critical caching operations.
                This must complete successfully even if animation fails.
                """
                try:
                    print("[DEBUG] Starting login work with caching...")
                    
                    embed = await render_hub_embed(self.bot, interaction.user)
                    view = EphemeralPanelView(self.bot, interaction.user)
                    
                    # Critical caching operations - these must succeed
                    print("[DEBUG] Pre-caching skill tree data...")
                    try:
                        from features.skills.ui.skill_tree_panel import get_cached_library_data, get_cached_profile_data
                        await get_cached_library_data(interaction.user)
                        await get_cached_profile_data(interaction.user)
                        print("[DEBUG] Caching completed successfully")
                    except Exception as cache_error:
                        # Don't fail the main operation if caching fails
                        print(f"[DEBUG] Pre-caching failed: {cache_error}")
                    
                    print("[DEBUG] System hub embed and view built successfully")
                    return embed, view
                    
                except Exception as e:
                    print(f"[ERROR] Critical error in login work: {e}")
                    # Even if something fails, try to return a basic response
                    from shared.utils.headers import render_logging_in_embed
                    error_embed = render_logging_in_embed(interaction.user, dot_count=0)
                    return error_embed, None
            
            # Run the work with animation (with robust webhook handling)
            try:
                (embed, view), login_message = await run_with_login_animation(interaction, login_work())
                print("[DEBUG] Login animation and work completed successfully")
                
                # Try to edit the login message to show final result
                if login_message and embed:
                    try:
                        await login_message.edit(embed=embed, view=view)
                        print("[DEBUG] Successfully updated login message with final result")
                    except discord.errors.NotFound:
                        print("[WARNING] Login message webhook expired, sending new message")
                        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                    except Exception as e:
                        print(f"[WARNING] Failed to update login message, sending new: {e}")
                        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                else:
                    # No login message was created, send directly
                    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                    
            except Exception as e:
                print(f"[ERROR] Login animation failed: {e}")
                # Fallback: run the work directly without animation
                try:
                    embed, view = await login_work()
                    await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                    print("[DEBUG] Fallback direct execution successful")
                except Exception as fallback_error:
                    print(f"[ERROR] Fallback execution also failed: {fallback_error}")
                    raise
                    
        except Exception as e:
            print(f"[ERROR] Complete callback failure: {e}")
            # Final fallback - send error message
            try:
                await interaction.followup.send(
                    "❌ Failed to open System Hub. Please try again.", 
                    ephemeral=True
                )
            except Exception as final_error:
                print(f"[CRITICAL] Even error message failed: {final_error}")
                # Last resort - try basic text response
                try:
                    await interaction.followup.send(
                        "❌ System initialization failed. Please try again.", 
                        ephemeral=True
                    )
                except:
                    pass  # Nothing more we can do

class SystemHubPublicView(discord.ui.View):
    def __init__(self, bot, user=None):
        super().__init__(timeout=None)
        # Pass the bot instance down to the dropdown
        self.add_item(SystemHubPublicDropdown(bot, user))
