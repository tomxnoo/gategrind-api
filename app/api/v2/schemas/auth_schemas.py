"""
Authentication schemas for V2 API.

Defines request/response models for user registration and authentication.
"""
from pydantic import BaseModel, Field
from typing import Optional

class UserRegistrationRequest(BaseModel):
    """Request model for user registration."""
    discord_id: str = Field(..., description="Discord user ID")
    username: str = Field(..., description="Discord username")
    display_name: Optional[str] = Field(None, description="Discord display name")

class UserRegistrationResponse(BaseModel):
    """Response model for user registration."""
    user_id: int = Field(..., description="Database user ID")
    discord_id: str = Field(..., description="Discord user ID")
    username: str = Field(..., description="Username")
    is_new_user: bool = Field(..., description="Whether this is a new registration")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

class UserLoginRequest(BaseModel):
    """Request model for user login."""
    discord_id: str = Field(..., description="Discord user ID")

class UserLoginResponse(BaseModel):
    """Response model for user login."""
    user_id: int = Field(..., description="Database user ID")
    discord_id: str = Field(..., description="Discord user ID")
    username: str = Field(..., description="Username")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")