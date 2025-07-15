import sentry_sdk

import discord  # Pycord (discord.py compatible)
import asyncio
from typing import Union
from shared.utils.headers import render_loading_embed, get_system_status_header
from core.redis_cache import invalidate_user_json_cache
from core.database import db as db_utils
from shared.utils.ui_helpers import create_loading_animation, interaction_handler
# Import QuestPanel inside method to avoid circular import

# --- RPG-style embed builder ---
def build_abandon_quests_embed(user, confirm_type=None):
    from shared.utils.ui_styles import get_panel_sub_header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("abandon_quests")
    if confirm_type == "daily":
        content = "Are you sure you want to abandon ALL daily quests? This cannot be undone.\n\nPress again to confirm."
        desc = f"{header}\n{sub_header}\n{content}"
    elif confirm_type == "weekly":
        content = "Are you sure you want to abandon your weekly contract? This cannot be undone.\n\nPress again to confirm."
        desc = f"{header}\n{sub_header}\n{content}"
    elif confirm_type == "daily_done":
        content = "All daily quests have been abandoned."
        desc = f"{header}\n{sub_header}\n{content}"
    elif confirm_type == "weekly_done":
        content = "Your weekly contract has been abandoned."
        desc = f"{header}\n{sub_header}\n{content}"
    else:
        content = "You may abandon all daily quests or your weekly contract. This action cannot be undone.\n\nChoose an option below."
        desc = f"{header}\n{sub_header}\n{content}"
    return discord.Embed(description=f"```ansi\n{desc}\n```", color=discord.Color.red())

async def build_quest_abandon_embed(bot, user: Union[discord.User, discord.Member], quest: dict) -> discord.Embed:
    from shared.utils.ui_styles import get_panel_sub_header
    panel_key = "quest_abandon"
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header(panel_key)
    desc = f"{header}\n{sub_header}\nUser: {user.display_name}\n\nQuest: {quest.get('name', 'Unknown Quest')}\n\n{quest.get('flavor', '')}\n\nAre you sure you want to abandon this quest? This cannot be undone."
    embed = discord.Embed(
        title="⚠️ Abandon Quest?",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.orange()
    )
    embed.set_footer(text="Shadow Archive • Quest Database")
    return embed

async def build_quest_abandon_confirm_embed(bot, user: Union[discord.User, discord.Member], quest: dict) -> discord.Embed:
    from shared.utils.ui_styles import get_panel_sub_header
    panel_key = "quest_abandon_confirm"
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header(panel_key)
    desc = f"{header}\n{sub_header}\nUser: {user.display_name}\n\nQuest: {quest.get('name', 'Unknown Quest')}\n\n{quest.get('flavor', '')}\n\nQuest has been abandoned."
    embed = discord.Embed(
        title="❌ Quest Abandoned",
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.red()
    )
    embed.set_footer(text="Shadow Archive • Quest Database")
    return embed

# --- RPG-style Abandon Quests Panel ---
class AbandonQuestsView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], has_daily=True, has_weekly=True):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.has_daily = has_daily
        self.has_weekly = has_weekly
        self.daily_abandon_confirm = False
        self.weekly_abandon_confirm = False
        # Track abandonment status
        self.daily_abandoned = False
        self.weekly_abandoned = False
        self.add_buttons()

    def add_buttons(self):
        self.clear_items()
        
        # Daily abandon button
        if self.daily_abandoned:
            daily_label = "Daily abandoned ✓"
            daily_style = discord.ButtonStyle.secondary
            daily_disabled = True
        else:
            daily_label = "Abandon daily"
            daily_style = discord.ButtonStyle.danger
            daily_disabled = not self.has_daily
            
        self.abandon_daily_button = discord.ui.Button(
            label=daily_label, 
            style=daily_style, 
            disabled=daily_disabled
        )
        self.abandon_daily_button.callback = self.abandon_daily
        self.add_item(self.abandon_daily_button)
        
        # Weekly abandon button
        if self.weekly_abandoned:
            weekly_label = "Weekly abandoned ✓"
            weekly_style = discord.ButtonStyle.secondary
            weekly_disabled = True
        else:
            weekly_label = "Abandon weekly"
            weekly_style = discord.ButtonStyle.danger
            weekly_disabled = not self.has_weekly
            
        self.abandon_weekly_button = discord.ui.Button(
            label=weekly_label, 
            style=weekly_style, 
            disabled=weekly_disabled
        )
        self.abandon_weekly_button.callback = self.abandon_weekly
        self.add_item(self.abandon_weekly_button)
        
        # Back button
        self.back_button = discord.ui.Button(label="Back to menu", style=discord.ButtonStyle.secondary)
        self.back_button.callback = self.back_to_menu
        self.add_item(self.back_button)

    def show_confirm_cancel(self, confirm_type):
        self.clear_items()
        confirm_btn = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        if confirm_type == "daily":
            confirm_btn.callback = self.confirm_abandon_daily
            cancel_btn.callback = self.cancel_abandon_daily
        elif confirm_type == "weekly":
            confirm_btn.callback = self.confirm_abandon_weekly
            cancel_btn.callback = self.cancel_abandon_weekly
        self.add_item(confirm_btn)
        self.add_item(cancel_btn)

    async def abandon_daily(self, interaction: discord.Interaction):
        # Show confirm/cancel buttons with RPG style embed
        embed = build_abandon_quests_embed(self.user, confirm_type="daily")
        self.show_confirm_cancel("daily")
        await interaction.response.edit_message(embed=embed, view=self)

    async def confirm_abandon_daily(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            from features.quests.logic.daily_quests.daily_quest_logic import abandon_daily_quests
            await abandon_daily_quests(self.user.id, self.bot)
            
            self.daily_abandoned = True
            embed = build_abandon_quests_embed(self.user, confirm_type="daily_done")
            self.add_buttons()
            return embed, self
        
        await run_with_animation(interaction, do_work())
    
    async def confirm_abandon_weekly(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            from features.quests.logic.weekly_quests.weekly_quest_logic import abandon_weekly_contract
            await abandon_weekly_contract(self.bot, self.user.id)
            
            self.weekly_abandoned = True
            embed = build_abandon_quests_embed(self.user, confirm_type="weekly_done")
            self.add_buttons()
            return embed, self
        
        await run_with_animation(interaction, do_work())
    
    async def back_to_menu(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            await invalidate_user_json_cache(self.bot, self.user.id)
            
            from features.quests.ui.quest_panel import QuestPanel
            embed = await QuestPanel.render_embed(self.bot, self.user)
            view = await QuestPanel.build_view(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

    async def cancel_abandon_daily(self, interaction: discord.Interaction):
        # Return to main abandon view
        embed = build_abandon_quests_embed(self.user)
        self.add_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def abandon_weekly(self, interaction: discord.Interaction):
        # Show confirm/cancel buttons with RPG style embed
        embed = build_abandon_quests_embed(self.user, confirm_type="weekly")
        self.show_confirm_cancel("weekly")
        await interaction.response.edit_message(embed=embed, view=self)

    async def cancel_abandon_weekly(self, interaction: discord.Interaction):
        # Return to main abandon view
        embed = build_abandon_quests_embed(self.user)
        self.add_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

class AbandonQuestSelect(discord.ui.Select):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quests=None):
        options = []
        if quests:
            for i, quest in enumerate(quests):
                quest_name = quest.get('name', f"Quest {i+1}")
                options.append(discord.SelectOption(label=quest_name[:25], value=str(i), description=f"Abandon {quest_name[:20]}..."))
        
        super().__init__(placeholder="Select a quest to abandon...", options=options, min_values=1, max_values=1)
        self.bot = bot
        self.user = user
        self.quests = quests or []

    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            selected_index = int(self.values[0])
            if 0 <= selected_index < len(self.quests):
                selected_quest = self.quests[selected_index]
                
                # Show confirmation view
                embed = await build_quest_abandon_embed(self.bot, self.user, selected_quest)
                view = AbandonQuestConfirmationView(self.bot, self.user, selected_quest)
                return embed, view
            else:
                embed = discord.Embed(
                    title="❌ Invalid Selection",
                    description="Invalid selection. Please try again.",
                    color=discord.Color.red()
                )
                return embed, None
        
        await run_with_animation(interaction, do_work())

class AbandonQuestConfirmationView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quest):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.quest = quest
        
        # Add confirm button
        confirm_btn = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger)
        confirm_btn.callback = self.confirm_abandon
        self.add_item(confirm_btn)
        
        # Add cancel button
        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        cancel_btn.callback = self.cancel_abandon
        self.add_item(cancel_btn)

    async def confirm_abandon(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            # Logic to abandon the specific quest
            quest_id = self.quest.get('id') or self.quest.get('quest_id')
            quest_type = self.quest.get('type', 'daily')
            
            if quest_type == 'daily':
                from features.quests.logic.daily_quests.daily_quest_logic import abandon_specific_quest
                await abandon_specific_quest(self.bot, self.user.id, quest_id)
            elif quest_type == 'weekly':
                from features.quests.logic.weekly_quests.weekly_quest_logic import abandon_specific_contract
                await abandon_specific_contract(self.bot, self.user.id, quest_id)
            
            # Show confirmation
            embed = await build_quest_abandon_confirm_embed(self.bot, self.user, self.quest)
            
            # Invalidate cache
            await invalidate_user_json_cache(self.bot, self.user.id)
            
            return embed, None
        
        await run_with_animation(interaction, do_work())

    async def cancel_abandon(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            # Return to quest panel
            from features.quests.ui.quest_panel import QuestPanel
            embed = await QuestPanel.render_embed(self.bot, self.user)
            view = await QuestPanel.build_view(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())