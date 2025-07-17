import sentry_sdk
import discord  # Pycord (discord.py compatible)
from shared.utils.ui_styles import get_panel_sub_header
from shared.utils.headers import get_system_status_header
from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
from features.quests.ui.quest_panel import build_quest_panel_embed
from core.database import db as db_utils
from typing import Union
import asyncio
from shared.utils.headers import render_loading_embed
from shared.utils.ui_helpers import create_loading_animation, interaction_handler

async def build_quest_reroll_embed(bot, user: Union[discord.User, discord.Member]):
    json_data = None
    try:
        header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
        sub_header = get_panel_sub_header("quest_reroll")
        import json
        json_data = await get_or_cache_user_json_data(bot, user.id)
        daily_quests_raw = json_data.get("daily_quests", {})
        daily_quests = daily_quests_raw.get("quests", []) if isinstance(daily_quests_raw, dict) else daily_quests_raw
        # Parse quest objects if they are strings
        parsed_daily_quests = []
        for q in daily_quests:
            if isinstance(q, str):
                try:
                    parsed_daily_quests.append(json.loads(q))
                except Exception:
                    sentry_sdk.capture_message(f"Failed to parse daily quest: {q}")
            elif isinstance(q, dict):
                parsed_daily_quests.append(q)
        # Build daily quest summary
        if parsed_daily_quests:
            dq = parsed_daily_quests[0]
            dq_name = dq.get("QuestName") or dq.get("name") or dq.get("quest_name") or "?"
            dq_tasks = dq.get("Movements") or dq.get("movements") or []
            if isinstance(dq_tasks, str):
                try:
                    dq_tasks = json.loads(dq_tasks)
                except Exception:
                    dq_tasks = [dq_tasks]
            dq_xp = dq.get("XPReward") or dq.get("xpReward") or dq.get("xp_reward") or 0
            dq_buff = dq.get("BuffReward") or dq.get("buffReward") or dq.get("buff_reward")
            daily_summary = f"**{dq_name}**\nTasks: {', '.join(dq_tasks)}\nReward: {dq_xp} XP" + (f", {dq_buff}" if dq_buff else "")
        else:
            daily_summary = "No daily quest."
        weekly_contracts_raw = json_data.get("weekly_contracts", {})
        weekly_contracts = weekly_contracts_raw.get("contracts", []) if isinstance(weekly_contracts_raw, dict) else weekly_contracts_raw
        parsed_weekly_contracts = []
        for q in weekly_contracts:
            if isinstance(q, str):
                try:
                    parsed_weekly_contracts.append(json.loads(q))
                except Exception:
                    sentry_sdk.capture_message(f"Failed to parse weekly contract: {q}")
            elif isinstance(q, dict):
                parsed_weekly_contracts.append(q)
            else:
                sentry_sdk.capture_message(f"Unexpected weekly contract type: {type(q)} value: {q}")
        if parsed_weekly_contracts and isinstance(parsed_weekly_contracts[0], dict):
            wc = parsed_weekly_contracts[0]
            wc_name = wc.get("ContractName") or wc.get("name") or wc.get("contract_name") or "?"
            wc_obj = wc.get("Objectives") or []
            wc_obj_lines = []
            for obj in wc_obj:
                t = obj.get("type")
                tgt = obj.get("target", 0)
                if t == "complete_dailies":
                    wc_obj_lines.append(f"Complete Daily Quests x{tgt}")
                elif t == "total_reps":
                    wc_obj_lines.append(f"Log {tgt} reps")
                elif t == "training_days":
                    wc_obj_lines.append(f"Train {tgt} days")
                elif t == "side_quest":
                    wc_obj_lines.append(f"Side Quest: {obj.get('desc', '?')}")
                else:
                    wc_obj_lines.append(f"{t or '?'}: {tgt}")
            wc_xp = wc.get("XPReward") or wc.get("xpReward") or wc.get("xp_reward") or 0
            wc_buff = wc.get("BuffReward") or wc.get("buffReward") or wc.get("buff_reward")
            weekly_summary = f"**{wc_name}**\nTasks: {', '.join(wc_obj_lines)}\nReward: {wc_xp} XP" + (f", {wc_buff}" if wc_buff else "")
        else:
            weekly_summary = "No weekly contract."
        desc = (
            f"{header}\n{sub_header}\n\nYour quests have been rerolled!\n\n"
            f"**New Daily Quest:**\n{daily_summary}\n\n"
            f"**New Weekly Contract:**\n{weekly_summary}\n"
        )
        embed = discord.Embed(
            title="🔄 Quests Rerolled!",
            description=f"```ansi\n{desc}\n```",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Shadow Archive • Quest Database")
        return embed
    except KeyError as e:
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message(f"Quest reroll KeyError: {e}, user={getattr(user, 'id', None)}, json_data={json_data}")
        embed = discord.Embed(
            title="🔄 Quests Rerolled!",
            description="```ansi\nYour quests have been rerolled, but some data is missing. Please contact support or try again later.\n```",
            color=discord.Color.red()
        )
        embed.set_footer(text="Shadow Archive • Quest Database")
        return embed

def get_reroll_summary_view(bot, user):
    return BackToMenuView(bot, user)

class ConfirmRerollView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        # Red danger button with triangle danger icon
        self.confirm_button = discord.ui.Button(label="⚠️ Confirm Reroll", style=discord.ButtonStyle.danger)
        self.confirm_button.callback = self.confirm_reroll
        self.add_item(self.confirm_button)
        self.cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        self.cancel_button.callback = self.cancel_reroll
        self.add_item(self.cancel_button)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return bool(interaction.user) and interaction.user.id == self.user.id

    async def on_timeout(self):
        self.clear_items()

    async def _check_reroll_limit(self, user_id, bot):
        from features.user.logic.user_data import load_user_data
        import datetime
        today = datetime.date.today().isoformat()
        user_data = await load_user_data(user_id, bot=bot)
        dq_data = user_data.get("daily_quests", {})
        return dq_data.get("rerolled") == today

    @interaction_handler(ephemeral=True, with_loading=True)
    async def confirm_reroll(self, interaction: discord.Interaction):
        try:
            sentry_sdk.capture_message(f"confirm_reroll called for user {self.user.id}")
            
            from features.quests.logic.daily_quests.daily_quest_logic import reroll_daily_quests
            from features.user.logic.user_data import load_user_data, save_user_data
            import datetime
            user_id = self.user.id
            today = datetime.date.today().isoformat()
            # Always force cache invalidation and fetch fresh user data
            await invalidate_user_json_cache(self.bot, user_id)
            user_data = await load_user_data(user_id, bot=self.bot)
            dq_data = user_data.get("daily_quests", {})
            rerolled_flag = dq_data.get("rerolled")
            sentry_sdk.capture_message(f"[REROLL CHECK] user={user_id} rerolled_flag={repr(rerolled_flag)} source=pre-reroll")
            print(f"[REROLL CHECK] user={user_id} rerolled_flag={repr(rerolled_flag)} source=pre-reroll")
            # Only block reroll if rerolled is a non-empty string and equals today
            reroll_blocked = isinstance(rerolled_flag, str) and rerolled_flag == today
            
            if reroll_blocked:
                embed = build_reroll_confirm_embed(self.user, already_rerolled=True, add_back_button=True)
                view = get_reroll_limit_view(self.bot, self.user)
                await interaction.edit_original_response(embed=embed, view=view)
                return
            # Actually reroll (generates 3-5 quests with random tiers)
            await reroll_daily_quests(user_id, bot=self.bot)
            # After reroll, set rerolled flag and save, then show success embed directly
            await invalidate_user_json_cache(self.bot, user_id)
            user_data = await load_user_data(user_id, bot=self.bot)
            dq_data = user_data.get("daily_quests", {})
            dq_data["rerolled"] = today
            user_data["daily_quests"] = dq_data
            await save_user_data(user_id, user_data, bot=self.bot)
            await invalidate_user_json_cache(self.bot, user_id)
            embed = await build_quest_reroll_embed(self.bot, self.user)
            view = get_reroll_summary_view(self.bot, self.user)
            self.clear_items()
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"[REROLL ERROR] {e}")
            try:
                await interaction.edit_original_response(content="❌ An error occurred while processing your reroll. Please try again or contact support.", embed=None, view=None)
            except Exception:
                pass

    async def cancel_reroll(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            from ui.quest_panel import QuestPanel
            view = await QuestPanel.build_view(self.bot, self.user)
            embed = await build_quest_panel_embed(self.bot, self.user)
            self.clear_items()
            return embed, view
        
        await run_with_animation(interaction, do_work())

class BackToMenuView(discord.ui.View):
    def __init__(self, bot, user: Union[discord.User, discord.Member]):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.back_button = discord.ui.Button(label="Back to Menu", style=discord.ButtonStyle.primary)
        self.back_button.callback = self.back_to_menu
        self.add_item(self.back_button)

    async def back_to_menu(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            from features.quests.ui.quest_panel import QuestPanel
            view = await QuestPanel.build_view(self.bot, self.user)
            embed = await QuestPanel.render_embed(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

class RerollLimitView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.back_button = discord.ui.Button(label="Back to Menu", style=discord.ButtonStyle.primary)
        self.back_button.callback = self.back_to_menu
        self.add_item(self.back_button)

    async def back_to_menu(self, interaction: discord.Interaction):
        from shared.utils.ui_helpers import run_with_animation
        
        async def do_work():
            from features.quests.ui.quest_panel import QuestPanel
            view = await QuestPanel.build_view(self.bot, self.user)
            embed = await QuestPanel.render_embed(self.bot, self.user)
            return embed, view
        
        await run_with_animation(interaction, do_work())

# --- RPG-style reroll confirmation embed builder ---
def build_reroll_confirm_embed(user, already_rerolled=False, add_back_button=False, bot=None):
    from shared.utils.ui_styles import get_panel_sub_header
    from shared.utils.headers import get_system_status_header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("quest_reroll")
    if already_rerolled:
        desc = f"{header}\n{sub_header}\n\nYou can only reroll your daily quests once per day. Try again tomorrow."
        embed = discord.Embed(description=f"```ansi\n{desc}\n```", color=discord.Color.red())
    else:
        desc = f"{header}\n{sub_header}\n\nAre you sure you want to reroll your daily quests? This cannot be undone.\n\nYou can only reroll once per day."
        embed = discord.Embed(description=f"```ansi\n{desc}\n```", color=discord.Color.orange())
    embed.set_footer(text="Shadow Archive • Quest Database")
    return embed

def get_reroll_limit_view(bot, user):
    return RerollLimitView(bot, user)
