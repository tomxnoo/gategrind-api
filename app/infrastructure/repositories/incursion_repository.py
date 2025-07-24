"""
IncursionRepository - Data access layer for incursions

This repository provides:
- Database operations for incursions
- Query optimization and caching
- Data mapping between models and entities
- Transaction management
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.v2.incursions import (
    Incursion, IncursionParticipant, IncursionType, IncursionStatus
)


class IncursionRepository:
    """
    Repository for incursion data access operations.
    
    Provides a clean interface for database operations while
    maintaining separation of concerns from business logic.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, incursion: Incursion) -> Incursion:
        """
        Create a new incursion in the database.
        
        Args:
            incursion: Incursion entity to create
            
        Returns:
            Incursion: The created incursion with updated fields
        """
        self.session.add(incursion)
        await self.session.flush()  # Get the ID without committing
        await self.session.refresh(incursion)
        return incursion
    
    async def get_by_id(self, incursion_id: str) -> Optional[Incursion]:
        """
        Get an incursion by its ID.
        
        Args:
            incursion_id: The incursion identifier
            
        Returns:
            Optional[Incursion]: The incursion if found, None otherwise
        """
        stmt = (
            select(Incursion)
            .options(selectinload(Incursion.participants))
            .where(Incursion.incursion_id == incursion_id)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_database_id(self, id: int) -> Optional[Incursion]:
        """
        Get an incursion by its database ID.
        
        Args:
            id: The database ID
            
        Returns:
            Optional[Incursion]: The incursion if found, None otherwise
        """
        stmt = (
            select(Incursion)
            .options(selectinload(Incursion.participants))
            .where(Incursion.id == id)
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_incursions(self) -> List[Incursion]:
        """
        Get all currently active incursions.
        
        Returns:
            List[Incursion]: List of active incursions
        """
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
            .order_by(desc(Incursion.created_at))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_expired_incursions(self) -> List[Incursion]:
        """
        Get all expired but still active incursions.
        
        Returns:
            List[Incursion]: List of expired incursions that need cleanup
        """
        current_time = datetime.now(timezone.utc)
        
        stmt = (
            select(Incursion)
            .where(
                and_(
                    Incursion.is_active == True,
                    Incursion.expires_at <= current_time
                )
            )
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_type(self, incursion_type: IncursionType, active_only: bool = True) -> List[Incursion]:
        """
        Get incursions by type.
        
        Args:
            incursion_type: The type of incursions to retrieve
            active_only: Whether to only return active incursions
            
        Returns:
            List[Incursion]: List of incursions of the specified type
        """
        conditions = [Incursion.incursion_type == incursion_type]
        
        if active_only:
            current_time = datetime.now(timezone.utc)
            conditions.extend([
                Incursion.is_active == True,
                Incursion.expires_at > current_time
            ])
        
        stmt = (
            select(Incursion)
            .options(selectinload(Incursion.participants))
            .where(and_(*conditions))
            .order_by(desc(Incursion.created_at))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, incursion: Incursion) -> Incursion:
        """
        Update an existing incursion.
        
        Args:
            incursion: Incursion entity with updated data
            
        Returns:
            Incursion: The updated incursion
        """
        await self.session.merge(incursion)
        await self.session.flush()
        await self.session.refresh(incursion)
        return incursion
    
    async def update_status(self, incursion_id: str, status: IncursionStatus, is_active: bool = None) -> bool:
        """
        Update the status of an incursion.
        
        Args:
            incursion_id: The incursion identifier
            status: New status
            is_active: New active state (optional)
            
        Returns:
            bool: True if update was successful, False if incursion not found
        """
        update_values = {"status": status}
        if is_active is not None:
            update_values["is_active"] = is_active
        
        stmt = (
            update(Incursion)
            .where(Incursion.incursion_id == incursion_id)
            .values(**update_values)
        )
        
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def bulk_update_expired(self) -> int:
        """
        Bulk update expired incursions to inactive status.
        
        Returns:
            int: Number of incursions updated
        """
        current_time = datetime.now(timezone.utc)
        
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
        
        result = await self.session.execute(stmt)
        return result.rowcount
    
    async def delete(self, incursion_id: str) -> bool:
        """
        Delete an incursion (soft delete by marking inactive).
        
        Args:
            incursion_id: The incursion identifier
            
        Returns:
            bool: True if deletion was successful, False if incursion not found
        """
        return await self.update_status(incursion_id, IncursionStatus.EXPIRED, False)
    
    async def hard_delete(self, incursion_id: str) -> bool:
        """
        Permanently delete an incursion from the database.
        
        Args:
            incursion_id: The incursion identifier
            
        Returns:
            bool: True if deletion was successful, False if incursion not found
        """
        # First delete participants
        participant_stmt = (
            delete(IncursionParticipant)
            .where(IncursionParticipant.incursion_id.in_(
                select(Incursion.id).where(Incursion.incursion_id == incursion_id)
            ))
        )
        await self.session.execute(participant_stmt)
        
        # Then delete the incursion
        incursion_stmt = delete(Incursion).where(Incursion.incursion_id == incursion_id)
        result = await self.session.execute(incursion_stmt)
        
        return result.rowcount > 0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about incursions.
        
        Returns:
            Dict[str, Any]: Statistics data
        """
        stats = {}
        
        # Count by status
        for status in IncursionStatus:
            stmt = select(func.count(Incursion.id)).where(Incursion.status == status)
            result = await self.session.execute(stmt)
            stats[f"status_{status.value}"] = result.scalar()
        
        # Count by type (active only)
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
            result = await self.session.execute(stmt)
            stats[f"type_{inc_type.value}"] = result.scalar()
        
        # Total participants
        stmt = select(func.count(IncursionParticipant.id))
        result = await self.session.execute(stmt)
        stats["total_participants"] = result.scalar()
        
        # Average completion rate
        completed_stmt = (
            select(func.count(Incursion.id))
            .where(Incursion.status == IncursionStatus.COMPLETED)
        )
        total_stmt = select(func.count(Incursion.id))
        
        completed_result = await self.session.execute(completed_stmt)
        total_result = await self.session.execute(total_stmt)
        
        completed_count = completed_result.scalar()
        total_count = total_result.scalar()
        
        stats["completion_rate"] = (completed_count / total_count * 100) if total_count > 0 else 0
        
        return stats
    
    async def get_leaderboard(self, incursion_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the leaderboard for a specific incursion.
        
        Args:
            incursion_id: The incursion identifier
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Leaderboard data
        """
        stmt = (
            select(
                IncursionParticipant.user_id,
                IncursionParticipant.reps_contributed,
                IncursionParticipant.participated_at
            )
            .join(Incursion, IncursionParticipant.incursion_id == Incursion.id)
            .where(Incursion.incursion_id == incursion_id)
            .order_by(desc(IncursionParticipant.reps_contributed))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        leaderboard = []
        for i, row in enumerate(rows, 1):
            leaderboard.append({
                "rank": i,
                "user_id": row.user_id,
                "reps_contributed": row.reps_contributed,
                "participated_at": row.participated_at
            })
        
        return leaderboard
    
    async def get_user_participation(self, user_id: int, limit: int = 20) -> List[Incursion]:
        """
        Get incursions that a user has participated in.
        
        Args:
            user_id: The user's ID
            limit: Maximum number of incursions to return
            
        Returns:
            List[Incursion]: List of incursions the user participated in
        """
        stmt = (
            select(Incursion)
            .join(IncursionParticipant, Incursion.id == IncursionParticipant.incursion_id)
            .where(IncursionParticipant.user_id == user_id)
            .order_by(desc(IncursionParticipant.participated_at))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_active_incursions(self) -> int:
        """
        Count the number of currently active incursions.
        
        Returns:
            int: Number of active incursions
        """
        current_time = datetime.now(timezone.utc)
        
        stmt = (
            select(func.count(Incursion.id))
            .where(
                and_(
                    Incursion.is_active == True,
                    Incursion.expires_at > current_time,
                    Incursion.status == IncursionStatus.ACTIVE
                )
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def search_incursions(
        self, 
        query: str, 
        incursion_type: Optional[IncursionType] = None,
        status: Optional[IncursionStatus] = None,
        limit: int = 50
    ) -> List[Incursion]:
        """
        Search incursions by title or description.
        
        Args:
            query: Search query string
            incursion_type: Optional type filter
            status: Optional status filter
            limit: Maximum number of results
            
        Returns:
            List[Incursion]: Matching incursions
        """
        conditions = [
            Incursion.title.ilike(f"%{query}%") | 
            Incursion.description.ilike(f"%{query}%")
        ]
        
        if incursion_type:
            conditions.append(Incursion.incursion_type == incursion_type)
        
        if status:
            conditions.append(Incursion.status == status)
        
        stmt = (
            select(Incursion)
            .options(selectinload(Incursion.participants))
            .where(and_(*conditions))
            .order_by(desc(Incursion.created_at))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())