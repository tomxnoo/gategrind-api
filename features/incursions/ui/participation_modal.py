# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Union

from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.rep_integration import RepIntegration
from features.incursions.models.incursion import IncursionType

class ParticipationModal(discord.ui.Modal):
    """Modal for logging reps towards an incursion"""
    
    def __init__(self, bot, incursion):
        super().__init__(title=f"Log Reps: {incursion.title}")
        self.bot = bot
        self.incursion = incursion
        
        # Rep count input
        self.rep_input = discord.ui.TextInput(
            label=f"How many {incursion.exercise_type} did you complete?",
            placeholder="Enter number of reps (e.g., 25)",
            required=True,
            max_length=10
        )
        self.add_item(self.rep_input)
        
        # Optional notes input
        self.notes_input = discord.ui.TextInput(
            label="Notes (optional)",
            placeholder="Any additional details about your workout...",
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.notes_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate rep count
            rep_count = int(self.rep_input.value.strip())
            if rep_count <= 0:
                await interaction.response.send_message(
                    "❌ Rep count must be a positive number!", 
                    ephemeral=True
                )
                return
            
            if rep_count > 1000:  # Reasonable upper limit
                await interaction.response.send_message(
                    "❌ Rep count seems too high. Please enter a realistic number.", 
                    ephemeral=True
                )
                return
            
            # Process the rep submission
            rep_integration = RepIntegration(self.bot.db_pool)
            result = await rep_integration.process_incursion_reps(
                user_id=interaction.user.id,
                incursion_id=self.incursion.id,
                exercise_type=self.incursion.exercise_type,
                rep_count=rep_count,
                notes=self.notes_input.value.strip() or None
            )
            
            if result["success"]:
                # Create success embed
                embed = discord.Embed(
                    title="⚡ Reps Logged Successfully!",
                    color=0x00ff00
                )
                
                # Add progress info
                progress = result["new_progress"]
                target = self.incursion.target_reps
                progress_pct = min(100, (progress / target) * 100) if target > 0 else 0
                
                # Progress bar
                filled = int(progress_pct / 10)
                bar = "█" * filled + "░" * (10 - filled)
                
                embed.add_field(
                    name="📊 Your Progress",
                    value=f"[{bar}] {progress}/{target} ({progress_pct:.1f}%)",
                    inline=False
                )
                
                embed.add_field(
                    name="💪 Reps Added",
                    value=f"+{rep_count} {self.incursion.exercise_type}",
                    inline=True
                )
                
                # Check for completion
                if progress >= target:
                    embed.add_field(
                        name="🎉 Incursion Complete!",
                        value=f"Reward: {self.incursion.reward_description}",
                        inline=False
                    )
                    embed.color = 0xffd700  # Gold color for completion
                
                # Add anomaly effects if applicable
                if (self.incursion.incursion_type == IncursionType.ANOMALY and 
                    "anomaly_effects" in result):
                    effects = result["anomaly_effects"]
                    embed.add_field(
                        name="🌀 Anomaly Effects Applied",
                        value=effects,
                        inline=False
                    )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            else:
                # Handle errors
                error_msg = result.get("error", "Unknown error occurred")
                await interaction.response.send_message(
                    f"❌ Failed to log reps: {error_msg}", 
                    ephemeral=True
                )
        
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number for rep count!", 
                ephemeral=True
            )
        except Exception as e:
            print(f"[ERROR] Participation modal error: {e}")
            await interaction.response.send_message(
                "❌ An unexpected error occurred. Please try again.", 
                ephemeral=True
            )