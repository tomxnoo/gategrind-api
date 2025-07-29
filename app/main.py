"""
REALM OF SHADOWS - API SERVER V2
================================
This is the V2 FastAPI-only application server featuring:
- Clean FastAPI implementation
- Modern async/await patterns
- Comprehensive API routing
- Database connection pooling (asyncpg)
- Redis caching
- Sentry error tracking
- Logfire observability

This is the preferred entry point for API development.
For Discord bot functionality, see main_v1.py in root.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncpg
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Load environment variables from .env file
load_dotenv()

# Sentry configuration
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    print(f"[OK] Sentry initialized with DSN: {sentry_dsn[:50]}...")
else:
    print("[WARN] No Sentry DSN found in environment variables")

# Logfire removed - causing authentication issues in production
print("[INFO] Logfire monitoring disabled")

# Get project root for static files
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from core.redis_cache import RedisCache
# Import route modules directly to avoid __init__.py issues
from api.routes.health import router as health_router
from api.routes.users import router as users_router
from api.routes.quests import router as quests_router
from api.routes.logging import router as logging_router
from api.routes.auth import router as auth_router
from api.routes.buffs import router as buffs_router
from api.routes.incursions import router as incursions_router
from api.routes.awakening import router as awakening_router
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
            # Convert SQLAlchemy URL to asyncpg format
            database_url = os.getenv("DATABASE_URL")
            if database_url and database_url.startswith("postgresql+asyncpg://"):
                # Remove the +asyncpg part for asyncpg.create_pool
                asyncpg_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            else:
                asyncpg_url = database_url
            
            app.state.db_pool = await asyncpg.create_pool(
                dsn=asyncpg_url,
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
        await app.state.redis.close()
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
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(quests_router, prefix="/api/quests", tags=["Quests"])
app.include_router(logging_router, prefix="/api/logging", tags=["Logging"])
app.include_router(buffs_router, prefix="/api/buffs", tags=["Buffs"])
app.include_router(incursions_router, prefix="/api/incursions", tags=["Incursions"])
app.include_router(awakening_router, prefix="/api/awakening", tags=["Awakening"])

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