"""
User Service for managing user registration and authentication.

This service handles user creation, retrieval, and management
for the V2 API.
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.application.services.base_service import BaseService
from app.infrastructure.database.models.v2 import Ascendant

logger = logging.getLogger(__name__)

class UserService(BaseService):
    """Service for managing user operations."""
    
    async def get_user_by_discord_id(self, discord_id: str) -> Optional[Ascendant]:
        """
        Get a user by their Discord ID.
        
        Args:
            discord_id: The Discord user ID
            
        Returns:
            Ascendant instance if found, None otherwise
        """
        session = await self.get_session()
        query = select(Ascendant).where(Ascendant.discord_id == discord_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[Ascendant]:
        """
        Get a user by their database ID.
        
        Args:
            user_id: The database user ID
            
        Returns:
            Ascendant instance if found, None otherwise
        """
        session = await self.get_session()
        return await session.get(Ascendant, user_id)
    
    async def create_user(
        self, 
        discord_id: str, 
        username: str,
        display_name: Optional[str] = None
    ) -> Ascendant:
        """
        Create a new user.
        
        Args:
            discord_id: Discord user ID
            username: Discord username
            display_name: Optional display name
            
        Returns:
            Created Ascendant instance
        """
        try:
            # Create the user
            user = Ascendant(
                discord_id=discord_id,
                username=username,
                last_login=datetime.utcnow()
            )
            
            session = await self.get_session()
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            logger.info(f"Created new user: {username} (Discord ID: {discord_id})")
            
            # Initialize user's default data (stats, progression, etc.)
            await self._initialize_user_data(user)
            
            return user
            
        except Exception as e:
            session = await self.get_session()
            await session.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    async def update_last_login(self, user: Ascendant) -> None:
        """
        Update the user's last login timestamp.
        
        Args:
            user: The user to update
        """
        session = await self.get_session()
        user.last_login = datetime.utcnow()
        await session.commit()
    
    async def _initialize_user_data(self, user: Ascendant) -> None:
        """
        Initialize default data for a new user.
        
        This includes creating default stats, progression entries, etc.
        
        Args:
            user: The newly created user
        """
        # Import here to avoid circular imports
        from app.infrastructure.database.models.v2 import (
            AscendantStats, UserSkillProgress
        )
        
        try:
            # Create default stats
            stats = AscendantStats(
                ascendant_id=user.id,
                str_level=1,
                str_xp=0.0,
                end_level=1,
                end_xp=0.0,
                tech_level=1,
                tech_xp=0.0,
                str_value=10,
                end_value=10,
                tech_value=10
            )
            session = await self.get_session()
            session.add(stats)
            
            # Create skill tree root node progress (if skill tree exists)
            try:
                # Give new users access to all foundation nodes (level 1 of each category)
                foundation_nodes = [
                    "upper_dynamic_1", "mobility_flow_1", "pull_vertical_1", "push_1", "pull_1", 
                    "squat_1", "hinge_1", "lunge_1", "rotation_1", "gait_1"
                ]
                
                for node_id in foundation_nodes:
                    root_skill = UserSkillProgress(
                        ascendant_id=user.id,
                        node_id=node_id,
                        unlocked_at=datetime.utcnow()
                    )
                    session.add(root_skill)
            except Exception as e:
                logger.warning(f"Could not create foundation skill progress: {e}")
            
            await session.commit()
            logger.info(f"Initialized default data for user {user.username}")
            
        except Exception as e:
            logger.error(f"Failed to initialize user data: {str(e)}")
            # Don't fail user creation if initialization fails
            session = await self.get_session()
            await session.rollback()
    
    async def get_or_create_user(
        self,
        discord_id: str,
        username: str,
        display_name: Optional[str] = None
    ) -> tuple[Ascendant, bool]:
        """
        Get an existing user or create a new one.
        
        Args:
            discord_id: Discord user ID
            username: Discord username
            display_name: Optional display name
            
        Returns:
            Tuple of (user, is_new) where is_new indicates if user was created
        """
        # Check if user exists
        user = await self.get_user_by_discord_id(discord_id)
        
        if user:
            # Update last login
            await self.update_last_login(user)
            return user, False
        
        # Create new user
        user = await self.create_user(discord_id, username, display_name)
        return user, True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the user service.
        
        Returns:
            Dict containing health check results
        """
        try:
            # Try to count users
            session = await self.get_session()
            query = select(Ascendant).limit(1)
            await session.execute(query)
            
            return {
                "service": "UserService",
                "status": "healthy",
                "message": "User service is operational"
            }
        except Exception as e:
            return {
                "service": "UserService",
                "status": "unhealthy",
                "message": f"Database connection error: {str(e)}"
            }