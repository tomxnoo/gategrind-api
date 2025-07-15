import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
import logging
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.content_generator import IncursionContentGenerator

logger = logging.getLogger(__name__)

class IncursionScheduler:
    """Intelligent scheduler for Shadow Incursions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = IncursionManager(bot)
        self.generator = IncursionContentGenerator()
        self.is_running = False
        self._scheduler_task = None
    
    async def start_scheduler(self):
        """Start the automated incursion scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Incursion scheduler started")
    
    async def stop_scheduler(self):
        """Stop the automated incursion scheduler"""
        self.is_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Incursion scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check for expired incursions
                await self.manager.cleanup_expired_incursions()
                
                # Check if we should spawn a new incursion
                should_spawn = await self._should_spawn_incursion()
                if should_spawn:
                    await self._spawn_random_incursion()
                
                # Wait before next check (5-15 minutes)
                wait_time = random.randint(300, 900)  # 5-15 minutes
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _should_spawn_incursion(self) -> bool:
        """Determine if a new incursion should be spawned"""
        # Get current active incursions
        active_incursions = await self.manager.get_active_incursions()
        
        # Don't spawn if we already have 2+ active incursions
        if len(active_incursions) >= 2:
            return False
        
        # Base spawn chance: 15% per check
        base_chance = 0.15
        
        # Increase chance if no active incursions
        if len(active_incursions) == 0:
            base_chance = 0.25
        
        # Time-based modifiers
        current_hour = datetime.now().hour
        
        # Peak hours (6-9 AM, 12-2 PM, 6-10 PM) - higher chance
        if current_hour in [6, 7, 8, 9, 12, 13, 14, 18, 19, 20, 21, 22]:
            base_chance *= 1.5
        
        # Late night/early morning (11 PM - 5 AM) - lower chance
        elif current_hour in [23, 0, 1, 2, 3, 4, 5]:
            base_chance *= 0.3
        
        # Weekend bonus (slightly higher chance)
        if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
            base_chance *= 1.2
        
        return random.random() < base_chance
    
    async def _spawn_random_incursion(self):
        """Spawn a new random incursion"""
        try:
            # Generate incursion content
            incursion_data = self.generator.generate_random_incursion()
            
            # Create the incursion
            incursion = await self.manager.create_incursion(**incursion_data)
            
            # Announce the incursion
            await self._announce_incursion(incursion)
            
            logger.info(f"Spawned new incursion: {incursion.incursion_id}")
            
        except Exception as e:
            logger.error(f"Error spawning incursion: {e}")
    
    async def _announce_incursion(self, incursion):
        """Announce a new incursion to the main channel"""
        # Get the main channel (you'll need to configure this)
        channel_id = getattr(self.bot, 'main_channel_id', None)
        if not channel_id:
            logger.warning("No main channel configured for incursion announcements")
            return
        
        channel = self.bot.get_channel(channel_id)
        if not channel:
            logger.error(f"Could not find channel {channel_id}")
            return
        
        # Create announcement embed
        import discord
        
        # Color based on incursion type
        colors = {
            "surge": 0x00FF00,    # Green
            "challenge": 0xFF8C00,  # Orange
            "anomaly": 0x8A2BE2     # Purple
        }
        
        embed = discord.Embed(
            title=f"🌑 {incursion.title}",
            description=incursion.description,
            color=colors.get(incursion.incursion_type.value, 0x4B0082)
        )
        
        # Add fields based on incursion type
        if incursion.incursion_type.value == "challenge":
            embed.add_field(
                name="🎯 Objective",
                value=f"{incursion.target_reps} {incursion.target_exercise.replace('_', ' ').title()}",
                inline=True
            )
        
        embed.add_field(
            name="🏆 Reward",
            value=incursion.reward_description,
            inline=True
        )
        
        embed.add_field(
            name="⏰ Time Limit",
            value=incursion.time_remaining or "Expired",
            inline=True
        )
        
        embed.add_field(
            name="📊 Progress",
            value=f"{incursion.current_reps}/{incursion.target_reps} ({incursion.progress_percentage:.1f}%)",
            inline=False
        )
        
        embed.set_footer(text="Use /incursions to participate • This message will auto-delete when the event expires")
        
        # Send the announcement
        message = await channel.send(embed=embed)
        
        # Store message ID for cleanup
        incursion.metadata["announcement_message_id"] = message.id
        incursion.metadata["announcement_channel_id"] = channel.id
        
        # Update the incursion with message info
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE active_incursions SET metadata = $1 WHERE incursion_id = $2",
                incursion.metadata, incursion.incursion_id
            )
    
    async def force_spawn_incursion(self, incursion_type: str = None) -> Optional[str]:
        """Manually force spawn an incursion (for testing/admin use)"""
        try:
            if incursion_type == "surge":
                incursion_data = self.generator.generate_surge_incursion()
            elif incursion_type == "challenge":
                incursion_data = self.generator.generate_challenge_incursion()
            elif incursion_type == "anomaly":
                incursion_data = self.generator.generate_anomaly_incursion()
            else:
                incursion_data = self.generator.generate_random_incursion()
            
            incursion = await self.manager.create_incursion(**incursion_data)
            await self._announce_incursion(incursion)
            
            return incursion.incursion_id
            
        except Exception as e:
            logger.error(f"Error force spawning incursion: {e}")
            return None