from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncpg
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.redis_cache import RedisCache
from api.routes import health, users, quests, logging, auth, buffs, incursions, awakening
from app.api.v2.router import api_v2_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan"""
    # Startup
    print("[INFO] Starting FastAPI application...")
    
    # Check if we're in development mode (no database/redis required)
    dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    
    # Initialize database pool
    app.state.db_pool = None
    if not dev_mode:
        try:
            app.state.db_pool = await asyncpg.create_pool(
                dsn=os.getenv("DATABASE_URL"),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print("[OK] Database connection pool created successfully.")
        except Exception as e:
            print(f"[WARN] Could not create database connection pool: {e}")
            print("[INFO] Running in development mode without database.")
    else:
        print("[INFO] Development mode: Skipping database connection.")
    
    # Initialize Redis
    app.state.redis = None
    if not dev_mode:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            app.state.redis = RedisCache(url=redis_url)
            await app.state.redis.connect()
            print("[OK] Connected to Redis successfully.")
        except Exception as e:
            print(f"[WARN] Could not connect to Redis: {e}")
            print("[INFO] Running in development mode without Redis.")
    else:
        print("[INFO] Development mode: Skipping Redis connection.")
    
    print("[OK] FastAPI application startup complete.")
    yield
    
    # Shutdown
    print("[INFO] Shutting down FastAPI application...")
    if app.state.db_pool:
        await app.state.db_pool.close()
        print("[OK] Database pool closed.")
    if app.state.redis:
        await app.state.redis.disconnect()
        print("[OK] Redis disconnected.")
    print("[OK] FastAPI application shutdown complete.")

app = FastAPI(
    title="Realm of Shadows API",
    description="The Living Nexus - Fitness RPG Backend",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(quests.router, prefix="/api/quests", tags=["Quests"])
app.include_router(logging.router, prefix="/api/logging", tags=["Logging"])
app.include_router(buffs.router, prefix="/api/buffs", tags=["Buffs"])
app.include_router(incursions.router, prefix="/api/incursions", tags=["Incursions"])
app.include_router(awakening.router, prefix="/api/awakening", tags=["Awakening"])

# Include V2 API router
app.include_router(api_v2_router)

# Mount static files for admin interface
static_path = os.path.join(project_root, "app", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    print(f"[OK] Static files mounted from {static_path}")
else:
    print(f"[WARN] Static directory not found: {static_path}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🌒 Welcome to the Realm of Shadows API",
        "description": "The Living Nexus - Fitness RPG Backend",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "quests": "/api/quests",
            "logging": "/api/logging",
            "buffs": "/api/buffs",
            "incursions": "/api/incursions",
            "awakening": "/api/awakening",
            "health": "/api/health",
            "v2": {
                "movements": "/api/v2/movements"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)