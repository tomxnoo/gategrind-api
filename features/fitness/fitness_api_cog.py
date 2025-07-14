# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
import aiohttp
from discord.ext import commands
from features.user.logic.user_data import load_user_data, save_user_data, add_recent_activity
from features.user.logic.xp_engine import add_xp, calculate_xp_for_movement
from features.quests.logic.daily_quests.daily_quest_logic import update_quest_progress
from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress

class FitnessAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Your deployed OAuth server URL
        self.fitness_hub_url = "https://syncros.replit.app"

    async def sync_fitness_data(self, user_id: int, force_refresh: bool = False, sync_date: str = None):
        """Sync fitness data from Garmin via external API"""
        async with aiohttp.ClientSession() as session:
            try:
                # Use single primary endpoint to avoid rate limiting
                from datetime import datetime, timedelta
                if sync_date:
                    today = sync_date
                else:
                    today = datetime.now().strftime("%Y-%m-%d")

                # Use only the primary sync endpoint with date and refresh parameters
                endpoint = f"{self.fitness_hub_url}/api/sync/{user_id}?date={today}&refresh={force_refresh}"

                try:
                    async with session.get(endpoint) as response:
                        print(f"[DEBUG] Using endpoint: {endpoint}, Status: {response.status}")

                        if response.status == 200:
                            data = await response.json()
                            print(f"[DEBUG] Response data: {data}")

                            # Handle different response formats
                            total_steps = data.get('total_steps', 0) or data.get('steps', 0)

                            # Check nested platform data
                            if total_steps == 0 and 'platforms' in data:
                                platforms = data['platforms']
                                if 'garmin' in platforms:
                                    garmin_data = platforms['garmin']
                                    if isinstance(garmin_data, dict):
                                        total_steps = garmin_data.get('steps', 0)
                                    else:
                                        total_steps = garmin_data if isinstance(garmin_data, int) else 0

                            # Check if there's a direct garmin key
                            if total_steps == 0 and 'garmin' in data:
                                garmin_data = data['garmin']
                                if isinstance(garmin_data, dict):
                                    total_steps = garmin_data.get('steps', 0)
                                else:
                                    total_steps = garmin_data if isinstance(garmin_data, int) else 0

                            print(f"[DEBUG] Extracted total_steps: {total_steps}")
                            print(f"[DEBUG] Platform status: {data.get('platforms', {}).get('garmin', {}).get('status', 'unknown')}")

                                # Always update sync status
                            user_data = await load_user_data(user_id)
                            sync_info = {
                                "last_sync": datetime.now().isoformat(),
                                "sync_date": today,
                                "raw_response": data,
                                "extracted_steps": total_steps
                            }
                            user_data["last_step_sync"] = sync_info

                            if total_steps > 0:
                                # Improved duplicate protection and step tracking
                                from datetime import datetime, timedelta
                                current_time = datetime.now()

                                # Store daily steps with date key
                                daily_steps_key = f"daily_steps_{today}"
                                previous_daily_steps = user_data.get(daily_steps_key, 0)

                                # Calculate only NEW steps since last sync
                                new_steps = max(0, total_steps - previous_daily_steps)
                                walking_reps = new_steps // 100 if new_steps >= 100 else 0

                                print(f"[DEBUG] Previous steps: {previous_daily_steps}, Current: {total_steps}, New: {new_steps}, Reps: {walking_reps}")

                                # Update daily steps regardless of reps
                                user_data[daily_steps_key] = total_steps

                                if walking_reps > 0:
                                    # Update log stats first
                                    stats = user_data.setdefault("log_stats", {})
                                    stats["Walking"] = stats.get("Walking", 0) + walking_reps

                                    # Calculate and add XP properly  
                                    xp_earned = calculate_xp_for_movement("Walking", walking_reps)
                                    print(f"[DEBUG] Calculated {xp_earned} XP for {walking_reps} walking reps")

                                    xp_result = await add_xp(user_id, xp_earned)
                                    print(f"[DEBUG] XP addition result: {xp_result}")

                                    # Update quest progress
                                    await update_quest_progress(user_id, "Walking", walking_reps)
                                    await update_weekly_progress(user_id, self.bot, "Walking", walking_reps)

                                    # Add activity log entry for the XP gain (not sync message)
                                    from features.user.logic.user_data import add_recent_activity
                                    await add_recent_activity(user_id, f"Earned {xp_earned} XP from {walking_reps} walking reps (+{new_steps} steps)")

                                    print(f"[DEBUG] Successfully processed {walking_reps} walking reps for {xp_earned} XP")

                                # Update connection status for profile display  
                                fitness_integrations = user_data.setdefault("fitness_integrations", {})
                                fitness_integrations["apple_health"] = {
                                    "enabled": True,
                                    "connection_type": "health_app_sync",
                                    "last_sync": current_time.isoformat(),
                                    "credentials": {"connected": True}
                                }
                                
                                # Save the updated fitness integration status
                                await save_user_data(user_id, user_data)
                                # Write-through: Invalidate cache after DB write
                                from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
                                await invalidate_user_json_cache(self.bot, user_id)
                                await get_or_cache_user_json_data(self.bot, user_id)

                                return {
                                    "success": True,
                                    "total_steps": total_steps,
                                    "walking_reps": walking_reps,
                                    "platforms": data.get('platforms', {"garmin": total_steps}),
                                    "sync_date": today
                                }
                            else:
                                user_data = await load_user_data(user_id)
                                await save_user_data(user_id, user_data)
                                # Write-through: Invalidate cache after DB write
                                from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
                                await invalidate_user_json_cache(self.bot, user_id)
                                await get_or_cache_user_json_data(self.bot, user_id)
                                return {
                                    "success": True,
                                    "total_steps": 0,
                                    "walking_reps": 0,
                                    "platforms": data.get('platforms', {"garmin": 0}),
                                    "message": f"Garmin connected but no steps found for {today}. Status: {data.get('platforms', {}).get('garmin', {}).get('status', 'unknown')}",
                                    "sync_date": today
                                }
                        elif response.status == 429:
                            return {"success": False, "error": "Rate limited by Garmin API. Please wait a few minutes before syncing again."}
                        elif response.status == 404:
                            return {"success": False, "error": "User not found or not connected to Garmin. Please link your account first."}
                        else:
                            text = await response.text()
                            print(f"[DEBUG] Error response: {response.status} - {text}")
                            return {"success": False, "error": f"API error: {response.status}"}

                except Exception as endpoint_error:
                    print(f"[DEBUG] Error with endpoint {endpoint}: {endpoint_error}")
                    return {"success": False, "error": f"Connection error: {str(endpoint_error)}"}

            except Exception as e:
                print(f"[DEBUG] Sync error: {e}")
                return {"success": False, "error": str(e)}

async def setup(bot):
    await bot.add_cog(FitnessAPI(bot))