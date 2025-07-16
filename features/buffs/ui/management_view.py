# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from core.api_client import api_client
from typing import Union
from core.config import BUFF_DEFINITIONS
from features.buffs.ui.view import render_buff_panel

class BuffManagementView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_buffs(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only manage your own buffs!", ephemeral=True)
            return
        
        try:
            embed, _ = await render_buff_panel(interaction.user)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"[BUFF_MANAGEMENT] Error refreshing buffs: {e}")
            await interaction.response.send_message("❌ Failed to refresh buffs. Please try again.", ephemeral=True)

    @discord.ui.button(label="📋 All Buff Details", style=discord.ButtonStyle.primary)
    async def view_all_buff_details(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only view your own buffs!", ephemeral=True)
            return
        
        try:
            all_buffs = list(BUFF_DEFINITIONS.values())
            buff_data = await api_client.get_buff_inventory(interaction.user)
            active_buffs = buff_data.get("active_buffs", [])
            
            view = AllBuffDetailsView(interaction.user, all_buffs, active_buffs)
            embed = view.create_embed()
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(f"[BUFF_MANAGEMENT] Error viewing buff details: {e}")
            await interaction.response.send_message("❌ Failed to load buff details. Please try again.", ephemeral=True)

    @discord.ui.button(label="🎒 Use Item", style=discord.ButtonStyle.success)
    async def use_consumable(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only use your own items!", ephemeral=True)
            return
        
        try:
            buff_data = await api_client.get_consumable_buffs(interaction.user)
            consumable_buffs = buff_data.get("consumable_buffs", [])
            
            if not consumable_buffs:
                await interaction.response.send_message("🎒 Your inventory is empty!", ephemeral=True)
                return
            
            view = ConsumableSelectView(interaction.user, consumable_buffs)
            await interaction.response.send_message("🎒 Select an item to use:", view=view, ephemeral=True)
        except Exception as e:
            print(f"[BUFF_MANAGEMENT] Error loading consumables: {e}")
            await interaction.response.send_message("❌ Failed to load inventory. Please try again.", ephemeral=True)

class ConsumableSelectView(discord.ui.View):
    def __init__(self, user: Union[discord.User, discord.Member], consumable_buffs: list):
        super().__init__(timeout=60)
        self.user = user
        self.user_id = user.id
        
        options = []
        for buff in consumable_buffs[:25]:  # Discord limit
            options.append(discord.SelectOption(
                label=buff.get("name", "Unknown Item")[:100],
                description=buff.get("description", "Unknown effect")[:100],
                value=str(buff.get("id", buff.get("buff_id", 0)))
            ))
        
        if options:
            self.add_item(ConsumableSelect(options, self.user))

class ConsumableSelect(discord.ui.Select):
    def __init__(self, options, user: Union[discord.User, discord.Member]):
        super().__init__(placeholder="Choose an item to use...", options=options)
        self.user = user
        self.user_id = user.id
    
    async def callback(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your inventory!", ephemeral=True)
            return
        
        try:
            buff_id = int(self.values[0])
            result = await api_client.use_consumable_buff(interaction.user, buff_id)
            
            if result.get("success"):
                buff_info = result.get("buff", {})
                buff_name = buff_info.get("name", "Unknown Item")
                await interaction.response.send_message(f"✅ Used {buff_name}! Effects applied immediately.", ephemeral=True)
            else:
                error_msg = result.get("error", "Unknown error")
                await interaction.response.send_message(f"❌ Failed to use item: {error_msg}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid item selection.", ephemeral=True)
        except Exception as e:
            print(f"[CONSUMABLE_SELECT] Error using consumable: {e}")
            await interaction.response.send_message("❌ Failed to use item. Please try again.", ephemeral=True)

class AllBuffDetailsView(discord.ui.View):
    def __init__(self, user: Union[discord.User, discord.Member], all_buffs: list, active_buffs: list):
        super().__init__(timeout=300)
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
        self.add_item(BackToBuffsButton(self.user))
        
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
        
        if is_active and "expires_at" in buff_data:
            try:
                expires_at = datetime.fromisoformat(buff_data["expires_at"].replace('Z', '+00:00'))
                now = datetime.now(expires_at.tzinfo)
                remaining = expires_at - now
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    description += f"⏰ **Time Remaining:** {hours}h {minutes}m\n"
            except:
                pass
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
        
        try:
            embed, _ = await render_buff_panel(interaction.user)
            view = create_buff_management_view(self.user_id)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(f"[BUFF_DETAILS] Error returning to buffs: {e}")
            await interaction.response.send_message("❌ Failed to return to buffs panel.", ephemeral=True)
    
    async def toggle_active_only(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff details!", ephemeral=True)
            return
        
        self.showing_active_only = not self.showing_active_only
        self.current_page = 0
        self.update_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def previous_page(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff details!", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
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
            await interaction.response.edit_message(embed=embed, view=self)

class BackToBuffsButton(discord.ui.Button):
    def __init__(self, user: Union[discord.User, discord.Member]):
        super().__init__(
            label="← Back to Buffs",
            style=discord.ButtonStyle.danger
        )
        self.user = user
        self.user_id = user.id
        
    async def callback(self, interaction: discord.Interaction):
        if not interaction.user or interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your buff panel!", ephemeral=True)
            return
        
        try:
            embed, view = await render_buff_panel(interaction.user)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(f"[BACK_TO_BUFFS] Error: {e}")
            await interaction.response.send_message("❌ Failed to return to buffs panel.", ephemeral=True)

def create_buff_management_view(user_id: int) -> BuffManagementView:
    return BuffManagementView(user_id)