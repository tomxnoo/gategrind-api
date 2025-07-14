import discord
import asyncio  # Add this missing import
from typing import Callable, List, Dict, Any, Union
from shared.utils.ui_helpers import interaction_handler

class QuestSelectorView(discord.ui.View):
    def __init__(self, bot, user_id: int, get_quests_func: Callable, page_dict: dict, detail_view_class, quest_type: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.get_quests_func = get_quests_func
        self.page_dict = page_dict
        self.detail_view_class = detail_view_class
        self.quest_type = quest_type
        self.prev_btn = PrevQuestButton(self)
        self.details_btn = ViewDetailsButton(self)
        self.next_btn = NextQuestButton(self)
        self.menu_btn = BackToMenuButton(self)
        
        self.add_item(self.prev_btn)
        self.add_item(self.details_btn)
        self.add_item(self.next_btn)
        self.add_item(self.menu_btn)

    async def refresh_panel(self, interaction: discord.Interaction):
        if not interaction.user:
            return
        
        self.page_dict.setdefault(self.user_id, 0)
        quests = await self.get_quests_func(self.user_id, self.bot)
        if not quests:
            embed = discord.Embed(description=f"❌ No {self.quest_type} quests found.", color=discord.Color.red())
            # Always use edit_original_response for consistency with loading animations
            await interaction.edit_original_response(embed=embed, view=self)
            return
        index = self.page_dict[self.user_id]
        if index < 0:
            index = 0
        if index >= len(quests):
            index = len(quests) - 1
            self.page_dict[self.user_id] = index
        quest = quests[index]
        is_current_active = bool(quest.get("active"))
        # Fix: Check for completion status as well
        is_completed = bool(quest.get("_completed_flag") or quest.get("Completed"))
        
        # Update button based on both active and completion status
        if is_completed:
            self.details_btn.disabled = True
            self.details_btn.label = "Completed"
            self.details_btn.style = discord.ButtonStyle.success
        elif is_current_active:
            self.details_btn.disabled = True
            self.details_btn.label = "Active Quest"
            self.details_btn.style = discord.ButtonStyle.secondary
        else:
            self.details_btn.disabled = False
            self.details_btn.label = "View Details"
            self.details_btn.style = discord.ButtonStyle.primary
        
        embed = await self.build_embed(self.bot, quest, interaction.user)
        # Always use edit_original_response for consistency with loading animations
        await interaction.edit_original_response(embed=embed, view=self)

    async def build_embed(self, bot, quest, user):
        raise NotImplementedError("Override build_embed in subclass or instance.")

class PrevQuestButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="⬅️ Prev", style=discord.ButtonStyle.primary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import create_loading_animation
        
        # Defer the interaction first, then create loading animation
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception:
            pass
        
        loading_task, stop_loading = await create_loading_animation(interaction, interaction.user)
        
        try:
            user_id = interaction.user.id
            quests = await self.parent_view.get_quests_func(user_id, self.parent_view.bot)
            if not quests:
                stop_loading()
                await asyncio.wait_for(loading_task, timeout=1.0)
                await interaction.edit_original_response(
                    embed=discord.Embed(description="❌ No quests.", color=discord.Color.red()),
                    view=self.parent_view
                )
                return
            
            self.parent_view.page_dict[user_id] = (self.parent_view.page_dict[user_id] - 1) % len(quests)
            
            # Call refresh_panel BEFORE stopping loading animation
            await self.parent_view.refresh_panel(interaction)
            
            # Add delay BEFORE stopping loading to let UI settle
            await asyncio.sleep(0.5)
            
            # Stop loading animation AFTER delay
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
                
        except Exception as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            await interaction.edit_original_response(
                content=f"Error: {e}", embed=None, view=None
            )

class NextQuestButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Next ➡️", style=discord.ButtonStyle.primary)
        self.parent_view = parent_view
    
    async def callback(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import create_loading_animation
        
        # Defer the interaction first, then create loading animation
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception:
            pass
        
        loading_task, stop_loading = await create_loading_animation(interaction, interaction.user)
        
        try:
            user_id = interaction.user.id
            quests = await self.parent_view.get_quests_func(user_id, self.parent_view.bot)
            if not quests:
                stop_loading()
                await asyncio.wait_for(loading_task, timeout=1.0)
                await interaction.edit_original_response(
                    embed=discord.Embed(description="❌ No quests.", color=discord.Color.red()),
                    view=self.parent_view
                )
                return
            
            self.parent_view.page_dict[user_id] = (self.parent_view.page_dict[user_id] + 1) % len(quests)
            
            # Call refresh_panel BEFORE stopping loading animation
            await self.parent_view.refresh_panel(interaction)
            
            # Add delay BEFORE stopping loading to let UI settle
            await asyncio.sleep(0.5)
            
            # Stop loading animation AFTER delay
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
                
        except Exception as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            await interaction.edit_original_response(
                content=f"Error: {e}", embed=None, view=None
            )

class ViewDetailsButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="View Details", style=discord.ButtonStyle.success)
        self.parent_view = parent_view
        # Remove user attribute since we'll get it from interaction
    
    # Remove the @interaction_handler decorator and handle loading manually
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception:
            pass
        
        # Create loading animation manually using interaction.user
        from shared.utils.ui_helpers import create_loading_animation
        loading_task, stop_loading = await create_loading_animation(interaction, interaction.user)
        
        try:
            user_id = interaction.user.id
            quests = await self.parent_view.get_quests_func(user_id, self.parent_view.bot)
            if not quests:
                stop_loading()
                await asyncio.wait_for(loading_task, timeout=1.0)
                await interaction.edit_original_response(
                    embed=discord.Embed(description="❌ No quests to view.", color=discord.Color.red()),
                    view=None
                )
                return
            
            selected = self.parent_view.page_dict.get(user_id, 0)
            if selected < 0:
                selected = 0
            if selected >= len(quests):
                selected = len(quests) - 1
            quest = quests[selected]
            active_quests = [q for q in quests if q.get("active")]
            view = self.parent_view.detail_view_class(self.parent_view.bot, interaction.user, quest, disable_accept=len(active_quests) > 0, quest_type=self.parent_view.quest_type)
            embed = await self.parent_view.build_embed(self.parent_view.bot, quest, interaction.user)
            
            # Stop loading animation
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            
            # Add small delay to ensure loading animation stops properly
            await asyncio.sleep(0.35)
            
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            await interaction.edit_original_response(
                content=f"Error: {e}", embed=None, view=None
            )

class BackToMenuButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Back to Menu", style=discord.ButtonStyle.danger)
        self.parent_view = parent_view
        # Remove user attribute since we'll get it from interaction
    
    # Remove the @interaction_handler decorator and handle loading manually
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception:
            pass
        
        # Create loading animation manually using interaction.user
        from shared.utils.ui_helpers import create_loading_animation
        loading_task, stop_loading = await create_loading_animation(interaction, interaction.user)
        
        try:
            from features.quests.ui.quest_panel import QuestPanel
            view = await QuestPanel.build_view(self.parent_view.bot, interaction.user)
            embed = await QuestPanel.render_embed(self.parent_view.bot, interaction.user)
            
            # Stop loading animation
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            
            # Add small delay to ensure loading animation stops cleanly
            await asyncio.sleep(0.1)
            
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
            stop_loading()
            try:
                await asyncio.wait_for(loading_task, timeout=1.0)
            except asyncio.TimeoutError:
                loading_task.cancel()
            await interaction.edit_original_response(
                content=f"Error: {e}", embed=None, view=None
            )

class QuestAcceptDeclineView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quest: dict, disable_accept=False, quest_type="daily"):
        super().__init__(timeout=120)
        self.bot = bot
        self.user = user
        self.quest = quest
        self.quest_type = quest_type
        accept_btn = discord.ui.Button(label="Accept", style=discord.ButtonStyle.success, custom_id="accept")
        decline_btn = discord.ui.Button(label="Decline", style=discord.ButtonStyle.danger, custom_id="decline")
        if disable_accept:
            accept_btn.disabled = True
            accept_btn.label = "Already Active"
            accept_btn.style = discord.ButtonStyle.secondary
        accept_btn.callback = self.accept_callback
        abandon_btn = discord.ui.Button(label="Abandon Quests", style=discord.ButtonStyle.danger)
        if not disable_accept:
            abandon_btn.disabled = True
            abandon_btn.label = "No Active Quest"
            abandon_btn.style = discord.ButtonStyle.secondary
        async def abandon_callback(interaction):
            from features.quests.ui.quest_abandon_ui import build_abandon_quests_embed, AbandonQuestsView
            from features.quests.logic.daily_quests.daily_quest_logic import get_today_quests
            from features.quests.ui.weekly.weekly_contract_panel import get_weekly_contracts

            daily_quests = await get_today_quests(interaction.user.id, self.bot)
            has_active_daily = any(q.get("active") for q in daily_quests)

            weekly_contracts = await get_weekly_contracts(interaction.user.id, self.bot)
            has_active_weekly = any(c.get("active") for c in weekly_contracts)

            embed = build_abandon_quests_embed(interaction.user)
            view = AbandonQuestsView(self.bot, interaction.user, has_daily=has_active_daily, has_weekly=has_active_weekly)
            
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.defer()
                await interaction.edit_original_response(embed=embed, view=view)
        abandon_btn.callback = abandon_callback
        decline_btn.callback = self.decline_callback
        self.add_item(accept_btn)
        self.add_item(decline_btn)
        self.add_item(abandon_btn)
    @interaction_handler(ephemeral=False, with_loading=True)
    async def accept_callback(self, interaction: discord.Interaction):
        # Implement in subclass or instance
        pass
    async def decline_callback(self, interaction: discord.Interaction):
        # Implement in subclass or instance
        pass
