from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import os
import sys

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.redis_cache import RedisCache
from api.routes import health, users, quests

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan"""
    # Startup
    print("[INFO] Starting FastAPI application...")
    
    # Check if we're in development mode (no database/redis required)
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    
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
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(quests.router, prefix="/api/quests", tags=["Quests"])

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
            "users": "/api/users",
            "quests": "/api/quests",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)