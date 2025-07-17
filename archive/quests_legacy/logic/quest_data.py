# utils/quest_data.py
# LEGACY FILE-BASED QUEST STORAGE - DEPRECATED
# All quest data should now be stored in the database and accessed via DB+Redis helpers.
# These functions are retained for reference only and should not be used in production.

import os
import json
from datetime import datetime, timedelta
# Change line 9 from:
# from shared.utils.database import db as db_utils
# To:
from core.database import db as db_utils

QUEST_TEMPLATES_FILE = 'data/quest_templates.json'
QUEST_DIR = "data/quests"
os.makedirs(QUEST_DIR, exist_ok=True)

def get_quest_file_path(user_id):
    return os.path.join(QUEST_DIR, f"{user_id}.json")

def load_user_quests(user_id):
    path = get_quest_file_path(user_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_user_quests(user_id, data):
    path = get_quest_file_path(user_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_today_quests(user_id):
    data = load_user_quests(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if data and data.get("date") == today:
        return data["quests"]
    return None

def save_today_quests(user_id, quests):
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "date": today,
        "quests": quests
    }
    save_user_quests(user_id, data)

# REVISED: Use DB+cache for quest saving
async def save_today_quests_db(conn, user_id, quests, bot=None):
    today = datetime.now().strftime("%Y-%m-%d")
    # Fetch current user JSON data
    json_data = await db_utils.get_user_json_data(conn, user_id)
    json_data["daily_quests"] = {"date": today, "quests": quests}
    await db_utils.update_user_json_data(conn, user_id, json_data, bot=bot)
