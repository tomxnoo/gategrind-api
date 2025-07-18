"""
Awakening System Service
Handles the core logic for daily awakening ritual and quest generation
"""

import asyncio
import json
import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import asyncpg
from core.database.db import get_unified_user_data, update_user_json_data
from core.redis_cache import get_or_cache_user_json_data, invalidate_user_json_cache
from features.quests.logic.quest_templates import QUEST_THEMES, MOVEMENT_DATA
from api.models.awakening import ReadinessLevel, AwakeningStatus, ReadinessEffects

class AwakeningService:
    """Core service for awakening system functionality"""
    
    def __init__(self, bot=None):
        self.bot = bot
        
    async def get_today_awakening(self, user_id: int, conn: asyncpg.Connection) -> Optional[Dict]:
        """Get today's awakening session for a user"""
        today = date.today()
        
        result = await conn.fetchrow(
            """
            SELECT * FROM awakening_sessions 
            WHERE user_id = $1 AND awakening_date = $2
            """,
            user_id, today
        )
        
        if result:
            return dict(result)
        return None
    
    async def create_awakening_session(
        self, 
        user_id: int, 
        readiness_level: ReadinessLevel,
        conn: asyncpg.Connection
    ) -> Dict:
        """Create a new awakening session and generate quests"""
        today = date.today()
        
        # Check if awakening already exists for today
        existing = await self.get_today_awakening(user_id, conn)
        if existing:
            raise ValueError("Awakening already completed for today")
        
        # Get user data for quest generation
        user_data = await get_unified_user_data(conn, user_id, self.bot)
        user_level = user_data.get("level", 1)
        
        # Determine quest count based on readiness and user level
        quest_count = self._calculate_quest_count(readiness_level, user_level)
        
        # Create awakening session
        awakening_id = await conn.fetchval(
            """
            INSERT INTO awakening_sessions 
            (user_id, awakening_date, readiness_level, quest_count, awakened_at, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            user_id, today, readiness_level.value, quest_count, datetime.utcnow(), AwakeningStatus.AWAKENED.value
        )
        
        # Generate quests based on readiness level
        quests = await self._generate_awakening_quests(
            awakening_id, user_id, readiness_level, quest_count, user_data, conn
        )
        
        # Update awakening session with quest IDs
        quest_ids = [quest["id"] for quest in quests]
        await conn.execute(
            """
            UPDATE awakening_sessions 
            SET generated_quests = $1, updated_at = $2
            WHERE id = $3
            """,
            quest_ids, datetime.utcnow(), awakening_id
        )
        
        # Update user's awakening stats
        await self._update_awakening_stats(user_id, readiness_level, conn)
        
        # Record readiness history
        await self._record_readiness_history(user_id, readiness_level, conn)
        
        return {
            "awakening_id": awakening_id,
            "readiness_level": readiness_level.value,
            "quest_count": quest_count,
            "quests": quests,
            "awakened_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_awakening_quests(
        self,
        awakening_id: int,
        user_id: int,
        readiness_level: ReadinessLevel,
        quest_count: int,
        user_data: Dict,
        conn: asyncpg.Connection
    ) -> List[Dict]:
        """Generate quests based on readiness level and autoregulation"""
        
        readiness_effects = self._get_readiness_effects(readiness_level)
        user_level = user_data.get("level", 1)
        
        quests = []
        
        for i in range(quest_count):
            # Determine quest tier based on readiness and position
            tier = self._determine_quest_tier(readiness_level, i, quest_count)
            
            # Generate quest with readiness modifications
            quest_data = await self._generate_single_quest(
                tier, user_level, readiness_effects, user_data
            )
            
            # Calculate XP reward with readiness modifier
            base_xp = self._calculate_base_xp(tier, user_level)
            xp_reward = int(base_xp * readiness_effects.xp_modifier)
            
            # Insert quest into database
            quest_id = await conn.fetchval(
                """
                INSERT INTO awakening_quests 
                (awakening_session_id, quest_data, tier, xp_reward, status)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                awakening_id, json.dumps(quest_data), tier, xp_reward, "available"
            )
            
            quest_data["id"] = quest_id
            quest_data["xp_reward"] = xp_reward
            quest_data["status"] = "available"
            
            quests.append(quest_data)
        
        return quests
    
    def _get_readiness_effects(self, readiness_level: ReadinessLevel) -> ReadinessEffects:
        """Get the effects of readiness level on quest generation"""
        
        effects_map = {
            ReadinessLevel.LOW: ReadinessEffects(
                difficulty_modifier=0.7,
                xp_modifier=0.9,
                quest_themes=["recovery", "mobility", "light_volume"],
                movement_preferences={"bodyweight": 1.5, "stretching": 2.0, "light_cardio": 1.3},
                description="Low energy - Focus on recovery and gentle movement"
            ),
            ReadinessLevel.STANDARD: ReadinessEffects(
                difficulty_modifier=1.0,
                xp_modifier=1.0,
                quest_themes=["balanced", "technique", "moderate_volume"],
                movement_preferences={"strength": 1.0, "endurance": 1.0, "technique": 1.2},
                description="Standard energy - Balanced training approach"
            ),
            ReadinessLevel.HIGH: ReadinessEffects(
                difficulty_modifier=1.4,
                xp_modifier=1.3,
                quest_themes=["intensity", "strength", "challenge"],
                movement_preferences={"strength": 1.5, "intensity": 1.8, "compound": 1.4},
                description="High energy - Push limits and embrace intensity"
            )
        }
        
        return effects_map[readiness_level]
    
    def _calculate_quest_count(self, readiness_level: ReadinessLevel, user_level: int) -> int:
        """Calculate number of quests based on readiness and user level"""
        base_count = 3
        
        # Readiness adjustments
        if readiness_level == ReadinessLevel.LOW:
            base_count = 2  # Fewer quests for recovery
        elif readiness_level == ReadinessLevel.HIGH:
            base_count = 4  # More quests for high energy
        
        # Level adjustments (higher level users can handle more)
        if user_level >= 10:
            base_count += 1
        elif user_level >= 25:
            base_count += 1
        
        return min(max(base_count, 1), 5)  # Clamp between 1-5
    
    def _determine_quest_tier(self, readiness_level: ReadinessLevel, quest_index: int, total_quests: int) -> int:
        """Determine quest tier based on readiness level and quest position"""
        
        if readiness_level == ReadinessLevel.LOW:
            # Low energy: mostly practice (tier 1), some technique (tier 2)
            return 1 if quest_index < total_quests - 1 else random.choice([1, 2])
        elif readiness_level == ReadinessLevel.STANDARD:
            # Standard energy: balanced distribution
            tier_weights = [0.4, 0.4, 0.2]  # 40% tier 1, 40% tier 2, 20% tier 3
            return random.choices([1, 2, 3], weights=tier_weights)[0]
        else:  # HIGH energy
            # High energy: favor higher tiers
            tier_weights = [0.2, 0.4, 0.4]  # 20% tier 1, 40% tier 2, 40% tier 3
            return random.choices([1, 2, 3], weights=tier_weights)[0]
    
    async def _generate_single_quest(
        self,
        tier: int,
        user_level: int,
        readiness_effects: ReadinessEffects,
        user_data: Dict
    ) -> Dict:
        """Generate a single quest based on tier and readiness effects"""
        
        # Select theme based on readiness preferences
        available_themes = list(QUEST_THEMES.keys())
        theme = random.choice(available_themes)
        theme_info = QUEST_THEMES[theme]
        
        # Filter movements by theme and tier
        possible_movements = [
            m for m, data in MOVEMENT_DATA.items()
            if data['stat'] == theme and data['tier'] <= tier
        ]
        
        # Fallback if no movements found
        if not possible_movements:
            possible_movements = [m for m, data in MOVEMENT_DATA.items() if data['tier'] <= tier]
        if not possible_movements:
            possible_movements = ["Standard Push-Ups"]  # Ultimate fallback
        
        # Select movement(s) for the quest
        movement_count = min(3, len(possible_movements))
        movements = random.sample(possible_movements, movement_count)
        
        # Calculate reps based on tier and readiness
        base_reps = 5 + (tier * 3)
        adjusted_reps = int(base_reps * readiness_effects.difficulty_modifier)
        sets = 3 + (tier - 1)  # More sets for higher tiers
        
        # Create quest data
        quest_data = {
            "tier": tier,
            "theme": theme,
            "name": f"T{tier}: {theme_info['name']}",
            "flavor": random.choice(theme_info['flavor']),
            "movements": movements,
            "target": {"sets": sets, "reps": adjusted_reps},
            "progress": {move: {"sets": 0, "reps": 0} for move in movements},
            "readiness_modifier": readiness_effects.difficulty_modifier,
            "completed": False,
            "active": False
        }
        
        return quest_data
    
    def _calculate_base_xp(self, tier: int, user_level: int) -> int:
        """Calculate base XP reward for a quest"""
        base_xp = 50 + (tier * 25)  # 75, 100, 125 for tiers 1, 2, 3
        level_bonus = user_level * 2  # Small level scaling
        return base_xp + level_bonus
    
    async def _update_awakening_stats(self, user_id: int, readiness_level: ReadinessLevel, conn: asyncpg.Connection):
        """Update user's awakening statistics"""
        # This could track awakening streaks, readiness patterns, etc.
        pass
    
    async def _record_readiness_history(self, user_id: int, readiness_level: ReadinessLevel, conn: asyncpg.Connection):
        """Record readiness level for historical analysis"""
        await conn.execute(
            """
            INSERT INTO awakening_readiness_history (user_id, readiness_level, recorded_at)
            VALUES ($1, $2, $3)
            """,
            user_id, readiness_level.value, datetime.utcnow()
        )
    
    async def get_awakening_quests(self, user_id: int, conn: asyncpg.Connection) -> List[Dict]:
        """Get today's awakening quests for a user"""
        today = date.today()
        
        results = await conn.fetch(
            """
            SELECT aq.*, aws.readiness_level
            FROM awakening_quests aq
            JOIN awakening_sessions aws ON aq.awakening_session_id = aws.id
            WHERE aws.user_id = $1 AND aws.awakening_date = $2
            ORDER BY aq.tier
            """,
            user_id, today
        )
        
        return [dict(row) for row in results]
    
    async def complete_awakening_quest(
        self,
        user_id: int,
        quest_id: int,
        conn: asyncpg.Connection
    ) -> Dict:
        """Mark an awakening quest as completed and update progress"""
        
        # Get quest details
        quest = await conn.fetchrow(
            """
            SELECT aq.*, aws.user_id, aws.awakening_date
            FROM awakening_quests aq
            JOIN awakening_sessions aws ON aq.awakening_session_id = aws.id
            WHERE aq.id = $1 AND aws.user_id = $2
            """,
            quest_id, user_id
        )
        
        if not quest:
            raise ValueError("Quest not found or doesn't belong to user")
        
        if quest['status'] == 'completed':
            raise ValueError("Quest already completed")
        
        # Mark quest as completed
        await conn.execute(
            """
            UPDATE awakening_quests 
            SET status = 'completed', completed_at = $1
            WHERE id = $2
            """,
            datetime.utcnow(), quest_id
        )
        
        # Award XP
        from features.user.logic.xp_engine import add_xp
        await add_xp(conn, user_id, quest['xp_reward'], bot=self.bot)
        
        # Check if all quests for today are completed
        remaining_quests = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM awakening_quests aq
            JOIN awakening_sessions aws ON aq.awakening_session_id = aws.id
            WHERE aws.user_id = $1 AND aws.awakening_date = $2 AND aq.status != 'completed'
            """,
            user_id, quest['awakening_date']
        )
        
        session_complete = remaining_quests == 0
        
        if session_complete:
            # Mark awakening session as completed
            await conn.execute(
                """
                UPDATE awakening_sessions 
                SET status = $1, completed_at = $2
                WHERE user_id = $3 AND awakening_date = $4
                """,
                AwakeningStatus.COMPLETED.value, datetime.utcnow(), user_id, quest['awakening_date']
            )
        
        return {
            "quest_completed": True,
            "xp_awarded": quest['xp_reward'],
            "session_complete": session_complete
        }
    
    async def get_awakening_status(self, user_id: int, conn: asyncpg.Connection) -> Dict:
        """Get the current awakening status for a user"""
        today = date.today()
        
        awakening = await self.get_today_awakening(user_id, conn)
        
        if not awakening:
            return {
                "status": AwakeningStatus.PENDING.value,
                "awakened": False,
                "quests_available": False,
                "readiness_level": None,
                "quests": []
            }
        
        quests = await self.get_awakening_quests(user_id, conn)
        
        return {
            "status": awakening['status'],
            "awakened": True,
            "quests_available": len(quests) > 0,
            "readiness_level": awakening['readiness_level'],
            "quest_count": awakening['quest_count'],
            "quests": quests,
            "awakened_at": awakening['awakened_at'].isoformat() if awakening['awakened_at'] else None,
            "completed_at": awakening['completed_at'].isoformat() if awakening.get('completed_at') else None
        }
    
    async def get_daily_briefing(self, user_id: int, conn: asyncpg.Connection) -> Dict:
        """Generate daily briefing after awakening"""
        
        today_awakening = await self.get_today_awakening(user_id, conn)
        if not today_awakening:
            return {"error": "No awakening found for today"}
        
        # Get quest details
        quests = await conn.fetch(
            """
            SELECT * FROM awakening_quests 
            WHERE awakening_session_id = $1
            ORDER BY id
            """,
            today_awakening["id"]
        )
        
        # Get user data for personalization
        user_data = await get_unified_user_data(conn, user_id, self.bot)
        
        # Generate briefing
        briefing = {
            "awakening_summary": self._generate_awakening_summary(today_awakening, user_data),
            "quest_overview": [self._generate_quest_summary(dict(q)) for q in quests],
            "readiness_impact": self._generate_readiness_impact(today_awakening["readiness_level"]),
            "motivation_message": self._generate_motivation_message(today_awakening, user_data),
            "progress_highlights": await self._generate_progress_highlights(user_id, conn)
        }
        
        return briefing
    
    def _generate_awakening_summary(self, awakening: Dict, user_data: Dict) -> str:
        """Generate awakening summary message"""
        readiness = awakening["readiness_level"]
        quest_count = awakening["quest_count"]
        
        readiness_messages = {
            "low": f"You've awakened with {quest_count} recovery-focused quests. Listen to your body today.",
            "standard": f"You've awakened with {quest_count} balanced quests. Execute with precision.",
            "high": f"You've awakened with {quest_count} intense quests. Channel that energy!"
        }
        
        return readiness_messages.get(readiness, f"You've awakened with {quest_count} quests.")
    
    def _generate_quest_summary(self, quest: Dict) -> str:
        """Generate individual quest summary"""
        quest_data = quest["quest_data"]
        return f"**{quest_data['title']}** - {quest_data['target_sets']} sets × {quest_data['target_reps']} reps"
    
    def _generate_readiness_impact(self, readiness_level: str) -> str:
        """Generate readiness impact explanation"""
        impacts = {
            "low": "Your quests are tuned for recovery. Focus on movement quality over intensity.",
            "standard": "Your quests follow standard protocols. Maintain consistent effort.",
            "high": "Your quests are amplified for maximum challenge. Push your boundaries!"
        }
        return impacts.get(readiness_level, "")
    
    def _generate_motivation_message(self, awakening: Dict, user_data: Dict) -> str:
        """Generate personalized motivation message"""
        level = user_data.get("level", 1)
        awakening_stats = user_data.get("awakening_stats", {})
        total_awakenings = awakening_stats.get("total_awakenings", 0)
        
        if total_awakenings == 1:
            return "Welcome to the Realm of Shadows, operative. Your journey begins now."
        elif total_awakenings % 7 == 0:
            return f"Week {total_awakenings // 7} complete! Your dedication shapes your destiny."
        elif level >= 10:
            return "Your skills are sharpening, operative. The shadows bend to your will."
        else:
            return "Another day, another step toward mastery. Execute with purpose."
    
    async def _generate_progress_highlights(self, user_id: int, conn: asyncpg.Connection) -> Dict:
        """Generate progress highlights for motivation"""
        
        # Get recent completion stats
        week_ago = date.today() - timedelta(days=7)
        
        recent_awakenings = await conn.fetch(
            """
            SELECT * FROM awakening_sessions 
            WHERE user_id = $1 AND awakening_date >= $2
            ORDER BY awakening_date DESC
            """,
            user_id, week_ago
        )
        
        completed_count = sum(1 for a in recent_awakenings if a["status"] == "completed")
        total_xp = sum(a["total_xp_gained"] for a in recent_awakenings)
        
        return {
            "weekly_completions": completed_count,
            "weekly_xp": total_xp,
            "consistency_streak": len(recent_awakenings),
            "average_readiness": self._calculate_average_readiness(recent_awakenings)
        }
    
    def _calculate_average_readiness(self, awakenings: List) -> str:
        """Calculate average readiness level"""
        if not awakenings:
            return "standard"
        
        level_counts = {"low": 0, "standard": 0, "high": 0}
        for awakening in awakenings:
            level_counts[awakening["readiness_level"]] += 1
        
        return max(level_counts, key=level_counts.get)