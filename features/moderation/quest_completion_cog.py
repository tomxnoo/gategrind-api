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

    @commands.command(name="complete_quest", aliases=["cq"])
    @commands.is_owner()  # Only bot owner can use this command
    async def complete_quest_admin(self, ctx, user: Optional[discord.User] = None, quest_index: Optional[int] = None):
        """Complete a quest for a user (admin/test only). Usage: !complete_quest @user [quest_index]"""
        # Delete the user's command message for cleaner chat
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except discord.Forbidden:
            pass  # No permission to delete
        
        user_id = user.id if user else ctx.author.id
        target_user = user if user else ctx.author
        
        try:
            # Show loading UI for quest completion operations
            if quest_index is not None:
                loading_embed = render_loading_embed(target_user, dot_count=1)
                loading_message = await ctx.send(embed=loading_embed, delete_after=30)
            
            # Get user's current quests
            quests = await get_today_quests(user_id, bot=self.bot)
            
            if not quests:
                if quest_index is not None:
                    await loading_message.delete()
                embed = discord.Embed(
                    title="❌ No Quests Found",
                    description=f"No daily quests found for {target_user.display_name}.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            # If no quest index specified, show available quests
            if quest_index is None:
                embed = discord.Embed(
                    title="📋 Available Quests",
                    description=f"Quests for {target_user.display_name}:",
                    color=discord.Color.blue()
                )
                
                for i, quest in enumerate(quests, 1):
                    status = "✅ Completed" if quest.get("_completed_flag") or quest.get("Completed") else ("🔥 Active" if quest.get("active") or quest.get("Active") else "⏸️ Inactive")
                    quest_name = quest.get("QuestName", quest.get("name", f"Quest {i}"))
                    movements = ", ".join(quest.get("Movements", quest.get("movements", [])))
                    xp_reward = quest.get("XPReward", quest.get("xp_reward", 0))
                    embed.add_field(
                        name=f"{i}. {quest_name} ({status})",
                        value=f"Movements: {movements}\nXP Reward: {xp_reward}",
                        inline=False
                    )
                
                embed.set_footer(text="Use !complete_quest @user <quest_number> to complete a specific quest")
                await ctx.send(embed=embed, delete_after=30)
                return
            
            # Validate quest index
            if quest_index < 1 or quest_index > len(quests):
                await loading_message.delete()
                embed = discord.Embed(
                    title="❌ Invalid Quest Index",
                    description=f"Please choose between 1 and {len(quests)}.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            quest = quests[quest_index - 1]
            
            # Check if already completed
            if quest.get("_completed_flag") or quest.get("Completed"):
                await loading_message.delete()
                embed = discord.Embed(
                    title="❌ Quest Already Completed",
                    description=f"Quest {quest_index} is already completed.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)
                return
            
            # Update loading message with more dots for animation
            processing_embed = render_loading_embed(target_user, dot_count=3)
            await loading_message.edit(embed=processing_embed)
            
            # Complete the quest
            async with self.bot.db_pool.acquire() as conn:
                user_data = await get_unified_user_data(conn, user_id, self.bot)
                
                # Mark quest as completed (handle both field name formats)
                quest["_completed_flag"] = True
                quest["Completed"] = True
                quest["active"] = False
                quest["Active"] = False
                
                # Complete all progress for the quest (handle both field name formats)
                movements = quest.get("Movements", quest.get("movements", []))
                targets = quest.get("Targets", quest.get("target", {}))
                progress = quest.get("Progress", quest.get("progress", {}))
                
                for movement in movements:
                    if movement in progress:
                        # Handle both progress formats
                        if isinstance(progress[movement], dict):
                            progress[movement]["sets"] = targets.get(movement, targets.get("sets", 1))
                            progress[movement]["reps"] = 0
                        else:
                            progress[movement] = targets.get(movement, 0)
                
                # Add to completed quests history
                if "completed_quests" not in user_data:
                    user_data["completed_quests"] = []
                
                completed_quest_entry = {
                    "quest": quest.copy(),
                    "completed_at": discord.utils.utcnow().isoformat(),
                    "completed_by": "admin"
                }
                user_data["completed_quests"].append(completed_quest_entry)
                
                # Award XP - Get the correct XP reward value
                xp_reward = quest.get("XPReward", quest.get("xp_reward", 0))
                if xp_reward > 0:
                    # Call add_xp with connection for proper transaction handling
                    await add_xp(conn, user_id, xp_reward, bot=self.bot)
                
                # Save updated data - THIS WAS MISSING!
                await update_user_json_data(conn, user_id, user_data, bot=self.bot)
                
                # Invalidate cache to ensure fresh data
                await invalidate_user_json_cache(self.bot, user_id)
                await get_or_cache_user_json_data(self.bot, user_id)
            
            # Small delay to show the processing step
            await asyncio.sleep(0.5)
            
            quest_name = quest.get("QuestName", quest.get("name", f"Quest {quest_index}"))
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Quest Completed!",
                description=f"**{quest_name}** has been completed for {target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="XP Awarded", value=f"+{xp_reward} XP", inline=True)
            embed.add_field(name="Completed By", value="Admin Override", inline=True)
            embed.add_field(name="Status", value="✅ Logged to History", inline=True)
            embed.set_footer(text="Quest completion processed successfully")
            
            # Replace loading message with success message (auto-delete after 15 seconds)
            await loading_message.edit(embed=embed)
            await asyncio.sleep(15)
            try:
                await loading_message.delete()
            except discord.NotFound:
                pass
            
            print(f"[DEBUG] Admin completed quest {quest_index} for user {user_id} (+{xp_reward} XP)")
            
        except Exception as e:
            # Clean up loading message on error
            if quest_index is not None and 'loading_message' in locals():
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

    # Alternative slash command version for true ephemeral responses
    @app_commands.command(name="complete_quest", description="Complete a quest for a user (admin only)")
    @app_commands.describe(
        user="The user to complete a quest for",
        quest_index="The quest number to complete (1-based index)"
    )
    async def complete_quest_slash(self, interaction: discord.Interaction, user: discord.User, quest_index: int = None):
        """Slash command version with true ephemeral support"""
        # Check if user is bot owner
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return
        
        user_id = user.id
        target_user = user
        
        try:
            # Defer the response as ephemeral
            await interaction.response.defer(ephemeral=True)
            
            # Show loading UI for quest completion operations
            if quest_index is not None:
                loading_embed = render_loading_embed(target_user, dot_count=1)
                await interaction.followup.send(embed=loading_embed, ephemeral=True)
            
            # Get user's current quests
            quests = await get_today_quests(user_id, bot=self.bot)
            
            if not quests:
                embed = discord.Embed(
                    title="❌ No Quests Found",
                    description=f"No daily quests found for {target_user.display_name}.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # If no quest index specified, show available quests
            if quest_index is None:
                embed = discord.Embed(
                    title="📋 Available Quests",
                    description=f"Quests for {target_user.display_name}:",
                    color=discord.Color.blue()
                )
                
                for i, quest in enumerate(quests, 1):
                    status = "✅ Completed" if quest.get("_completed_flag") or quest.get("Completed") else ("🔥 Active" if quest.get("active") or quest.get("Active") else "⏸️ Inactive")
                    quest_name = quest.get("QuestName", quest.get("name", f"Quest {i}"))
                    movements = ", ".join(quest.get("Movements", quest.get("movements", [])))
                    xp_reward = quest.get("XPReward", quest.get("xp_reward", 0))
                    embed.add_field(
                        name=f"{i}. {quest_name} ({status})",
                        value=f"Movements: {movements}\nXP Reward: {xp_reward}",
                        inline=False
                    )
                
                embed.set_footer(text="Use /complete_quest user:<user> quest_index:<number> to complete a specific quest")
                await interaction.edit_original_response(embed=embed)
                return
            
            # Validate quest index
            if quest_index < 1 or quest_index > len(quests):
                embed = discord.Embed(
                    title="❌ Invalid Quest Index",
                    description=f"Please choose between 1 and {len(quests)}.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            quest = quests[quest_index - 1]
            
            # Check if already completed
            if quest.get("_completed_flag") or quest.get("Completed"):
                embed = discord.Embed(
                    title="❌ Quest Already Completed",
                    description=f"Quest {quest_index} is already completed.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Update loading message with more dots for animation
            processing_embed = render_loading_embed(target_user, dot_count=3)
            await interaction.edit_original_response(embed=processing_embed)
            
            # Complete the quest (same logic as prefix command)
            async with self.bot.db_pool.acquire() as conn:
                user_data = await get_unified_user_data(conn, user_id, self.bot)
                
                # Mark quest as completed
                quest["_completed_flag"] = True
                quest["Completed"] = True
                quest["active"] = False
                quest["Active"] = False
                
                # Complete all progress for the quest
                movements = quest.get("Movements", quest.get("movements", []))
                targets = quest.get("Targets", quest.get("target", {}))
                progress = quest.get("Progress", quest.get("progress", {}))
                
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
                    "quest": quest.copy(),
                    "completed_at": discord.utils.utcnow().isoformat(),
                    "completed_by": "admin"
                }
                user_data["completed_quests"].append(completed_quest_entry)
                
                # Award XP
                xp_reward = quest.get("XPReward", quest.get("xp_reward", 0))
                if xp_reward > 0:
                    await add_xp(conn, user_id, xp_reward, bot=self.bot)
                
                # Save updated data
                await update_user_json_data(conn, user_id, user_data, bot=self.bot)
                
                # Invalidate cache
                await invalidate_user_json_cache(self.bot, user_id)
                await get_or_cache_user_json_data(self.bot, user_id)
            
            # Small delay for UX
            await asyncio.sleep(0.5)
            
            quest_name = quest.get("QuestName", quest.get("name", f"Quest {quest_index}"))
            
            # Create success embed
            embed = discord.Embed(
                title="✅ Quest Completed!",
                description=f"**{quest_name}** has been completed for {target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="XP Awarded", value=f"+{xp_reward} XP", inline=True)
            embed.add_field(name="Completed By", value="Admin Override", inline=True)
            embed.add_field(name="Status", value="✅ Logged to History", inline=True)
            embed.set_footer(text="Quest completion processed successfully")
            
            # Update with success message
            await interaction.edit_original_response(embed=embed)
            
            print(f"[DEBUG] Admin completed quest {quest_index} for user {user_id} (+{xp_reward} XP)")
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Quest Completion Failed",
                description=f"Error completing quest: {str(e)}",
                color=discord.Color.red()
            )
            error_embed.set_footer(text="Please try again or check logs for details")
            await interaction.edit_original_response(embed=error_embed)
            print(f"[ERROR] Failed to complete quest: {e}")


async def setup(bot):
    await bot.add_cog(QuestCompletionCog(bot))