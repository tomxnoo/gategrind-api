import asyncio
import random
import json
from datetime import datetime, timedelta, timezone  # Add timezone import
from typing import Optional, List
import logging
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.content_generator import IncursionContentGenerator
from features.incursions.models.incursion import IncursionType, Incursion

logger = logging.getLogger(__name__)

# Add these imports at the top
from core.database.db import get_system_setting, set_system_setting

class IncursionScheduler:
    """Intelligent scheduler for Shadow Incursions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.manager = IncursionManager(bot)
        self.generator = IncursionContentGenerator()
        self.is_running = False
        self._scheduler_task = None
        # Default values - will be loaded from database
        self.testing_mode = True
        self.auto_start_enabled = False
        
        # Configure the main channel for incursion announcements
        self.bot.main_channel_id = 1390756464250847353
    
    async def load_settings(self):
        """Load scheduler settings from database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                # Load testing mode setting
                testing_mode_raw = await get_system_setting(conn, 'incursion_scheduler_testing_mode', True)
                self.testing_mode = bool(json.loads(testing_mode_raw) if isinstance(testing_mode_raw, str) else testing_mode_raw)
                
                # Load auto-start setting
                auto_start_raw = await get_system_setting(conn, 'incursion_scheduler_auto_start', False)
                self.auto_start_enabled = bool(json.loads(auto_start_raw) if isinstance(auto_start_raw, str) else auto_start_raw)
                
                logger.info(f"Loaded scheduler settings: testing_mode={self.testing_mode}, auto_start={self.auto_start_enabled}")
                
                # Auto-start if enabled
                if self.auto_start_enabled and not self.is_running:
                    await self.start_scheduler()
                    logger.info("Auto-started incursion scheduler")
                    
        except Exception as e:
            logger.error(f"Error loading scheduler settings: {e}")
            # Use defaults if loading fails
            self.testing_mode = True
            self.auto_start_enabled = False
    
    async def save_settings(self):
        """Save current scheduler settings to database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await set_system_setting(conn, 'incursion_scheduler_testing_mode', self.testing_mode)
                await set_system_setting(conn, 'incursion_scheduler_auto_start', self.is_running)
                logger.info(f"Saved scheduler settings: testing_mode={self.testing_mode}, auto_start={self.is_running}")
        except Exception as e:
            logger.error(f"Error saving scheduler settings: {e}")
    
    def set_testing_mode(self, enabled: bool):
        """Enable or disable testing mode and save to database"""
        self.testing_mode = enabled
        logger.info(f"Testing mode {'enabled' if enabled else 'disabled'}")
        # Save settings asynchronously
        asyncio.create_task(self.save_settings())
    
    async def start_scheduler(self):
        """Start the automated incursion scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info(f"Incursion scheduler started (Testing mode: {self.testing_mode})")
        
        # Save the running state
        await self.save_settings()
    
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
        
        # Save the stopped state
        await self.save_settings()
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check for expired incursions and clean up messages
                await self._cleanup_expired_incursions()
                
                # Check if we should spawn a new incursion
                should_spawn = await self._should_spawn_incursion()
                if should_spawn:
                    await self._spawn_random_incursion()
                
                # Wait before next check
                if self.testing_mode:
                    # Testing: 1 minute
                    wait_time = 60  # 1 minute
                else:
                    # Production: 2-3 minutes
                    wait_time = random.randint(120, 180)  # 2-3 minutes
                
                logger.info(f"Next incursion check in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _cleanup_expired_incursions(self):
        """Clean up expired incursions and delete their announcement messages"""
        # Get expired incursions before cleanup
        async with self.bot.db_pool.acquire() as conn:
            expired_rows = await conn.fetch(
                """
                SELECT incursion_id, metadata 
                FROM active_incursions 
                WHERE expires_at <= NOW() AND is_active = TRUE
                """
            )
        
        # Delete announcement messages for expired incursions
        for row in expired_rows:
            try:
                metadata = {}
                if row['metadata']:
                    metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                
                message_id = metadata.get('announcement_message_id')
                channel_id = metadata.get('announcement_channel_id')
                
                if message_id and channel_id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                            logger.info(f"Deleted announcement message for expired incursion {row['incursion_id']}")
                        except Exception as e:
                            logger.warning(f"Could not delete announcement message {message_id}: {e}")
            except Exception as e:
                logger.error(f"Error processing expired incursion {row['incursion_id']}: {e}")
        
        # Now cleanup the database records
        count = await self.manager.cleanup_expired_incursions()
        if count > 0:
            logger.info(f"Cleaned up {count} expired incursions")
    
    def _get_incursion_duration(self, incursion_type: IncursionType, difficulty_modifier: float = 1.0) -> float:
        """Get duration in hours based on incursion type and difficulty"""
        if self.testing_mode:
            # Testing: 45 seconds
            return 45 / 3600  # Convert seconds to hours
        
        # Production durations (30 minutes to 3 hours)
        base_durations = {
            IncursionType.SURGE: 0.5,      # 30 minutes - quick buffs
            IncursionType.CHALLENGE: 1.5,   # 1.5 hours - moderate challenges
            IncursionType.ANOMALY: 2.5      # 2.5 hours - complex anomalies
        }
        
        base_duration = base_durations.get(incursion_type, 1.0)
        
        # Apply difficulty modifier (0.5 to 1.5)
        final_duration = base_duration * difficulty_modifier
        
        # Clamp to 30 minutes - 3 hours
        return max(0.5, min(3.0, final_duration))
    
    async def _should_spawn_incursion(self) -> bool:
        """Determine if a new incursion should be spawned"""
        # Get active incursions first
        active_incursions = await self.manager.get_active_incursions()
        
        if self.testing_mode:
            # In testing mode, always spawn if no active incursions
            return len(active_incursions) == 0
        
        # Don't spawn if we already have 3+ active incursions
        if len(active_incursions) >= 3:
            return False
        
        # Base spawn chance (2-3%)
        spawn_chance = random.uniform(2.0, 3.0)
        
        # Apply 1.5x boost if no active incursions
        if len(active_incursions) == 0:
            spawn_chance *= 1.5
            
            # Add escalation bonus: +0.5% per hour since last incursion (max +2%)
            hours_since_last = await self.manager.get_hours_since_last_incursion()
            escalation_bonus = min(hours_since_last * 0.5, 2.0)  # Cap at +2%
            spawn_chance += escalation_bonus
            
            logger.info(f"No active incursions. Hours since last: {hours_since_last:.1f}, "
                       f"escalation bonus: +{escalation_bonus:.1f}%, final chance: {spawn_chance:.1f}%")
        
        # Roll for spawn
        roll = random.uniform(0, 100)
        should_spawn = roll < spawn_chance
        
        logger.debug(f"Spawn check: {roll:.2f} < {spawn_chance:.2f}% = {should_spawn}")
        return should_spawn
        
        # Don't spawn if we already have 3+ active incursions
        if len(active_incursions) >= 3:
            return False
        
        if self.testing_mode:
            # Testing: 100% spawn chance
            return True
        
        # Production: 2-3% spawn chance (no time-based modifiers)
        spawn_chance = random.uniform(0.02, 0.03)
        
        # Slight increase if no active incursions
        if len(active_incursions) == 0:
            spawn_chance *= 1.5
        
        return random.random() < spawn_chance
    
    async def _spawn_random_incursion(self):
        """Spawn a new random incursion"""
        try:
            # Generate incursion content
            incursion_data = self.generator.generate_random_incursion()
            
            # Determine incursion type and difficulty
            incursion_type = incursion_data['incursion_type']
            
            # Generate difficulty modifier (0.8 to 1.2 for variation)
            difficulty_modifier = random.uniform(0.8, 1.2)
            
            # Set duration based on type and difficulty
            duration = self._get_incursion_duration(incursion_type, difficulty_modifier)
            incursion_data['duration_hours'] = duration
            
            # Create the incursion
            incursion = await self.manager.create_incursion(**incursion_data)
            
            # Announce the incursion
            await self._announce_incursion(incursion)
            
            duration_text = f"{int(duration * 60)} minutes" if duration < 1 else f"{duration:.1f} hours"
            logger.info(f"Spawned {incursion_type.value} incursion: {incursion.incursion_id} (Duration: {duration_text}, Testing: {self.testing_mode})")
            
        except Exception as e:
            logger.error(f"Error spawning incursion: {e}")
    
    async def _announce_incursion(self, incursion):
        """Announce a new incursion to the main channel"""
        # Get the main channel
        channel_id = getattr(self.bot, 'main_channel_id', None)
        if not channel_id:
            logger.warning("No main channel configured for incursion announcements")
            return
        
        channel = self.bot.get_channel(channel_id)
        if not channel:
            logger.error(f"Could not find channel {channel_id}")
            return
        
        # Create announcement embed using universal styling
        import discord
        from shared.utils.headers import get_system_status_header
        from shared.utils.ui_styles import get_panel_sub_header
        
        # Use universal header pattern (no main header, just sub-header)
        sub_header = "[ INCURSION ALERT MODULE ]\nSystem: SHADOW_PACT // Incursion Alert [DETECTED]\n──────────────────────────"
        
        # Type-specific ANSI colors and styling
        type_colors = {
            "surge": "\x1b[1;33m",      # Bright yellow/orange
            "challenge": "\x1b[1;36m",  # Bright cyan
            "anomaly": "\x1b[1;35m"     # Bright magenta
        }
        
        # Watcher messages with more dramatic flair
        watcher_messages = {
            "surge": "🔮 **The Watcher** detects surging shadow energy...",
            "challenge": "⚔️ **The Watcher** reports hostile breach detected...",
            "anomaly": "🌀 **The Watcher** warns of reality distortion manifesting..."
        }
        
        incursion_type = incursion.incursion_type.value
        color_code = type_colors.get(incursion_type, "\x1b[1;37m")
        
        # Build mobile-friendly ANSI content
        content = (
            f"```ansi\n"
            f"{sub_header}\n\n"
            f"{color_code}🌑 SHADOW INCURSION DETECTED\x1b[0m\n"
            f"{watcher_messages.get(incursion_type, '🔮 **The Watcher** detects anomalous activity...')}\n\n"
            f"📊 THREAT ASSESSMENT\n"
            f"├─ ⚡ Threat Level: {incursion_type.upper()}\n"
            f"├─ ⏰ Window: {int((incursion.expires_at - datetime.now(timezone.utc)).total_seconds() // 60)} minutes\n"
            f"└─ 🎯 Response: **CLASSIFIED**\n\n"
            f"🔍 Access your Incursions Panel in the System Hub\n"
            f"   for classified mission details and participation.\n\n"
            f"\x1b[2;37m• The Watcher is monitoring all operative responses\x1b[0m\n"
            f"──────────────────────────\n"
            f"```\n\n"
            f"⏰ **Expires:** <t:{int(incursion.expires_at.timestamp())}:R>"
        )
        
        # Color based on incursion type
        embed_colors = {
            "surge": 0xFF8C00,      # Orange
            "challenge": 0x00BFFF,   # Cyan
            "anomaly": 0x8A2BE2      # Purple
        }
        
        embed = discord.Embed(
            description=content,
            color=embed_colors.get(incursion_type, 0x9146FF)  # Use primary color as fallback
        )
        
        # Mobile-friendly footer
        embed.set_footer(
            text="Shadow Archive • Incursion Alert System",
            icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"  # Optional: Add icon
        )
        
        # Send the announcement
        message = await channel.send(embed=embed)
        
        # Store message ID for cleanup
        if not incursion.metadata:
            incursion.metadata = {}
        incursion.metadata["announcement_message_id"] = message.id
        incursion.metadata["announcement_channel_id"] = channel.id
        
        # Update the incursion with message info
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE active_incursions SET metadata = $1 WHERE incursion_id = $2",
                json.dumps(incursion.metadata), incursion.incursion_id
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
            
            # Set appropriate duration
            incursion_type_enum = incursion_data['incursion_type']
            duration = self._get_incursion_duration(incursion_type_enum)
            incursion_data['duration_hours'] = duration
            
            incursion = await self.manager.create_incursion(**incursion_data)
            await self._announce_incursion(incursion)
            
            return incursion.incursion_id
            
        except Exception as e:
            logger.error(f"Error force spawning incursion: {e}")
            return None