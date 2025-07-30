# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import asyncio
import traceback
from typing import Union

from discord.ui import Select, View
from shared.utils.base_views import BaseEphemeralView, SimpleFallbackView

# This import is no longer needed as we will pass the connection pool via the bot object.
# from utils.database.db import get_db
from shared.utils.panel_registry import get_panel_by_key, get_registered_panels
from shared.utils.headers import render_loading_embed
from shared.utils.ui_helpers import run_with_animation

class EphemeralPanelSelect(Select):
    """
    A dropdown for switching between all registered panels.
    """
    def __init__(self, bot, user_id: int):
        self.bot = bot
        self.user_id = user_id
        
        excluded_panels = {"fitness_integration"}

        # Debug: Print registered panels
        from shared.utils.panel_registry import debug_registry
        debug_registry()

        options = [
            discord.SelectOption(label=p.label, value=p.key, emoji=p.emoji)
            for p in get_registered_panels()
            if p.key not in excluded_panels
        ]
        
        print(f"[DEBUG] Panel options: {[(opt.label, opt.value) for opt in options]}")
        
        super().__init__(
            placeholder="Switch Panel…",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"panel_switch:{user_id}"
        )

    async def callback(self, interaction: discord.Interaction):
        
        try:
            if not interaction.user or interaction.user.id != self.user_id:
                await interaction.response.send_message("This menu isn't for you.", ephemeral=True)
                return

            key = self.values[0]
            if not isinstance(key, str):
                await interaction.response.send_message("Invalid panel key.", ephemeral=True)
                return
            panel_cls = get_panel_by_key(key)
            if panel_cls is None:
                await interaction.response.send_message("❌ Panel not found.", ephemeral=True)
                return

            async def do_work():
                try:
                    embed = await asyncio.wait_for(panel_cls.render_embed(self.bot, interaction.user), timeout=15)
                    view = await asyncio.wait_for(panel_cls.build_view(self.bot, interaction.user), timeout=15)
                    return embed, view
                except asyncio.TimeoutError:
                    print(f"[ERROR] Panel render timed out for {key}")
                    embed = discord.Embed(
                        title="⚠️ Panel Loading Timeout",
                        description=f"Panel `{key}` took too long to load. Please try again.",
                        color=0xff6b35
                    )
                    # Use fallback view to avoid circular dependency
                    view = SimpleFallbackView(timeout=300)
                    return embed, view
                except Exception as render_error:
                    print(f"[ERROR] Panel render failed for {key}: {render_error}")
                    traceback.print_exc()
                    
                    # Create detailed error information with RPG styling
                    from shared.utils.headers import get_system_status_header
                    from shared.utils.ui_styles import get_panel_sub_header
                    
                    error_type = type(render_error).__name__
                    error_msg = str(render_error)
                    
                    header = get_system_status_header(interaction.user).replace('```ansi', '').replace('```', '').strip()
                    sub_header = get_panel_sub_header("system_error")
                    
                    content = (
                        f"```ansi\n"
                        f"{header}\n"
                        f"{sub_header}\n\n"
                        f"\x1b[1;31m● PANEL LOADING FAILURE\x1b[0m\n"
                        f"Panel: \x1b[1;33m{key}\x1b[0m\n"
                        f"Error Type: \x1b[1;31m{error_type}\x1b[0m\n"
                        f"Details: \x1b[0;37m{error_msg[:80]}{'...' if len(error_msg) > 80 else ''}\x1b[0m\n\n"
                        f"\x1b[1;33m⚠️ SYSTEM DIAGNOSTICS\x1b[0m\n"
                        f"• Panel initialization failure\n"
                        f"• API connection timeout\n"
                        f"• Missing or corrupted data\n"
                        f"• Authentication issues\n\n"
                        f"\x1b[1;37m🔧 RECOVERY PROCEDURES\x1b[0m\n"
                        f"• Try selecting the panel again\n"
                        f"• Check your internet connection\n"
                        f"• Restart the bot if error persists\n"
                        f"• Contact support with error details\n\n"
                        f"\x1b[1;90m[ERROR LOGGED FOR DEBUGGING]\x1b[0m\n"
                        f"```"
                    )
                    
                    embed = discord.Embed(
                        description=content,
                        color=0xff6b35
                    )
                    embed.set_footer(text="Shadow Archive • System Diagnostics • Error State")
                    # Use fallback view to avoid circular dependency
                    view = SimpleFallbackView(timeout=300)
                    return embed, view
            
            # CRITICAL FIX: Pass the function, not the coroutine result
            await run_with_animation(interaction, do_work)

        except Exception as e:
            print(f"[ERROR] Unexpected error in EphemeralPanelSelect: {e}")
            traceback.print_exc()

    async def animate_loading(self, interaction: discord.Interaction):
        dots = 1
        while True:
            if not interaction.user:
                break
            loading_embed = render_loading_embed(interaction.user, dot_count=dots)
            try:
                await interaction.edit_original_response(embed=loading_embed, view=None)
            except (discord.NotFound, discord.InteractionResponded):
                break # Stop if the message is gone
            dots = dots % 3 + 1
            await asyncio.sleep(0.4)


class EphemeralPanelView(BaseEphemeralView):
    """
    A view that contains the EphemeralPanelSelect dropdown.
    """
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(bot, user, timeout=None)
        self.add_item(EphemeralPanelSelect(self.bot, user.id))