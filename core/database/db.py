# c:\Users\sakko\Downloads\RoFS (1)\RoFS\utils\database\db.py

"""
This module contains all the asynchronous database functions for the bot.
It's designed to work with a connection pool managed by the bot instance.
Each function expects an active asyncpg.Connection object.
"""
import json
import asyncio
from datetime import datetime
import asyncpg
import logging
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
import sentry_sdk

logger = logging.getLogger(__name__)

# Custom JSON encoder to handle datetime objects which are not native to JSON
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

async def get_user(conn: asyncpg.Connection, user_id: int):
    """Fetches a user's core data."""
    row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    return dict(row) if row else None

async def get_user_stats(conn: asyncpg.Connection, user_id: int):
    """Fetches a user's core stats (STR, END, SPR)."""
    rows = await conn.fetch('SELECT stat_name, level, xp FROM user_stats WHERE user_id = $1', user_id)
    stats = {r['stat_name']: {'level': r['level'], 'xp': r['xp']} for r in rows}
    for stat in ['STR', 'END', 'SPR']:
        if stat not in stats:
            stats[stat] = {'level': 1, 'xp': 0.0}
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

# Add these functions to the existing db.py file

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