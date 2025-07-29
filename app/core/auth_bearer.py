"""
JWT Bearer authentication for FastAPI.

This module provides JWT token creation and validation for the V2 API.
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

class JWTBearer(HTTPBearer):
    """JWT Bearer authentication dependency."""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return decoded payload."""
        # Check if in development mode
        is_dev = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            
            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            
            return payload
        elif is_dev:
            # In development mode, return a default user
            return {
                "user_id": 1,
                "discord_id": "123456789",
                "username": "DevUser"
            }
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
    
    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload if valid."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt