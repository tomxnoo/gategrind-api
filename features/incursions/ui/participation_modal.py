# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from typing import Union

from core.api_client import api_client

class ParticipationModal(discord.ui.Modal):
    """Modal for logging reps towards an incursion"""
    
    def __init__(self, bot, incursion):
        super().__init__(title=f"Log Reps: {incursion.get('title', 'Unknown Incursion')}")
        self.bot = bot
        self.incursion = incursion
        
        # Rep count input
        self.rep_input = discord.ui.TextInput(
            label=f"How many {incursion.get('target_exercise', 'reps')} did you complete?",
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
            
            # First log the reps via the logging API
            log_data = {
                "exercise": self.incursion.get("target_exercise", "unknown"),
                "reps": rep_count,
                "sets": 1,
                "notes": self.notes_input.value.strip() if self.notes_input.value else None
            }
            
            try:
                log_result = await api_client.log_reps(interaction.user, log_data)
            except Exception as e:
                print(f"Error logging reps: {e}")
                await interaction.response.send_message(
                    "❌ Failed to log reps. Please try again.", 
                    ephemeral=True
                )
                return
            
            # Then contribute to the incursion
            try:
                contrib_result = await api_client.contribute_to_incursion(
                    interaction.user, 
                    self.incursion["incursion_id"], 
                    rep_count
                )
            except Exception as e:
                print(f"Error contributing to incursion: {e}")
                await interaction.response.send_message(
                    "❌ Reps logged but failed to contribute to incursion. Please try again.", 
                    ephemeral=True
                )
                return
            
            # Create success embed
            embed = discord.Embed(
                title="⚡ Reps Logged Successfully!",
                color=0x00ff00
            )
            
            # Add contribution info
            embed.add_field(
                name="💪 Reps Contributed",
                value=f"+{rep_count} to {self.incursion.get('title', 'Unknown Incursion')}",
                inline=True
            )
            
            # Add bonus XP info if available
            if contrib_result.get("bonus_xp", 0) > 0:
                embed.add_field(
                    name="✨ Bonus XP",
                    value=f"+{contrib_result['bonus_xp']} XP",
                    inline=True
                )
            
            # Check for completion
            if contrib_result.get("incursion_completed", False):
                embed.add_field(
                    name="🎉 Incursion Complete!",
                    value=f"Completion bonus: +{contrib_result.get('completion_bonus', 0)} XP",
                    inline=False
                )
                embed.color = 0xffd700  # Gold color for completion
            
            # Add any special effects if available
            if contrib_result.get("special_effects"):
                embed.add_field(
                    name="🌀 Special Effects Applied",
                    value=contrib_result["special_effects"],
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
                
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