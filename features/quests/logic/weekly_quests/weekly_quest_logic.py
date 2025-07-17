"""
Weekly Quest Logic - Core functionality for weekly quest management
"""

from datetime import datetime, timedelta, date
from features.quests.logic.quest_templates import generate_weekly_contract, get_user_tier_from_level
from features.user.logic.xp_engine import add_xp
from core.database.db import get_unified_user_data, update_user_json_data

def _require_bot(bot):
    """Helper function to ensure bot is provided"""
    if bot is None:
        raise ValueError("Bot instance is required for this operation")

async def abandon_weekly_contract(user_id: int, bot=None):
    """Abandon the user's current weekly contract"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        weekly_contracts = user_data.get("weekly_contracts", {})
        if "contracts" in weekly_contracts:
            for contract in weekly_contracts["contracts"]:
                contract["Active"] = False
                contract["active"] = False
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def abandon_specific_contract(user_id: int, contract_tier: int, bot=None):
    """Abandon a specific weekly contract by tier"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        weekly_contracts = user_data.get("weekly_contracts", {})
        if "contracts" in weekly_contracts:
            for contract in weekly_contracts["contracts"]:
                contract_tier_value = contract.get("tier") or contract.get("Tier")
                if str(contract_tier_value) == str(contract_tier):
                    contract["Active"] = False
                    contract["active"] = False
                    break
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return True

async def update_weekly_progress(user_id: int, bot, movement: str, reps: int):
    """Update progress on weekly contracts"""
    _require_bot(bot)
    async with bot.db_pool.acquire() as conn:
        user_data = await get_unified_user_data(conn, user_id, bot)
        weekly_contracts = user_data.get("weekly_contracts", {})
        
        completed_contracts = []
        
        if "contracts" in weekly_contracts:
            for contract in weekly_contracts["contracts"]:
                if contract.get("Active", False) or contract.get("active", False):
                    # Check if this movement matches the contract
                    contract_movement = contract.get("movement", "").lower()
                    if movement.lower() in contract_movement or contract_movement in movement.lower():
                        # Update progress
                        current_progress = contract.get("progress", 0)
                        target = contract.get("target", contract.get("Target", 0))
                        
                        new_progress = current_progress + reps
                        contract["progress"] = new_progress
                        
                        # Check if completed
                        if new_progress >= target:
                            contract["Active"] = False
                            contract["active"] = False
                            contract["completed"] = True
                            contract["completed_at"] = datetime.utcnow().isoformat()
                            
                            # Award XP
                            xp_reward = contract.get("xp_reward", 100)
                            await add_xp(user_id, xp_reward)
                            
                            completed_contracts.append(contract)
        
        await update_user_json_data(conn, user_id, user_data, bot=bot)
        return completed_contracts