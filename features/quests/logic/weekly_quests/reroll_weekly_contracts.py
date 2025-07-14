from datetime import date
from features.user.logic.user_data import load_user_data, save_user_data

async def reroll_weekly_contracts(user_id: int):
    """Force reroll of weekly contracts for the current week. Preserves active contract if possible."""
    data = await load_user_data(user_id)
    today = date.today()
    week_key = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]}"
    wc = data.get("weekly_contracts", {})
    active_tier = None
    for contract in wc.get("contracts", []):
        if contract.get("Active"):
            active_tier = contract.get("Tier")
            break
    new_contracts = await _generate_weekly_contracts(user_id, bot=None)
    # If there was an active contract, set the same tier as active in the new list
    if active_tier is not None:
        for contract in new_contracts:
            if contract.get("Tier") == active_tier:
                contract["Active"] = True
                contract["_completed_flag"] = False
                # Optionally reset progress if needed
    data["weekly_contracts"] = {"week": week_key, "contracts": new_contracts}
    await save_user_data(user_id, data)
    return True
from .weekly_contract_logic import _generate_weekly_contracts
