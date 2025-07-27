"""
API Client for Discord Bot to communicate with FastAPI backend
"""

import httpx
import jwt
import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .async_polling import APIClientPollingMixin

class APIClient(APIClientPollingMixin):
    """Client for making authenticated requests to the FastAPI backend"""
    
    def __init__(self, base_url: str = None):
        # Debug logging to understand environment
        replit_url = os.getenv("REPLIT_URL")
        custom_api_domain = os.getenv("CUSTOM_API_DOMAIN")
        print(f"[API_CLIENT] REPLIT_URL: {replit_url}")
        print(f"[API_CLIENT] CUSTOM_API_DOMAIN: {custom_api_domain}")
        
        # Check if we're in Replit by looking for multiple indicators
        is_replit = (
            os.getenv("REPLIT_URL") is not None or 
            os.getenv("REPL_SLUG") is not None or 
            os.getenv("REPL_OWNER") is not None or
            os.path.exists("/.replit")
        )
        
        if is_replit:
            # In Replit, the bot and API run in the same container. Always use localhost for internal communication.
            self.base_url = "http://127.0.0.1:5000/api"
            print(f"[API_CLIENT] Using Replit internal connection: {self.base_url}")
        elif base_url:
            self.base_url = base_url
            print(f"[API_CLIENT] Using provided base_url: {self.base_url}")
        else:
            # For external clients or local development
            if custom_api_domain:
                # Remove any existing protocol prefix to avoid double https://
                domain = custom_api_domain.replace("https://", "").replace("http://", "")
                self.base_url = f"https://{domain}/api"
                print(f"[API_CLIENT] Using custom domain: {self.base_url}")
            else:
                # Fallback for local development, assuming API runs on port 5000.
                self.base_url = os.getenv("API_BASE_URL", "http://localhost:5000/api")
                print(f"[API_CLIENT] Using fallback: {self.base_url}")

        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self._user_tokens: Dict[int, str] = {}  # Cache tokens by discord user_id
        self._system_token: Optional[str] = None  # Cache system token
        
        # Check if we're in development mode
        self.dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        if self.dev_mode:
            print(f"[API_CLIENT] Running in development mode - authentication disabled")
        
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
    
    def _create_system_token(self) -> str:
        """Create JWT token for system operations"""
        now = datetime.utcnow()
        exp = now + timedelta(hours=24)  # 24 hours for system token
        
        payload = {
            "user_id": 0,  # System user ID
            "discord_id": "system",
            "username": "System",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp())
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _get_system_token(self) -> str:
        """Get or create JWT token for system operations"""
        # Check if we have a cached token
        if self._system_token:
            try:
                # Verify token is still valid
                payload = jwt.decode(self._system_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                if payload["exp"] > datetime.utcnow().timestamp():
                    return self._system_token
            except jwt.InvalidTokenError:
                pass
        
        # Create new system token
        self._system_token = self._create_system_token()
        return self._system_token

    async def _get_user_token(self, discord_user) -> str:
        """Get or create JWT token for Discord user"""
        # Handle system operations - check if it's a bot user
        if hasattr(discord_user, 'bot') and discord_user.bot:
            return await self._get_system_token()
        
        # Handle None or system user
        if discord_user is None or (hasattr(discord_user, 'id') and discord_user.id == 0):
            return await self._get_system_token()
        
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
        headers = kwargs.get("headers", {})
        
        # Only add Authorization header if not in development mode
        if not self.dev_mode:
            token = await self._get_user_token(discord_user)
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
    
    async def get_user_profile_v2(self, discord_user) -> Dict[str, Any]:
        """Get comprehensive user profile from V2 endpoint"""
        return await self._make_request("GET", "/v2/users/me/profile", discord_user)
    
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

    # Incursion endpoints
    async def get_active_incursions(self, discord_user) -> Dict[str, Any]:
        """Get active incursions from API"""
        return await self._make_request("GET", "/incursions/active", discord_user)

    async def create_incursion(self, discord_user, incursion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incursion via API"""
        return await self._make_request("POST", "/incursions/", discord_user, json=incursion_data)

    # Awakening endpoints
    async def get_awakening_status(self, discord_user, include_quests: bool = False) -> Dict[str, Any]:
        """Get awakening status from API"""
        params = {"include_quests": include_quests}
        return await self._make_request("GET", "/awakening/status", discord_user, params=params)

    async def perform_awakening(self, discord_user, readiness: str) -> Dict[str, Any]:
        """Perform awakening via API"""
        return await self._make_request("POST", "/awakening/action", discord_user, json={"readiness_level": readiness})

    async def get_awakening_quests(self, discord_user) -> Dict[str, Any]:
        """Get awakening quests from API"""
        # Use the status endpoint with include_quests=True instead of non-existent action endpoint
        return await self.get_awakening_status(discord_user, include_quests=True)

    async def complete_awakening_quest(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Complete an awakening quest via API"""
        return await self._make_request("POST", f"/awakening/complete_quest/{quest_id}", discord_user)

    async def get_awakening_briefing(self, discord_user) -> Dict[str, Any]:
        """Get awakening briefing from API"""
        return await self._make_request("GET", "/awakening/daily_briefing", discord_user)

    async def get_awakening_history(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get awakening history from API"""
        return await self._make_request("GET", f"/awakening/history?limit={limit}", discord_user)

    async def recover_awakening_session(self, discord_user) -> Dict[str, Any]:
        """Recover awakening session via API"""
        return await self._make_request("POST", "/awakening/recover", discord_user)
    
    # Async operation examples using the polling strategy
    async def start_dungeon_generation(self, discord_user, generation_params: Dict[str, Any], wait_for_completion: bool = True) -> Dict[str, Any]:
        """
        Start async dungeon generation and optionally wait for completion.
        
        Example of how to use the async polling strategy for long-running operations.
        """
        return await self._submit_async_operation(
            discord_user,
            "/v2/dungeons/generate",
            generation_params,
            wait_for_completion=wait_for_completion,
            status_endpoint="/v2/dungeons/generation/status"
        )
    
    async def start_quest_generation(self, discord_user, quest_params: Dict[str, Any], wait_for_completion: bool = True) -> Dict[str, Any]:
        """
        Start async quest generation and optionally wait for completion.
        
        Example of how to use the async polling strategy for AI-generated content.
        """
        return await self._submit_async_operation(
            discord_user,
            "/v2/quests/generate",
            quest_params,
            wait_for_completion=wait_for_completion,
            status_endpoint="/v2/quests/generation/status"
        )
    
    async def start_profile_analysis(self, discord_user, analysis_params: Dict[str, Any], wait_for_completion: bool = True) -> Dict[str, Any]:
        """
        Start async profile analysis and optionally wait for completion.
        
        Example of how to use the async polling strategy for complex data processing.
        """
        return await self._submit_async_operation(
            discord_user,
            "/v2/users/me/analyze",
            analysis_params,
            wait_for_completion=wait_for_completion,
            status_endpoint="/v2/users/me/analysis/status"
        )


api_client = APIClient()