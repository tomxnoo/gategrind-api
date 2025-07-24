"""
IncursionService - Core business logic for managing incursions

This service handles:
- Creating and managing incursions
- Tracking participant progress
- Managing incursion lifecycle (active, completed, expired)
- Reward distribution logic
- Integration with progression system
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.infrastructure.database.models.v2.incursions import (
    Incursion, IncursionParticipant, IncursionType, RewardType, IncursionStatus
)


class IncursionService(BaseService):
    """
    Service for managing incursion lifecycle and operations.
    
    Follows hexagonal architecture pattern and integrates with the existing
    BaseService infrastructure for transaction management and error handling.
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """Initialize the IncursionService with optional session."""
        super().__init__(session)
    
    async def create_incursion(
        self,
        title: str,
        description: str,
        incursion_type: IncursionType,
        target_exercise: str,
        target_reps: int,
        reward_type: RewardType,
        reward_value: int,
        reward_description: str,
        duration_hours: float = 24.0,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Incursion:
        """
        Create a new incursion.
        
        Args:
            title: Incursion title
            description: Detailed description
            incursion_type: Type of incursion (SURGE, CHALLENGE, ANOMALY)
            target_exercise: Exercise type for the incursion
            target_reps: Target repetitions to complete
            reward_type: Type of reward (XP, BUFF, ITEM)
            reward_value: Numeric value of the reward
            reward_description: Human-readable reward description
            duration_hours: How long the incursion lasts
            extra_data: Additional metadata for the incursion
            
        Returns:
            Incursion: The created incursion object
            
        Raises:
            ValueError: If invalid parameters are provided
            Exception: Database or other service errors
        """
        try:
            # Validate inputs
            if target_reps <= 0:
                raise ValueError("Target reps must be positive")
            if reward_value <= 0:
                raise ValueError("Reward value must be positive")
            if duration_hours <= 0:
                raise ValueError("Duration must be positive")
            
            # Generate unique incursion ID
            timestamp = int(datetime.now().timestamp())
            incursion_id = f"incursion_{timestamp}_{incursion_type.value}"
            
            # Calculate expiration time
            expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
            
            # Create incursion object
            incursion = Incursion(
                incursion_id=incursion_id,
                title=title,
                description=description,
                incursion_type=incursion_type,
                target_exercise=target_exercise,
                target_reps=target_reps,
                reward_type=reward_type,
                reward_value=reward_value,
                reward_description=reward_description,
                expires_at=expires_at,
                extra_data=extra_data or {}
            )
            
            # Save to database
            session = await self.get_session()
            session.add(incursion)
            await session.commit()
            await session.refresh(incursion)
            
            self.logger.info(f"Created incursion {incursion_id} of type {incursion_type.value}")
            return incursion
            
        except Exception as e:
            self.handle_service_error(e, "create_incursion")
            raise
    
    async def get_active_incursions(self) -> List[Incursion]:
        """
        Get all currently active incursions.
        
        Returns:
            List[Incursion]: List of active incursions with participant data
        """
        try:
            session = await self.get_session()
            
            # Query for active incursions that haven't expired
            current_time = datetime.now(timezone.utc)
            stmt = (
                select(Incursion)
                .options(selectinload(Incursion.participants))
                .where(
                    and_(
                        Incursion.is_active == True,
                        Incursion.expires_at > current_time,
                        Incursion.status == IncursionStatus.ACTIVE
                    )
                )
                .order_by(Incursion.created_at.desc())
            )
            
            result = await session.execute(stmt)
            incursions = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(incursions)} active incursions")
            return list(incursions)
            
        except Exception as e:
            self.handle_service_error(e, "get_active_incursions")
            raise
    
    async def get_incursion_by_id(self, incursion_id: str) -> Optional[Incursion]:
        """
        Get an incursion by its ID.
        
        Args:
            incursion_id: The incursion identifier
            
        Returns:
            Optional[Incursion]: The incursion if found, None otherwise
        """
        try:
            session = await self.get_session()
            
            stmt = (
                select(Incursion)
                .options(selectinload(Incursion.participants))
                .where(Incursion.incursion_id == incursion_id)
            )
            
            result = await session.execute(stmt)
            incursion = result.scalar_one_or_none()
            
            if incursion:
                self.logger.debug(f"Retrieved incursion {incursion_id}")
            else:
                self.logger.warning(f"Incursion {incursion_id} not found")
            
            return incursion
            
        except Exception as e:
            self.handle_service_error(e, f"get_incursion_by_id({incursion_id})")
            raise
    
    async def end_incursion(self, incursion_id: str, reason: str = "completed") -> bool:
        """
        End an incursion by marking it as inactive.
        
        Args:
            incursion_id: The incursion to end
            reason: Reason for ending (completed, expired, manual)
            
        Returns:
            bool: True if successfully ended, False if not found
        """
        try:
            session = await self.get_session()
            
            # Update incursion status
            stmt = (
                update(Incursion)
                .where(Incursion.incursion_id == incursion_id)
                .values(
                    is_active=False,
                    status=IncursionStatus.COMPLETED if reason == "completed" else IncursionStatus.EXPIRED
                )
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                self.logger.info(f"Ended incursion {incursion_id} (reason: {reason})")
                return True
            else:
                self.logger.warning(f"Incursion {incursion_id} not found for ending")
                return False
                
        except Exception as e:
            self.handle_service_error(e, f"end_incursion({incursion_id})")
            raise
    
    async def add_participant_contribution(
        self, 
        incursion_id: str, 
        user_id: int, 
        reps: int
    ) -> bool:
        """
        Add a user's contribution to an incursion.
        
        Args:
            incursion_id: The incursion ID
            user_id: The user's ID
            reps: Number of reps contributed
            
        Returns:
            bool: True if contribution was added successfully
        """
        try:
            if reps <= 0:
                raise ValueError("Reps must be positive")
            
            session = await self.get_session()
            
            # Check if incursion exists and is active
            incursion = await self.get_incursion_by_id(incursion_id)
            if not incursion or not incursion.is_active:
                self.logger.warning(f"Cannot contribute to inactive incursion {incursion_id}")
                return False
            
            # Check if user already participated
            existing_participant = None
            for participant in incursion.participants:
                if participant.user_id == user_id:
                    existing_participant = participant
                    break
            
            if existing_participant:
                # Update existing participation
                existing_participant.reps_contributed += reps
            else:
                # Create new participation record
                participant = IncursionParticipant(
                    incursion_id=incursion.id,
                    user_id=user_id,
                    reps_contributed=reps,
                    participated_at=datetime.now(timezone.utc)
                )
                session.add(participant)
            
            # Update incursion progress
            incursion.current_reps += reps
            
            # Check if incursion is completed
            if incursion.is_completed:
                incursion.status = IncursionStatus.COMPLETED
                incursion.is_active = False
                self.logger.info(f"Incursion {incursion_id} completed!")
            
            await session.commit()
            
            self.logger.info(f"User {user_id} contributed {reps} reps to incursion {incursion_id}")
            return True
            
        except Exception as e:
            self.handle_service_error(e, f"add_participant_contribution({incursion_id}, {user_id}, {reps})")
            raise
    
    async def cleanup_expired_incursions(self) -> int:
        """
        Clean up expired incursions by marking them as inactive.
        
        Returns:
            int: Number of incursions cleaned up
        """
        try:
            session = await self.get_session()
            current_time = datetime.now(timezone.utc)
            
            # Update expired incursions
            stmt = (
                update(Incursion)
                .where(
                    and_(
                        Incursion.is_active == True,
                        Incursion.expires_at <= current_time
                    )
                )
                .values(
                    is_active=False,
                    status=IncursionStatus.EXPIRED
                )
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            cleaned_count = result.rowcount
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} expired incursions")
            
            return cleaned_count
            
        except Exception as e:
            self.handle_service_error(e, "cleanup_expired_incursions")
            raise
    
    async def get_incursion_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about incursions.
        
        Returns:
            Dict[str, Any]: Statistics including counts by status and type
        """
        try:
            session = await self.get_session()
            
            # Count by status
            status_counts = {}
            for status in IncursionStatus:
                stmt = select(func.count(Incursion.id)).where(Incursion.status == status)
                result = await session.execute(stmt)
                status_counts[status.value] = result.scalar()
            
            # Count by type (active only)
            type_counts = {}
            for inc_type in IncursionType:
                stmt = (
                    select(func.count(Incursion.id))
                    .where(
                        and_(
                            Incursion.incursion_type == inc_type,
                            Incursion.is_active == True
                        )
                    )
                )
                result = await session.execute(stmt)
                type_counts[inc_type.value] = result.scalar()
            
            # Total participants
            stmt = select(func.count(IncursionParticipant.id))
            result = await session.execute(stmt)
            total_participants = result.scalar()
            
            return {
                "status_counts": status_counts,
                "type_counts": type_counts,
                "total_participants": total_participants,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.handle_service_error(e, "get_incursion_statistics")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the IncursionService.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            session = await self.get_session()
            
            # Test database connectivity
            stmt = select(func.count(Incursion.id))
            result = await session.execute(stmt)
            total_incursions = result.scalar()
            
            # Get active incursions count
            stmt = select(func.count(Incursion.id)).where(Incursion.is_active == True)
            result = await session.execute(stmt)
            active_incursions = result.scalar()
            
            return {
                "status": "healthy",
                "service": "IncursionService",
                "database_connected": True,
                "total_incursions": total_incursions,
                "active_incursions": active_incursions,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.handle_service_error(e, "health_check")
            return {
                "status": "unhealthy",
                "service": "IncursionService",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }