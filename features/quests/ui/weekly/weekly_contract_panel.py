# ui/weekly_contract_panel.py
import discord

from discord.ui import View, Button
from datetime import date
from typing import Union, Dict, Any, List, Optional
from core.database.db import get_unified_user_data, update_user_json_data
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
from features.quests.logic.quest_templates import generate_weekly_contract, get_user_tier_from_level
from features.quests.ui.weekly.weekly_contract_ansi import render_weekly_contract_ansi_block
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header
from discord.ext import commands
from features.quests.ui.quest_panel_common import QuestSelectorView, QuestAcceptDeclineView

_weekly_pages: Dict[int, int] = {}

# region: --- Data Functions ---

async def load_user_data(user_id: int, bot) -> dict: return await get_or_cache_user_json_data(bot, user_id)

async def save_user_data(user_id: int, data: dict, bot) -> None:
    conn = getattr(bot, 'db_pool', None)
    if not conn: raise RuntimeError("DB pool not found.")
    await update_user_json_data(conn, user_id, data, bot)
    await invalidate_user_json_cache(bot, user_id)

async def _generate_weekly_contracts(user_id: int, user_data: dict, bot) -> List[Dict[str, Any]]:
    user_level = user_data.get("level", 1)
    base_tier = get_user_tier_from_level(user_level)
    return [generate_weekly_contract(min(base_tier + i, 5)) for i in range(3)]

async def get_weekly_contracts(user_id: int, bot) -> List[Dict[str, Any]]:
    user_data = await load_user_data(user_id, bot)
    today = date.today()
    current_week = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]}"
    wc_data = user_data.get("weekly_contracts", {})
    contracts = wc_data.get("contracts", [])
    if wc_data.get("week") != current_week or not contracts:
        contracts = await _generate_weekly_contracts(user_id, user_data, bot)
        user_data["weekly_contracts"] = {"week": current_week, "contracts": contracts, "progress": {}}
        await save_user_data(user_id, user_data, bot)
    contracts.sort(key=lambda c: not c.get("active", False))
    return contracts

async def activate_weekly_contract(user_id: int, contract_tier: int, bot):
    data = await load_user_data(user_id, bot)
    contracts = data.get("weekly_contracts", {}).get("contracts", [])
    for c in contracts:
        c["active"] = c.get("Tier") == contract_tier
        if c["active"]: c["_completed_flag"] = False
    await save_user_data(user_id, data, bot)
    _weekly_pages[user_id] = 0

async def abandon_active_weekly_contract(user_id: int, bot):
    data = await load_user_data(user_id, bot)
    contracts = data.get("weekly_contracts", {}).get("contracts", [])
    for c in contracts: c["active"] = False
    await save_user_data(user_id, data, bot)
    _weekly_pages.pop(user_id, None)
    
async def update_weekly_progress(user_id: int, bot, movement: Optional[str] = None, count: int = 1):
    pass

# endregion

# region: --- Embeds ---

def build_weekly_contract_panel_embed(user: Union[discord.User, discord.Member], contract: dict, page: int, total: int) -> discord.Embed:
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("weekly_contract")
    ansi_block = render_weekly_contract_ansi_block(contract, user)
    return discord.Embed(description=f"```ansi\n{header}\n{sub_header}\n\n{ansi_block}\n```", color=discord.Color.dark_purple()).set_footer(text=f"Shadow Archive • Contract {page}/{total}")

def render_quest_details_embed(user: Union[discord.User, discord.Member], contract: dict) -> discord.Embed:
    from shared.utils.ui_styles import get_panel_sub_header
    from shared.utils.headers import get_system_status_header
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("weekly_quest")
    lines = [f"**{contract.get('Flavor', '')}**", f"*{contract.get('Lore', '')}*", "\n**Objectives:**"]
    for obj in contract.get("Objectives", []):
        description = obj.get("description", "Unknown")
        lines.append(f"- {description}")
    content = f"{header}\n{sub_header}\n\n**{contract.get('ContractName', '')}**\n\n*{contract.get('Lore', '')}*\n\n**Objectives:**\n" + "\n".join([f"- {desc}" for desc in lines[2:]])
    return discord.Embed(description=f"```ansi\n{content}\n```", color=discord.Color.blurple()).set_footer(text="Shadow Archive • Quest Database")

def render_quest_accepted_embed(user: Union[discord.User, discord.Member], contract: dict) -> discord.Embed:
    header = get_system_status_header(user).replace('```ansi', '').replace('```', '').strip()
    sub_header = get_panel_sub_header("quest_accept")
    
    contract_name = contract.get('ContractName', 'Unknown Contract')
    flavor_text = contract.get('Flavor', 'The contract has been sealed.')
    
    desc = f"{header}\n{sub_header}\n\n**Contract Accepted:** {contract_name}\n\n{flavor_text}"
    
    embed = discord.Embed(
        description=f"```ansi\n{desc}\n```",
        color=discord.Color.green()
    )
    embed.set_footer(text="Shadow Archive • Contract Division")
    return embed

def create_weekly_contract_completion_embed(contract: dict) -> discord.Embed:
    reward = f"+{contract.get('XPReward', 0)} XP" + (f", {buff}" if (buff := contract.get('BuffReward')) else "")
    return discord.Embed(title="🏆 Contract Complete", description=f"Completed: **{contract.get('ContractName')}**!\nRewards: {reward}", color=discord.Color.gold())

# endregion

# region: --- Views and Buttons ---



class WeeklyQuestSelectorView(QuestSelectorView):
    def __init__(self, bot, user_id: int):
        super().__init__(
            bot=bot,
            user_id=user_id,
            get_quests_func=get_weekly_contracts,
            page_dict=_weekly_pages,
            detail_view_class=WeeklyQuestAcceptDeclineView,
            quest_type="weekly"
        )
    async def build_embed(self, bot, quest, user):
        page = _weekly_pages.get(user.id, 0)
        contracts = await get_weekly_contracts(user.id, bot)
        return build_weekly_contract_panel_embed(user, contracts[page], page + 1, len(contracts))


class WeeklyQuestAcceptDeclineView(QuestAcceptDeclineView):
    def __init__(self, bot, user: Union[discord.User, discord.Member], quest: dict, disable_accept=False, quest_type="weekly"):
        super().__init__(bot, user, quest, disable_accept, quest_type)
    
    async def accept_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=False)
        except Exception:
            pass
        
        user_id = self.user.id
        tier = self.quest.get("Tier") or self.quest.get("tier")
        if tier is None:
            tier = 1
        await activate_weekly_contract(user_id, tier, bot=self.bot)
        
        # Invalidate cache to ensure fresh data
        from core.redis_cache import invalidate_user_json_cache
        await invalidate_user_json_cache(self.bot, user_id)
        
        # Reset page index to 0 since active quest will be first
        _weekly_pages[user_id] = 0
        
        contracts = await get_weekly_contracts(user_id, self.bot)
        active_contract = next((c for c in contracts if c.get("active")), None)
        if active_contract is None:
            active_contract = self.quest
        embed = render_quest_accepted_embed(self.user, active_contract)
        view = BackToMenuFromWeeklyAcceptView(self.bot, self.user)
        await interaction.edit_original_response(embed=embed, view=view)
    async def decline_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass
        user_id = self.user.id
        view = WeeklyQuestSelectorView(self.bot, user_id)
        contracts = await get_weekly_contracts(user_id, self.bot)
        index = _weekly_pages.get(user_id, 0)
        embed = build_weekly_contract_panel_embed(self.user, contracts[index], index + 1, len(contracts))
        await interaction.edit_original_response(embed=embed, view=view)

class BackToMenuFromWeeklyAcceptView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.add_item(BackToWeeklyMenuButton(self))

class BackToWeeklyMenuButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="Back to Menu", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        from core.redis_cache import invalidate_user_json_cache
        
        await interaction.response.defer(ephemeral=False)
        
        # Invalidate cache to ensure fresh data
        await invalidate_user_json_cache(self.parent_view.bot, self.parent_view.user.id)
        
        # Reset page index to show active quest first
        _weekly_pages[self.parent_view.user.id] = 0

        view = WeeklyQuestSelectorView(self.parent_view.bot, self.parent_view.user.id)
        await view.refresh_panel(interaction)


# endregion

# region: --- Cog ---

class WeeklyContractsCog(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    @commands.command(name="contracts", aliases=["weekly"])
    async def view_contracts(self, ctx: commands.Context):
        if not ctx.author: return
        
        contracts = await get_weekly_contracts(ctx.author.id, self.bot)
        if not contracts:
            await ctx.send("No weekly contracts are available.")
            return
        
        _weekly_pages[ctx.author.id] = 0
        embed = build_weekly_contract_panel_embed(ctx.author, contracts[0], 1, len(contracts))
        view = WeeklyQuestSelectorView(self.bot, ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    bot.add_cog(WeeklyContractsCog(bot))

# endregion
