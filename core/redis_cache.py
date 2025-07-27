import redis.asyncio as aioredis
import json
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta

# Import fakeredis for development
try:
    import fakeredis.aioredis
    FAKEREDIS_AVAILABLE = True
except ImportError:
    FAKEREDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, url: str):
        self.url = url
        self.pool = None
        self.use_fake_redis = FAKEREDIS_AVAILABLE
        
        # Cache key patterns for different data types
        self.CACHE_KEYS = {
            'user_json_data': 'user:json:{user_id}',
            'user_stats': 'user:stats:{user_id}',
            'user_profile': 'user:profile:{user_id}',
            'active_incursions': 'incursions:active',
            'incursion_messages': 'incursions:messages:{incursion_id}',
            'system_settings': 'system:settings:{key}',
            'daily_quests': 'user:quests:daily:{user_id}',
            'weekly_contracts': 'user:quests:weekly:{user_id}',
            'active_buffs': 'user:buffs:{user_id}',
            'leaderboard': 'leaderboard:{type}:{period}',
        }
        
        # Default TTL values (in seconds)
        self.DEFAULT_TTL = {
            'user_json_data': 3600,      # 1 hour
            'user_stats': 1800,          # 30 minutes
            'user_profile': 1800,        # 30 minutes
            'active_incursions': 30,     # 30 seconds
            'incursion_messages': 60,    # 1 minute
            'system_settings': 7200,     # 2 hours
            'daily_quests': 3600,        # 1 hour
            'weekly_contracts': 7200,    # 2 hours
            'active_buffs': 900,         # 15 minutes
            'leaderboard': 300,          # 5 minutes
        }

    async def connect(self):
        if self.use_fake_redis:
            # Use fakeredis for development (no Docker required)
            self.pool = fakeredis.aioredis.FakeRedis(decode_responses=True)
            logger.info("Connected to FakeRedis (development mode)")
        else:
            # Use real Redis in production
            self.pool = await aioredis.from_url(self.url, decode_responses=True)
            logger.info(f"Connected to Redis at {self.url}")

    async def close(self):
        if self.pool:
            if self.use_fake_redis:
                # FakeRedis doesn't need explicit closing
                self.pool = None
                logger.info("FakeRedis connection closed")
            else:
                await self.pool.close()
                logger.info("Redis connection closed")

    async def get(self, key: str):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        return await self.pool.get(key)

    async def set(self, key: str, value, expire: int | None = None):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        await self.pool.set(key, value, ex=expire)

    async def delete(self, key: str):
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        await self.pool.delete(key)
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching a pattern"""
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        try:
            keys = await self.pool.keys(pattern)
            if keys:
                await self.pool.delete(*keys)
                logger.debug(f"Deleted {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Error deleting keys with pattern {pattern}: {e}")
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """Get and deserialize JSON data"""
        try:
            data = await self.get(key)
            return json.loads(data) if data else None
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Error deserializing JSON from cache key {key}: {e}")
            return None
    
    async def set_json(self, key: str, data: Any, expire: int | None = None):
        """Serialize and set JSON data"""
        try:
            await self.set(key, json.dumps(data), expire)
        except Exception as e:
            logger.warning(f"Error serializing JSON to cache key {key}: {e}")
    
    def get_cache_key(self, key_type: str, **kwargs) -> str:
        """Generate cache key from pattern"""
        pattern = self.CACHE_KEYS.get(key_type)
        if not pattern:
            raise ValueError(f"Unknown cache key type: {key_type}")
        return pattern.format(**kwargs)
    
    def get_ttl(self, key_type: str) -> int:
        """Get default TTL for key type"""
        return self.DEFAULT_TTL.get(key_type, 3600)

# Enhanced caching functions with comprehensive coverage

async def get_or_cache_user_json_data(bot, user_id: int) -> dict:
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            return await db.get_user_json_data(conn, user_id)
    
    cache_key = f"user_json_data:{user_id}"
    user_json = await get_user_json_from_cache(bot, user_id)
    if user_json is None:
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            data = await db.get_user_json_data(conn, user_id)
            await bot.redis.set(cache_key, json.dumps(data), expire=3600)
            return data
    return user_json

async def get_user_json_from_cache(bot, user_id: int):
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            return await db.get_user_json_data(conn, user_id)
    
    cache_key = f"user_json_data:{user_id}"
    cached = await bot.redis.get(cache_key)
    if cached:
        return json.loads(cached)
    async with bot.db_pool.acquire() as conn:
        from core.database import db
        data = await db.get_user_json_data(conn, user_id)
        await bot.redis.set(cache_key, json.dumps(data), expire=3600)
        return data

async def get_or_cache_user_profile(bot, user_id: int) -> Optional[Dict]:
    """Get complete user profile with comprehensive caching"""
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            return await db.get_unified_user_data(conn, user_id, bot)
    
    cache_key = bot.redis.get_cache_key('user_profile', user_id=user_id)
    
    # Try cache first
    cached_data = await bot.redis.get_json(cache_key)
    if cached_data:
        logger.debug(f"Cache hit for user profile {user_id}")
        return cached_data
    
    # Fallback to database
    try:
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            profile_data = await db.get_unified_user_data(conn, user_id, bot)
            
            # Cache the result
            ttl = bot.redis.get_ttl('user_profile')
            await bot.redis.set_json(cache_key, profile_data, expire=ttl)
            logger.debug(f"Cached user profile {user_id} for {ttl}s")
            
            return profile_data
    except Exception as e:
        logger.error(f"Error fetching user profile {user_id}: {e}")
        return None

async def get_or_cache_user_stats(bot, user_id: int) -> Optional[Dict]:
    """Get user stats with caching"""
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            return await db.get_user_stats(conn, user_id)
    
    cache_key = bot.redis.get_cache_key('user_stats', user_id=user_id)
    
    cached_data = await bot.redis.get_json(cache_key)
    if cached_data:
        return cached_data
    
    try:
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            stats_data = await db.get_user_stats(conn, user_id)
            
            ttl = bot.redis.get_ttl('user_stats')
            await bot.redis.set_json(cache_key, stats_data, expire=ttl)
            
            return stats_data
    except Exception as e:
        logger.error(f"Error fetching user stats {user_id}: {e}")
        return None

async def get_or_cache_daily_quests(bot, user_id: int) -> List:
    """Get daily quests with caching"""
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database.db import get_user_daily_quests
            return await get_user_daily_quests(conn, user_id, bot)
    
    cache_key = bot.redis.get_cache_key('daily_quests', user_id=user_id)
    
    cached_data = await bot.redis.get_json(cache_key)
    if cached_data:
        return cached_data
    
    try:
        async with bot.db_pool.acquire() as conn:
            from core.database.db import get_user_daily_quests
            quests_data = await get_user_daily_quests(conn, user_id, bot)
            
            ttl = bot.redis.get_ttl('daily_quests')
            await bot.redis.set_json(cache_key, quests_data, expire=ttl)
            
            return quests_data
    except Exception as e:
        logger.error(f"Error fetching daily quests {user_id}: {e}")
        return []

async def get_or_cache_active_buffs(bot, user_id: int) -> List:
    """Get active buffs with caching"""
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            buffs_data = await conn.fetch(
                "SELECT * FROM active_buffs WHERE user_id = $1 AND expires_at > NOW()",
                user_id
            )
            return [dict(row) for row in buffs_data]
    
    cache_key = bot.redis.get_cache_key('active_buffs', user_id=user_id)
    
    cached_data = await bot.redis.get_json(cache_key)
    if cached_data:
        return cached_data
    
    try:
        async with bot.db_pool.acquire() as conn:
            buffs_data = await conn.fetch(
                "SELECT * FROM active_buffs WHERE user_id = $1 AND expires_at > NOW()",
                user_id
            )
            buffs_list = [dict(row) for row in buffs_data]
            
            ttl = bot.redis.get_ttl('active_buffs')
            await bot.redis.set_json(cache_key, buffs_list, expire=ttl)
            
            return buffs_list
    except Exception as e:
        logger.error(f"Error fetching active buffs {user_id}: {e}")
        return []

async def get_or_cache_system_setting(bot, setting_key: str, default_value=None):
    """Get system setting with caching"""
    cache_key = bot.redis.get_cache_key('system_settings', key=setting_key)
    
    cached_data = await bot.redis.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        async with bot.db_pool.acquire() as conn:
            from core.database.db import get_system_setting
            setting_value = await get_system_setting(conn, setting_key, default_value)
            
            ttl = bot.redis.get_ttl('system_settings')
            await bot.redis.set(cache_key, setting_value or '', expire=ttl)
            
            return setting_value
    except Exception as e:
        logger.error(f"Error fetching system setting {setting_key}: {e}")
        return default_value

# Cache invalidation functions

async def invalidate_user_cache(bot, user_id: int):
    """Invalidate all cache entries for a user"""
    # Check if Redis is available
    if bot.redis is None:
        logger.debug(f"Redis not available, skipping cache invalidation for user {user_id}")
        return
        
    patterns = [
        f"user:*:{user_id}",
        f"user:*:*:{user_id}",
    ]
    
    for pattern in patterns:
        await bot.redis.delete_pattern(pattern)
    
    logger.debug(f"Invalidated all cache for user {user_id}")

async def invalidate_system_settings_cache(bot, setting_key: str = None):
    """Invalidate system settings cache"""
    # Check if Redis is available
    if bot.redis is None:
        logger.debug(f"Redis not available, skipping system settings cache invalidation")
        return
        
    if setting_key:
        cache_key = bot.redis.get_cache_key('system_settings', key=setting_key)
        await bot.redis.delete(cache_key)
    else:
        await bot.redis.delete_pattern("system:settings:*")
    
    logger.debug(f"Invalidated system settings cache: {setting_key or 'all'}")

async def invalidate_incursions_cache(bot):
    """Invalidate incursions cache"""
    # Check if Redis is available
    if bot.redis is None:
        logger.debug("Redis not available, skipping incursions cache invalidation")
        return
        
    await bot.redis.delete_pattern("incursions:*")
    logger.debug("Invalidated incursions cache")

# Legacy functions for backward compatibility
async def get_user_json_from_cache(bot, user_id: int):
    # Check if Redis is available
    if bot.redis is None:
        # Fallback to direct database access
        async with bot.db_pool.acquire() as conn:
            from core.database import db
            return await db.get_user_json_data(conn, user_id)
            
    cache_key = f"user_json_data:{user_id}"
    cached = await bot.redis.get(cache_key)
    if cached:
        return json.loads(cached)
    async with bot.db_pool.acquire() as conn:
        from core.database import db
        data = await db.get_user_json_data(conn, user_id)
        await bot.redis.set(cache_key, json.dumps(data), expire=3600)
        return data

async def invalidate_user_json_cache(bot, user_id: int):
    # Check if Redis is available
    if bot.redis is None:
        logger.debug(f"Redis not available, skipping user JSON cache invalidation for user {user_id}")
        return
        
    cache_key = f"user_json_data:{user_id}"
    await bot.redis.delete(cache_key)