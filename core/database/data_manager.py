# --- PROFILE RESET WRAPPER ---
async def reset_user_profile(bot, user_id: int):
    """
    Resets all data for a specific user by calling the db layer.
    """
    async with bot.db_pool.acquire() as conn:
        from core.database import db
        await db.reset_user_data(conn, user_id, bot)
# utils/database/data_manager.py
"""
Data Manager for all user-profile related database and cache operations.
This module abstracts the data layer from the UI, providing a clean interface
for fetching user data from PostgreSQL with a Redis caching layer.
"""
import asyncio
import datetime
from typing import Any, Dict, List, Optional, Tuple
import sentry_sdk
import logging
import redis.asyncio as redis
from typing import Dict, Any, Optional

from core.database import db


async def get_user_profile(bot, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a user's complete profile data from the database, with Redis caching.

    Args:
        bot: The bot instance, which holds the db and redis pools.
        user_id: The Discord user's ID.

    Returns:
        A dictionary containing the user's profile data, or None if not found.
    """
    try:
        async with bot.db_pool.acquire() as conn:
            # get_unified_user_data already handles caching for the JSON part
            user_data = await db.get_unified_user_data(conn, user_id, bot)
            
            # Manually fetch and merge health data for a truly unified profile
            health_data = await db.get_latest_health_data(conn, user_id)
            if health_data:
                user_data['health_fitness'] = health_data

            # Restructure stats to match the desired UI format
            if 'core_stats' in user_data:
                user_data['stats'] = {
                    "Strength": user_data['core_stats'].get('STR', {}).get('level', 1),
                    "Dexterity": user_data['core_stats'].get('DEX', {}).get('level', 1), # Assuming DEX might exist
                    "Endurance": user_data['core_stats'].get('END', {}).get('level', 1),
                    "Intelligence": user_data['core_stats'].get('INT', {}).get('level', 1), # Assuming INT might exist
                    "Charisma": user_data['core_stats'].get('CHA', {}).get('level', 1), # Assuming CHA might exist
                }
                # Add any other stats as needed
            
            return user_data
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error fetching profile for user {user_id}: {e}")
        return None

async def get_completed_quests(bot, user_id: int, page: int = 1, page_size: int = 5) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fetches a paginated list of a user's completed quests from their JSON data.

    Args:
        bot: The bot instance.
        user_id: The Discord user's ID.
        page: The page number to fetch.
        page_size: The number of items per page.

    Returns:
        A tuple containing the list of quests for the current page and the total number of pages.
    """
    try:
        json_data = await get_or_cache_user_json_data(bot, user_id)
        
        # FIXED: Look in the completed_quests array instead of daily_quests.quests
        all_completed_quests = json_data.get("completed_quests", [])
        
        # Also include any completed quests from daily_quests for backward compatibility
        daily_quests = json_data.get("daily_quests", {}).get("quests", [])
        for quest in daily_quests:
            if isinstance(quest, dict) and quest.get("_completed_flag"):
                # Add to completed quests if not already there
                quest_entry = {
                    "quest": quest,
                    "completed_at": quest.get("completed_at", "Unknown"),
                    "completed_by": quest.get("completed_by", "Unknown")
                }
                all_completed_quests.append(quest_entry)
        
        # Sort by completion date (newest first)
        all_completed_quests.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
        
        total_items = len(all_completed_quests)
        total_pages = (total_items + page_size - 1) // page_size or 1
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        return all_completed_quests[start_index:end_index], total_pages
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error fetching completed quests for user {user_id}: {e}")
        return [], 1

async def get_movement_logs(bot, user_id: int, page: int = 1, page_size: int = 5) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fetches a paginated list of a user's movement logs from their JSON data.

    Args:
        bot: The bot instance.
        user_id: The Discord user's ID.
        page: The page number to fetch.
        page_size: The number of items per page.

    Returns:
        A tuple containing the list of logs for the current page and the total number of pages.
    """
    try:
        json_data = await get_or_cache_user_json_data(bot, user_id)
        all_logs = json_data.get("movement_logs", [])
        
        total_items = len(all_logs)
        total_pages = (total_items + page_size - 1) // page_size or 1
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        return all_logs[start_index:end_index], total_pages
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error fetching movement logs for user {user_id}: {e}")
        return [], 1

async def get_movement_summary_last_7_days(bot, user_id: int) -> Dict[str, int]:
    """
    Fetches and aggregates total reps per day for the last 7 days from JSON data.

    Args:
        bot: The bot instance.
        user_id: The Discord user's ID.

    Returns:
        A dictionary with dates as keys and total reps as values.
    """
    try:
        summary = {}
        today = datetime.date.today()
        for i in range(7):
            day = today - datetime.timedelta(days=i)
            summary[day.strftime("%Y-%m-%d")] = 0

        json_data = await get_or_cache_user_json_data(bot, user_id)
        all_logs = json_data.get("movement_logs", [])
        
        for log in all_logs:
            try:
                # Handle different possible datetime formats
                log_date_str = log.get("logged_at", "")
                if 'T' in log_date_str:
                    log_date = datetime.datetime.fromisoformat(log_date_str.replace("Z", "+00:00")).date()
                else:
                    log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d").date()

                log_date_key = log_date.strftime("%Y-%m-%d")
                if log_date_key in summary:
                    summary[log_date_key] += log.get("reps", 0)
            except (ValueError, TypeError):
                continue # Ignore logs with invalid date formats
                
        return summary
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error(f"Error fetching movement summary for user {user_id}: {e}")
        return {}


async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    return await db.get_user_data(user_id)


async def update_user_data(user_id: int, data: Dict[str, Any]):
    from core.database import db
    await db.update_user_data(user_id, data)