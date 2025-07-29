from fastapi import Depends, HTTPException, Request
from typing import Optional
import asyncpg
import jwt
import os
from datetime import datetime

from api.models.user import UserProfile, UserStats
from core.redis_cache import RedisCache
from core.database.db import get_user_profile_from_db, get_unified_user_data, create_user_profile

# Development mode helpers
def is_development_mode() -> bool:
    """Check if we're running in development mode"""
    import logging
    logger = logging.getLogger(__name__)
    
    dev_mode_raw = os.getenv("DEVELOPMENT_MODE", "NOT_SET")
    dev_mode = dev_mode_raw.lower() == "true"
    
    # Use both print and logging to ensure we see the output
    debug_msg = f"DEBUG V1 AUTH: DEVELOPMENT_MODE env var: '{dev_mode_raw}', is_development_mode: {dev_mode}"
    print(debug_msg)
    logger.info(debug_msg)
    
    return dev_mode

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

async def get_db_pool_optional(request: Request) -> Optional[asyncpg.Pool]:
    """Get database connection pool, returns None if not available"""
    return getattr(request.app.state, 'db_pool', None)

async def require_db_pool(db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)) -> asyncpg.Pool:
    """Require database pool, raise error if not available"""
    if db_pool is None:
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

async def get_current_user_with_optional_db(request: Request, db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional)) -> UserProfile:
    """Get current authenticated user from JWT token, with optional database for system tokens"""
    auth_header = request.headers.get("Authorization")
    
    # In development mode, allow requests without auth for testing
    if is_development_mode() and (not auth_header or not auth_header.startswith("Bearer ")):
        if db_pool is None:
            # Return a mock dev user when no database is available
            return UserProfile(
                user_id=1,
                discord_id="123456789",
                username="DevUser",
                display_name="Development User",
                level=1,
                xp=0,
                xp_max=100,
                stats=UserStats(),
                active_buffs={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        user_id = 1
        user_profile_data = await get_user_profile_from_db(db_pool, user_id)
        if not user_profile_data:
            # Create a default dev user if not found
            dev_user_data = {
                "user_id": user_id,
                "discord_id": 123456789,
                "username": "DevUser",
                "display_name": "Development User",
            }
            await create_user_profile(db_pool, dev_user_data)
            user_profile_data = await get_user_profile_from_db(db_pool, user_id)

        if not user_profile_data:
            raise HTTPException(status_code=500, detail="Failed to create or find dev user")

        return UserProfile(**user_profile_data)
    
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
        
        user_id = payload["user_id"]
        
        # Handle system tokens (user_id = 0)
        if user_id == 0 and payload.get("discord_id") == "system":
            # Create a virtual system user profile
            return UserProfile(
                user_id=0,
                discord_id="0",
                username="System",
                display_name="System",
                level=1,
                xp=0,
                xp_max=100,
                stats=UserStats(),
                active_buffs={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        # Handle regular user tokens - require database
        if db_pool is None:
            raise HTTPException(
                status_code=503, 
                detail="Database not available for user authentication"
            )
            
        user_profile_data = await get_user_profile_from_db(db_pool, user_id)
        if not user_profile_data:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfile(**user_profile_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(request: Request, db_pool: asyncpg.Pool = Depends(require_db_pool)) -> UserProfile:
    """Get current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    
    # In development mode, allow requests without auth for testing
    if is_development_mode() and (not auth_header or not auth_header.startswith("Bearer ")):
        user_id = 1
        user_profile_data = await get_user_profile_from_db(db_pool, user_id)
        if not user_profile_data:
            # Create a default dev user if not found
            dev_user_data = {
                "user_id": user_id,
                "discord_id": 123456789,
                "username": "DevUser",
                "display_name": "Development User",
            }
            await create_user_profile(db_pool, dev_user_data)
            user_profile_data = await get_user_profile_from_db(db_pool, user_id)

        if not user_profile_data:
            raise HTTPException(status_code=500, detail="Failed to create or find dev user")

        return UserProfile(**user_profile_data)
    
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
        
        user_id = payload["user_id"]
        
        # Handle system tokens (user_id = 0)
        if user_id == 0 and payload.get("discord_id") == "system":
            # Create a virtual system user profile
            return UserProfile(
                user_id=0,
                discord_id="0",
                username="System",
                display_name="System",
                level=1,
                xp=0,
                xp_max=100,
                stats=UserStats(),
                active_buffs={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        
        # Handle regular user tokens
        user_profile_data = await get_user_profile_from_db(db_pool, user_id)
        if not user_profile_data:
            raise HTTPException(status_code=404, detail="User not found")

        return UserProfile(**user_profile_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_optional_user(request: Request, db_pool: asyncpg.Pool = Depends(require_db_pool)) -> Optional[UserProfile]:
    """Get current user if authenticated, None otherwise"""
    try:
        return await get_current_user(request, db_pool)
    except HTTPException:
        return None