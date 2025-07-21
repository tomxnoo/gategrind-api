import sentry_sdk
sentry_sdk.init(
    dsn="https://a79a94e31ba80fa8835018abc3e28dfb@o4509645249118208.ingest.de.sentry.io/4509645253312592",
    send_default_pii=True,
    traces_sample_rate=1.0,
    # Removed deprecated profile_session_sample_rate parameter
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
from api.main import app as fastapi_app
import uvicorn

from core.redis_cache import RedisCache

# Add the project root directory to the Python path
# This allows for absolute imports from the project root
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")  # <-- Get DB URL from .env

def run_fastapi():
    """Run FastAPI server in a separate thread"""
    port = int(os.environ.get("API_PORT", 8000))
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
            print(f"[FAIL] Could not connect to Redis: {e}", file=sys.stderr)
            await self.close()

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
            from features.user.ui.profile_view import ProfilePanel
            from features.logging.ui.view import LogRepsPanel
            from features.buffs.ui.view import BuffsPanel
            from features.incursions.ui.incursion_panel import IncursionPanel
            from features.quests.ui.quest_panel import QuestPanel
            
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
    'features.buffs.cog',                    # Buffs system
    'features.logging.cog',                  # Logging system
    'features.quests.cog',                   # New quest system
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
    except Exception as e:
        print(f"[FAIL] {ext}: Extension '{ext}' raised an error: {type(e).__name__}: {e}", file=sys.stderr)
        # Don't re-raise the exception to allow other extensions to load

async def discord_bot_main():
    """Main Discord bot coroutine"""
    if not TOKEN:
        print("[FAIL] DISCORD_TOKEN not found in environment variables.", file=sys.stderr)
        return
    
    if not DATABASE_URL:
        print("[FAIL] DATABASE_URL not found in environment variables.", file=sys.stderr)
        return
    
    # The setup_hook now handles loading extensions
    print("[INFO] Starting Discord bot...")
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"[FAIL] Discord bot failed to start: {e}", file=sys.stderr)
        traceback.print_exc()

def start_bot_thread():
    """Start the Discord bot in an asyncio event loop"""
    try:
        asyncio.run(discord_bot_main())
    except KeyboardInterrupt:
        print("[INFO] Discord bot shutdown requested")
    except Exception as e:
        print(f"[FAIL] Discord bot thread error: {e}", file=sys.stderr)
        traceback.print_exc()

if __name__ == "__main__":
    print("🌒 Starting Realm of Shadows - Dual Mode (FastAPI + Discord Bot)")
    print("=" * 60)
    
    # Start FastAPI in a thread
    print("[INFO] Starting FastAPI server...")
    try:
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        print("[OK] FastAPI server thread started")
    except Exception as e:
        print(f"[FAIL] Could not start FastAPI server: {e}", file=sys.stderr)
    
    # Start Discord bot in main thread
    print("[INFO] Starting Discord bot...")
    start_bot_thread()
