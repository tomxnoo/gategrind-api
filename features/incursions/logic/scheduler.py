import asyncio
import random
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging
import discord
from features.incursions.logic.incursion_manager import IncursionManager
from features.incursions.logic.content_generator import IncursionContentGenerator
from features.incursions.models.incursion import IncursionType, Incursion

# Add these imports for universal header
from shared.utils.headers import get_system_status_header
from shared.utils.ui_styles import get_panel_sub_header

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
        
        # Cache keys for Redis optimization
        self.CACHE_KEYS = {
            'active_incursions': 'incursions:active',
            'last_incursion_time': 'incursions:last_time',
            'message_cache': 'incursions:messages:{}',  # Format with incursion_id
        }
    
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
    
    async def _get_cached_active_incursions(self) -> List[Incursion]:
        """Get active incursions with Redis caching"""
        try:
            # Try to get from cache first
            cached_data = await self.bot.redis.get(self.CACHE_KEYS['active_incursions'])
            if cached_data:
                incursions_data = json.loads(cached_data)
                return [self._dict_to_incursion(data) for data in incursions_data]
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")
        
        # Fallback to database
        incursions = await self.manager.get_active_incursions()
        
        # Cache the result for 10 seconds
        try:
            incursions_data = [self._incursion_to_dict(inc) for inc in incursions]
            await self.bot.redis.set(
                self.CACHE_KEYS['active_incursions'], 
                json.dumps(incursions_data), 
                expire=10
            )
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")
        
        return incursions
    
    def _incursion_to_dict(self, incursion: Incursion) -> dict:
        """Convert Incursion object to dictionary for caching"""
        return {
            'id': incursion.id,
            'incursion_id': incursion.incursion_id,
            'incursion_type': incursion.incursion_type.value,
            'title': incursion.title,
            'description': incursion.description,
            'target_exercise': incursion.target_exercise,
            'target_reps': incursion.target_reps,
            'current_reps': incursion.current_reps,
            'reward_type': incursion.reward_type.value,
            'reward_value': incursion.reward_value,
            'reward_description': incursion.reward_description,
            'created_at': incursion.created_at.isoformat(),
            'expires_at': incursion.expires_at.isoformat(),
            'is_active': incursion.is_active,
            'metadata': incursion.metadata
        }
    
    def _dict_to_incursion(self, data: dict) -> Incursion:
        """Convert dictionary back to Incursion object"""
        return Incursion(
            id=data['id'],
            incursion_id=data['incursion_id'],
            incursion_type=IncursionType(data['incursion_type']),
            title=data['title'],
            description=data['description'],
            target_exercise=data['target_exercise'],
            target_reps=data['target_reps'],
            current_reps=data['current_reps'],
            reward_type=data['reward_type'],
            reward_value=data['reward_value'],
            reward_description=data['reward_description'],
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            is_active=data['is_active'],
            metadata=data['metadata']
        )
    
    async def _invalidate_incursion_cache(self):
        """Invalidate cached incursion data"""
        try:
            await self.bot.redis.delete(self.CACHE_KEYS['active_incursions'])
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop with 5-second updates"""
        while self.is_running:
            try:
                # Check for expired incursions and clean up messages
                await self._cleanup_expired_incursions()
                
                # Update existing incursion messages with current timers
                await self._update_incursion_messages()
                
                # Check if we should spawn a new incursion
                should_spawn = await self._should_spawn_incursion()
                if should_spawn:
                    await self._spawn_random_incursion()
                
                # Wait 5 seconds for smooth timer updates with Redis optimization
                wait_time = 5
                
                logger.debug(f"Next incursion check in {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _cleanup_expired_incursions(self):
        """Clean up expired incursions and delete their announcement messages"""
        try:
            # First, mark expired incursions as inactive in database
            count = await self.manager.cleanup_expired_incursions()
            if count > 0:
                logger.info(f"Marked {count} expired incursions as inactive")
                # Invalidate cache immediately after database update
                await self._invalidate_incursion_cache()
            
            # Then get the expired incursions that still have messages to delete
            async with self.bot.db_pool.acquire() as conn:
                expired_rows = await conn.fetch(
                    """
                    SELECT incursion_id, metadata 
                    FROM active_incursions 
                    WHERE expires_at <= NOW() AND is_active = FALSE
                    AND metadata IS NOT NULL
                    """
                )
            
            # Delete announcement messages for expired incursions
            messages_deleted = 0
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
                                messages_deleted += 1
                                logger.info(f"Deleted announcement message for expired incursion {row['incursion_id']}")
                                
                                # Clear the metadata after successful deletion
                                async with self.bot.db_pool.acquire() as conn:
                                    await conn.execute(
                                        "UPDATE active_incursions SET metadata = NULL WHERE incursion_id = $1",
                                        row['incursion_id']
                                    )
                                    
                            except discord.NotFound:
                                # Message already deleted, clear metadata
                                logger.info(f"Message {message_id} already deleted for incursion {row['incursion_id']}")
                                async with self.bot.db_pool.acquire() as conn:
                                    await conn.execute(
                                        "UPDATE active_incursions SET metadata = NULL WHERE incursion_id = $1",
                                        row['incursion_id']
                                    )
                            except Exception as e:
                                logger.warning(f"Could not delete announcement message {message_id}: {e}")
                                
                        # Clear message cache
                        try:
                            cache_key = self.CACHE_KEYS['message_cache'].format(row['incursion_id'])
                            await self.bot.redis.delete(cache_key)
                        except Exception:
                            pass
                            
                except Exception as e:
                    logger.error(f"Error processing expired incursion {row['incursion_id']}: {e}")
            
            if messages_deleted > 0:
                logger.info(f"Successfully deleted {messages_deleted} expired incursion messages")
                    
        except Exception as e:
            logger.error(f"Error in cleanup_expired_incursions: {e}")
    
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
        # Get active incursions using cached method
        active_incursions = await self._get_cached_active_incursions()
        
        if self.testing_mode:
            # In testing mode, always spawn if no active incursions
            return len(active_incursions) == 0
        
        # Don't spawn if we already have 2+ active incursions (reduced from 3)
        if len(active_incursions) >= 2:
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
            
            # Invalidate cache since we added a new incursion
            await self._invalidate_incursion_cache()
            
            # Announce the incursion
            await self._announce_incursion(incursion)
            
            duration_text = f"{int(duration * 60)} minutes" if duration < 1 else f"{duration:.1f} hours"
            logger.info(f"Spawned {incursion_type.value} incursion: {incursion.incursion_id} (Duration: {duration_text}, Testing: {self.testing_mode})")
            
        except Exception as e:
            logger.error(f"Error spawning incursion: {e}")
    
    def _get_time_color_and_percentage(self, incursion):
        """Get ANSI color code and formatted time for remaining duration"""
        now = datetime.now(timezone.utc)
        total_duration = (incursion.expires_at - incursion.created_at).total_seconds()
        remaining_time = (incursion.expires_at - now).total_seconds()
        
        if remaining_time <= 0:
            return "\x1b[1;31m", "00:00:00"  # Red for expired
        
        percentage = (remaining_time / total_duration) * 100
        
        # Format time as HH:MM:SS
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        seconds = int(remaining_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if percentage >= 66:
            return "\x1b[1;32m", time_str  # Green
        elif percentage >= 33:
            return "\x1b[1;33m", time_str  # Yellow
        else:
            return "\x1b[1;31m", time_str  # Red

    async def _update_incursion_messages(self):
        """Update all active incursion announcement messages with current timers (optimized)"""
        try:
            # Use cached active incursions
            active_incursions = await self._get_cached_active_incursions()
            
            # Batch process message updates
            update_tasks = []
            
            for incursion in active_incursions:
                if not incursion.metadata:
                    continue
                    
                message_id = incursion.metadata.get('announcement_message_id')
                channel_id = incursion.metadata.get('announcement_channel_id')
                
                if not message_id or not channel_id:
                    continue
                
                # Create update task for each message
                task = self._update_single_message(incursion, message_id, channel_id)
                update_tasks.append(task)
            
            # Execute all updates concurrently
            if update_tasks:
                await asyncio.gather(*update_tasks, return_exceptions=True)
                    
        except Exception as e:
            logger.error(f"Error updating incursion messages: {e}")
    
    async def _update_single_message(self, incursion, message_id, channel_id):
        """Update a single incursion message with caching and universal header"""
        try:
            # Check if we need to update (cache last content)
            cache_key = self.CACHE_KEYS['message_cache'].format(incursion.incursion_id)
            
            # Get current time info
            time_color, time_formatted = self._get_time_color_and_percentage(incursion)
            
            # Create content hash for change detection
            content_hash = f"{time_formatted}_{incursion.current_reps}"
            
            try:
                cached_hash = await self.bot.redis.get(cache_key)
                if cached_hash == content_hash:
                    # No changes needed
                    return
            except Exception:
                pass  # Continue with update if cache fails
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return
                
            message = await channel.fetch_message(message_id)
            
            # Rebuild the announcement with updated timer and universal header
            import discord
            
            # Create a dummy user for the header (using bot user)
            bot_user = self.bot.user
            header = get_system_status_header(bot_user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("incursion_alert")
            
            type_colors = {
                "surge": "\x1b[1;33m",
                "challenge": "\x1b[1;36m",
                "anomaly": "\x1b[1;35m"
            }
            
            watcher_messages = {
                "surge": "🔮 **The Watcher** detects surging shadow energy...",
                "challenge": "⚔️ **The Watcher** reports hostile breach detected...",
                "anomaly": "🌀 **The Watcher** warns of reality distortion manifesting..."
            }
            
            incursion_type = incursion.incursion_type.value
            color_code = type_colors.get(incursion_type, "\x1b[1;37m")
            
            # Build clean ANSI content with universal header and colored timer
            # In _update_single_message method around line 450:
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"{color_code}🌑 SHADOW INCURSION DETECTED\x1b[0m\n"
                f"{watcher_messages.get(incursion_type, '🔮 **The Watcher** detects anomalous activity...')}\n\n"
                f"📊 THREAT ASSESSMENT\n"
                f"├─ ⚡ Threat Level: {incursion_type.upper()}\n"
                f"├─ ⏰ Window: {time_color}{time_formatted}\x1b[0m\n"
                f"└─ 🎯 Response: **CLASSIFIED**\n\n"
                f"🔍 Access your Incursions Panel in the System Hub\n"
                f"   for classified mission details and participation.\n\n"
                f"\x1b[2;37m• The Watcher is monitoring all operative responses\x1b[0m\n"
                f"──────────────────────────\n"
                f"```"
                f"`🌀 Incursion closes in:` <t:{int(incursion.expires_at.timestamp())}:R>"
            )
            
            # In _announce_incursion method around line 520:
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"{color_code}🌑 SHADOW INCURSION DETECTED\x1b[0m\n"
                f"{watcher_messages.get(incursion_type, '🔮 **The Watcher** detects anomalous activity...')}\n\n"
                f"📊 THREAT ASSESSMENT\n"
                f"├─ ⚡ Threat Level: {incursion_type.upper()}\n"
                f"├─ ⏰ Window: {time_color}{time_formatted}\x1b[0m\n"
                f"└─ 🎯 Response: **CLASSIFIED**\n\n"
                f"🔍 Access your Incursions Panel in the System Hub\n"
                f"   for classified mission details and participation.\n\n"
                f"\x1b[2;37m• The Watcher is monitoring all operative responses\x1b[0m\n"
                f"──────────────────────────\n"
                f"```"
                f"`🌀 Incursion closes in:` <t:{int(incursion.expires_at.timestamp())}:R>"
            )
            
            # Color based on incursion type
            embed_colors = {
                "surge": 0xFF8C00,      # Orange
                "challenge": 0x00CED1,  # Dark Turquoise
                "anomaly": 0x9932CC     # Dark Orchid
            }
            
            embed = discord.Embed(
                description=content,
                color=embed_colors.get(incursion_type, 0x2f3136)
            )
            embed.set_footer(text="Shadow Archive • Incursion Alert System")
            
            await message.edit(embed=embed)
            
            # Cache the content hash to avoid unnecessary updates
            try:
                await self.bot.redis.set(cache_key, content_hash, expire=30)
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Error updating incursion message {message_id}: {e}")

    async def _announce_incursion(self, incursion):
        """Announce a new incursion with universal header"""
        try:
            channel = self.bot.get_channel(self.bot.main_channel_id)
            if not channel:
                logger.error(f"Could not find announcement channel {self.bot.main_channel_id}")
                return
            
            import discord
            
            # Create a dummy user for the header (using bot user)
            bot_user = self.bot.user
            header = get_system_status_header(bot_user).replace('```ansi', '').replace('```', '').strip()
            sub_header = get_panel_sub_header("incursion_alert")
            
            type_colors = {
                "surge": "\x1b[1;33m",
                "challenge": "\x1b[1;36m",
                "anomaly": "\x1b[1;35m"
            }
            
            watcher_messages = {
                "surge": "🔮 **The Watcher** detects surging shadow energy...",
                "challenge": "⚔️ **The Watcher** reports hostile breach detected...",
                "anomaly": "🌀 **The Watcher** warns of reality distortion manifesting..."
            }
            
            incursion_type = incursion.incursion_type.value
            color_code = type_colors.get(incursion_type, "\x1b[1;37m")
            
            # Get initial time info
            time_color, time_formatted = self._get_time_color_and_percentage(incursion)
            
            # Build clean ANSI content with universal header
            content = (
                f"```ansi\n"
                f"{header}\n"
                f"{sub_header}\n\n"
                f"{color_code}🌑 SHADOW INCURSION DETECTED\x1b[0m\n"
                f"{watcher_messages.get(incursion_type, '🔮 **The Watcher** detects anomalous activity...')}\n\n"
                f"📊 THREAT ASSESSMENT\n"
                f"├─ ⚡ Threat Level: {incursion_type.upper()}\n"
                f"├─ ⏰ Window: {time_color}{time_formatted}\x1b[0m\n"
                f"└─ 🎯 Response: **CLASSIFIED**\n\n"
                f"🔍 Access your Incursions Panel in the System Hub\n"
                f"   for classified mission details and participation.\n\n"
                f"\x1b[2;37m• The Watcher is monitoring all operative responses\x1b[0m\n"
                f"──────────────────────────\n"
                f"```\n"
                f"`🌀 Incursion closes in:` <t:{int(incursion.expires_at.timestamp())}:R>"
            )
            
            # Color based on incursion type
            embed_colors = {
                "surge": 0xFF8C00,      # Orange
                "challenge": 0x00CED1,  # Dark Turquoise
                "anomaly": 0x9932CC     # Dark Orchid
            }
            
            embed = discord.Embed(
                description=content,
                color=embed_colors.get(incursion_type, 0x2f3136)
            )
            embed.set_footer(text="Shadow Archive • Incursion Alert System")
            
            # Send the announcement
            message = await channel.send(embed=embed)
            
            # Store message info in incursion metadata for future updates
            metadata = incursion.metadata or {}
            metadata['announcement_message_id'] = message.id
            metadata['announcement_channel_id'] = channel.id
            
            # Update the incursion with message metadata
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE active_incursions SET metadata = $1 WHERE incursion_id = $2",
                    json.dumps(metadata), incursion.incursion_id
                )
            
            # Invalidate cache since metadata changed
            await self._invalidate_incursion_cache()
            
            logger.info(f"Announced incursion {incursion.incursion_id} in channel {channel.id}")
            
        except Exception as e:
            logger.error(f"Error announcing incursion: {e}")

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
            
            # Invalidate cache
            await self._invalidate_incursion_cache()
            
            await self._announce_incursion(incursion)
            
            return incursion.incursion_id
            
        except Exception as e:
            logger.error(f"Error force spawning incursion: {e}")
