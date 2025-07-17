"""
Weekly Contract Panel UI
Simplified version for the new quest system
"""
import discord
from typing import Optional

async def update_weekly_progress(user_id: int, bot, movement: Optional[str] = None, count: int = 1):
    """Update weekly quest progress - placeholder implementation"""
    # This is a placeholder function to prevent import errors
    # The actual implementation will be added when weekly quests are fully implemented
    pass

def create_weekly_contract_completion_embed(contract: dict) -> discord.Embed:
    """Create embed for weekly contract completion"""
    reward = f"+{contract.get('XPReward', 0)} XP"
    if buff := contract.get('BuffReward'):
        reward += f", {buff}"
    
    return discord.Embed(
        title="🏆 Contract Complete", 
        description=f"Completed: **{contract.get('ContractName', 'Unknown Contract')}**!\nRewards: {reward}", 
        color=discord.Color.gold()
    )