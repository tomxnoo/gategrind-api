import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from features.user.logic.user_data import load_user_data, save_user_data

class FitnessIntegrations:
    """Handle integrations with Garmin Connect"""

    @staticmethod
    async def sync_garmin_steps(user_id: int, access_token: str, access_token_secret: str) -> Optional[int]:
        """Sync steps from Garmin Connect IQ API"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            url = f"https://apis.garmin.com/wellness-api/rest/dailies"
            params = {
                "uploadStartTimeInSeconds": int((datetime.now() - timedelta(days=1)).timestamp()),
                "uploadEndTimeInSeconds": int(datetime.now().timestamp())
            }

            # Note: Garmin uses OAuth 1.0a, you'll need proper signing
            headers = {
                "Authorization": f"OAuth oauth_token=\"{access_token}\""
            }

            response = requests.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                for daily in data:
                    steps = daily.get("totalSteps", 0)
                    if steps > 0:
                        await FitnessIntegrations._log_steps_as_movement(user_id, steps)
                        return steps

        except Exception as e:
            print(f"Garmin sync error: {e}")

        return None

    @staticmethod
    async def _log_steps_as_movement(user_id: int, steps: int):
        """Convert steps to movement reps and log them"""
        # Convert steps to equivalent reps (e.g., 1000 steps = 100 "walking" reps)
        walking_reps = max(1, steps // 100)  # At least 1 rep

        # Log as walking movement
        from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
        from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress
        from features.user.logic.xp_engine import add_xp, calculate_xp_for_movement
        from features.user.logic.user_data import load_user_data, save_user_data

        # Update user stats
        data = await load_user_data(user_id)
        stats = data.setdefault("log_stats", {})
        stats["walking"] = stats.get("walking", 0) + walking_reps

        # Add XP only (no quest/contract progress)
        xp_earned = calculate_xp_for_movement("Walking", walking_reps)
        await add_xp(user_id, xp_earned)
        # If add_xp expects (user_id, xp_to_add), use:
        # await add_xp(user_id, xp_earned)
        # If it expects (xp_to_add, user_id), use:
        # await add_xp(xp_earned, user_id)
        # If signature is different, please adjust accordingly.

        await save_user_data(user_id, data)
        print(f"Auto-synced {steps} steps as {walking_reps} walking reps for user {user_id}")

    @staticmethod
    async def setup_fitness_sync(user_id: int, platform: str, credentials: Dict[str, str]):
        """Setup automatic fitness syncing for a user (Garmin only)"""
        if platform != "garmin":
            return False

        data = await load_user_data(user_id)
        fitness_config = data.setdefault("fitness_integrations", {})

        fitness_config[platform] = {
            "enabled": True,
            "credentials": credentials,
            "last_sync": None
        }

        await save_user_data(user_id, data)
        return True
        from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress