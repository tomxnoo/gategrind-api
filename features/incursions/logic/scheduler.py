import asyncio
import random
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging
import discord
from core.api_client import api_client
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
        self.api_client = api_client  # Use the global api_client instance
        self.generator = IncursionContentGenerator()  # Fixed class name
        self._scheduler_task = None
        self._last_spawn_time = None
        
        # Initialize scheduler state
        self.is_running = False
        self.testing_mode = True
        self.auto_start_enabled = False
        
        # Cache configuration
        self.CACHE_KEYS = {
            'active_incursions': 'incursions:active',
            'message_cache': 'incursions:message:{}'
        }
        self.CACHE_TTL = 30  # 30 seconds
        
        # Track last spawn time to prevent rapid spawning in testing mode
        self._last_spawn_time = None
        
        # Cache keys for Redis optimization
        self.CACHE_KEYS = {
            'active_incursions': 'incursions:active',
            'last_incursion_time': 'incursions:last_time',
            'message_cache': 'incursions:messages:{}',  # Format with incursion_id
        }
        self.is_running = False
        self.testing_mode = True
        self.auto_start_enabled = False
    
    def _get_system_user(self):
        """Get a system user for API calls"""
        return self.bot.user
    
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
                
                # Load announcement channel ID setting - FIX: Handle JSON string properly
                announcement_channel_raw = await get_system_setting(conn, 'incursion_announcement_channel_id', '1390756464250847353')
                if isinstance(announcement_channel_raw, str):
                    try:
                        # Try to parse as JSON first (in case it's stored as "1390756464250847353")
                        parsed_value = json.loads(announcement_channel_raw)
                        self.announcement_channel_id = int(parsed_value)
                    except json.JSONDecodeError:
                        # If not JSON, treat as plain string
                        self.announcement_channel_id = int(announcement_channel_raw)
                else:
                    self.announcement_channel_id = int(announcement_channel_raw) if announcement_channel_raw else 1390756464250847353
                
                logger.info(f"Loaded scheduler settings: testing_mode={self.testing_mode}, auto_start={self.auto_start_enabled}, announcement_channel={self.announcement_channel_id}")
                
                # Auto-start if enabled
                if self.auto_start_enabled and not self.is_running:
                    await self.start_scheduler()
                    logger.info("Auto-started incursion scheduler")
                    
        except Exception as e:
            logger.error(f"Error loading scheduler settings: {e}")
            # Use defaults if loading fails
            self.testing_mode = True
            self.auto_start_enabled = False
            self.announcement_channel_id = 1390756464250847353
    
    async def save_settings(self):
        """Save current scheduler settings to database"""
        try:
            async with self.bot.db_pool.acquire() as conn:
                await set_system_setting(conn, 'incursion_scheduler_testing_mode', self.testing_mode)
                await set_system_setting(conn, 'incursion_scheduler_auto_start', self.is_running)
                await set_system_setting(conn, 'incursion_announcement_channel_id', str(self.announcement_channel_id))
                logger.info(f"Saved scheduler settings: testing_mode={self.testing_mode}, auto_start={self.is_running}, announcement_channel={self.announcement_channel_id}")
        except Exception as e:
            logger.error(f"Error saving scheduler settings: {e}")
    
    async def _get_announcement_channel_id(self) -> int:
        """Get the configured announcement channel ID"""
        # Return the configured channel ID, with fallback to default
        return getattr(self, 'announcement_channel_id', 1390756464250847353)
    
    def set_announcement_channel(self, channel_id: int):
        """Set the announcement channel ID and save to database"""
        self.announcement_channel_id = channel_id
        logger.info(f"Announcement channel set to {channel_id}")
        # Save settings asynchronously
        asyncio.create_task(self.save_settings())
    
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
        
        # Fallback to API
        try:
            system_user = self._get_system_user()
            response = await self.api_client.get_active_incursions(system_user)
            incursions = []
            
            # Fix: Use 'active_incursions' instead of 'incursions'
            for inc_data in response.get('active_incursions', []):
                incursion = Incursion(
                    id=inc_data.get('id'),
                    incursion_id=inc_data['incursion_id'],
                    incursion_type=IncursionType(inc_data['incursion_type']),
                    title=inc_data['title'],
                    description=inc_data['description'],
                    target_exercise=inc_data['target_exercise'],
                    target_reps=inc_data['target_reps'],
                    current_reps=inc_data['current_reps'],
                    reward_type=inc_data['reward_type'],
                    reward_value=inc_data['reward_value'],
                    reward_description=inc_data['reward_description'],
                    created_at=datetime.fromisoformat(inc_data['created_at'].replace('Z', '+00:00')),
                    expires_at=datetime.fromisoformat(inc_data['expires_at'].replace('Z', '+00:00')),
                    is_active=inc_data.get('is_active', True),  # Fix: Use 'is_active' instead of checking 'status'
                    metadata=inc_data.get('metadata', {})
                )
                incursions.append(incursion)
            
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
            
        except Exception as e:
            logger.error(f"Failed to get active incursions from API: {e}")
            return []
    
    def _incursion_to_dict(self, incursion: Incursion) -> dict:
        """Convert Incursion object to dictionary for caching"""
        return {
            'id': incursion.id,
            'incursion_id': incursion.incursion_id,
            'incursion_type': incursion.incursion_type.value if hasattr(incursion.incursion_type, 'value') else incursion.incursion_type,
            'title': incursion.title,
            'description': incursion.description,
            'target_exercise': incursion.target_exercise,
            'target_reps': incursion.target_reps,
            'current_reps': incursion.current_reps,
            'reward_type': incursion.reward_type.value if hasattr(incursion.reward_type, 'value') else incursion.reward_type,
            'reward_value': incursion.reward_value,
            'reward_description': incursion.reward_description,
            'created_at': incursion.created_at.isoformat(),
            'expires_at': incursion.expires_at.isoformat(),
            'is_active': incursion.is_active,
            'metadata': incursion.metadata
        }
    
    def _dict_to_incursion(self, data: dict) -> Incursion:
        """Convert dictionary back to Incursion object"""
        # Parse datetime strings with proper timezone handling
        def parse_datetime(dt_str):
            if dt_str.endswith('Z'):
                dt_str = dt_str.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt_str)
            # Ensure timezone awareness - if naive, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        
        return Incursion(
            id=data['id'],
            incursion_id=data['incursion_id'],
            incursion_type=IncursionType(data['incursion_type']) if isinstance(data['incursion_type'], str) else data['incursion_type'],
            title=data['title'],
            description=data['description'],
            target_exercise=data['target_exercise'],
            target_reps=data['target_reps'],
            current_reps=data['current_reps'],
            reward_type=data['reward_type'] if isinstance(data['reward_type'], str) else data['reward_type'],
            reward_value=data['reward_value'],
            reward_description=data['reward_description'],
            created_at=parse_datetime(data['created_at']),
            expires_at=parse_datetime(data['expires_at']),
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
    
    async def _update_incursion_messages(self):
        """Update all active incursion announcement messages with current timers"""
        try:
            # Use cached active incursions
            active_incursions = await self._get_cached_active_incursions()
            
            # Batch process message updates
            update_tasks = []
            
            for incursion in active_incursions:
                # Only update messages for incursions that have been announced
                if incursion.metadata and incursion.metadata.get('announcement_message_id'):
                    message_id = incursion.metadata.get('announcement_message_id')
                    channel_id = incursion.metadata.get('announcement_channel_id')
                    
                    if message_id and channel_id:
                        # Create update task for existing message
                        task = self._update_single_message(incursion, message_id, channel_id)
                        update_tasks.append(task)
                else:
                    # No metadata means this incursion hasn't been announced yet
                    task = self._announce_incursion(incursion)
                    update_tasks.append(task)
            
            # Execute all updates concurrently
            if update_tasks:
                results = await asyncio.gather(*update_tasks, return_exceptions=True)
                # Log any exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error in update task {i}: {result}")
                    
        except Exception as e:
            logger.error(f"Error updating incursion messages: {e}")
    
    async def _update_single_message(self, incursion, message_id, channel_id):
        """Update a single incursion message with caching and universal header"""
        try:
            # Check if incursion is expired
            if incursion.expires_at <= datetime.now(timezone.utc):
                logger.debug(f"Skipping update for expired incursion {incursion.incursion_id}")
                return
            
            # Check if we need to update (cache last content)
            cache_key = self.CACHE_KEYS['message_cache'].format(incursion.incursion_id)
            
            # Get current time info
            time_color, time_formatted = self._get_time_color_and_percentage(incursion)
            
            # Create content hash for change detection
            content_hash = f"{time_formatted}_{incursion.current_reps}_{int(incursion.expires_at.timestamp())}"
            
            try:
                cached_hash = await self.bot.redis.get(cache_key)
                if cached_hash == content_hash:
                    # No changes needed
                    logger.debug(f"No update needed for incursion {incursion.incursion_id}")
                    return
            except Exception:
                pass  # Continue with update if cache fails
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning(f"Channel {channel_id} not found for incursion {incursion.incursion_id}")
                return
                
            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                logger.warning(f"Message {message_id} not found for incursion {incursion.incursion_id}")
                return
            except Exception as e:
                logger.error(f"Error fetching message {message_id}: {e}")
                return
            
            # Rebuild the announcement with updated timer and universal header
            
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
            logger.debug(f"Updated incursion message {message_id} for {incursion.incursion_id}")
            
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
            # Get the announcement channel ID
            channel_id = await self._get_announcement_channel_id()
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Could not find announcement channel {channel_id}")
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
            
            # Update the incursion with message metadata via API
            try:
                system_user = self._get_system_user()
                await self.api_client.update_incursion_metadata(system_user, incursion.incursion_id, metadata)
                logger.debug(f"Updated metadata for incursion {incursion.incursion_id}")
            except Exception as e:
                logger.error(f"Error updating incursion metadata via API: {e}")
                # Fallback to direct database update if API fails
                try:
                    async with self.bot.db_pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE active_incursions SET metadata = $1 WHERE incursion_id = $2",
                            json.dumps(metadata), incursion.incursion_id
                        )
                    logger.debug(f"Updated metadata via database fallback for incursion {incursion.incursion_id}")
                except Exception as db_e:
                    logger.error(f"Error updating incursion metadata via database fallback: {db_e}")
            
            # Invalidate cache since metadata changed
            await self._invalidate_incursion_cache()
            
            logger.info(f"Announced incursion {incursion.incursion_id} in channel {channel.id}")
            
        except Exception as e:
            logger.error(f"Error announcing incursion: {e}")
    
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
            # In testing mode, only spawn if no active incursions AND enough time has passed
            if len(active_incursions) == 0:
                # Add cooldown period in testing mode (60 seconds)
                if self._last_spawn_time is None:
                    return True  # First spawn
                
                time_since_last_spawn = (datetime.now(timezone.utc) - self._last_spawn_time).total_seconds()
                cooldown_period = 60  # 60 seconds cooldown in testing mode
                
                if time_since_last_spawn >= cooldown_period:
                    logger.info(f"Testing mode: Spawning new incursion after {time_since_last_spawn:.1f}s cooldown")
                    return True
                else:
                    remaining_cooldown = cooldown_period - time_since_last_spawn
                    logger.debug(f"Testing mode: Cooldown active, {remaining_cooldown:.1f}s remaining")
                    return False
            return False
        
        # Don't spawn if we already have 2+ active incursions (reduced from 3)
        if len(active_incursions) >= 2:
            return False
        
        # Base spawn chance (2-3%)
        spawn_chance = random.uniform(2.0, 3.0)
        
        # Apply 1.5x boost if no active incursions
        if len(active_incursions) == 0:
            spawn_chance *= 1.5
            
            # Add escalation bonus: +0.5% per hour since last incursion (max +2%)
            hours_since_last = await self._get_hours_since_last_incursion()
            escalation_bonus = min(hours_since_last * 0.5, 2.0)  # Cap at +2%
            spawn_chance += escalation_bonus
            
            logger.info(f"No active incursions. Hours since last: {hours_since_last:.1f}, "
                       f"escalation bonus: +{escalation_bonus:.1f}%, final chance: {spawn_chance:.1f}%")
        
        # Roll for spawn
        roll = random.uniform(0, 100)
        should_spawn = roll < spawn_chance
        
        logger.debug(f"Spawn check: {roll:.2f} < {spawn_chance:.2f}% = {should_spawn}")
        return should_spawn

    async def _get_hours_since_last_incursion(self) -> float:
        """Get hours since the last incursion ended (expired or completed)"""
        async with self.bot.db_pool.acquire() as conn:
            # Get the most recent incursion that ended (either expired or manually completed)
            row = await conn.fetchrow(
                """
                SELECT expires_at, created_at
                FROM active_incursions 
                WHERE is_active = FALSE
                ORDER BY 
                    CASE 
                        WHEN expires_at <= NOW() THEN expires_at  -- Use expiry time for expired incursions
                        ELSE created_at  -- Use creation time for manually completed ones
                    END DESC
                LIMIT 1
                """
            )
            
            if not row:
                # No previous incursions found, return a large number to trigger escalation
                return 24.0  # 24 hours to ensure escalation kicks in
            
            # Calculate time since the incursion ended
            end_time = row['expires_at'] if row['expires_at'] <= datetime.now(timezone.utc) else row['created_at']
            time_diff = datetime.now(timezone.utc) - end_time
            return time_diff.total_seconds() / 3600  # Convert to hours
    
    async def _spawn_random_incursion(self):
        """Spawn a new random incursion"""
        try:
            # Record spawn time for cooldown tracking
            self._last_spawn_time = datetime.now(timezone.utc)
            
            # Generate incursion content
            incursion_data = self.generator.generate_random_incursion()
            
            # Determine incursion type and difficulty
            incursion_type = incursion_data['incursion_type']
            
            # Generate difficulty modifier (0.8 to 1.2 for variation)
            difficulty_modifier = random.uniform(0.8, 1.2)
            
            # Set duration based on type and difficulty
            duration = self._get_incursion_duration(incursion_type, difficulty_modifier)
            incursion_data['duration_hours'] = duration
            
            # Create the incursion via API
            system_user = self._get_system_user()
            api_data = {
                "title": incursion_data['title'],
                "description": incursion_data['description'],
                "incursion_type": incursion_data['incursion_type'].value,
                "target_exercise": incursion_data['target_exercise'],
                "target_reps": incursion_data['target_reps'],
                "reward_type": incursion_data['reward_type'].value,
                "reward_value": incursion_data['reward_value'],
                "reward_description": incursion_data['reward_description'],
                "duration_hours": duration
            }
            
            response = await self.api_client.create_incursion(system_user, api_data)
            
            # Convert response back to Incursion object
            incursion = Incursion(
                id=response.get('id'),
                incursion_id=response['incursion_id'],
                incursion_type=IncursionType(response['incursion_type']),
                title=response['title'],
                description=response['description'],
                target_exercise=response['target_exercise'],
                target_reps=response['target_reps'],
                current_reps=response['current_reps'],
                reward_type=response['reward_type'],
                reward_value=response['reward_value'],
                reward_description=response['reward_description'],
                created_at=datetime.fromisoformat(response['created_at'].replace('Z', '+00:00')),
                expires_at=datetime.fromisoformat(response['expires_at'].replace('Z', '+00:00')),
                is_active=response.get('status') == 'active',
                metadata=response.get('metadata', {})
            )
            
            # Invalidate cache since we added a new incursion
            await self._invalidate_incursion_cache()
            
            # Announce the incursion
            await self._announce_incursion(incursion)
            
            duration_text = f"{int(duration * 60)} minutes" if duration < 1 else f"{duration:.1f} hours"
            logger.info(f"Spawned {incursion_type.value} incursion: {incursion.incursion_id} (Duration: {duration_text}, Testing: {self.testing_mode})")
            
        except Exception as e:
            logger.error(f"Error spawning incursion: {e}")

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
            
            # Create via API
            system_user = self._get_system_user()
            api_data = {
                "title": incursion_data['title'],
                "description": incursion_data['description'],
                "incursion_type": incursion_data['incursion_type'].value,
                "target_exercise": incursion_data['target_exercise'],
                "target_reps": incursion_data['target_reps'],
                "reward_type": incursion_data['reward_type'].value,
                "reward_value": incursion_data['reward_value'],
                "reward_description": incursion_data['reward_description'],
                "duration_hours": duration
            }
            
            response = await self.api_client.create_incursion(system_user, api_data)
            
            # Convert response back to Incursion object
            incursion = Incursion(
                id=response.get('id'),
                incursion_id=response['incursion_id'],
                incursion_type=IncursionType(response['incursion_type']),
                title=response['title'],
                description=response['description'],
                target_exercise=response['target_exercise'],
                target_reps=response['target_reps'],
                current_reps=response['current_reps'],
                reward_type=response['reward_type'],
                reward_value=response['reward_value'],
                reward_description=response['reward_description'],
                created_at=datetime.fromisoformat(response['created_at'].replace('Z', '+00:00')),
                expires_at=datetime.fromisoformat(response['expires_at'].replace('Z', '+00:00')),
                is_active=response.get('status') == 'active',
                metadata=response.get('metadata', {})
            )
            
            # Invalidate cache
            await self._invalidate_incursion_cache()
            
            await self._announce_incursion(incursion)
            
            return incursion.incursion_id
            
        except Exception as e:
            logger.error(f"Error force spawning incursion: {e}")
            return None

    def _get_time_color_and_percentage(self, incursion) -> tuple[str, str]:
        """Get time color and formatted string based on remaining time"""
        now = datetime.now(timezone.utc)
        
        # Ensure timezone awareness for incursion datetimes
        created_at = incursion.created_at
        expires_at = incursion.expires_at
        
        # If naive, assume UTC
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        total_duration = (expires_at - created_at).total_seconds()
        remaining_time = (expires_at - now).total_seconds()
        
        if remaining_time <= 0:
            return "\x1b[1;31m", "EXPIRED"
        
        # Calculate percentage remaining
        percentage = remaining_time / total_duration
        
        # Color based on time remaining
        if percentage > 0.5:
            color = "\x1b[1;32m"  # Green
        elif percentage > 0.25:
            color = "\x1b[1;33m"  # Yellow
        else:
            color = "\x1b[1;31m"  # Red
        
        # Format time
        if remaining_time < 60:
            time_str = f"{int(remaining_time)}s"
        elif remaining_time < 3600:
            time_str = f"{int(remaining_time // 60)}m {int(remaining_time % 60)}s"
        else:
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            time_str = f"{hours}h {minutes}m"
        
        return color, time_str

    async def _cleanup_expired_incursions(self):
        """Clean up expired incursions and their announcement messages"""
        try:
            # Get all active incursions
            active_incursions = await self._get_cached_active_incursions()
            
            for incursion in active_incursions:
                # Check if incursion has expired
                if incursion.expires_at <= datetime.now(timezone.utc):
                    logger.info(f"Cleaning up expired incursion: {incursion.incursion_id}")
                    
                    # Delete announcement message first (prioritize Discord cleanup)
                    if incursion.metadata and incursion.metadata.get('announcement_message_id'):
                        message_id = incursion.metadata.get('announcement_message_id')
                        channel_id = incursion.metadata.get('announcement_channel_id')
                        
                        if message_id and channel_id:
                            try:
                                channel = self.bot.get_channel(channel_id)
                                if channel:
                                    message = await channel.fetch_message(message_id)
                                    await message.delete()
                                    logger.info(f"Deleted announcement message {message_id} for expired incursion {incursion.incursion_id}")
                            except discord.NotFound:
                                logger.warning(f"Message {message_id} already deleted for incursion {incursion.incursion_id}")
                            except Exception as e:
                                logger.error(f"Error deleting message {message_id}: {e}")
                    
                    # Clear message cache
                    try:
                        cache_key = self.CACHE_KEYS['message_cache'].format(incursion.incursion_id)
                        await self.bot.redis.delete(cache_key)
                    except Exception as e:
                        logger.warning(f"Failed to clear message cache for {incursion.incursion_id}: {e}")
                    
                    # Mark incursion as inactive in database
                    try:
                        system_user = self._get_system_user()
                        await self.api_client.mark_incursion_inactive(system_user, incursion.incursion_id)
                        logger.info(f"Marked incursion {incursion.incursion_id} as inactive")
                    except Exception as e:
                        logger.error(f"Error marking incursion {incursion.incursion_id} as inactive: {e}")
            
            # Invalidate cache after cleanup
            await self._invalidate_incursion_cache()
            
        except Exception as e:
            logger.error(f"Error in cleanup_expired_incursions: {e}")
