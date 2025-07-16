from fastapi import Depends, HTTPException, Request
from typing import Optional
import asyncpg
import jwt
import os

from core.redis_cache import RedisCache

async def get_db_pool(request: Request) -> Optional[asyncpg.Pool]:
    """Get database connection pool"""
    db_pool = getattr(request.app.state, 'db_pool', None)
    if db_pool is None:
        # In development mode, return None instead of raising an error
        return None
    return db_pool

async def get_redis(request: Request) -> Optional[RedisCache]:
    """Get Redis cache instance"""
    redis = getattr(request.app.state, 'redis', None)
    if redis is None:
        # In development mode, return None instead of raising an error
        return None
    return redis

async def get_current_user(request: Request) -> dict:
    """Get current authenticated user from JWT token"""
    # For now, we'll implement a simple version
    # This will be enhanced with proper Discord OAuth2 later
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # For development, allow requests without auth
        # In production, this should raise an exception
        return {"user_id": 1, "discord_id": "dev_user", "username": "dev_user"}
    
    token = auth_header.split(" ")[1]
    secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(request: Request) -> Optional[dict]:
    """Get current user if authenticated, None otherwise"""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

# Development mode helpers
def is_development_mode() -> bool:
    """Check if we're running in development mode"""
    return os.getenv("DEV_MODE", "false").lower() == "true"

async def require_db_pool(db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)) -> asyncpg.Pool:
    """Require database pool, raise error if not available"""
    if db_pool is None:
        raise HTTPException(
            status_code=503, 
            detail="Database not available. This endpoint requires a database connection."
        )
    return db_pool

async def require_redis(redis: Optional[RedisCache] = Depends(get_redis)) -> RedisCache:
    """Require Redis cache, raise error if not available"""
    if redis is None:
        raise HTTPException(
            status_code=503, 
            detail="Redis not available. This endpoint requires Redis connection."
        )
    return redis