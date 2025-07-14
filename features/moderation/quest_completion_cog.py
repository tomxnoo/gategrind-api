import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio

from features.quests.logic.daily_quests.daily_quest_logic import get_today_quests, update_quest_progress
from features.user.logic.user_data import load_user_data, save_user_data
from features.user.logic.xp_engine import add_xp
from core.database.db import get_unified_user_data, update_user_json_data
from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
from shared.utils.headers import render_loading_embed


class QuestCompletionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processing_users = set()  # Track users currently being processed

    @commands.command(name="complete_quest", aliases=["cq"])
    @commands.is_owner()  # Only bot owner can use this command
    async def complete_quest_admin(self, ctx, user: Optional[discord.User] = None, quest_type: Optional[str] = None):
        """Complete a quest for a user. Usage: !cq @user 1 (daily) or !cq @user 2 (weekly)"""
        # Delete the user's command message for cleaner chat
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except discord.Forbidden:
            pass  # No permission to delete
        
        user_id = user.id if user else ctx.author.id
        target_user = user if user else ctx.author
        
        # Spam protection
        if user_id in self.processing_users:
            embed = discord.Embed(
                title="⏳ Processing in Progress",
                description=f"Quest completion for {target_user.display_name} is already being processed.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
            return
        
        try:
            self.processing_users.add(user_id)
            
            # Parse quest type (1 = daily, 2 = weekly)
            if quest_type not in ["1", "2"]:
                embed = discord.Embed(
                    title="📋 Quest Completion Help",
                    description=f"**Usage for {target_user.display_name}:**\n\n"
                               "🔹 `!cq @user 1` - Complete currently active daily quest\n"
                               "🔹 `!cq @user 2` - Complete currently active weekly quest",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Choose 1 for daily or 2 for weekly quest completion")
                await ctx.send(embed=embed, delete_after=20)
                return
            
            # Show loading UI
            loading_embed = render_loading_embed(target_user, dot_count=1)
            loading_message = await ctx.send(embed=loading_embed, delete_after=30)
            
            if quest_type == "1":
                # Complete daily quest
                result = await self._complete_daily_quest(user_id, target_user)
            else:
                # Complete weekly quest
                result = await self._complete_weekly_quest(user_id, target_user)
            
            if not result["success"]:
                await loading_message.delete()
                embed = discord.Embed(
                    title="❌ Quest Completion Failed",
                    description=result["message"],
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            # Update loading message with more dots for animation
            processing_embed = render_loading_embed(target_user, dot_count=3)
            await loading_message.edit(embed=processing_embed)
            
            # Small delay to show the processing step
            await asyncio.sleep(0.5)
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Quest Completed!",
                description=f"**{result['quest_name']}** has been completed for {target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="XP Awarded", value=f"+{result['xp_reward']} XP", inline=True)
            embed.add_field(name="Completed By", value="Admin Override", inline=True)
            embed.add_field(name="Status", value="✅ Logged to History", inline=True)
            embed.set_footer(text="Quest completion processed successfully")
            
            # Replace loading message with success message
            await loading_message.edit(embed=embed)
            await asyncio.sleep(15)
            try:
                await loading_message.delete()
            except discord.NotFound:
                pass
            
            print(f"[DEBUG] Admin completed {result['quest_type']} quest for user {user_id} (+{result['xp_reward']} XP)")
            
        except Exception as e:
            # Clean up loading message on error
            if 'loading_message' in locals():
                try:
                    await loading_message.delete()
                except:
                    pass
            
            error_embed = discord.Embed(
                title="❌ Quest Completion Failed",
                description=f"Error completing quest: {str(e)}",
                color=discord.Color.red()
            )
            error_embed.set_footer(text="Please try again or check logs for details")
            await ctx.send(embed=error_embed, delete_after=10)
            print(f"[ERROR] Failed to complete quest: {e}")
        finally:
            # Always remove from processing set
            self.processing_users.discard(user_id)
    
    async def _complete_daily_quest(self, user_id: int, target_user: discord.User) -> dict:
        """Complete the currently active daily quest"""
        try:
            # Get user's current daily quests
            quests = await get_today_quests(user_id, bot=self.bot)
            
            if not quests:
                return {
                    "success": False,
                    "message": f"No daily quests found for {target_user.display_name}."
                }
            
            # Find the first active (incomplete) daily quest
            active_quest = None
            quest_index = -1
            for i, quest in enumerate(quests):
                if not (quest.get("_completed_flag") or quest.get("Completed")):
                    active_quest = quest
                    quest_index = i
                    break
            
            if not active_quest:
                return {
                    "success": False,
                    "message": f"No active daily quests found for {target_user.display_name}. All quests are already completed."
                }
            
            # Complete the quest
            async with self.bot.db_pool.acquire() as conn:
                user_data = await get_unified_user_data(conn, user_id, self.bot)
                
                # Update the quest in the actual daily_quests array
                daily_quests_data = user_data.get("daily_quests", {})
                if "quests" in daily_quests_data and quest_index < len(daily_quests_data["quests"]):
                    stored_quest = daily_quests_data["quests"][quest_index]
                    
                    # Mark quest as completed
                    stored_quest["_completed_flag"] = True
                    stored_quest["Completed"] = True
                    stored_quest["active"] = False
                    stored_quest["Active"] = False
                    stored_quest["completed_at"] = discord.utils.utcnow().isoformat()
                    stored_quest["completed_by"] = "admin"
                    
                    # Complete all progress for the quest
                    movements = stored_quest.get("Movements", stored_quest.get("movements", []))
                    targets = stored_quest.get("Targets", stored_quest.get("target", {}))
                    progress = stored_quest.get("Progress", stored_quest.get("progress", {}))
                    
                    for movement in movements:
                        if movement in progress:
                            if isinstance(progress[movement], dict):
                                progress[movement]["sets"] = targets.get(movement, targets.get("sets", 1))
                                progress[movement]["reps"] = 0
                            else:
                                progress[movement] = targets.get(movement, 0)
                
                # Add to completed quests history
                if "completed_quests" not in user_data:
                    user_data["completed_quests"] = []
                
                completed_quest_entry = {
                    "quest": active_quest.copy(),
                    "completed_at": discord.utils.utcnow().isoformat(),
                    "completed_by": "admin",
                    "quest_type": "daily"
                }
                user_data["completed_quests"].append(completed_quest_entry)
                
                # Award XP - Get the correct XP reward value
                xp_reward = active_quest.get("XPReward", active_quest.get("xp_reward", 0))
                if xp_reward > 0:
                    # Fix: Pass the connection properly
                    await add_xp(conn, user_id, xp_reward, bot=self.bot)

                # Save updated data
                await update_user_json_data(conn, user_id, user_data, bot=self.bot)
                
                # Invalidate cache to ensure fresh data
                await invalidate_user_json_cache(self.bot, user_id)
            
            quest_name = active_quest.get("QuestName", active_quest.get("name", "Daily Quest"))
            
            return {
                "success": True,
                "quest_name": quest_name,
                "xp_reward": xp_reward,
                "quest_type": "daily"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error completing daily quest: {str(e)}"
            }
    
    async def _complete_weekly_quest(self, user_id: int, target_user: discord.User) -> dict:
        """Complete the currently active weekly quest"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                user_data = await get_unified_user_data(conn, user_id, self.bot)
                
                # Get weekly contracts
                weekly_contracts = user_data.get("weekly_contracts", {}).get("contracts", [])
                
                if not weekly_contracts:
                    return {
                        "success": False,
                        "message": f"No weekly contracts found for {target_user.display_name}."
                    }
                
                # Find the active weekly contract
                active_contract = None
                contract_index = -1
                for i, contract in enumerate(weekly_contracts):
                    if contract.get("active") or contract.get("Active"):
                        if not (contract.get("_completed_flag") or contract.get("Completed")):
                            active_contract = contract
                            contract_index = i
                            break
                
                if not active_contract:
                    return {
                        "success": False,
                        "message": f"No active weekly contract found for {target_user.display_name}. Either no contract is active or it's already completed."
                    }
                
                # In _complete_weekly_quest method, ensure all completion flags are set:
                # Complete the weekly contract
                active_contract["_completed_flag"] = True
                active_contract["Completed"] = True
                active_contract["active"] = False
                active_contract["Active"] = False
                active_contract["completed_at"] = discord.utils.utcnow().isoformat()
                active_contract["completed_by"] = "admin"
                
                # Complete all objectives
                objectives = active_contract.get("Objectives", [])
                progress = active_contract.get("Progress", {})
                
                for obj in objectives:
                    obj_type = obj.get("type")
                    target = obj.get("target", 0)
                    if obj_type:
                        progress[obj_type] = target
                
                active_contract["Progress"] = progress
                
                # Add to completed quests history
                if "completed_quests" not in user_data:
                    user_data["completed_quests"] = []
                
                completed_quest_entry = {
                    "quest": active_contract.copy(),
                    "completed_at": discord.utils.utcnow().isoformat(),
                    "completed_by": "admin",
                    "quest_type": "weekly"
                }
                user_data["completed_quests"].append(completed_quest_entry)
                
                # Award XP
                xp_reward = active_contract.get("XPReward", active_contract.get("xp_reward", 0))
                if xp_reward > 0:
                    # Fix: Pass the connection properly
                    await add_xp(conn, user_id, xp_reward, bot=self.bot)
                
                # Save updated data
                await update_user_json_data(conn, user_id, user_data, bot=self.bot)
                
                # Invalidate cache
                await invalidate_user_json_cache(self.bot, user_id)
            
            contract_name = active_contract.get("ContractName", active_contract.get("name", "Weekly Contract"))
            
            return {
                "success": True,
                "quest_name": contract_name,
                "xp_reward": xp_reward,
                "quest_type": "weekly"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error completing weekly contract: {str(e)}"
            }

    # Alternative slash command version for true ephemeral responses
    @app_commands.command(name="complete_quest", description="Complete a quest for a user (admin only)")
    @app_commands.describe(
        user="The user to complete a quest for",
        quest_type="1 for daily quest, 2 for weekly quest"
    )
    async def complete_quest_slash(self, interaction: discord.Interaction, user: discord.User, quest_type: int):
        """Slash command version with true ephemeral support"""
        # Check if user is bot owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return
        
        if quest_type not in [1, 2]:
            await interaction.response.send_message("❌ Quest type must be 1 (daily) or 2 (weekly).", ephemeral=True)
            return
        
        user_id = user.id
        
        # Spam protection
        if user_id in self.processing_users:
            await interaction.response.send_message(
                f"⏳ Quest completion for {user.display_name} is already being processed.",
                ephemeral=True
            )
            return
        
        try:
            self.processing_users.add(user_id)
            
            # Defer the response as ephemeral
            await interaction.response.defer(ephemeral=True)
            
            if quest_type == 1:
                result = await self._complete_daily_quest(user_id, user)
            else:
                result = await self._complete_weekly_quest(user_id, user)
            
            if not result["success"]:
                embed = discord.Embed(
                    title="❌ Quest Completion Failed",
                    description=result["message"],
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Quest Completed!",
                description=f"**{result['quest_name']}** has been completed for {user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="XP Awarded", value=f"+{result['xp_reward']} XP", inline=True)
            embed.add_field(name="Completed By", value="Admin Override", inline=True)
            embed.add_field(name="Status", value="✅ Logged to History", inline=True)
            embed.set_footer(text="Quest completion processed successfully")
            
            await interaction.edit_original_response(embed=embed)
            
            print(f"[DEBUG] Admin completed {result['quest_type']} quest for user {user_id} (+{result['xp_reward']} XP)")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Quest Completion Failed",
                description=f"Error completing quest: {str(e)}",
                color=discord.Color.red()
            )
            error_embed.set_footer(text="Please try again or check logs for details")
            await interaction.edit_original_response(embed=error_embed)
            print(f"[ERROR] Failed to complete quest: {e}")
        finally:
            # Always remove from processing set
            self.processing_users.discard(user_id)


async def setup(bot):
    await bot.add_cog(QuestCompletionCog(bot))