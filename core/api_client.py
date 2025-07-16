"""
API Client for Discord Bot to communicate with FastAPI backend
"""

import httpx
import jwt
import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class APIClient:
    """Client for making authenticated requests to the FastAPI backend"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self._user_tokens: Dict[int, str] = {}  # Cache tokens by discord user_id
        
    def _create_user_token(self, discord_user_id: int, username: str, user_id: int = None) -> str:
        """Create JWT token for Discord user"""
        now = datetime.utcnow()
        exp = now + timedelta(hours=24 * 7)  # 7 days
        
        payload = {
            "user_id": user_id or discord_user_id,  # Use database user_id if available
            "discord_id": str(discord_user_id),
            "username": username,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp())
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _get_user_token(self, discord_user) -> str:
        """Get or create JWT token for Discord user"""
        discord_user_id = discord_user.id
        username = discord_user.display_name or discord_user.name
        
        # Check if we have a cached token
        if discord_user_id in self._user_tokens:
            token = self._user_tokens[discord_user_id]
            try:
                # Verify token is still valid
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                if payload["exp"] > datetime.utcnow().timestamp():
                    return token
            except jwt.InvalidTokenError:
                pass
        
        # Create new token
        token = self._create_user_token(discord_user_id, username)
        self._user_tokens[discord_user_id] = token
        return token
    
    async def _make_request(self, method: str, endpoint: str, discord_user, **kwargs) -> Dict[Any, Any]:
        """Make authenticated API request"""
        token = await self._get_user_token(discord_user)
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        kwargs["headers"] = headers
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"[API_CLIENT] HTTP Error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                print(f"[API_CLIENT] Request failed: {e}")
                raise
    
    # User endpoints
    async def get_user_profile(self, discord_user) -> Dict[str, Any]:
        """Get user profile from API"""
        return await self._make_request("GET", "/users/me", discord_user)
    
    async def update_user_profile(self, discord_user, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile via API"""
        return await self._make_request("PUT", "/users/me", discord_user, json=update_data)
    
    # Quest endpoints
    async def get_daily_quests(self, discord_user) -> Dict[str, Any]:
        """Get daily quests from API"""
        return await self._make_request("GET", "/quests/daily", discord_user)
    
    async def activate_daily_quest(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Activate a daily quest via API"""
        return await self._make_request("POST", f"/quests/daily/{quest_id}/activate", discord_user)
    
    async def complete_daily_quest(self, discord_user, quest_id: int, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a daily quest via API"""
        return await self._make_request("POST", f"/quests/daily/{quest_id}/complete", discord_user, json=completion_data)
    
    async def get_quest_history(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get quest history from API"""
        return await self._make_request("GET", f"/quests/history?limit={limit}", discord_user)
    
    async def get_weekly_quests(self, discord_user) -> Dict[str, Any]:
        """Get weekly quests from API"""
        return await self._make_request("GET", "/quests/weekly", discord_user)
    
    # Logging endpoints
    async def log_reps(self, discord_user, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log reps via API"""
        return await self._make_request("POST", "/logging/reps", discord_user, json=log_data)
    
    async def get_rep_history(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get rep history from API"""
        return await self._make_request("GET", f"/logging/reps/history?limit={limit}", discord_user)
    
    async def get_available_movements(self, discord_user) -> Dict[str, Any]:
        """Get available movements from API"""
        return await self._make_request("GET", "/logging/movements", discord_user)
    
    async def get_logging_stats(self, discord_user) -> Dict[str, Any]:
        """Get logging statistics from API"""
        return await self._make_request("GET", "/logging/stats/summary", discord_user)
    
    # Buff endpoints
    async def get_buff_inventory(self, discord_user) -> Dict[str, Any]:
        """Get user's buff inventory (active and consumable buffs) from API"""
        return await self._make_request("GET", "/buffs/inventory", discord_user)
    
    async def get_consumable_buffs(self, discord_user) -> Dict[str, Any]:
        """Get user's consumable buff inventory from API"""
        return await self._make_request("GET", "/buffs/consumables", discord_user)
    
    async def use_consumable_buff(self, discord_user, buff_id: int) -> Dict[str, Any]:
        """Use a consumable buff from inventory via API"""
        return await self._make_request("POST", f"/buffs/consumables/{buff_id}/use", discord_user)
    
    async def apply_buff(self, discord_user, buff_id: int, duration_minutes: int = None) -> Dict[str, Any]:
        """Apply a buff to user (admin/testing) via API"""
        data = {}
        if duration_minutes is not None:
            data["duration_minutes"] = duration_minutes
        return await self._make_request("POST", f"/buffs/apply/{buff_id}", discord_user, json=data)
    
    async def add_consumable_buff(self, discord_user, buff_id: int, quantity: int = 1) -> Dict[str, Any]:
        """Add consumable buff to user's inventory (admin/testing) via API"""
        data = {"quantity": quantity}
        return await self._make_request("POST", f"/buffs/consumables/{buff_id}/add", discord_user, json=data)
    
    async def grant_random_buff(self, discord_user, rarity: str = None) -> Dict[str, Any]:
        """Grant a random buff to user (admin/testing) via API"""
        data = {}
        if rarity:
            data["rarity"] = rarity
        return await self._make_request("POST", "/buffs/random", discord_user, json=data)
    
    # Health endpoint
    async def get_health_status(self) -> Dict[str, Any]:
        """Get API health status (no auth required)"""
        url = f"{self.base_url}/health/"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    # Incursion endpoints
    async def get_active_incursions(self, discord_user) -> Dict[str, Any]:
        """Get active incursions from API"""
        return await self._make_request("GET", "/incursions/active", discord_user)
    
    async def get_incursion(self, discord_user, incursion_id: str) -> Dict[str, Any]:
        """Get specific incursion by ID from API"""
        return await self._make_request("GET", f"/incursions/{incursion_id}", discord_user)
    
    async def contribute_to_incursion(self, discord_user, incursion_id: str, reps: int) -> Dict[str, Any]:
        """Contribute reps to an incursion via API"""
        data = {"reps": reps}
        return await self._make_request("POST", f"/incursions/{incursion_id}/contribute", discord_user, json=data)
    
    async def get_incursion_leaderboard(self, discord_user, incursion_id: str) -> Dict[str, Any]:
        """Get incursion leaderboard from API"""
        return await self._make_request("GET", f"/incursions/{incursion_id}/leaderboard", discord_user)
    
    async def create_incursion(self, discord_user, incursion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incursion via API"""
        return await self._make_request("POST", "/incursions/", discord_user, json=incursion_data)
    
    async def complete_incursion(self, discord_user, incursion_id: str) -> Dict[str, Any]:
        """Complete an incursion via API"""
        return await self._make_request("POST", f"/incursions/{incursion_id}/complete", discord_user)
    
    async def cleanup_expired_incursions(self, discord_user) -> Dict[str, Any]:
        """Clean up expired incursions via API"""
        return await self._make_request("POST", "/incursions/cleanup", discord_user)

# Global API client instance
api_client = APIClient()