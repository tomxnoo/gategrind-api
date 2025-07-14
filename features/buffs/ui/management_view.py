# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from features.buffs.logic.engine import (
    get_active_buffs,
    use_consumable_buff,
)
from features.user.logic.user_data import load_user_data
from typing import Union
from core.config import BUFF_DEFINITIONS
from features.buffs.ui.view import render_buff_panel

class BuffManagementView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.user_id = user.id

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_buffs(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only manage your own buffs!", ephemeral=True)
            return
        embed, _ = await render_buff_panel(self.bot, interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📋 All Buff Details", style=discord.ButtonStyle.primary)
    async def view_all_buff_details(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only view your own buffs!", ephemeral=True)
            return
        all_buffs = list(BUFF_DEFINITIONS.values())
        active_buffs = await get_active_buffs(self.user_id)
        view = AllBuffDetailsView(self.bot, self.user, all_buffs, active_buffs)
        embed = view.create_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🎒 Use Item", style=discord.ButtonStyle.success)
    async def use_consumable(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only use your own items!", ephemeral=True)
            return
        user_data = await load_user_data(self.user_id)
        inventory = user_data.get("buff_inventory", {})
        if not inventory:
            await interaction.response.send_message("🎒 Your inventory is empty!", ephemeral=True)
            return
        view = ConsumableSelectView(self.bot, self.user, list(inventory.keys()))
        await interaction.response.send_message("🎒 Select an item to use:", view=view, ephemeral=True)

class ConsumableSelectView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], consumable_ids: list):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        options = []
        for buff_id in consumable_ids[:25]:
            buff_def = BUFF_DEFINITIONS.get(buff_id, {})
            options.append(discord.SelectOption(
                label=buff_def.get("name", buff_id)[:100],
                description=buff_def.get("description", "Unknown effect")[:100],
                value=buff_id
            ))
        if options:
            self.add_item(ConsumableSelect(self.bot, options, self.user))

class ConsumableSelect(discord.ui.Select):
    def __init__(self, bot, options, user: Union[discord.User, discord.Member]):
        super().__init__(placeholder="Choose an item to use...", options=options)
        self.bot = bot
        self.user = user
        self.user_id = user.id
    async def callback(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your inventory!", ephemeral=True)
            return
        buff_id = str(self.values[0])
        result = await use_consumable_buff(self.bot, interaction.user.id, buff_id)
        if result["success"]:
            buff_name = result["buff"]["name"]
            await interaction.response.send_message(f"✅ Used {buff_name}! Effects applied immediately.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Failed to use item: {result.get('error', 'Unknown error')}", ephemeral=True)

class AllBuffDetailsView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], all_buffs: list, active_buffs: list):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.user_id = user.id
        self.all_buffs = all_buffs
        self.active_buffs = active_buffs
        self.current_page = 0
        self.max_pages = len(all_buffs)
        self.showing_active_only = False
        self.update_buttons()
    def update_buttons(self):
        self.clear_items()
        self.add_item(BackToBuffsButton(self.bot, self.user))
        toggle_button = discord.ui.Button(
            label="Show Active Only" if not self.showing_active_only else "Show All Buffs",
            style=discord.ButtonStyle.success if not self.showing_active_only else discord.ButtonStyle.secondary
        )
        async def toggle_callback(interaction):
            await self.toggle_active_only(interaction)
        toggle_button.callback = toggle_callback
        self.add_item(toggle_button)
        current_list = self.active_buffs if self.showing_active_only else self.all_buffs
        if len(current_list) > 1:
            max_pages = len(current_list) + 1
            prev_button = discord.ui.Button(
                label="← Previous",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0
            )
            async def prev_callback(interaction):
                await self.previous_page(interaction)
            prev_button.callback = prev_callback
            self.add_item(prev_button)
            next_button = discord.ui.Button(
                label="Next →",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= max_pages - 1
            )
            async def next_callback(interaction):
                await self.next_page(interaction)
            next_button.callback = next_callback
            self.add_item(next_button)
    def create_embed(self) -> discord.Embed:
        current_list = self.active_buffs if self.showing_active_only else self.all_buffs
        if not current_list:
            title = "🔥 No Active Buffs" if self.showing_active_only else "📋 No Buffs Available"
            return discord.Embed(
                title=title,
                description="No buffs to display.",
                color=discord.Color.red()
            )
        if len(current_list) > 1 and self.current_page == 0:
            description = "Select a buff below to view detailed information:\n\n"
            for i, buff_data in enumerate(current_list):
                is_active = any(ab.get("buff_id") == buff_data.get("buff_id") for ab in self.active_buffs)
                status = "🔥 ACTIVE" if is_active else f"⭐ {buff_data.get('rarity', 'Unknown').title()}"
                description += f"**{i+1}.** {buff_data.get('name', 'Unknown')} - {status}\n"
                description += f"     {buff_data.get('description', 'No description')}\n\n"
            embed = discord.Embed(
                title=f"📋 All Buffs Overview ({len(current_list)} total)",
                description=description,
                color=discord.Color.purple()
            )
            return embed
        buff_index = self.current_page if len(current_list) == 1 else self.current_page - 1
        buff_data = current_list[buff_index]
        is_active = any(ab.get("buff_id") == buff_data.get("buff_id") for ab in self.active_buffs)
        description = f"**{buff_data.get('name', 'Unknown')}**\n\n"
        description += f"📝 **Description:** {buff_data.get('description', 'No description')}\n"
        description += f"🏷️ **Type:** {buff_data.get('type', 'Unknown').title()}\n"
        description += f"⭐ **Rarity:** {buff_data.get('rarity', 'Unknown').title()}\n\n"
        if is_active and "remaining_hours" in buff_data:
            remaining = int(buff_data["remaining_hours"])
            minutes = int((buff_data["remaining_hours"] - remaining) * 60)
            description += f"⏰ **Time Remaining:** {remaining}h {minutes}m\n"
        elif "duration_hours" in buff_data:
            description += f"⏰ **Duration:** {buff_data['duration_hours']} hours\n"
        if "effects" in buff_data:
            description += "\n💫 **Effects:**\n"
            effects = buff_data["effects"]
            for effect, value in effects.items():
                if effect == "xp_bonus":
                    description += f"• +{value}% XP gain\n"
                elif effect == "cooldown_reduction":
                    description += f"• -{value}% cooldown reduction\n"
                elif effect == "quest_xp_bonus":
                    description += f"• +{value}% quest XP bonus\n"
                elif effect == "xp_multiplier":
                    description += f"• {value}x XP multiplier\n"
                elif effect == "instant_xp":
                    description += f"• +{value} instant XP\n"
                elif effect == "remove_cooldowns":
                    description += "• Removes all cooldowns\n"
        if is_active:
            description += "\n🔥 **STATUS: CURRENTLY ACTIVE**"
        page_num = buff_index + 1 if len(current_list) == 1 else self.current_page
        total_pages = len(current_list) if len(current_list) == 1 else len(current_list) + 1
        embed = discord.Embed(
            title=f"📋 Buff Details ({page_num}/{total_pages})",
            description=description,
            color=discord.Color.gold() if is_active else discord.Color.purple()
        )
        return embed
    async def back_to_buffs(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff panel!", ephemeral=True)
            return
        embed, _ = await render_buff_panel(self.bot, interaction.user)
        view = create_buff_management_view(self.bot, self.user)
        await interaction.response.edit_message(embed=embed, view=view)
    async def toggle_active_only(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff details!", ephemeral=True)
            return
        self.showing_active_only = not self.showing_active_only
        self.current_page = 0
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.defer()
        await interaction.edit_original_response(embed=embed, view=self)
    async def previous_page(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff details!", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=self)
    async def next_page(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff details!", ephemeral=True)
            return
        current_list = self.active_buffs if self.showing_active_only else self.all_buffs
        max_pages = len(current_list) + 1 if len(current_list) > 1 else len(current_list)
        if self.current_page < max_pages - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=self)

class BackToBuffsButton(discord.ui.Button):
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(
            label="← Back to Buffs",
            style=discord.ButtonStyle.danger
        )
        self.bot = bot
        self.user = user
        self.user_id = user.id
    async def callback(self, interaction: discord.Interaction):
        import asyncio
        from shared.utils.headers import render_loading_embed
        loading = True
        task = None
        async def animate_loading():
            dots = 1
            while loading:
                if not interaction.user:
                    break
                loading_embed = render_loading_embed(interaction.user, dot_count=dots)
                try:
                    await interaction.edit_original_response(embed=loading_embed, view=None)
                except Exception:
                    pass
                dots = dots % 3 + 1
                await asyncio.sleep(0.35)
        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
            task = asyncio.create_task(animate_loading())
            from features.buffs.ui.view import render_buff_panel
            embed, view = await render_buff_panel(self.bot, interaction.user)
            loading = False
            if task:
                task.cancel()
                await asyncio.sleep(0.1)
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            loading = False
            if task:
                task.cancel()
            import traceback
            tb = traceback.format_exc()
            error_embed = discord.Embed(
                title="❌ BUFF PANEL ERROR",
                description=f"```\n{tb}\n```",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=error_embed, view=None)

def create_buff_management_view(bot, user: Union[discord.User, discord.Member]) -> BuffManagementView:
    return BuffManagementView(bot, user)