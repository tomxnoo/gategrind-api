# c:\Users\sakko\Downloads\RoFS (1)\RoFS\ui\buff_ui.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import logging
from typing import Union
from datetime import datetime
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from shared.utils import ui_styles
from shared.utils.headers import get_system_status_header
from core.api_client import api_client

logger = logging.getLogger(__name__)

async def build_buff_details_embed(user, buff):
    """Build embed for buff details"""
    desc = f"[BUFF DETAILS]\n──────────────────────────\nUser: {user.display_name}\n\nBuff: {buff.get('name', 'Unknown Buff')}\n\n{buff.get('description', '')}\n\nDuration: {buff.get('duration', 'Unknown')}"
    embed = discord.Embed(
        title="🧪 Buff Details",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.teal()
    )
    embed.set_footer(text="Shadow Archive • Buffs Database")
    return embed

async def build_buff_panel_embed(user: Union[discord.User, discord.Member], buff_data: dict) -> discord.Embed:
    """
    Build the main Buffs panel embed for the user using API data.
    Shows a summary of active buffs and consumables.
    """
    active_buffs = buff_data.get("active_buffs", [])
    consumable_buffs = buff_data.get("consumable_buffs", [])
    
    embed = discord.Embed(
        title="🧪 Buffs & Consumables",
        description=f"Active Buffs: {len(active_buffs)}\nConsumables: {len(consumable_buffs)}",
        color=discord.Color.purple()
    )
    
    if active_buffs:
        for buff in active_buffs[:5]:  # Limit to 5 for display
            name = buff.get("name", "Unknown Buff")
            desc = buff.get("description", "No description")
            # Calculate remaining time if available
            if "expires_at" in buff:
                try:
                    expires_at = datetime.fromisoformat(buff["expires_at"].replace('Z', '+00:00'))
                    now = datetime.now(expires_at.tzinfo)
                    remaining = expires_at - now
                    if remaining.total_seconds() > 0:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        desc += f"\n⏰ {hours}h {minutes}m remaining"
                except:
                    pass
            embed.add_field(name=f"🔥 {name}", value=desc, inline=False)
    else:
        embed.add_field(name="No Active Buffs", value="You have no active buffs.", inline=False)
    
    if consumable_buffs:
        inv_lines = []
        for buff in consumable_buffs[:10]:  # Limit to 10 for display
            name = buff.get("name", "Unknown Item")
            quantity = buff.get("quantity", 1)
            inv_lines.append(f"• {name} x{quantity}")
        embed.add_field(name="🎒 Consumables", value="\n".join(inv_lines), inline=False)
    else:
        embed.add_field(name="No Consumables", value="You have no consumable items.", inline=False)
    
    return embed

async def build_buffs_embed(user, buff_data):
    """Centralized RPG embed logic for buffs panel using API data"""
    active_buffs = buff_data.get("active_buffs", [])
    consumable_buffs = buff_data.get("consumable_buffs", [])
    
    lines = ["[BUFFS & CONSUMABLES]", "──────────────────────────"]
    lines.append("✨ Active Buffs")
    
    if active_buffs:
        for buff in active_buffs:
            # Calculate remaining time if available
            remaining_text = ""
            if "expires_at" in buff:
                try:
                    expires_at = datetime.fromisoformat(buff["expires_at"].replace('Z', '+00:00'))
                    now = datetime.now(expires_at.tzinfo)
                    remaining = expires_at - now
                    if remaining.total_seconds() > 0:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        remaining_text = f" - {hours}h {minutes}m remaining"
                except:
                    pass
            lines.append(f"• {buff.get('name', 'Unknown Buff')}{remaining_text}")
    else:
        lines.append("• No active buffs.")
    
    lines.append("──────────────────────────")
    lines.append("🎒 Inventory")
    
    if consumable_buffs:
        for item in consumable_buffs:
            lines.append(f"• {item.get('name', 'Unknown Item')} x{item.get('quantity', 0)}")
    else:
        lines.append("• Inventory is empty.")
    
    desc = "\n".join(lines)
    embed = discord.Embed(
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.dark_teal()
    )
    embed.set_footer(text="Shadow Archive • Buffs Database")
    return embed

@register
class BuffsPanel:
    key = "buffs"
    label = "Buffs & Consumables"
    emoji = "🧪"

    @staticmethod
    async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
        try:
            # Get buff data from API
            buff_data = await api_client.get_buff_inventory(user)
            embed = await build_buffs_embed(user, buff_data)
            return embed
        except Exception as e:
            logger.error(f"[BUFFS PANEL ERROR] {e}", exc_info=True)
            return discord.Embed(title="⚠️ Buffs Error", description="Could not load buffs and inventory.", color=discord.Color.red())

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        view = EphemeralPanelView(bot, user)
        return view

async def render_buff_panel(user, user_profile=None, buff_data=None):
    """Return the Buffs panel embed and view for the user."""
    if buff_data is None:
        try:
            buff_data = await api_client.get_buff_inventory(user)
        except Exception as e:
            logger.error(f"[BUFF_PANEL] Error getting buff data: {e}")
            buff_data = {"active_buffs": [], "consumable_buffs": []}
    
    embed = await build_buff_panel_embed(user, buff_data)
    view = await BuffsPanel.build_view(None, user)  # bot parameter not used in current implementation
    return embed, view