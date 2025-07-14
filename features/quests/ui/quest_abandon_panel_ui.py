# views/quest_abandon_panel_ui.py

import discord
from typing import Union

def build_abandon_quests_embed(user: Union[discord.User, discord.Member], is_weekly: bool = False) -> discord.Embed:
    """Builds the embed for the quest abandonment confirmation panel."""
    item_type = "Weekly Contract" if is_weekly else "Daily Quest"
    embed = discord.Embed(
        title=f"⚠️ Abandon {item_type}?",
        description=f"Are you sure you want to abandon your active {item_type.lower()}? Any progress will be lost.",
        color=discord.Color.orange()
    )
    embed.set_footer(text="This action cannot be undone.")
    return embed

class ConfirmAbandonButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(label="Confirm Abandon", style=discord.ButtonStyle.danger, custom_id="confirm_abandon")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user: return
        
        from features.quests.ui.weekly.weekly_contract_panel import abandon_active_weekly_contract, WeeklyQuestSelectorView
        
        # Respond to the interaction first
        await interaction.response.defer()
        
        # Abandon the contract
        await abandon_active_weekly_contract(interaction.user.id, self.bot)
        
        # Create new view and manually build the embed and update
        view = WeeklyQuestSelectorView(self.bot, interaction.user.id)
        
        # Get the contracts and build embed manually
        from features.quests.ui.weekly.weekly_contract_panel import get_weekly_contracts, build_weekly_contract_panel_embed
        contracts = await get_weekly_contracts(interaction.user.id, self.bot)
        
        if contracts:
            # Reset page to 0 after abandon
            view.page_dict[interaction.user.id] = 0
            embed = build_weekly_contract_panel_embed(interaction.user, contracts[0], 1, len(contracts))
        else:
            embed = discord.Embed(description="❌ No weekly contracts found.", color=discord.Color.red())
        
        # Update the message
        await interaction.edit_original_response(embed=embed, view=view)

class CancelAbandonButton(discord.ui.Button):
    def __init__(self, bot, user_id):
        super().__init__(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_abandon")
        self.bot = bot
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user: return
        
        from features.quests.ui.weekly.weekly_contract_panel import WeeklyQuestSelectorView, get_weekly_contracts, build_weekly_contract_panel_embed
        
        # Respond to the interaction first
        await interaction.response.defer()
        
        # Create new view and manually build the embed
        view = WeeklyQuestSelectorView(self.bot, self.user_id)
        
        # Get current contracts and build embed
        contracts = await get_weekly_contracts(self.user_id, self.bot)
        
        if contracts:
            current_page = view.page_dict.get(self.user_id, 0)
            if current_page >= len(contracts):
                current_page = 0
                view.page_dict[self.user_id] = current_page
            embed = build_weekly_contract_panel_embed(interaction.user, contracts[current_page], current_page + 1, len(contracts))
        else:
            embed = discord.Embed(description="❌ No weekly contracts found.", color=discord.Color.red())
        
        # Update the message
        await interaction.edit_original_response(embed=embed, view=view)


class AbandonQuestConfirmationView(discord.ui.View):
    """A view to confirm abandoning an active quest."""

    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.add_item(ConfirmAbandonButton(bot))
        self.add_item(CancelAbandonButton(bot, user.id))