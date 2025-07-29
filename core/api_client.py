"""
API Client for Discord Bot to communicate with FastAPI backend
"""

import httpx
import jwt
import os
import asyncio
import warnings
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .async_polling import APIClientPollingMixin

class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class APIClient(APIClientPollingMixin):
    """Client for making authenticated requests to the FastAPI backend"""
    
    def __init__(self, base_url: str = None):
        # Simplified configuration - use environment variable or default
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.getenv("API_BASE_URL", "http://localhost:5000/api")
        
        print(f"[API_CLIENT] Using base URL: {self.base_url}")

        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self._user_tokens: Dict[int, str] = {}  # Cache tokens by discord user_id
        self._system_token: Optional[str] = None  # Cache system token
        self._registered_users: Dict[int, bool] = {}  # Track registered users
        
        # Check if we're in development mode
        self.dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
        if self.dev_mode:
            print(f"[API_CLIENT] Running in development mode - authentication may be bypassed")
    
    def _validate_response(self, response_data: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """Validate API response and handle common error patterns"""
        if not isinstance(response_data, dict):
            raise APIError(f"Invalid response format from {endpoint}: expected dict, got {type(response_data)}")
        
        # Check for error indicators in response
        if "error" in response_data:
            error_msg = response_data.get("error", "Unknown error")
            raise APIError(f"API error from {endpoint}: {error_msg}", response_data=response_data)
        
        if "detail" in response_data and response_data.get("success") is False:
            error_msg = response_data.get("detail", "Unknown error")
            raise APIError(f"API error from {endpoint}: {error_msg}", response_data=response_data)
        
        # Log successful V2 endpoint usage
        if "/v2/" in endpoint:
            print(f"[API_CLIENT] Successfully called V2 endpoint: {endpoint}")
        
        return response_data
        
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
        
        # Check if user is registered, if not, register them
        if discord_user_id not in self._registered_users:
            await self._ensure_user_registered(discord_user)
        
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
        
        # Get token from login endpoint if we have a registered user
        if discord_user_id in self._registered_users:
            try:
                login_response = await self._login_user(str(discord_user_id))
                if login_response and "access_token" in login_response:
                    token = login_response["access_token"]
                    self._user_tokens[discord_user_id] = token
                    return token
            except Exception as e:
                print(f"[API_CLIENT] Failed to get token from login: {e}")
        
        # Fallback: Create new token locally
        token = self._create_user_token(discord_user_id, username)
        self._user_tokens[discord_user_id] = token
        return token

    async def _make_request(self, method: str, endpoint: str, discord_user, version: str = "v1", **kwargs) -> Dict[Any, Any]:
        """Make authenticated API request with version support"""
        headers = kwargs.get("headers", {})
        
        # Skip auth for health and auth endpoints
        if endpoint not in ["/v2/auth/health", "/v2/auth/register", "/v2/auth/login"]:
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
                response_data = response.json()
                return self._validate_response(response_data, endpoint)
            except httpx.HTTPStatusError as e:
                print(f"[API_CLIENT] HTTP Error {e.response.status_code}: {e.response.text}")
                try:
                    error_data = e.response.json()
                    raise APIError(f"HTTP {e.response.status_code}: {error_data.get('detail', e.response.text)}", 
                                 status_code=e.response.status_code, response_data=error_data)
                except (ValueError, KeyError, AttributeError) as json_error:
                    # JSON parsing failed or missing expected fields
                    raise APIError(f"HTTP {e.response.status_code}: {e.response.text}", 
                                 status_code=e.response.status_code) from json_error
            except Exception as e:
                print(f"[API_CLIENT] Request failed: {e}")
                raise APIError(f"Request failed: {str(e)}")

    async def _submit_async_operation(self, discord_user, endpoint: str, data: Dict[str, Any], 
                                    wait_for_completion: bool = True, status_endpoint: str = None,
                                    timeout_seconds: int = 300, poll_interval: int = 2) -> Dict[str, Any]:
        """
        Submit an async operation and optionally wait for completion using polling.
        
        Args:
            discord_user: Discord user object for authentication
            endpoint: API endpoint to submit the operation to
            data: Request data to send
            wait_for_completion: Whether to poll for completion
            status_endpoint: Endpoint to check operation status
            timeout_seconds: Maximum time to wait for completion
            poll_interval: Seconds between status checks
            
        Returns:
            Dict containing operation result or status
        """
        import asyncio
        import time
        
        # Submit the async operation
        response = await self._make_request("POST", endpoint, discord_user, json=data, version="v2")
        
        # If not waiting for completion, return the initial response
        if not wait_for_completion:
            return response
        
        # If no status endpoint provided, return the response (operation might be synchronous)
        if not status_endpoint:
            return response
        
        # Extract operation ID from response
        operation_id = response.get("operation_id") or response.get("id")
        if not operation_id:
            # If no operation ID, assume synchronous operation
            return response
        
        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                status_response = await self._make_request(
                    "GET", f"{status_endpoint}/{operation_id}", discord_user, version="v2"
                )
                
                status = status_response.get("status", "unknown")
                
                if status in ["completed", "success", "finished"]:
                    return status_response
                elif status in ["failed", "error"]:
                    raise Exception(f"Async operation failed: {status_response.get('error', 'Unknown error')}")
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                print(f"[API_CLIENT] Error polling async operation: {e}")
                # Continue polling unless it's a critical error
                if "not found" in str(e).lower():
                    break
                await asyncio.sleep(poll_interval)
        
        # Timeout reached
        raise Exception(f"Async operation timed out after {timeout_seconds} seconds")

    async def _handle_async_request(self, method: str, endpoint: str, discord_user, 
                                  wait_for_completion: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Handle potentially async requests with automatic polling support.
        
        This method automatically detects 202 Accepted responses and handles polling.
        """
        response = await self._make_request(method, endpoint, discord_user, version="v2", **kwargs)
        
        # Check if this is an async operation (202 Accepted)
        if isinstance(response, dict) and response.get("status") == "accepted":
            operation_id = response.get("operation_id")
            if operation_id and wait_for_completion:
                # Extract status endpoint from the response or construct it
                status_endpoint = response.get("status_endpoint", f"{endpoint}/status")
                return await self._poll_operation_status(discord_user, status_endpoint, operation_id)
        
        return response

    async def _poll_operation_status(self, discord_user, status_endpoint: str, operation_id: str,
                                   timeout_seconds: int = 300, poll_interval: int = 2) -> Dict[str, Any]:
        """Poll operation status until completion."""
        import asyncio
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                status_response = await self._make_request(
                    "GET", f"{status_endpoint}/{operation_id}", discord_user, version="v2"
                )
                
                status = status_response.get("status", "unknown")
                
                if status in ["completed", "success", "finished"]:
                    return status_response
                elif status in ["failed", "error"]:
                    raise Exception(f"Operation failed: {status_response.get('error', 'Unknown error')}")
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                print(f"[API_CLIENT] Error polling operation status: {e}")
                if "not found" in str(e).lower():
                    break
                await asyncio.sleep(poll_interval)
        
        raise Exception(f"Operation timed out after {timeout_seconds} seconds")
    
    # User endpoints
    async def get_user_profile(self, discord_user) -> Dict[str, Any]:
        """Get user profile from API"""
        return await self._make_request("GET", "/users/me", discord_user)
    
    async def get_user_profile_v2(self, discord_user) -> Dict[str, Any]:
        """Get comprehensive user profile from V2 endpoint"""
        return await self._make_request("GET", "/v2/profiles/me", discord_user, version="v2")
    
    async def update_user_profile(self, discord_user, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile via API"""
        return await self._make_request("PUT", "/users/me", discord_user, json=update_data)

    # V2 Movement System Methods
    async def get_movement_library_v2(self, discord_user) -> Dict[str, Any]:
        """Get complete movement library from V2 endpoint"""
        return await self._make_request("GET", "/v2/movements/library", discord_user, version="v2")
    
    async def log_movement_v2(self, discord_user, movement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log movement using V2 endpoint with enhanced tracking"""
        return await self._make_request("POST", "/v2/events/log-movement", discord_user, 
                                      json=movement_data, version="v2")
    
    async def get_movement_history_v2(self, discord_user, limit: int = 10, 
                                    movement_id: int = None) -> Dict[str, Any]:
        """Get movement history from V2 endpoint with filtering"""
        params = {"limit": limit}
        if movement_id:
            params["movement_id"] = movement_id
        return await self._make_request("GET", "/v2/movements/history", discord_user, 
                                      params=params, version="v2")
    
    async def get_skill_tree_progress_v2(self, discord_user) -> Dict[str, Any]:
        """Get user's skill tree progression from V2 endpoint"""
        return await self._make_request("GET", "/v2/movements/skill-tree/progress", discord_user, version="v2")

    # V2 Awakening System Methods
    async def get_awakening_status_v2(self, discord_user, include_quests: bool = False) -> Dict[str, Any]:
        """Get awakening status from V2 endpoint with enhanced data"""
        params = {"include_quests": include_quests}
        return await self._make_request("GET", f"/v2/awakening/status/{discord_user.id}", discord_user, 
                                      params=params, version="v2")
    
    async def perform_awakening_v2(self, discord_user, readiness: str) -> Dict[str, Any]:
        """Perform awakening via V2 endpoint with improved tracking"""
        print(f"[API_CLIENT] perform_awakening_v2 called with user_id={discord_user.id}, readiness={readiness}")
        request_data = {"user_id": discord_user.id, "readiness_level": readiness}
        print(f"[API_CLIENT] Sending POST to /v2/awakening/action with data: {request_data}")
        result = await self._make_request("POST", "/v2/awakening/action", discord_user, 
                                      json=request_data, version="v2")
        print(f"[API_CLIENT] Response: {result}")
        return result
    
    async def get_awakening_quests_v2(self, discord_user) -> Dict[str, Any]:
        """Get awakening quests from V2 endpoint"""
        return await self._make_request("GET", "/v2/awakening/quests", discord_user, version="v2")
    
    async def complete_awakening_quest_v2(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Complete awakening quest via V2 endpoint"""
        return await self._make_request("POST", f"/v2/awakening/quests/{quest_id}/complete", 
                                      discord_user, version="v2")
    
    async def get_awakening_briefing_v2(self, discord_user) -> Dict[str, Any]:
        """Get daily awakening briefing from V2 endpoint"""
        return await self._make_request("GET", "/v2/awakening/daily-briefing", discord_user, version="v2")
    
    async def get_awakening_history_v2(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get awakening history from V2 endpoint"""
        return await self._make_request("GET", f"/v2/awakening/history?limit={limit}", 
                                      discord_user, version="v2")

    # V2 Dungeon System Methods
    async def get_available_dungeons_v2(self, discord_user) -> Dict[str, Any]:
        """Get available dungeons and user progress"""
        return await self._make_request("GET", "/v2/dungeons/", discord_user, version="v2")
    
    async def get_dungeon_session_v2(self, discord_user) -> Dict[str, Any]:
        """Get current dungeon session"""
        return await self._make_request("GET", "/v2/dungeons/session", discord_user, version="v2")
    
    async def enter_dungeon_v2(self, discord_user, dungeon_level: int, 
                             wait_for_completion: bool = True) -> Dict[str, Any]:
        """Enter dungeon using V2 endpoint (async operation)"""
        return await self._handle_async_request("POST", "/v2/dungeons/enter", discord_user,
                                              wait_for_completion=wait_for_completion,
                                              json={"dungeon_level": dungeon_level})
    
    async def get_dungeon_status_v2(self, discord_user) -> Dict[str, Any]:
        """Get current dungeon session status"""
        return await self._make_request("GET", "/v2/dungeons/status", discord_user, version="v2")
    
    async def complete_dungeon_trial_v2(self, discord_user, trial_id: int, 
                                      completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete dungeon trial using V2 endpoint"""
        return await self._make_request("POST", f"/v2/dungeons/trials/{trial_id}/complete", 
                                      discord_user, json=completion_data, version="v2")
    
    async def get_dungeon_keys_v2(self, discord_user) -> Dict[str, Any]:
        """Get user's dungeon keys from V2 endpoint"""
        return await self._make_request("GET", "/v2/dungeons/keys", discord_user, version="v2")
    
    async def use_dungeon_key_v2(self, discord_user, key_type: str) -> Dict[str, Any]:
        """Use a dungeon key via V2 endpoint"""
        return await self._make_request("POST", "/v2/dungeons/keys/use", discord_user, 
                                      json={"key_type": key_type}, version="v2")

    # V2 Progression System Methods
    async def add_xp_v2(self, discord_user, amount: int, category: str = "global") -> Dict[str, Any]:
        """Add XP using V2 endpoint with enhanced progression tracking"""
        xp_data = {
            "user_id": discord_user.id,  # Assuming discord_user has an id attribute
            "amount": amount,
            "category": category
        }
        return await self._make_request("POST", "/v2/progression/add-xp", discord_user, 
                                      json=xp_data, version="v2")
    
    async def get_level_progress_v2(self, discord_user, category: str = "global") -> Dict[str, Any]:
        """Get level progress from V2 endpoint"""
        params = {
            "user_id": discord_user.id,
            "category": category
        }
        return await self._make_request("GET", "/v2/progression/level-progress", discord_user, 
                                      params=params, version="v2")
    
    async def get_progression_stats_v2(self, discord_user) -> Dict[str, Any]:
        """Get comprehensive progression statistics from V2 endpoint"""
        return await self._make_request("GET", "/v2/progression/stats", discord_user, version="v2")
    
    async def calculate_aura_v2(self, discord_user) -> Dict[str, Any]:
        """Calculate current aura value using V2 endpoint"""
        return await self._make_request("POST", "/v2/progression/calculate-aura", discord_user, version="v2")
    
    async def unlock_skill_v2(self, discord_user, node_id: str) -> Dict[str, Any]:
        """Unlock a skill tree node using V2 endpoint"""
        unlock_data = {"node_id": node_id}
        return await self._make_request("POST", "/v2/progression/unlock-skill", discord_user, 
                                      json=unlock_data, version="v2")

    # V2 Incursion System Methods (Enhanced)
    async def get_active_incursions_v2(self, discord_user) -> Dict[str, Any]:
        """Get active incursions from V2 endpoint with enhanced data"""
        return await self._make_request("GET", "/v2/incursions/active", discord_user, version="v2")
    
    async def create_incursion_v2(self, discord_user, incursion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create incursion via V2 endpoint with improved validation"""
        return await self._make_request("POST", "/v2/incursions/", discord_user, 
                                      json=incursion_data, version="v2")
    
    async def join_incursion_v2(self, discord_user, incursion_id: int) -> Dict[str, Any]:
        """Join an incursion via V2 endpoint"""
        return await self._make_request("POST", f"/v2/incursions/{incursion_id}/join", 
                                      discord_user, version="v2")
    
    async def get_incursion_status_v2(self, discord_user, incursion_id: int) -> Dict[str, Any]:
        """Get incursion status from V2 endpoint"""
        return await self._make_request("GET", f"/v2/incursions/{incursion_id}/status", 
                                      discord_user, version="v2")

    # V2 Quest System Methods (Enhanced)
    async def get_daily_quests_v2(self, discord_user) -> Dict[str, Any]:
        """Get daily quests from V2 endpoint with enhanced data"""
        return await self._make_request("GET", "/v2/quests/daily", discord_user, version="v2")
    
    async def activate_daily_quest_v2(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Activate daily quest via V2 endpoint"""
        return await self._make_request("POST", f"/v2/quests/daily/{quest_id}/activate", 
                                      discord_user, version="v2")
    
    async def complete_daily_quest_v2(self, discord_user, quest_id: int, 
                                    completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete daily quest via V2 endpoint"""
        return await self._make_request("POST", f"/v2/quests/daily/{quest_id}/complete", 
                                      discord_user, json=completion_data, version="v2")
    
    async def get_quest_history_v2(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get quest history from V2 endpoint"""
        return await self._make_request("GET", f"/v2/quests/history?limit={limit}", 
                                      discord_user, version="v2")
    
    # Quest endpoints
    async def get_daily_quests(self, discord_user) -> Dict[str, Any]:
        """Get daily quests from API"""
        warnings.warn(
            "get_daily_quests is deprecated. Use get_daily_quests_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("GET", "/quests/daily", discord_user)
    
    async def activate_daily_quest(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Activate a daily quest via API"""
        warnings.warn(
            "activate_daily_quest is deprecated. Use activate_daily_quest_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("POST", f"/quests/daily/{quest_id}/activate", discord_user)
    
    async def complete_daily_quest(self, discord_user, quest_id: int, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a daily quest via API"""
        warnings.warn(
            "complete_daily_quest is deprecated. Use complete_daily_quest_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("POST", f"/quests/daily/{quest_id}/complete", discord_user, json=completion_data)
    
    async def get_quest_history(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get quest history from API"""
        warnings.warn(
            "get_quest_history is deprecated. Use get_quest_history_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("GET", f"/quests/history?limit={limit}", discord_user)
    
    async def _ensure_user_registered(self, discord_user) -> bool:
        """Ensure user is registered in the database"""
        discord_id = str(discord_user.id)
        username = discord_user.name
        display_name = getattr(discord_user, 'display_name', None) or username
        
        try:
            # Try to register the user
            registration_data = {
                "discord_id": discord_id,
                "username": username,
                "display_name": display_name
            }
            
            response = await self._make_request(
                "POST", 
                "/v2/auth/register", 
                None,  # No auth needed for registration
                version="v2",
                json=registration_data
            )
            
            if response:
                self._registered_users[discord_user.id] = True
                # Cache the token if provided
                if "access_token" in response:
                    self._user_tokens[discord_user.id] = response["access_token"]
                print(f"[API_CLIENT] User {username} registered successfully")
                return True
        except Exception as e:
            print(f"[API_CLIENT] Failed to register user {username}: {e}")
        
        return False
    
    async def _login_user(self, discord_id: str) -> Dict[str, Any]:
        """Login user to get fresh token"""
        try:
            login_data = {"discord_id": discord_id}
            
            response = await self._make_request(
                "POST",
                "/v2/auth/login",
                None,  # No auth needed for login
                version="v2",
                json=login_data
            )
            
            return response
        except Exception as e:
            print(f"[API_CLIENT] Login failed for Discord ID {discord_id}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """Check API health without authentication"""
        return await self._make_request("GET", "/v2/auth/health", None, version="v2")
    
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
        warnings.warn(
            "get_active_incursions is deprecated. Use get_active_incursions_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("GET", "/incursions/active", discord_user)

    async def create_incursion(self, discord_user, incursion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incursion via API"""
        warnings.warn(
            "create_incursion is deprecated. Use create_incursion_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("POST", "/incursions/", discord_user, json=incursion_data)

    # Awakening endpoints
    async def get_awakening_status(self, discord_user, include_quests: bool = False) -> Dict[str, Any]:
        """Get awakening status from API"""
        warnings.warn(
            "get_awakening_status is deprecated. Use get_awakening_status_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        params = {"include_quests": include_quests}
        return await self._make_request("GET", f"/awakening/status/{discord_user.id}", discord_user, params=params)

    async def perform_awakening(self, discord_user, readiness: str) -> Dict[str, Any]:
        """Perform awakening via API"""
        warnings.warn(
            "perform_awakening is deprecated. Use perform_awakening_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("POST", "/awakening/action", discord_user, json={"readiness_level": readiness})

    async def get_awakening_quests(self, discord_user) -> Dict[str, Any]:
        """Get awakening quests from API"""
        warnings.warn(
            "get_awakening_quests is deprecated. Use get_awakening_quests_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        # Use the status endpoint with include_quests=True instead of non-existent action endpoint
        return await self.get_awakening_status(discord_user, include_quests=True)

    async def complete_awakening_quest(self, discord_user, quest_id: int) -> Dict[str, Any]:
        """Complete an awakening quest via API"""
        warnings.warn(
            "complete_awakening_quest is deprecated. Use complete_awakening_quest_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("POST", f"/awakening/complete_quest/{quest_id}", discord_user)

    async def get_awakening_briefing(self, discord_user) -> Dict[str, Any]:
        """Get awakening briefing from API"""
        warnings.warn(
            "get_awakening_briefing is deprecated. Use get_awakening_briefing_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
        return await self._make_request("GET", "/awakening/daily_briefing", discord_user)

    async def get_awakening_history(self, discord_user, limit: int = 10) -> Dict[str, Any]:
        """Get awakening history from API"""
        warnings.warn(
            "get_awakening_history is deprecated. Use get_awakening_history_v2 for enhanced functionality.",
            DeprecationWarning,
            stacklevel=2
        )
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