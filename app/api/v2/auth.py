"""
V2 Authentication and User Registration endpoints.

This module provides endpoints for user registration and authentication,
including automatic registration for Discord users.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional

from app.infrastructure.database.session import get_async_session
from app.application.services.user_service import UserService
from app.api.v2.schemas.auth_schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserLoginRequest,
    UserLoginResponse
)
from app.core.auth_bearer import JWTBearer, create_access_token
from app.infrastructure.database.models.v2 import Ascendant
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    registration: UserRegistrationRequest,
    db: AsyncSession = Depends(get_async_session)
) -> UserRegistrationResponse:
    """
    Register a new user or return existing user.
    
    This endpoint handles Discord user registration, creating a new user
    if they don't exist or returning the existing user if they do.
    """
    user_service = UserService(db)
    
    try:
        # Check if user already exists
        existing_user = await user_service.get_user_by_discord_id(registration.discord_id)
        
        if existing_user:
            # User exists, return their info with a new token
            token = create_access_token(
                data={
                    "user_id": existing_user.id,
                    "discord_id": str(existing_user.discord_id),
                    "username": existing_user.username
                }
            )
            
            return UserRegistrationResponse(
                user_id=existing_user.id,
                discord_id=str(existing_user.discord_id),
                username=existing_user.username,
                is_new_user=False,
                access_token=token,
                token_type="bearer"
            )
        
        # Create new user
        new_user = await user_service.create_user(
            discord_id=registration.discord_id,
            username=registration.username,
            display_name=registration.display_name
        )
        
        # Generate JWT token
        token = create_access_token(
            data={
                "user_id": new_user.id,
                "discord_id": str(new_user.discord_id),
                "username": new_user.username
            }
        )
        
        return UserRegistrationResponse(
            user_id=new_user.id,
            discord_id=str(new_user.discord_id),
            username=new_user.username,
            is_new_user=True,
            access_token=token,
            token_type="bearer"
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

@router.post("/login", response_model=UserLoginResponse)
async def login_user(
    login: UserLoginRequest,
    db: AsyncSession = Depends(get_async_session)
) -> UserLoginResponse:
    """
    Login a user by Discord ID.
    
    This endpoint is used when a Discord user interacts with the bot
    and needs a fresh JWT token.
    """
    user_service = UserService(db)
    
    try:
        # Get user by Discord ID
        user = await user_service.get_user_by_discord_id(login.discord_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first."
            )
        
        # Generate JWT token
        token = create_access_token(
            data={
                "user_id": user.id,
                "discord_id": str(user.discord_id),
                "username": user.username
            }
        )
        
        return UserLoginResponse(
            user_id=user.id,
            discord_id=str(user.discord_id),
            username=user.username,
            access_token=token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login user: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint that doesn't require authentication.
    
    Used to verify the API is running and accessible.
    """
    return {
        "status": "healthy",
        "service": "RoS-TRAE V2 API",
        "version": "2.0.0"
    }

@router.get("/verify", dependencies=[Depends(JWTBearer())])
async def verify_token(current_user: dict = Depends(JWTBearer())) -> Dict[str, Any]:
    """
    Verify the current JWT token is valid.
    
    Returns the decoded token payload if valid.
    """
    return {
        "valid": True,
        "user_id": current_user.get("user_id"),
        "discord_id": current_user.get("discord_id"),
        "username": current_user.get("username")
    }