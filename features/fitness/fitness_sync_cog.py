# NOTE: Pycord migration: Pycord is a maintained fork of discord.py with the same API, but should be imported as 'import discord' and 'from discord.ext import commands'.
# For maintainers: If you need to use Pycord-specific features, refer to https://docs.pycord.dev/en/master/
import discord  # Pycord (discord.py compatible)
from discord.ext import commands, tasks  # Pycord (discord.py compatible)
from typing import Optional

from features.fitness.logic.integrations import FitnessIntegrations
from features.user.logic.user_data import load_user_data, save_user_data

class FitnessSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.auto_sync_fitness.start() # Removed auto-sync

    @commands.group(name="fitness", invoke_without_command=True)
    async def fitness(self, ctx):
        """Fitness integration commands"""
        embed = discord.Embed(
            title="🏃‍♂️ Fitness Integration Hub",
            description="""
```ansi
[BIOMETRIC SYNC PROTOCOLS]
Available integrations:
🟢 Garmin Connect → !fitness setup garmin  
🟡 Apple Health   → Manual export support
🟡 HealthFit      → Manual export support

!fitness sync     → Manual sync now
!fitness status   → Check sync status
!fitness disable  → Disable auto-sync
```
""",
            color=0x007cc3
        )
        await ctx.send(embed=embed)

    @fitness.command(name="setup")
    async def setup_fitness(self, ctx, platform: Optional[str] = None):
        """Setup fitness platform integration"""
        if not platform:
            embed = discord.Embed(
                title="🔗 Fitness Setup",
                description="""
```ansi
[GARMIN CONNECT SETUP]
Available platforms:
🟢 garmin → Garmin Connect

Usage: !fitness setup garmin
This will provide you with setup instructions.
```
                """,
                color=0x007cc3
            )
            return await ctx.send(embed=embed)

        platform = platform.lower()

        if platform == "garmin":
            setup_url = f"https://syncros.replit.app/?user_id={ctx.author.id}&platform=garmin"
            embed = discord.Embed(
                title="🔗 Garmin Connect Setup",
                description=f"""
```ansi
[GARMIN CONNECT PROTOCOL]
Setting up Garmin Connect integration...
──────────────────────────

AUTOMATED SETUP:
🔗 {setup_url}

After connecting:
• Steps will auto-sync daily
• Use !fitness sync for manual sync
• View data in your profile

Required Permissions:
• Read daily step counts
• Read activity summaries
• Historical data access
──────────────────────────
"Fitness tracker integration ready."
```
                """,
                color=0x007cc3
            )
        else:
            embed = discord.Embed(
                title="❌ Unsupported Platform",
                description="Only Garmin Connect is currently supported.\nUse: `!fitness setup garmin`",
                color=0xff0000
            )

        await ctx.send(embed=embed)

    @fitness.command(name="auth")
    async def auth_fitness(self, ctx, platform: str, *tokens):
        """Authenticate with fitness platform"""
        platform = platform.lower()
        user_id = ctx.author.id

        if platform == "garmin" and len(tokens) == 2:
            success = FitnessIntegrations.setup_fitness_sync(
                user_id, "garmin", {
                    "access_token": tokens[0],
                    "access_token_secret": tokens[1]
                }
            )
        else:
            return await ctx.send("❌ Invalid platform or token format\nUsage: `!fitness auth garmin <token> <secret>`")

        if success:
            embed = discord.Embed(
                title="✅ Fitness Sync Enabled",
                description=f"Successfully connected {platform.title()}!\nSteps will auto-sync daily.",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Setup Failed", 
                description="Could not setup fitness integration",
                color=0xff0000
            )

        await ctx.send(embed=embed)

    @fitness.command(name="sync")
    async def manual_sync(self, ctx, date_option: str = "today"):
        """Manually sync fitness data now - options: today, yesterday"""
        user_id = ctx.author.id

        # Get fitness API cog to use OAuth server
        fitness_api_cog = self.bot.get_cog("FitnessAPI")
        if not fitness_api_cog:
            return await ctx.send("❌ Fitness API not available.")

        # Check if user has any connection (either old format or OAuth server)
        data = await load_user_data(user_id)
        integrations = data.get("fitness_integrations", {})
        has_old_integration = integrations.get("garmin", {}).get("enabled")

        # Try OAuth server sync with date option
        sync_date = None
        if date_option.lower() == "yesterday":
            from datetime import datetime, timedelta
            sync_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        result = await fitness_api_cog.sync_fitness_data(user_id, sync_date=sync_date)

        if not result["success"] and not has_old_integration:
            return await ctx.send("❌ No fitness integrations configured. Use `!fitness setup garmin` first.")

        # If OAuth server sync worked
        if result["success"]:
            total_steps = result.get("total_steps", 0)
            walking_reps = result.get("walking_reps", 0)
            if total_steps > 0 and walking_reps > 0:
                # Add XP and update stats (only if not already synced)
                from features.user.logic.xp_engine import add_xp, calculate_xp_for_movement
                from features.quests.ui.weekly.weekly_contract_panel import update_weekly_progress

                # Update quests and contracts
                await update_quest_progress(user_id, "walking", walking_reps)
                await update_weekly_contract_progress(user_id, self.bot, "walking", walking_reps)

                # Store sync record and connection status for profile display
                from datetime import datetime
                data.setdefault("last_step_sync", {})["garmin"] = datetime.now().isoformat()

                # Update fitness_integrations to show connected status in profile
                fitness_integrations = data.setdefault("fitness_integrations", {})
                fitness_integrations["garmin"] = {
                    "enabled": True,
                    "connection_type": "oauth_server",
                    "last_sync": datetime.now().isoformat(),
                    "credentials": {"oauth_connected": True}
                }

                await save_user_data(user_id, data)
                # Write-through: Invalidate cache after DB write
                from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
                await invalidate_user_json_cache(self.bot, user_id)
                await get_or_cache_user_json_data(self.bot, user_id)

                xp_earned = calculate_xp_for_movement("Walking", walking_reps)

                embed = discord.Embed(
                    title="✅ Fitness Sync Complete",
                    description=f"""
```ansi
[GARMIN SYNC RESULTS]
Daily Steps: {total_steps:,}
Walking Reps Added: {walking_reps}
XP Earned: {xp_earned}
────────────────────────────────
Garmin: ✅ Connected & Synced
────────────────────────────────
"Biometric data synchronized."
```
                    """,
                    color=0x00ff88
                )
            else:
                # No new reps added (already synced today)
                message = result.get("message", "No new data to sync")
                embed = discord.Embed(
                    title="🔄 No New Steps",
                    description=f"""
```ansi
[GARMIN SYNC STATUS]
Daily Steps: {total_steps:,}
Walking Reps: 0 (no new steps since last sync)
────────────────────────────────
{message}
────────────────────────────────
"No new activity detected."
```
                    """,
                    color=0x5865f2
                )

        # Fall back to old integration method if OAuth server has no data
        elif has_old_integration:
            credentials = integrations["garmin"]["credentials"]
            steps = FitnessIntegrations.sync_garmin_steps(
                user_id, 
                credentials.get("access_token"),
                credentials.get("access_token_secret")
            )
            if steps and steps > 0:
                walking_reps = max(1, steps // 100)
                embed = discord.Embed(
                    title="✅ Fitness Sync Complete",
                    description=f"""
```ansi
[GARMIN SYNC RESULTS]
Total Steps: {steps:,}
Walking Reps Added: {walking_reps}
XP Earned: {walking_reps * 2}
────────────────────────────────
Garmin: {steps} steps (Legacy)
────────────────────────────────
"Biometric data synchronized."
```
                    """,
                    color=0x00ff88
                )

                # Update last sync time
                from datetime import datetime
                data = await load_user_data(user_id)
                data["fitness_integrations"]["garmin"]["last_sync"] = datetime.now().isoformat()
                await save_user_data(user_id, data)
                # Write-through: Invalidate cache after DB write
                from core.redis_cache import invalidate_user_json_cache, get_or_cache_user_json_data
                await invalidate_user_json_cache(self.bot, user_id)
                await get_or_cache_user_json_data(self.bot, user_id)
            else:
                embed = discord.Embed(
                    title="❌ No Data Found",
                    description="No new step data available for sync.",
                    color=0xff6b35
                )
        else:
            embed = discord.Embed(
                title="✅ Garmin Connected",
                description=f"""
```ansi
[GARMIN SYNC STATUS]
Connection: ✅ Active & Connected
Daily Steps: {result.get("total_steps", 0):,}
────────────────────────────────
Garmin is properly connected!
No new steps to add since last sync.
────────────────────────────────
"Connection verified."
```
                """,
                color=0x00ff88
            )

        await ctx.send(embed=embed)

    @fitness.command(name="status")
    async def fitness_status(self, ctx):
        """Check fitness integration status"""
        user_id = ctx.author.id
        from datetime import datetime

        # Check OAuth server connection first
        fitness_api_cog = self.bot.get_cog("FitnessAPI")
        if fitness_api_cog:
            result = await fitness_api_cog.sync_fitness_data(user_id)

            if result["success"]:
                # Also update connection status in user data for profile display
                data = await load_user_data(user_id)
                fitness_integrations = data.setdefault("fitness_integrations", {})
                fitness_integrations["garmin"] = {
                    "enabled": True,
                    "connection_type": "oauth_server",
                    "last_sync": datetime.now().isoformat(),
                    "credentials": {"oauth_connected": True}
                }
                await save_user_data(user_id, data)

                embed = discord.Embed(
                    title="📊 Fitness Integration Status",
                    description=f"""
```ansi
[INTEGRATION STATUS]
────────────────────────────────
🟢 Garmin Connect: Active via OAuth Server
Connection: ✅ Verified
Steps Available: {result.get('total_steps', 0)}
────────────────────────────────
Your Garmin account is properly connected
and will persist across bot restarts.

Use !fitness sync to manually sync data
"Integration status verified."
```
                    """,
                    color=0x5865f2
                )
                return await ctx.send(embed=embed)

        # Fall back to checking local data for legacy connections
        data = await load_user_data(user_id)
        integrations = data.get("fitness_integrations", {})

        if integrations.get("garmin", {}).get("enabled"):
            last_sync = integrations["garmin"].get("last_sync", "Never")
            if last_sync != "Never":
                from datetime import datetime
                last_sync = datetime.fromisoformat(last_sync).strftime("%m-%d %H:%M")

            embed = discord.Embed(
                title="📊 Fitness Integration Status",
                description=f"""
```ansi
[INTEGRATION STATUS]
────────────────────────────────
🟡 Garmin Connect: Legacy Connection (Last: {last_sync})
Note: Consider reconnecting via OAuth for
better persistence across restarts.
────────────────────────────────
Use !fitness setup garmin to upgrade
"Legacy integration detected."
```
                """,
                color=0xffa500
            )
            return await ctx.send(embed=embed)

        # No connection
        status_lines = []
        embed = discord.Embed(
            title="❌ No Integrations",
            description="No fitness platforms connected.\nUse `!fitness setup garmin` to get started.",
            color=0xff6b35
        )
        await ctx.send(embed=embed)

        if not status_lines:
            status_lines.append("⚪ Garmin Connect: Available")

        embed = discord.Embed(
            title="📊 Fitness Integration Status",
            description=f"""
```ansi
[INTEGRATION STATUS]
────────────────────────────────
{chr(10).join(status_lines)}
────────────────────────────────
Use !fitness sync to manually sync data
Use !fitness test to test OAuth server connection
"Integration status displayed."
```
            """,
            color=0x5865f2
        )
        await ctx.send(embed=embed)

    @fitness.command(name="test")
    async def test_connection(self, ctx):
        """Test connection to OAuth server"""
        import aiohttp
        from datetime import datetime

        fitness_hub_url = "https://syncros.replit.app"
        user_id = ctx.author.id
        today = datetime.now().strftime("%Y-%m-%d")

        embed = discord.Embed(
            title="🔧 Testing OAuth Server Connection",
            description="Testing connection to fitness server...",
            color=0x5865f2
        )
        message = await ctx.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            try:
                # Test basic server health
                server_status = "❌ Server Offline"
                try:
                    async with session.get(f"{fitness_hub_url}/health") as response:
                        if response.status == 200:
                            server_status = "✅ Server Online"
                        else:
                            server_status = f"❌ Server Error: {response.status}"
                except:
                    try:
                        async with session.get(f"{fitness_hub_url}/") as response:
                            if response.status == 200:
                                server_status = "✅ Server Online (no /health endpoint)"
                            else:
                                server_status = f"❌ Server Error: {response.status}"
                    except:
                        server_status = "❌ Server Unreachable"

                # Test user endpoints with detailed responses
                endpoints_tested = []
                for endpoint in [f"/api/sync/{user_id}", f"/sync/{user_id}", f"/api/fitness/{user_id}"]:
                    try:
                        async with session.get(f"{fitness_hub_url}{endpoint}") as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                steps = data.get('total_steps', 0) or data.get('steps', 0)
                                endpoints_tested.append(f"{endpoint}: {resp.status} (Steps: {steps})")
                            else:
                                endpoints_tested.append(f"{endpoint}: {resp.status}")
                    except Exception as e:
                        endpoints_tested.append(f"{endpoint}: Error - {str(e)[:50]}")

                embed = discord.Embed(
                    title="🔧 OAuth Server Test Results",
                    description=f"""
```ansi
[SERVER CONNECTION TEST]
Date: {today}
────────────────────────────────
Server Status: {server_status}

Endpoint Tests:
{chr(10).join(endpoints_tested)}
────────────────────────────────
If steps show 0, try:
!fitness refresh - Force data refresh
!fitness debug - Show raw server data
```
                    """,
                    color=0x5865f2 if "✅" in server_status else 0xff6b35
                )

            except Exception as e:
                embed = discord.Embed(
                    title="❌ Connection Test Failed",
                    description=f"Could not connect to OAuth server: {str(e)}",
                    color=0xff0000
                )

        await message.edit(embed=embed)

    @fitness.command(name="refresh")
    async def force_refresh(self, ctx):
        """Force refresh fitness data from Garmin"""
        user_id = ctx.author.id

        fitness_api_cog = self.bot.get_cog("FitnessAPI")
        if not fitness_api_cog:
            return await ctx.send("❌ Fitness API not available.")

        embed = discord.Embed(
            title="🔄 Force Refreshing Fitness Data",
            description="Requesting fresh data from Garmin Connect...",
            color=0x5865f2
        )
        message = await ctx.send(embed=embed)

        # Force refresh with server
        result = await fitness_api_cog.sync_fitness_data(user_id, force_refresh=True)

        if result["success"]:
            if result.get("total_steps", 0) > 0:
                embed = discord.Embed(
                    title="✅ Refresh Complete",
                    description=f"""
```ansi
[FORCE REFRESH RESULTS]
Date: {result.get('sync_date', 'Unknown')}
Total Steps: {result['total_steps']:,}
Walking Reps: {result.get('walking_reps', 0)}
────────────────────────────────
Fresh data retrieved from Garmin!
```
                    """,
                    color=0x00ff88
                )
            else:
                debug_info = result.get('debug_info', {})
                embed = discord.Embed(
                    title="🔄 Refresh Complete - No Steps",
                    description=f"""
```ansi
[FORCE REFRESH RESULTS]
Date: {result.get('sync_date', 'Unknown')}
Steps Found: 0
Message: {result.get('message', 'No additional info')}
────────────────────────────────
Server Response Debug:
{str(debug_info)[:200]}...
────────────────────────────────
Steps may not have synced to Garmin
Connect yet. Try again in 30 minutes.
```
                    """,
                    color=0xffa500
                )
        else:
            embed = discord.Embed(
                title="❌ Refresh Failed",
                description=f"Error: {result.get('error', 'Unknown error')}",
                color=0xff0000
            )

        await message.edit(embed=embed)

    @fitness.command(name="debug")
    async def debug_sync(self, ctx, date: Optional[str] = None):
        """Show debug information about last sync or test a specific date (YYYY-MM-DD)"""
        user_id = ctx.author.id

        if date:
            # Test specific date
            fitness_api_cog = self.bot.get_cog("FitnessAPI")
            if not fitness_api_cog:
                return await ctx.send("❌ Fitness API not available.")

            result = await fitness_api_cog.sync_fitness_data(user_id, sync_date=date)

            embed = discord.Embed(
                title=f"🔍 Debug Test for {date}",
                description=f"""
```json
{str(result)[:1900]}
```
                """,
                color=0x5865f2
            )
            return await ctx.send(embed=embed)

        # Show detailed debug from OAuth server
        import aiohttp
        fitness_hub_url = "https://syncros.replit.app"
        from datetime import datetime, timedelta

        embed = discord.Embed(
            title="🔍 Fetching Detailed Debug Info",
            description="Getting detailed Garmin data from OAuth server...",
            color=0x5865f2
        )
        message = await ctx.send(embed=embed)

        # Test multiple dates and endpoints
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        async with aiohttp.ClientSession() as session:
            debug_info = {
                "server_status": "Unknown",
                "endpoints_tested": [],
                "dates_tested": [today, yesterday],
                "user_connected": False
            }

            # Test server health
            try:
                async with session.get(f"{fitness_hub_url}/health") as response:
                    debug_info["server_status"] = f"✅ Online ({response.status})" if response.status == 200 else f"⚠️ Issues ({response.status})"
            except:
                debug_info["server_status"] = "❌ Offline"

            # Test various endpoints for both dates
            endpoints_to_test = [
                f"/api/sync/{user_id}",
                f"/api/fitness/{user_id}",
                f"/sync/{user_id}",
                f"/api/debug/{user_id}"
            ]

            for endpoint in endpoints_to_test:
                for test_date in [today, yesterday]:
                    try:
                        url = f"{fitness_hub_url}{endpoint}?date={test_date}"
                        async with session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                steps = data.get('total_steps', 0) or data.get('steps', 0)
                                status = data.get('platforms', {}).get('garmin', {}).get('status', 'unknown')
                                debug_info["endpoints_tested"].append(f"{endpoint} ({test_date}): {steps} steps, Status: {status}")

                                if steps > 0 or status == 'success':
                                    debug_info["user_connected"] = True
                            else:
                                debug_info["endpoints_tested"].append(f"{endpoint} ({test_date}): HTTP {response.status}")
                    except Exception as e:
                        debug_info["endpoints_tested"].append(f"{endpoint} ({test_date}): Error - {str(e)[:30]}")

            # Format results
            embed = discord.Embed(
                title="🔍 Comprehensive OAuth Server Debug",
                description=f"""
```ansi
[SERVER DEBUG ANALYSIS]
Server Status: {debug_info["server_status"]}
User Connected: {"✅ Yes" if debug_info["user_connected"] else "❌ No"}
────────────────────────────────
Endpoint Tests:
{chr(10).join(debug_info["endpoints_tested"][:20])}
────────────────────────────────
Dates Tested: {', '.join(debug_info["dates_tested"])}

NEXT STEPS:
• If server offline: Wait and retry
• If no steps found: Check Garmin app sync
• If status "no data": Data may need time to sync
• Try !fitness refresh to force update
```
                """,
                color=0x5865f2 if debug_info["user_connected"] else 0xff6b35
            )

        await message.edit(embed=embed)

    async def trigger_fitness_sync(self, user_id: int) -> dict:
        """Trigger fitness sync for a specific user (called by health endpoint)"""
        print(f"[HEALTH-TRIGGER] Triggering fitness sync for user {user_id}")

        # Get fitness API cog
        fitness_api_cog = self.bot.get_cog("FitnessAPI")
        if not fitness_api_cog:
            print("[HEALTH-TRIGGER] FitnessAPI cog not available")
            return {"success": False, "error": "FitnessAPI not available"}

        # Check if user has fitness integrations enabled
        data = await load_user_data(user_id)
        fitness_integrations = data.get("fitness_integrations", {})
        has_garmin = fitness_integrations.get("garmin", {}).get("enabled", False)

        if not has_garmin:
            print(f"[HEALTH-TRIGGER] User {user_id} has no Garmin integration enabled")
            return {"success": False, "error": "No Garmin integration"}

        # Attempt to sync this user's data
        try:
            result = await fitness_api_cog.sync_fitness_data(user_id)
            if result["success"]:
                walking_reps = result.get("walking_reps", 0)
                total_steps = result.get("total_steps", 0)
                print(f"[HEALTH-TRIGGER] ✅ User {user_id}: {total_steps} steps, {walking_reps} reps")
                return result
            else:
                print(f"[HEALTH-TRIGGER] ❌ User {user_id} sync failed: {result.get('error', 'Unknown error')}")
                return result
        except Exception as e:
            print(f"[HEALTH-TRIGGER] Exception syncing user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def cog_load(self):
        """Called when the cog is loaded"""
        print("✅ Fitness sync cog loaded (event-driven mode)")

    async def cog_unload(self):
        """Called when the cog is unloaded"""
        print("🔄 Fitness sync cog unloaded")

async def setup(bot):
    await bot.add_cog(FitnessSync(bot))