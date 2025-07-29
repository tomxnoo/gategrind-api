"""
Authentication dependencies for API v2 endpoints.

This module provides authentication utilities specifically for the v2 API,
including user ID extraction and authentication validation.
"""
import os
from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_async_session


def is_development_mode() -> bool:
    """Check if we're running in development mode"""
    return os.getenv("DEV_MODE", "false").lower() == "true"


async def get_db_session_or_none() -> AsyncGenerator[Optional[AsyncSession], None]:
    """Get database session only if not in development mode"""
    if is_development_mode():
        yield None
    else:
        async for session in get_async_session():
            yield session


async def get_current_user_id(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session_or_none)
) -> int:
    """
    Extract the current user's ID from authentication.
    
    This is a simplified dependency that returns just the user ID
    instead of the full UserProfile object, which is more efficient
    for endpoints that only need the user ID.
    
    Args:
        request: FastAPI request object
        db_session: Database session (for compatibility, None in dev mode)
        
    Returns:
        int: The authenticated user's ID
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    # In development mode, return a default user ID
    if is_development_mode():
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return 1  # Default dev user ID
    
    # For production or when auth header is provided, validate properly
    auth_header = request.headers.get("Authorization")
    
    if is_development_mode() and (not auth_header or not auth_header.startswith("Bearer ")):
        return 1  # Default dev user ID
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header. Use 'Bearer <token>'"
        )
    
    # For now, we'll extract user ID from JWT token directly
    # This is a simplified version - in production you'd want full validation
    import jwt
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Validate required fields
        if "user_id" not in payload:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        
        user_id = payload["user_id"]
        
        # Handle system tokens
        if user_id == 0 and payload.get("discord_id") == "system":
            return 0  # System user ID
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_profile(
    request: Request,
    db_session: Optional[AsyncSession] = Depends(get_db_session_or_none)
):
    """
    Get the current user's full profile.
    
    This is a bridge function that adapts the old authentication system
    to work with the new SQLAlchemy async sessions.
    
    Args:
        request: FastAPI request object
        db_session: Database session (None in development mode)
        
    Returns:
        UserProfile: The authenticated user's profile
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    # This is a temporary bridge - ideally we'd refactor the auth system
    # to work directly with SQLAlchemy async sessions
    
    # Extract user ID first
    user_id = await get_current_user_id(request, db_session)
    
    # In development mode, return a mock user profile
    if is_development_mode():
        from datetime import datetime
        from api.models.user import UserStats, UserProfile
        
        return UserProfile(
            user_id=user_id,
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
    
    # For production, we'd need to implement proper user profile fetching
    # using the new database session. For now, raise an error indicating
    # this needs to be implemented.
    raise HTTPException(
        status_code=501,
        detail="Full user profile fetching with new auth system not yet implemented"
    )