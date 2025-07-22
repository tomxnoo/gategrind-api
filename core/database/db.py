# c:\Users\sakko\Downloads\RoFS (1)\RoFS\utils\database\db.py

"""
This module contains all the asynchronous database functions for the bot.
It's designed to work with a connection pool managed by the bot instance.
Each function expects an active asyncpg.Connection object.
"""
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any  # Add missing type imports
import asyncpg
import logging
from core.redis_cache import (
    get_or_cache_user_json_data, 
    invalidate_user_json_cache,
    get_or_cache_system_setting,  # Add missing cache imports
    invalidate_system_settings_cache
)
import sentry_sdk

logger = logging.getLogger(__name__)

# Custom JSON encoder to handle datetime objects which are not native to JSON
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

async def get_user_profile_from_db(conn: asyncpg.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a user's profile data from the users table."""
    row = await conn.fetchrow(
        'SELECT user_id, discord_id, username, display_name, created_at, updated_at FROM users WHERE user_id = $1',
        user_id
    )
    return dict(row) if row else None

async def create_user_profile(conn: asyncpg.Connection, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new user profile and returns it."""
    # Ensure all required fields are present
    required_fields = ["user_id", "discord_id", "username", "display_name"]
    if not all(field in user_data for field in required_fields):
        raise ValueError("Missing required fields for user creation")

    # Insert into the users table
    row = await conn.fetchrow(
        """
        INSERT INTO users (user_id, discord_id, username, display_name, created_at, updated_at)
        VALUES ($1, $2, $3, $4, NOW(), NOW())
        ON CONFLICT (user_id) DO NOTHING
        RETURNING user_id, discord_id, username, display_name, created_at, updated_at
        """,
        user_data["user_id"],
        user_data["discord_id"],
        user_data["username"],
        user_data["display_name"],
    )
    if not row:
        # If row is None, it means the user already existed (ON CONFLICT)
        # so we fetch the existing user's data.
        return await get_user_profile_from_db(conn, user_data["user_id"])

    # Initialize other related data for the new user
    user_id = row['user_id']
    await conn.execute('INSERT INTO user_json_data (user_id, data) VALUES ($1, $2)', user_id, json.dumps({}))
    for stat in ['STR', 'END', 'TECH']:
        await conn.execute(
            'INSERT INTO user_stats (user_id, stat_name, level, xp) VALUES ($1, $2, 1, 0)',
            user_id, stat
        )
    return dict(row)


async def get_user(conn: asyncpg.Connection, user_id: int):
    """Fetches a user's core data."""
    row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    return dict(row) if row else None

async def get_user_stats(connection, user_id: int):
    """Fetches a user's core stats (STR, END, TECH)."""
    stats = {}
    
    for stat in ['STR', 'END', 'TECH']:
        result = await connection.fetchrow(
            "SELECT level, xp FROM user_stats WHERE user_id = $1 AND stat_name = $2",
            user_id, stat
        )
        if result:
            stats[stat] = {"level": result["level"], "xp": result["xp"]}
        else:
            # Default values if no record exists
            stats[stat] = {"level": 1, "xp": 0}
    
    return stats

async def get_user_json_data(conn: asyncpg.Connection, user_id: int) -> dict:
    """Fetches the JSONB data for a user."""
    json_str = await conn.fetchval('SELECT data FROM user_json_data WHERE user_id = $1', user_id)
    if json_str:
        return json.loads(json_str) if isinstance(json_str, str) else json_str
    return {}

async def get_latest_health_data(conn: asyncpg.Connection, user_id: int) -> dict:
    """Fetches the most recent health data for a user."""
    row = await conn.fetchrow(
        'SELECT * FROM health_data WHERE user_id = $1 ORDER BY synced_at DESC LIMIT 1',
        user_id
    )
    return dict(row) if row else {}

async def get_unified_user_data(conn: asyncpg.Connection, user_id: int, bot=None) -> dict:
    """Fetches and merges all user-related data efficiently, using Redis cache if available."""
    if bot is not None:
        # Try Redis cache for user_json_data
        json_data_blob = await get_or_cache_user_json_data(bot, user_id)
    else:
        json_data_blob = await get_user_json_data(conn, user_id)
    # Run queries sequentially to avoid asyncpg concurrency issues
    user_data = await get_user(conn, user_id)
    stats_data = await get_user_stats(conn, user_id)
    data = {}
    if user_data:
        data.update(user_data)
    data['core_stats'] = stats_data
    if json_data_blob:
        data.update(json_data_blob)
    return data

async def clear_log_stats(conn: asyncpg.Connection, user_id: int):
    """Clears all logged stats for a user."""
    async with conn.transaction():
        await conn.execute('DELETE FROM log_stats WHERE user_id = $1', user_id)
        # Also clear the corresponding JSON data if it exists
        await conn.execute(
            """
            UPDATE user_json_data
            SET data = data - 'log_stats'
            WHERE user_id = $1;
            """,
            user_id
        )
    logger.info(f"Cleared log stats for user {user_id}")

async def reset_user_data(conn: asyncpg.Connection, user_id: int, bot=None):
    """Resets all data for a specific user in a single transaction. Invalidates Redis cache if bot is provided."""
    try:
        async with conn.transaction():
            await conn.execute('DELETE FROM activity_log WHERE user_id = $1', user_id)
            await conn.execute('DELETE FROM log_stats WHERE user_id = $1', user_id)
            await conn.execute('DELETE FROM active_buffs WHERE user_id = $1', user_id)
            await conn.execute('DELETE FROM health_data WHERE user_id = $1', user_id)
            await conn.execute('DELETE FROM user_json_data WHERE user_id = $1', user_id)
            await conn.execute('DELETE FROM user_stats WHERE user_id = $1', user_id)
            await conn.execute('UPDATE users SET xp = 0, level = 1, xp_max = 100 WHERE user_id = $1', user_id)
        logger.info(f"Reset all data for user {user_id}")
        if bot is not None:
            await invalidate_user_json_cache(bot, user_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error resetting user data for {user_id}: {e}")
        raise

async def update_user_stat(conn, user_id: int, stat_name: str, level: int, xp: float, bot=None):
    """Updates a user's stat level and xp."""
    try:
        await conn.execute(
            'UPDATE user_stats SET level = $1, xp = $2 WHERE user_id = $3 AND stat_name = $4',
            level, xp, user_id, stat_name
        )
        if bot is not None:
            await invalidate_user_json_cache(bot, user_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error updating user stat for {user_id}: {e}")
        raise

async def update_user(conn: asyncpg.Connection, user_id: int, xp: int, level: int, xp_max: int, bot=None):
    """Updates a user's xp, level, and xp_max."""
    try:
        await conn.execute(
            'UPDATE users SET xp = $1, level = $2, xp_max = $3 WHERE user_id = $4',
            xp, level, xp_max, user_id
        )
        if bot is not None:
            await invalidate_user_json_cache(bot, user_id)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error updating user for {user_id}: {e}")
        raise

async def get_user_daily_quests(conn: asyncpg.Connection, user_id: int, bot=None) -> list:
    """Fetches the user's daily quests from the JSON data, using Redis cache if bot is provided."""
    if bot is not None:
        json_data = await get_or_cache_user_json_data(bot, user_id)
    else:
        json_data = await get_user_json_data(conn, user_id)
    return json_data.get("daily_quests", [])

async def update_user_json_data(conn, user_id: int, new_data: dict, bot=None):
    """Updates the user's JSONB data and returns the new data. Invalidates Redis cache if bot is provided."""
    import json
    from core.database.db import DateTimeEncoder
    await conn.execute(
        'UPDATE user_json_data SET data = $1 WHERE user_id = $2',
        json.dumps(new_data, cls=DateTimeEncoder), user_id
    )
    if bot is not None:
        await invalidate_user_json_cache(bot, user_id)
    return new_data

async def reroll_quest(conn: asyncpg.Connection, user_id: int):
    """Reroll the user's daily quests by generating a new set and saving to DB."""
    from features.quests.logic.daily_quests.daily_quest_logic import reroll_daily_quests
    # This will update the user's daily_quests in the JSON data
    raise RuntimeError("reroll_quest must be called with a bot argument, not a connection")

async def complete_quest(conn: asyncpg.Connection, user_id: int, quest_id: int, bot=None):
    """Mark a daily quest as completed for the user, using DB+cache pattern and cache invalidation."""
    # Fetch user JSON data (prefer Redis cache if bot is provided)
    if bot is not None: 
        json_data = await get_or_cache_user_json_data(bot, user_id)
    else:
        json_data = await get_user_json_data(conn, user_id)
    quests = json_data.get("daily_quests", {}).get("quests", [])
    found = False
    for quest in quests:
        if quest.get("id") == quest_id:
            quest["_completed_flag"] = True
            quest["active"] = False
            found = True
            break
    if found:
        # Save updated JSON data and invalidate cache
        await update_user_json_data(conn, user_id, json_data, bot=bot)
        return True
    return False

# --- WEEKLY CONTRACT OPERATIONS ---

async def reroll_weekly_contract(conn: asyncpg.Connection, user_id: int) -> bool:
    """Reroll the user's weekly contract by generating a new set and saving to DB."""
    from features.quests.logic.weekly_quests.reroll_weekly_contracts import reroll_weekly_contracts
    # This will update the user's weekly contracts in the DB
    return await reroll_weekly_contracts(user_id)

# Add these optimized functions to the existing db.py file

async def get_user_profile_from_db(conn: asyncpg.Connection, user_id: int, bot=None) -> Optional[Dict[str, Any]]:
    """Fetches a complete user profile from the database, structured to match the UserProfile model."""
    if bot is not None:
        cache_key = bot.redis.get_cache_key('user_profile', user_id=user_id)
        cached_profile = await bot.redis.get_json(cache_key)
        if cached_profile:
            # Pydantic needs a real datetime object, not an ISO string
            if 'created_at' in cached_profile and isinstance(cached_profile['created_at'], str):
                cached_profile['created_at'] = datetime.fromisoformat(cached_profile['created_at'])
            if 'updated_at' in cached_profile and isinstance(cached_profile['updated_at'], str):
                cached_profile['updated_at'] = datetime.fromisoformat(cached_profile['updated_at'])
            return cached_profile

    query = """
    SELECT 
        u.user_id, 
        u.user_id AS discord_id, -- Aliasing user_id to discord_id
        u.username, 
        u.xp, 
        u.level, 
        u.xp_max, 
        u.created_at, 
        u.created_at as updated_at, -- Use created_at as a fallback for updated_at
        ujd.data as json_data,
        json_object_agg(
            us.stat_name, 
            json_build_object('level', us.level, 'xp', us.xp)
        ) FILTER (WHERE us.stat_name IS NOT NULL) as stats
    FROM users u
    LEFT JOIN user_json_data ujd ON u.user_id = ujd.user_id
    LEFT JOIN user_stats us ON u.user_id = us.user_id
    WHERE u.user_id = $1
    GROUP BY u.user_id, u.username, u.xp, u.level, u.xp_max, u.created_at, ujd.data
    """
    
    row = await conn.fetchrow(query, user_id)
    
    if not row:
        return None

    data = dict(row)
    
    # Start building the final profile dictionary
    profile = {
        'user_id': data.get('user_id'),
        'discord_id': str(data.get('discord_id', '0')),  # Ensure discord_id is a string
        'username': data.get('username', 'Unknown User'),
        'xp': data.get('xp', 0),
        'level': data.get('level', 1),
        'xp_max': data.get('xp_max', 100),
        'created_at': data.get('created_at') or datetime.utcnow(),
        'updated_at': data.get('updated_at') or datetime.utcnow(),
        'active_buffs': {},
        'stats': {}
    }

    # Process stats, ensuring all base stats are present
    user_stats = data.get('stats') or {}
    for stat_name in ['STR', 'END', 'TECH']:
        if stat_name not in user_stats:
            user_stats[stat_name] = {'level': 1, 'xp': 0}
    profile['stats'] = user_stats

    # Process JSON data for active_buffs and other dynamic fields
    if data.get('json_data'):
        json_data = json.loads(data['json_data']) if isinstance(data['json_data'], str) else data['json_data']
        profile['active_buffs'] = json_data.get('active_buffs', {})
        # Add any other fields from json_data that might be part of the profile
        # For now, we only explicitly need active_buffs for the UserProfile model

    if bot is not None:
        ttl = bot.redis.get_ttl('user_profile')
        # Use custom encoder for datetime objects before caching
        await bot.redis.set_json(cache_key, profile, expire=ttl, default=DateTimeEncoder().default)

    return profile

async def get_unified_user_data_optimized(conn: asyncpg.Connection, user_id: int, bot=None) -> dict:
    """Optimized version with better caching and single query where possible"""
    if bot is not None:
        # Try to get complete profile from cache first
        cache_key = bot.redis.get_cache_key('user_profile', user_id=user_id)
        cached_profile = await bot.redis.get_json(cache_key)
        if cached_profile:
            return cached_profile
    
    # Single optimized query to get all user data at once
    try:
        query = """
        SELECT 
            u.user_id, u.username, u.xp, u.level, u.xp_max, u.created_at,
            ujd.data as json_data,
            array_agg(
                json_build_object(
                    'stat_name', us.stat_name,
                    'level', us.level,
                    'xp', us.xp
                )
            ) FILTER (WHERE us.stat_name IS NOT NULL) as stats
        FROM users u
        LEFT JOIN user_json_data ujd ON u.user_id = ujd.user_id
        LEFT JOIN user_stats us ON u.user_id = us.user_id
        WHERE u.user_id = $1
        GROUP BY u.user_id, u.username, u.xp, u.level, u.xp_max, u.created_at, ujd.data
        """
        
        row = await conn.fetchrow(query, user_id)
        
        if not row:
            return {}
        
        # Build unified data structure
        data = {
            'user_id': row['user_id'],
            'username': row['username'],
            'xp': row['xp'],
            'level': row['level'],
            'xp_max': row['xp_max'],
            'created_at': row['created_at'],
        }
        
        # Process stats
        core_stats = {}
        if row['stats']:
            for stat in row['stats']:
                if stat:  # Filter out None values
                    core_stats[stat['stat_name']] = {
                        'level': stat['level'],
                        'xp': stat['xp']
                    }
        
        # Ensure all required stats exist
        for stat in ['STR', 'END', 'TECH']:
            if stat not in core_stats:
                core_stats[stat] = {'level': 1, 'xp': 0}
        
        data['core_stats'] = core_stats
        
        # Process JSON data
        if row['json_data']:
            json_data = json.loads(row['json_data']) if isinstance(row['json_data'], str) else row['json_data']
            data.update(json_data)
        
        # Cache the result if bot is available
        if bot is not None:
            ttl = bot.redis.get_ttl('user_profile')
            await bot.redis.set_json(cache_key, data, expire=ttl)
        
        return data
        
    except Exception as e:
        logger.error(f"Error in optimized user data fetch for {user_id}: {e}")
        # Fallback to original method
        return await get_unified_user_data(conn, user_id, bot)

async def batch_get_user_profiles(conn: asyncpg.Connection, user_ids: List[int], bot=None) -> Dict[int, dict]:
    """Batch fetch multiple user profiles efficiently"""
    if not user_ids:
        return {}
    
    profiles = {}
    uncached_ids = []
    
    # Check cache for each user if bot is available
    if bot is not None:
        for user_id in user_ids:
            cache_key = bot.redis.get_cache_key('user_profile', user_id=user_id)
            cached_profile = await bot.redis.get_json(cache_key)
            if cached_profile:
                profiles[user_id] = cached_profile
            else:
                uncached_ids.append(user_id)
    else:
        uncached_ids = user_ids
    
    # Batch fetch uncached profiles
    if uncached_ids:
        query = """
        SELECT 
            u.user_id, u.username, u.xp, u.level, u.xp_max, u.created_at,
            ujd.data as json_data,
            array_agg(
                json_build_object(
                    'stat_name', us.stat_name,
                    'level', us.level,
                    'xp', us.xp
                )
            ) FILTER (WHERE us.stat_name IS NOT NULL) as stats
        FROM users u
        LEFT JOIN user_json_data ujd ON u.user_id = ujd.user_id
        LEFT JOIN user_stats us ON u.user_id = us.user_id
        WHERE u.user_id = ANY($1)
        GROUP BY u.user_id, u.username, u.xp, u.level, u.xp_max, u.created_at, ujd.data
        """
        
        rows = await conn.fetch(query, uncached_ids)
        
        for row in rows:
            user_id = row['user_id']
            
            # Build profile data (same logic as optimized single fetch)
            data = {
                'user_id': user_id,
                'username': row['username'],
                'xp': row['xp'],
                'level': row['level'],
                'xp_max': row['xp_max'],
                'created_at': row['created_at'],
            }
            
            # Process stats
            core_stats = {}
            if row['stats']:
                for stat in row['stats']:
                    if stat:
                        core_stats[stat['stat_name']] = {
                            'level': stat['level'],
                            'xp': stat['xp']
                        }
            
            for stat in ['STR', 'END', 'TECH']:
                if stat not in core_stats:
                    core_stats[stat] = {'level': 1, 'xp': 0}
            
            data['core_stats'] = core_stats
            
            # Process JSON data
            if row['json_data']:
                json_data = json.loads(row['json_data']) if isinstance(row['json_data'], str) else row['json_data']
                data.update(json_data)
            
            profiles[user_id] = data
            
            # Cache individual profile
            if bot is not None:
                cache_key = bot.redis.get_cache_key('user_profile', user_id=user_id)
                ttl = bot.redis.get_ttl('user_profile')
                await bot.redis.set_json(cache_key, data, expire=ttl)
    
    return profiles

# Enhanced system settings with caching
async def get_system_setting_cached(conn: asyncpg.Connection, setting_key: str, default_value=None, bot=None):
    """Get system setting with Redis caching"""
    if bot is not None:
        return await get_or_cache_system_setting(bot, setting_key, default_value)
    else:
        return await get_system_setting(conn, setting_key, default_value)

async def set_system_setting_cached(conn: asyncpg.Connection, setting_key: str, setting_value, bot=None):
    """Set system setting and invalidate cache"""
    await set_system_setting(conn, setting_key, setting_value)
    
    if bot is not None:
        await invalidate_system_settings_cache(bot, setting_key)

async def get_system_setting(conn: asyncpg.Connection, setting_key: str, default_value=None):
    """Get a system setting value"""
    try:
        row = await conn.fetchrow(
            'SELECT setting_value FROM system_settings WHERE setting_key = $1',
            setting_key
        )
        if row:
            return row['setting_value']
        return default_value
    except Exception as e:
        logger.error(f"Error getting system setting {setting_key}: {e}")
        return default_value

async def set_system_setting(conn: asyncpg.Connection, setting_key: str, setting_value):
    """Set a system setting value"""
    try:
        await conn.execute(
            '''
            INSERT INTO system_settings (setting_key, setting_value, updated_at)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (setting_key) 
            DO UPDATE SET 
                setting_value = EXCLUDED.setting_value,
                updated_at = CURRENT_TIMESTAMP
            ''',
            setting_key, json.dumps(setting_value)
        )
        logger.info(f"Updated system setting {setting_key} = {setting_value}")
    except Exception as e:
        logger.error(f"Error setting system setting {setting_key}: {e}")
        raise