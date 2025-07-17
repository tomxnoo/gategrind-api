# daily_quest_panel.py
# Unified panel for daily quest UI, views, and embeds
import discord
import asyncio
import sentry_sdk
import logging
from typing import Union
from discord.ui import View, Button

from shared.utils.ui_helpers import run_with_animation
from features.quests.logic.daily_quests.daily_quest_logic import get_today_quests, activate_daily_quest
from features.quests.ui.daily.daily_quest_ansi import render_daily_quest_ansi_block
from features.quests.ui.quest_panel_common import QuestSelectorView, QuestAcceptDeclineView
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.ui_helpers import interaction_handler
from core.redis_cache import get_or_cache_user_json_data

# Global state for user quest pages (consistent naming)
_daily_pages = {}

def build_daily_quest_panel_embed(user: Union[discord.User, discord.Member], quest: dict, page: int, total: int) -> discord.Embed:
    """Build embed for daily quest display using ANSI format like weekly contracts"""
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("daily_quest")
    ansi_block = render_daily_quest_ansi_block(quest, user)
    
    description = f"```ansi\n{header}\n{sub_header}\n\n{ansi_block}\n```"
    
    embed = discord.Embed(
        description=description,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Shadow Archive • Quest {page}/{total}")
    return embed

def render_quest_accepted_embed(user: Union[discord.User, discord.Member], quest: dict) -> discord.Embed:
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("quest_accept")
    
    quest_name = quest.get('name', quest.get('QuestName', 'Unknown Quest'))
    flavor_text = quest.get('flavor', quest.get('Flavor', 'The quest has been accepted.'))
    
    desc = f"{header}\n{sub_header}\n\n**Quest Accepted:** {quest_name}\n\n{flavor_text}"
    
    embed = discord.Embed(
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.green()
    )
    embed.set_footer(text="Shadow Archive • Quest Division")
    return embed

class DailyQuestSelectorView(QuestSelectorView):
    def __init__(self, bot, user_id: int):
        super().__init__(
            bot=bot,
            user_id=user_id,
            get_quests_func=get_today_quests,
            page_dict=_daily_pages,
            detail_view_class=DailyQuestAcceptDeclineView,
            quest_type="daily"
        )
    
    async def build_embed(self, bot, quest, user):
        page = _daily_pages.get(user.id, 0)
        quests = await get_today_quests(user.id, bot)
        return build_daily_quest_panel_embed(user, quests[page], page + 1, len(quests))

class DailyQuestAcceptDeclineView(QuestAcceptDeclineView):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quest: dict, disable_accept=False, quest_type="daily"):
        super().__init__(bot, user, quest, disable_accept, quest_type)
    
    async def accept_callback(self, interaction: discord.Interaction):
        async def do_work():
            user_id = self.user.id
            # Fix: Use the correct field name for quest tier
            quest_tier = self.quest.get("tier")
            if quest_tier is None:
                quest_tier = self.quest.get("Tier")
            
            await activate_daily_quest(user_id, quest_tier, bot=self.bot)
            
            # Invalidate cache to ensure fresh data
            from core.redis_cache import invalidate_user_json_cache
            await invalidate_user_json_cache(self.bot, user_id)
            
            # Reset page index to 0 since active quest will be first
            _daily_pages[user_id] = 0
            
            quests = await get_today_quests(user_id, self.bot)
            active_quest = next((q for q in quests if q.get("active")), None)
            if active_quest is None:
                active_quest = self.quest
            embed = render_quest_accepted_embed(self.user, active_quest)
            view = BackToMenuFromDailyAcceptView(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work)
    
    async def decline_callback(self, interaction: discord.Interaction):
        async def do_work():
            user_id = self.user.id
            view = DailyQuestSelectorView(self.bot, user_id)
            quests = await get_today_quests(user_id, self.bot)
            index = _daily_pages.get(user_id, 0)
            embed = build_daily_quest_panel_embed(self.user, quests[index], index + 1, len(quests))
            return embed, view
        
        await run_with_animation(interaction, do_work)

class BackToMenuFromDailyAcceptView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.add_item(BackToMenuButton(self))

class BackToMenuButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Back to Menu", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        async def do_work():
            from core.redis_cache import invalidate_user_json_cache
            
            # Invalidate cache to ensure fresh data
            await invalidate_user_json_cache(self.parent_view.bot, self.parent_view.user.id)
            
            # Reset page index to show active quest first
            _daily_pages[self.parent_view.user.id] = 0

            view = DailyQuestSelectorView(self.parent_view.bot, self.parent_view.user.id)
            await view.refresh_panel(interaction)
            return None, None  # refresh_panel handles the response
        
        await run_with_animation(interaction, do_work)

class DailyQuestView(View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quest: dict, disable_accept=False, quest_type="daily"):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.quest = quest
        self.disable_accept = disable_accept
        self.quest_type = quest_type

        # Add buttons
        if not disable_accept:
            self.add_item(AcceptQuestButton())
        self.add_item(DeclineQuestButton())

    async def accept_callback(self, interaction: discord.Interaction):
        # Redirect to new implementation
        view = DailyQuestAcceptDeclineView(self.bot, self.user, self.quest, self.disable_accept, self.quest_type)
        await view.accept_callback(interaction)

    async def decline_callback(self, interaction: discord.Interaction):
        # Redirect to new implementation
        view = DailyQuestAcceptDeclineView(self.bot, self.user, self.quest, self.disable_accept, self.quest_type)
        await view.decline_callback(interaction)

class AcceptQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Accept", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        await self.view.accept_callback(interaction)

class DeclineQuestButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Decline", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await self.view.decline_callback(interaction)

# Static methods for panel registry compatibility
@staticmethod
async def render_embed(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.Embed:
    quests = await get_today_quests(user.id, bot)
    if not quests:
        return discord.Embed(
            title="📋 Daily Quests",
            description="No daily quests available.",
            color=discord.Color.orange()
        )
    page = _daily_pages.get(user.id, 0)
    return build_daily_quest_panel_embed(user, quests[page], page + 1, len(quests))

@staticmethod
async def build_view(bot, user: Union[discord.User, discord.Member], **kwargs) -> discord.ui.View:
    return DailyQuestSelectorView(bot, user.id)

__all__ = ["DailyQuestSelectorView", "build_daily_quest_panel_embed"]