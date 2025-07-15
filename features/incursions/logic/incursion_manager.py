import asyncio
import logging
import json  # Add this import
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import asyncpg
from features.incursions.models.incursion import Incursion, IncursionType, RewardType

logger = logging.getLogger(__name__)

class IncursionManager:
    """Central manager for Shadow Incursions logic"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_pool = bot.db_pool
    
    async def get_active_incursions(self) -> List[Incursion]:
        """Fetch all currently active incursions"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM active_incursions 
                WHERE is_active = TRUE AND expires_at > NOW()
                ORDER BY created_at DESC
                """
            )
            return [self._row_to_incursion(row) for row in rows]
    
    async def get_incursion_by_id(self, incursion_id: str) -> Optional[Incursion]:
        """Fetch a specific incursion by its ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM active_incursions WHERE incursion_id = $1",
                incursion_id
            )
            return self._row_to_incursion(row) if row else None
    
    async def create_incursion(self, 
                             incursion_id: str,
                             incursion_type: IncursionType,
                             title: str,
                             description: str,
                             target_exercise: str,
                             target_reps: int,
                             reward_type: RewardType,
                             reward_value: int,
                             reward_description: str,
                             duration_hours: float = 24.0,
                             metadata: Dict[str, Any] = None) -> Incursion:
        """Create a new incursion"""
        if metadata is None:
            metadata = {}
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        
        # Convert metadata dict to JSON string for database storage
        metadata_json = json.dumps(metadata)
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO active_incursions 
                (incursion_id, incursion_type, title, description, target_exercise, 
                 target_reps, reward_type, reward_value, reward_description, 
                 expires_at, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING *
                """,
                incursion_id, incursion_type.value, title, description, 
                target_exercise, target_reps, reward_type.value, reward_value,
                reward_description, expires_at, metadata_json
            )
            
        logger.info(f"Created new incursion: {incursion_id} (expires: {expires_at})")
        return self._row_to_incursion(row)
    
    async def contribute_reps(self, incursion_id: str, reps: int) -> bool:
        """Add reps to an incursion's progress"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE active_incursions 
                SET current_reps = current_reps + $1
                WHERE incursion_id = $2 AND is_active = TRUE
                """,
                reps, incursion_id
            )
            
        success = result.split()[-1] == '1'  # Check if one row was updated
        if success:
            logger.info(f"Added {reps} reps to incursion {incursion_id}")
        return success
    
    async def complete_incursion(self, incursion_id: str) -> bool:
        """Mark an incursion as completed"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE active_incursions 
                SET is_active = FALSE
                WHERE incursion_id = $1
                """,
                incursion_id
            )
        
        success = result.split()[-1] == '1'
        if success:
            logger.info(f"Completed incursion: {incursion_id}")
        return success
    
    async def cleanup_expired_incursions(self) -> int:
        """Remove expired incursions and return count"""
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE active_incursions 
                SET is_active = FALSE
                WHERE expires_at <= NOW() AND is_active = TRUE
                """
            )
        
        count = int(result.split()[-1])
        if count > 0:
            logger.info(f"Cleaned up {count} expired incursions")
        return count
    
    def _row_to_incursion(self, row) -> Incursion:
        """Convert database row to Incursion object"""
        # Parse metadata JSON string back to dict
        metadata = {}
        if row['metadata']:
            try:
                metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
            except (json.JSONDecodeError, TypeError):
                metadata = {}
        
        return Incursion(
            id=row['id'],
            incursion_id=row['incursion_id'],
            incursion_type=IncursionType(row['incursion_type']),
            title=row['title'],
            description=row['description'],
            target_exercise=row['target_exercise'],
            target_reps=row['target_reps'],
            current_reps=row['current_reps'],
            reward_type=RewardType(row['reward_type']),
            reward_value=row['reward_value'],
            reward_description=row['reward_description'],
            created_at=row['created_at'],
            expires_at=row['expires_at'],
            is_active=row['is_active'],
            metadata=metadata
        )
    
    async def get_user_progress(self, user_id: int) -> Dict[int, int]:
        """Get user's progress for all active incursions"""
        # For now, return empty dict - this will be implemented with user participation tracking
        return {}
    
    async def get_participant_count(self, incursion_id: str) -> int:
        """Get the number of participants for an incursion"""
        async with self.db_pool.acquire() as conn:
            result = await conn.fetchval(
                """
                SELECT COUNT(DISTINCT user_id) 
                FROM user_incursion_participation 
                WHERE incursion_id = $1
                """,
                incursion_id
            )
            return result or 0
    
    async def get_incursion_leaderboard(self, incursion_id: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for an incursion"""
        async with self.db_pool.acquire() as conn:
            try:
                rows = await conn.fetch(
                    """
                    SELECT 
                        user_id,
                        SUM(reps_contributed) as total_reps,
                        COUNT(id) as sessions
                    FROM user_incursion_participation
                    WHERE incursion_id = $1
                    GROUP BY user_id
                    ORDER BY total_reps DESC
                    LIMIT $2
                    """,
                    incursion_id, limit
                )
                return [{
                    'username': f'User {row["user_id"]}',  # Fallback username format
                    'total_reps': row['total_reps'],
                    'sessions': row['sessions']
                } for row in rows]
            except Exception as e:
                logger.warning(f"Error fetching leaderboard for {incursion_id}: {e}")
                return []  # Return empty list if query fails
    
    async def get_hours_since_last_incursion(self) -> float:
        """Get hours since the last incursion ended (expired or completed)"""
        async with self.db_pool.acquire() as conn:
            # Get the most recent incursion that ended (either expired or manually completed)
            row = await conn.fetchrow(
                """
                SELECT expires_at, created_at
                FROM active_incursions 
                WHERE is_active = FALSE
                ORDER BY 
                    CASE 
                        WHEN expires_at <= NOW() THEN expires_at  -- Use expiry time for expired incursions
                        ELSE created_at  -- Use creation time for manually completed ones
                    END DESC
                LIMIT 1
                """
            )
            
            if not row:
                # No previous incursions found, return a large number to trigger escalation
                return 24.0  # 24 hours to ensure escalation kicks in
            
            # Calculate time since the incursion ended
            end_time = row['expires_at'] if row['expires_at'] <= datetime.now(timezone.utc) else row['created_at']
            time_diff = datetime.now(timezone.utc) - end_time
            return time_diff.total_seconds() / 3600  # Convert to hours