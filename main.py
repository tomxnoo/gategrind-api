#!/usr/bin/env python3
"""
REALM OF SHADOWS - COMPLETE APPLICATION
=======================================
This is the main entry point that runs both:
- Discord Bot (RealmBot) with full functionality
- FastAPI web server integration
- Database connection pooling (asyncpg)
- Redis caching
- Extension loading system

This combines the functionality of both the Discord bot and FastAPI server
for seamless deployment on Replit and other platforms.
"""

import sentry_sdk
sentry_sdk.init(
    dsn="https://a79a94e31ba80fa8835018abc3e28dfb@o4509645249118208.ingest.de.sentry.io/4509645253312592",
    send_default_pii=True,
    traces_sample_rate=1.0,
)

import os
import sys
import traceback
import threading
import asyncio

import discord  # Pycord (discord.py compatible)
from discord.ext import commands
from dotenv import load_dotenv
import asyncpg  # <-- Import asyncpg

# ---- FASTAPI IMPORT ----
from app.main import app as fastapi_app
import uvicorn

from core.redis_cache import RedisCache

# Add the project root directory to the Python path
# This allows for absolute imports from the project root
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()
# Import settings to get Discord token properly
from app.core.config import get_settings
settings = get_settings()
TOKEN = settings.get_discord_token()
DATABASE_URL = os.getenv("DATABASE_URL")  # <-- Get DB URL from .env

def run_fastapi():
    """Run FastAPI server in a separate thread"""
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")

# ---- DISCORD BOT SETUP ----
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

class RealmBot(commands.AutoShardedBot):  # <-- Use AutoShardedBot
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_pool = None  # Placeholder for the pool
        self.redis = None  # Placeholder for RedisCache

    async def setup_hook(self):
        """This is called when the bot is setting up."""
        print("[INFO] Initializing database connection pool...")
        try:
            # Create the connection pool
            self.db_pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                min_size=5,  # Minimum number of connections
                max_size=20,  # Maximum number of connections
                command_timeout=60
            )
            print("[OK] Database connection pool created successfully.")
        except Exception as e:
            print(f"[FAIL] Could not create database connection pool: {e}", file=sys.stderr)
            # If the DB fails, we probably don't want the bot to start.
            # Depending on desired resilience, you might handle this differently.
            await self.close()

        # Initialize RedisCache
        print("[INFO] Connecting to Redis...")
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = RedisCache(url=redis_url)
            await self.redis.connect()
            print("[OK] Connected to Redis successfully.")
        except Exception as e:
            print(f"[WARN] Could not connect to Redis: {e}", file=sys.stderr)
            print("[WARN] Bot will continue without Redis caching")
            self.redis = None  # Set to None so bot can still function

        # Import all panels BEFORE loading cogs to ensure they're registered
        print("[INFO] Pre-loading panel registrations...")
        await self._preload_panels()

        # Load extensions after the pool is ready
        print("[INFO] Loading Discord bot extensions...")
        for ext in EXTS:
            await load_extension(self, ext)

    async def _preload_panels(self):
        """Import all panel classes to ensure they're registered before UI components are created"""
        try:
            # Import all panel classes to trigger their @register decorators
            from features.awakening.ui.awakening_panel import EnhancedAwakeningPanel
            from features.dungeons.ui.dungeon_panel import DungeonPanel
            from features.user.ui.profile_view import ProfilePanel
            from features.user.ui.profile_v2_panel import ProfileV2Panel  # V2 Profile Panel
            from features.logging.ui.view import LogRepsPanel
            from features.buffs.ui.view import BuffsPanel
            from features.incursions.ui.incursion_panel import IncursionPanel
            # Import skills panel if it exists
            try:
                from features.skills.ui.skill_tree_panel import SkillTreePanel
                print("[OK] Skill Tree panel loaded")
            except ImportError:
                print("[INFO] Skill Tree panel not available")
            
            # Debug: Show what panels are now registered
            from shared.utils.panel_registry import debug_registry
            debug_registry()
            print("[OK] All panels pre-loaded and registered")
            
        except Exception as e:
            print(f"[WARN] Could not pre-load some panels: {e}")
            # Don't fail startup if panel imports fail

bot = RealmBot(command_prefix="!", intents=intents)

# Updated extension list with proper order and all necessary cogs
EXTS = [
    'features.system.system_hub_cog',        # Core system hub - load first
    'features.awakening.cog',                # Awakening system
    # 'features.dungeons.cog',               # Dungeons system - disabled (accessed via system hub)
    'features.buffs.cog',                    # Buffs system
    'features.logging.cog',                  # Logging system
    'features.quests.cog',                   # Quest system
    'features.user.cog',                     # User management
    'features.moderation.message_management_cog',  # Moderation
    'features.moderation.reroll_reset_cog',
    'features.moderation.quest_completion_cog',
    'features.fitness.fitness_sync_cog',     # Fitness integration
    'features.fitness.fitness_api_cog',
    'features.incursions.cog',               # Incursions system
]

@bot.event
async def on_ready():
    if not bot.user:
        print("[ERROR] Bot user not found on ready.", file=sys.stderr)
        return
    print("═" * 60)
    print(f"🌒 {bot.user} online • ID {bot.user.id}")
    print(f"Guilds: {len(bot.guilds)}  •  Cogs: {len(bot.cogs)}")
    print("═" * 60)
    
    # Check API health and connectivity
    try:
        from core.api_client import api_client
        health = await api_client.health_check()
        print(f"[OK] API Health Check: {health.get('status', 'unknown')} - {health.get('service', 'unknown')} v{health.get('version', '?')}")
        
        # Verify API base URL configuration
        print(f"[INFO] API Base URL: {api_client.base_url}")
        print(f"[INFO] Development Mode: {api_client.dev_mode}")
        
    except Exception as e:
        print(f"[WARN] API Health Check failed: {e}")
        print("[WARN] Bot will continue but API features may not work properly")
    
    # Add persistent views
    try:
        from features.system.ui.dropdown import SystemHubPublicView
        bot.add_view(SystemHubPublicView(bot))
        print("[OK] System Hub persistent view added")
    except Exception as e:
        print(f"[WARN] Could not add System Hub persistent view: {e}")
    
    # Set bot presence
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching,
                                  name="the shadows move")
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    WEBHOOK_CHANNEL_ID = 1390426998526181377  # <-- Change to your Discord channel ID
    if message.channel.id != WEBHOOK_CHANNEL_ID:
        await bot.process_commands(message)
        return
        
    # Handle health data sync webhook
    if "Health data synced for <@" in message.content:
        if not bot.db_pool:
            print("[ERROR] Database pool not available in on_message.", file=sys.stderr)
            await bot.process_commands(message)
            return
        try:
            import re
            match = re.search(r'<@(\d+)>', message.content)
            if match:
                user_id = int(match.group(1))
                # Now, acquire a connection from the bot's pool
                async with bot.db_pool.acquire() as conn:
                    # You would replace this with your actual query logic
                    # Example: health_row = await conn.fetchrow("SELECT ...", user_id)
                    print(f"[BOT] Acquired DB connection for user {user_id} on webhook trigger.")
                    # The old get_unified_user_data would need to be adapted to take a 'conn' object.
                    # For now, this demonstrates the pattern.
        except Exception as e:
            print(f"[ERROR] Failed to process webhook: {e}", file=sys.stderr)
    
    await bot.process_commands(message)

@bot.event
async def on_error(evt, *args, **kwargs):
    print(f"[ERROR] {evt}", file=sys.stderr)
    traceback.print_exc()

@bot.event
async def on_application_command_error(ctx, err):
    print(f"[ERROR] cmd {ctx.command}: {err}", file=sys.stderr)
    traceback.print_exc()

async def load_extension(bot_instance, ext):
    """Load a single extension with proper error handling"""
    try:
        await bot_instance.load_extension(ext)
        print(f"[OK] {ext}")
    except discord.ext.commands.ExtensionNotFound:
        print(f"[SKIP] {ext} - Extension not found (optional)")
    except Exception as e:
        print(f"[FAIL] {ext} - {e}", file=sys.stderr)
        if os.getenv("DEBUG", "false").lower() == "true":
            traceback.print_exc()

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Start the Discord bot
    try:
        print("[INFO] Starting Discord bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"[FATAL] Bot failed to start: {e}", file=sys.stderr)
        traceback.print_exc()