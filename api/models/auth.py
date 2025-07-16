from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    """Response model for authentication tokens"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    discord_id: str
    username: str

class DiscordOAuthRequest(BaseModel):
    """Request model for Discord OAuth2 callback"""
    code: str
    redirect_uri: Optional[str] = None

class LoginRequest(BaseModel):
    """Request model for development login"""
    discord_id: str
    username: str

class UserClaims(BaseModel):
    """JWT token claims"""
    user_id: int
    discord_id: str
    username: str
    exp: int
    iat: int