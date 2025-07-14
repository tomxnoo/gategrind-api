# c:\Users\sakko\Downloads\RoFS (1)\RoFS\ui\buff_ui.py

# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import logging
from typing import Union
from datetime import datetime
from shared.utils.panel_registry import register
from shared.utils.common_views import EphemeralPanelView
from core.database import db as db_utils
from shared.utils import ui_styles
from shared.utils.headers import get_system_status_header
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
from core.database.db import get_unified_user_data

logger = logging.getLogger(__name__)

async def build_buff_details_embed(bot, user, buff):
    # Centralized RPG embed logic for buff details panel
    desc = f"[BUFF DETAILS]\n──────────────────────────\nUser: {user.display_name}\n\nBuff: {buff.get('name', 'Unknown Buff')}\n\n{buff.get('description', '')}\n\nDuration: {buff.get('duration', 'Unknown')}"
    embed = discord.Embed(
        title="🧪 Buff Details",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.teal()
    )
    embed.set_footer(text="Shadow Archive • Buffs Database")
    return embed

async def get_user_buffs_from_db(conn, user_id: int, bot=None) -> dict:
    """
    Fetch and return the user's active buffs from the database or Redis, filtering out expired buffs.
    Returns a dict of buff_id: {name, description, ...}
    """
    data = await get_unified_user_data(conn, user_id, bot=bot)
    active_buffs = data.get("active_buffs", {})
    valid_buffs = {}
    now = datetime.now()
    for buff_id, buff in active_buffs.items():
        try:
            end_time = datetime.fromisoformat(buff["end_time"])
            if now < end_time:
                valid_buffs[buff_id] = buff
        except Exception:
            continue
    return valid_buffs

async def get_user_buff_inventory_from_db(conn, user_id: int, bot=None) -> dict:
    """
    Fetch and return the user's buff inventory from the database or Redis.
    Returns a dict of buff_id: qty
    """
    data = await get_unified_user_data(conn, user_id, bot=bot)
    return data.get("buff_inventory", {})

async def build_buff_panel_embed(
    conn, bot, user: Union[discord.User, discord.Member]
) -> discord.Embed:
    """
    Build the main Buffs panel embed for the user, fetching live data from Redis or the database.
    Shows a summary of active buffs and consumables.
    """
    user_id = user.id
    # Fetch latest data from Redis or DB
    active_buffs = await get_user_buffs_from_db(conn, user_id, bot=bot)
    inventory = await get_user_buff_inventory_from_db(conn, user_id, bot=bot)
    embed = discord.Embed(
        title="🧪 Buffs & Consumables",
        description=f"Active Buffs: {len(active_buffs)}\nConsumables: {sum(inventory.values())}",
        color=discord.Color.purple()
    )
    if active_buffs:
        for buff_id, buff in active_buffs.items():
            name = buff.get("name", buff_id)
            desc = buff.get("description", "No description")
            embed.add_field(name=name, value=desc, inline=False)
    else:
        embed.add_field(name="No Active Buffs", value="You have no active buffs.", inline=False)
    if inventory:
        inv_lines = [f"{buff_id}: {qty}" for buff_id, qty in inventory.items()]
        embed.add_field(name="Consumables", value="\n".join(inv_lines), inline=False)
    else:
        embed.add_field(name="No Consumables", value="You have no consumable items.", inline=False)
    return embed

async def build_buffs_embed(bot, user, json_data):
    # Centralized RPG embed logic for buffs panel
    active_buffs = json_data.get("active_buffs", [])
    inventory = json_data.get("inventory", [])
    lines = ["[BUFFS & CONSUMABLES]", "──────────────────────────"]
    lines.append("✨ Active Buffs")
    if active_buffs:
        for buff in active_buffs:
            rem = buff.get("remaining_hours", 0)
            hours, mins = int(rem), int((rem - int(rem)) * 60)
            lines.append(f"• {buff.get('name', 'Unknown Buff')} - {hours}h {mins}m remaining")
    else:
        lines.append("• No active buffs.")
    lines.append("──────────────────────────")
    lines.append("🎒 Inventory")
    if inventory:
        for item in inventory:
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
            # Use Redis cache-aside for user JSON data
            json_data = await get_or_cache_user_json_data(bot, user.id)
            embed = await build_buffs_embed(bot, user, json_data)
            return embed
        except Exception as e:
            logger.error(f"[BUFFS PANEL ERROR] {e}", exc_info=True)
            return discord.Embed(title="⚠️ Buffs Error", description="Could not load buffs and inventory.", color=discord.Color.red())

    @staticmethod
    async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
        view = EphemeralPanelView(bot, user)
        # Example: If a consumable is used, update DB and invalidate cache
        async def use_consumable(consumable_id):
            async with bot.db_pool.acquire() as connection:
                # await db_utils.use_consumable(connection, user.id, consumable_id)  # Removed: not implemented
                pass  # Placeholder for future logic
            # Write-through: Invalidate cache after DB write
            await invalidate_user_json_cache(bot, user.id)
            # Pre-warm cache for best UX
            await get_or_cache_user_json_data(bot, user.id)
        # Attach use_consumable to the view or button as needed
        return view

async def render_buff_panel(bot, user):
    """Return the Buffs panel embed and view for the user."""
    async with bot.db_pool.acquire() as conn:
        embed = await build_buff_panel_embed(conn, bot, user)
    view = await BuffsPanel.build_view(bot, user)
    return embed, view