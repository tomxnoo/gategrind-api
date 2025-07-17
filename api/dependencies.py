from fastapi import Depends, HTTPException, Request
from typing import Optional
import asyncpg
import jwt
import os

from core.redis_cache import RedisCache

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

async def get_db_pool_optional(request: Request) -> Optional[asyncpg.Pool]:
    """Get database connection pool, returns None if not available"""
    return getattr(request.app.state, 'db_pool', None)

async def require_db_pool_dev_aware(db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)) -> Optional[asyncpg.Pool]:
    """Require database pool in production, allow None in development mode"""
    if db_pool is None and not is_development_mode():
        raise HTTPException(
            status_code=503, 
            detail="Database not available. This endpoint requires a database connection."
        )
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
    auth_header = request.headers.get("Authorization")
    
    # In development mode, allow requests without auth for testing
    if is_development_mode() and (not auth_header or not auth_header.startswith("Bearer ")):
        return {"user_id": 1, "discord_id": "dev_user", "username": "dev_user"}
    
    # Require authentication in production or when token is provided
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid authorization header. Use 'Bearer <token>'"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Validate required fields
        required_fields = ["user_id", "discord_id", "username"]
        for field in required_fields:
            if field not in payload:
                raise HTTPException(status_code=401, detail=f"Invalid token: missing {field}")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
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

async def require_db_pool(db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)) -> asyncpg.Pool:
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