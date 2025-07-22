"""
Awakening System Service
Handles the core logic for daily awakening ritual and quest generation.
"""
import asyncpg
import json
from datetime import date, datetime
from typing import Dict, List, Any, Optional
from api.models.awakening import ReadinessLevel

class AwakeningService:
    """Core service for awakening system functionality"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_today_awakening(self, user_id: int, conn: asyncpg.Connection) -> Optional[Dict]:
        """Get today's awakening session for a user"""
        today = date.today()
        
        query = """
        SELECT id, user_id, awakening_date, readiness_level, status, quest_count,
               generated_quests, completed_quests, total_xp_gained, awakened_at,
               completed_at, created_at, updated_at
        FROM awakening_sessions 
        WHERE user_id = $1 AND awakening_date = $2
        """
        
        row = await conn.fetchrow(query, user_id, today)
        if row:
            return dict(row)
        return None

    async def get_awakening_quests_db(self, user_id: int, conn: asyncpg.Connection) -> List[Dict]:
        """Get awakening quests from database for today's session"""
        today = date.today()
        
        query = """
        SELECT aq.id, aq.quest_data, aq.tier, aq.xp_reward, aq.status, 
               aq.progress, aq.completed_at, aq.created_at
        FROM awakening_quests aq
        JOIN awakening_sessions as_session ON aq.awakening_session_id = as_session.id
        WHERE as_session.user_id = $1 AND as_session.awakening_date = $2
        ORDER BY aq.tier, aq.created_at
        """
        
        rows = await conn.fetch(query, user_id, today)
        return [dict(row) for row in rows]

    async def get_awakening_status(self, user_id: int, include_quests: bool = False) -> Dict:
        """Get the current awakening status for a user"""
        async with self.db_pool.acquire() as conn:
            awakening = await self.get_today_awakening(user_id, conn)

            if not awakening:
                return {
                    "status": "pending",
                    "awakened": False,
                    "quests_available": False,
                    "readiness_level": None,
                    "quests": [],
                    "active_session": None,
                }

            quests = []
            if include_quests:
                quests = await self.get_awakening_quests_db(user_id, conn)

            return {
                "status": awakening['status'],
                "awakened": awakening['status'] != 'pending',
                "quests_available": len(quests) > 0,
                "readiness_level": awakening['readiness_level'],
                "quest_count": awakening['quest_count'],
                "completed_quests": len(awakening.get('completed_quests', [])),
                "total_xp_gained": awakening['total_xp_gained'],
                "session_theme": "Shadow Training",
                "quests": quests,
                "active_session": awakening,
            }

    async def process_awakening(self, user_id: int, readiness_level: ReadinessLevel) -> Dict:
        """Process a new awakening ritual"""
        async with self.db_pool.acquire() as conn:
            today = date.today()
            
            # Check if already awakened today
            existing = await self.get_today_awakening(user_id, conn)
            if existing:
                return await self.get_awakening_status(user_id, include_quests=True)
            
            # Create new awakening session
            query = """
            INSERT INTO awakening_sessions 
            (user_id, awakening_date, readiness_level, status, quest_count, awakened_at)
            VALUES ($1, $2, $3, 'awakened', $4, $5)
            RETURNING id
            """
            
            quest_count = self._get_quest_count_for_readiness(readiness_level)
            awakened_at = datetime.now()
            
            session_id = await conn.fetchval(
                query, user_id, today, readiness_level.value, quest_count, awakened_at
            )
            
            # Generate quests (simplified for now)
            await self._generate_quests(user_id, session_id, quest_count, readiness_level, conn)
            
            return await self.get_awakening_status(user_id, include_quests=True)

    async def complete_quest(self, user_id: int, quest_id: int) -> Dict:
        """Mark a quest as completed"""
        async with self.db_pool.acquire() as conn:
            # Update quest status
            query = """
            UPDATE awakening_quests 
            SET status = 'completed', completed_at = $1
            WHERE id = $2 AND awakening_session_id IN (
                SELECT id FROM awakening_sessions 
                WHERE user_id = $3 AND awakening_date = $4
            )
            """
            
            await conn.execute(query, datetime.now(), quest_id, user_id, date.today())
            
            # Update session progress
            await self._update_session_progress(user_id, conn)
            
            return await self.get_awakening_status(user_id, include_quests=True)

    async def get_awakening_history(self, user_id: int, limit: int = 10) -> Dict:
        """Get user's awakening history"""
        async with self.db_pool.acquire() as conn:
            query = """
            SELECT awakening_date, readiness_level, status, quest_count,
                   completed_quests, total_xp_gained, awakened_at, completed_at
            FROM awakening_sessions 
            WHERE user_id = $1 
            ORDER BY awakening_date DESC 
            LIMIT $2
            """
            
            rows = await conn.fetch(query, user_id, limit)
            sessions = [dict(row) for row in rows]
            
            return {
                "sessions": sessions,
                "total_sessions": len(sessions),
            }

    async def recover_session(self, user_id: int) -> Dict:
        """Recover a stuck awakening session"""
        async with self.db_pool.acquire() as conn:
            today = date.today()
            
            # Reset today's session if it exists
            query = """
            UPDATE awakening_sessions 
            SET status = 'pending', awakened_at = NULL, completed_at = NULL
            WHERE user_id = $1 AND awakening_date = $2
            """
            
            await conn.execute(query, user_id, today)
            
            # Delete associated quests
            delete_query = """
            DELETE FROM awakening_quests 
            WHERE awakening_session_id IN (
                SELECT id FROM awakening_sessions 
                WHERE user_id = $1 AND awakening_date = $2
            )
            """
            
            await conn.execute(delete_query, user_id, today)
            
            return await self.get_awakening_status(user_id)

    def _get_quest_count_for_readiness(self, readiness_level: ReadinessLevel) -> int:
        """Determine quest count based on readiness level"""
        if readiness_level == ReadinessLevel.LOW:
            return 2
        elif readiness_level == ReadinessLevel.STANDARD:
            return 3
        else:  # HIGH
            return 4

    async def _generate_quests(self, user_id: int, session_id: int, quest_count: int, 
                             readiness_level: ReadinessLevel, conn: asyncpg.Connection):
        """Generate quests for the awakening session"""
        # Simplified quest generation - in a real implementation, 
        # this would use the quest engine
        for i in range(quest_count):
            quest_data = {
                "title": f"Shadow Training {i+1}",
                "description": f"Complete training exercise {i+1}",
                "type": "practice" if i == 0 else "technique" if i == 1 else "intensity",
                "difficulty": readiness_level.value,
            }
            
            query = """
            INSERT INTO awakening_quests 
            (awakening_session_id, quest_data, tier, xp_reward, status)
            VALUES ($1, $2::jsonb, $3, $4, 'available')
            """
            
            tier = (i % 3) + 1
            xp_reward = 50 * tier
            
            # Convert quest_data to JSON string for JSONB column
            quest_data_json = json.dumps(quest_data)
            
            await conn.execute(query, session_id, quest_data_json, tier, xp_reward)

    async def _update_session_progress(self, user_id: int, conn: asyncpg.Connection):
        """Update session progress after quest completion"""
        today = date.today()
        
        # Get completed quest count
        query = """
        SELECT COUNT(*) as completed_count,
               (SELECT quest_count FROM awakening_sessions 
                WHERE user_id = $1 AND awakening_date = $2) as total_count
        FROM awakening_quests aq
        JOIN awakening_sessions as_session ON aq.awakening_session_id = as_session.id
        WHERE as_session.user_id = $1 AND as_session.awakening_date = $2 
        AND aq.status = 'completed'
        """
        
        result = await conn.fetchrow(query, user_id, today)
        completed_count = result['completed_count']
        total_count = result['total_count']
        
        # Update session status if all quests completed
        if completed_count >= total_count:
            update_query = """
            UPDATE awakening_sessions 
            SET status = 'completed', completed_at = $1
            WHERE user_id = $2 AND awakening_date = $3
            """
            await conn.execute(update_query, datetime.now(), user_id, today)