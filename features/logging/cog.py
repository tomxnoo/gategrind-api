import discord  # py-cord
from datetime import datetime, timedelta
from discord.ext import commands  # py-cord
from features.logging.ui.view import LogRepsPanel, render_log_complete_embed
from features.quests.ui.quest_completion_ui import render_quest_completion_panel
from features.user.ui.level_up_view import render_level_up_embed
from features.quests.ui.weekly.weekly_contract_panel import create_weekly_contract_completion_embed
from core.api_client import api_client

class MovementLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_log_reps(self, interaction: discord.Interaction, movement: str, reps: int, sets: int = 1):
        from shared.utils.ui_helpers import run_with_animation
        
        user = interaction.user

        async def do_work():
            try:
                # Call API to log reps
                log_data = {
                    "movement": movement,
                    "reps": reps,
                    "sets": sets,
                    "notes": None
                }
                
                result = await api_client.log_reps(user, log_data)
                
                # Extract data from API response
                api_data = result.get("data", {})
                total_reps = api_data.get("total_reps", reps * sets)
                xp_gained = api_data.get("xp_gained", 0)
                completed_quests = api_data.get("completed_quests", [])
                weekly_completed = api_data.get("weekly_completed", [])
                leveled_up = api_data.get("leveled_up", False)
                new_level = api_data.get("new_level")
                
                # Get user profile for rendering embed
                profile_data = await api_client.get_user_profile(user)
                user_data = profile_data.get("data", {})
                
                # Get daily quests and weekly contracts for embed
                daily_quests_response = await api_client.get_daily_quests(user)
                daily_quests = daily_quests_response if isinstance(daily_quests_response, list) else []
                
                # Render completion embed
                embed, view = await render_log_complete_embed(
                    user, movement, reps, xp_gained, 
                    user_data=user_data, 
                    daily_quests=daily_quests, 
                    weekly_contracts=[]  # TODO: Add weekly contracts API
                )
                
                # Store completion data for follow-up messages
                self._last_log_result = {
                    "completed_quests": completed_quests,
                    "weekly_completed": weekly_completed,
                    "leveled_up": leveled_up,
                    "new_level": new_level
                }
                
                return embed, view
                
            except Exception as e:
                # Handle API errors gracefully
                if "429" in str(e) or "Cooldown active" in str(e):
                    # Extract cooldown message from error
                    error_msg = str(e)
                    if "Cooldown active" in error_msg:
                        cooldown_msg = error_msg.split("detail=")[-1].strip("'\"")
                        await interaction.response.send_message(
                            f"⏳ {cooldown_msg}", ephemeral=True
                        )
                        return None, None
                
                print(f"[ERROR] Failed to log reps via API: {e}")
                await interaction.response.send_message(
                    "❌ Failed to log reps. Please try again later.", ephemeral=True
                )
                return None, None
        
        # Use run_with_animation for the main work
        result = await run_with_animation(interaction, do_work)
        
        # Handle follow-up notifications if we have results
        if hasattr(self, '_last_log_result') and self._last_log_result:
            log_result = self._last_log_result
            
            # Send level up notification if user leveled up
            if log_result.get("leveled_up", False):
                level_up_embed = await render_level_up_embed(
                    self.bot, user, log_result["new_level"]
                )
                await interaction.followup.send(embed=level_up_embed, ephemeral=True)

            # Send quest completion notifications as follow-up ephemeral messages
            completed_quests = log_result.get('completed_quests', [])
            for quest in completed_quests:
                completion_embed = render_quest_completion_panel(
                    quest, user if isinstance(user, discord.User) else user._user
                )
                await interaction.followup.send(embed=completion_embed, ephemeral=True)

            # Send weekly contract completion notifications as follow-up ephemeral messages
            weekly_completed = log_result.get('weekly_completed', [])
            for contract in weekly_completed:
                weekly_completion_embed = create_weekly_contract_completion_embed(contract)
                await interaction.followup.send(embed=weekly_completion_embed, ephemeral=True)
            
            # Clean up
            delattr(self, '_last_log_result')

async def setup(bot: commands.Bot):
    await bot.add_cog(MovementLogger(bot))