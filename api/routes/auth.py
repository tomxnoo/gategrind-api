from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
import httpx
import jwt
import os
from datetime import datetime, timedelta
import asyncpg

from api.models.auth import TokenResponse, DiscordOAuthRequest, LoginRequest, UserClaims
from api.models.common import SuccessResponse
from api.dependencies import get_db_pool, is_development_mode

router = APIRouter()

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/api/auth/discord/callback")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

def create_jwt_token(user_id: int, discord_id: str, username: str) -> str:
    """Create JWT token for user"""
    now = datetime.utcnow()
    exp = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "user_id": user_id,
        "discord_id": discord_id,
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_or_create_user(db_pool: Optional[asyncpg.Pool], discord_id: str, username: str) -> int:
    """Get existing user or create new one, returns user_id"""
    if not db_pool:
        # Development mode - return mock user_id
        return 1
    
    async with db_pool.acquire() as conn:
        # Check if user exists
        user_id = await conn.fetchval(
            "SELECT user_id FROM users WHERE discord_id = $1", 
            int(discord_id)
        )
        
        if user_id:
            # Update username if changed
            await conn.execute(
                "UPDATE users SET username = $1 WHERE user_id = $2",
                username, user_id
            )
            return user_id
        else:
            # Create new user
            user_id = await conn.fetchval(
                """
                INSERT INTO users (discord_id, username, xp, level, xp_max) 
                VALUES ($1, $2, 0, 1, 100) 
                RETURNING user_id
                """,
                int(discord_id), username
            )
            
            # Create user_json_data entry
            await conn.execute(
                "INSERT INTO user_json_data (user_id, data) VALUES ($1, $2)",
                user_id, "{}"
            )
            
            return user_id

@router.post("/discord/callback", response_model=TokenResponse)
async def discord_oauth_callback(
    request: DiscordOAuthRequest,
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Handle Discord OAuth2 callback"""
    if is_development_mode():
        raise HTTPException(
            status_code=501, 
            detail="Discord OAuth2 not available in development mode. Use /auth/dev/login instead."
        )
    
    if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Discord OAuth2 not configured"
        )
    
    # Exchange authorization code for access token
    token_data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": request.code,
        "redirect_uri": request.redirect_uri or DISCORD_REDIRECT_URI,
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    async with httpx.AsyncClient() as client:
        # Get access token from Discord
        token_response = await client.post(
            "https://discord.com/api/oauth2/token",
            data=token_data,
            headers=headers
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to exchange code for token"
            )
        
        token_info = token_response.json()
        access_token = token_info["access_token"]
        
        # Get user info from Discord
        user_response = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to get user info from Discord"
            )
        
        user_info = user_response.json()
        discord_id = user_info["id"]
        username = user_info["username"]
    
    # Get or create user in database
    user_id = await get_or_create_user(db_pool, discord_id, username)
    
    # Create JWT token
    jwt_token = create_jwt_token(user_id, discord_id, username)
    
    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user_id=user_id,
        discord_id=discord_id,
        username=username
    )

@router.post("/dev/login", response_model=TokenResponse)
async def dev_login(
    request: LoginRequest,
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool)
):
    """Development login endpoint (only available in dev mode)"""
    if not is_development_mode():
        raise HTTPException(
            status_code=404,
            detail="Development login only available in development mode"
        )
    
    # Get or create user
    user_id = await get_or_create_user(db_pool, request.discord_id, request.username)
    
    # Create JWT token
    jwt_token = create_jwt_token(user_id, request.discord_id, request.username)
    
    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user_id=user_id,
        discord_id=request.discord_id,
        username=request.username
    )

@router.get("/me", response_model=UserClaims)
async def get_current_user_info(request: Request):
    """Get current user info from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return UserClaims(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout", response_model=SuccessResponse)
async def logout():
    """Logout endpoint (client-side token removal)"""
    return SuccessResponse(
        success=True,
        message="Logged out successfully. Please remove the token from client storage."
    )

@router.get("/discord/url")
async def get_discord_oauth_url():
    """Get Discord OAuth2 authorization URL"""
    if is_development_mode():
        return {
            "auth_url": None,
            "message": "Discord OAuth2 not available in development mode. Use /auth/dev/login instead.",
            "dev_mode": True
        }
    
    if not DISCORD_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Discord OAuth2 not configured"
        )
    
    auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )
    
    return {
        "auth_url": auth_url,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "dev_mode": False
    }