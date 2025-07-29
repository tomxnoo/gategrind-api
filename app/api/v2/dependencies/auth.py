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
    import logging
    logger = logging.getLogger(__name__)
    
    dev_mode_raw = os.getenv("DEV_MODE", "NOT_SET")
    dev_mode = dev_mode_raw.lower() == "true"
    
    # Use both print and logging to ensure we see the output
    debug_msg = f"DEBUG V2 AUTH: DEV_MODE env var: '{dev_mode_raw}', is_development_mode: {dev_mode}"
    print(debug_msg)
    logger.info(debug_msg)
    
    return dev_mode


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
        return 1  # Default dev user ID
    
    # For production, validate auth header
    auth_header = request.headers.get("Authorization")
    
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
    
    This function provides full user profile data for authenticated users,
    with development mode fallback for testing.
    
    Args:
        request: FastAPI request object
        db_session: Database session (None in development mode)
        
    Returns:
        UserProfile: The authenticated user's profile
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
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
    
    # Production mode - fetch from database
    if db_session is None:
        raise HTTPException(
            status_code=500,
            detail="Database session not available in production mode"
        )
    
    try:
        from sqlalchemy import select, text
        from datetime import datetime
        from api.models.user import UserStats, UserProfile
        
        # Query user data from ascendants table
        query = text("""
            SELECT 
                id as user_id,
                discord_id,
                username,
                display_name,
                level,
                xp,
                xp_max,
                created_at,
                updated_at
            FROM ascendants 
            WHERE id = :user_id
        """)
        
        result = await db_session.execute(query, {"user_id": user_id})
        user_data = result.fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        
        # Convert to dict for easier handling
        user_dict = dict(user_data._mapping)
        
        # Get user stats (you may need to adjust this based on your stats table structure)
        stats_query = text("""
            SELECT 
                strength, dexterity, constitution, intelligence, 
                wisdom, charisma, luck, vitality
            FROM user_stats 
            WHERE user_id = :user_id
        """)
        
        stats_result = await db_session.execute(stats_query, {"user_id": user_id})
        stats_data = stats_result.fetchone()
        
        # Create UserStats object
        if stats_data:
            stats = UserStats(**dict(stats_data._mapping))
        else:
            # Default stats if none found
            stats = UserStats()
        
        # Get active buffs (adjust based on your buffs table structure)
        buffs_query = text("""
            SELECT buff_type, buff_data, expires_at
            FROM active_buffs 
            WHERE user_id = :user_id AND (expires_at IS NULL OR expires_at > NOW())
        """)
        
        buffs_result = await db_session.execute(buffs_query, {"user_id": user_id})
        active_buffs = {}
        
        for buff_row in buffs_result.fetchall():
            buff_dict = dict(buff_row._mapping)
            active_buffs[buff_dict['buff_type']] = {
                'data': buff_dict['buff_data'],
                'expires_at': buff_dict['expires_at']
            }
        
        # Create and return UserProfile
        return UserProfile(
            user_id=user_dict['user_id'],
            discord_id=str(user_dict['discord_id']),
            username=user_dict['username'],
            display_name=user_dict.get('display_name', user_dict['username']),
            level=user_dict['level'],
            xp=user_dict['xp'],
            xp_max=user_dict['xp_max'],
            stats=stats,
            active_buffs=active_buffs,
            created_at=user_dict['created_at'],
            updated_at=user_dict['updated_at']
        )
        
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching user profile for user_id {user_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user profile: {str(e)}"
        )