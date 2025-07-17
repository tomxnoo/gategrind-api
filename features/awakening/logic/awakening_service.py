"""
Awakening System Service
Handles the core logic for daily awakening ritual and quest generation
"""

import asyncio
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
                awakening_id, quest_data, tier, xp_reward, "available"
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
            # Standard: balanced distribution
            if quest_index == 0:
                return 1  # Start with practice
            elif quest_index == total_quests - 1:
                return random.choice([2, 3])  # End with technique or intensity
            else:
                return random.choice([1, 2])  # Middle quests
        
        else:  # HIGH
            # High energy: more technique and intensity
            if quest_index == 0:
                return random.choice([1, 2])  # Warm up with practice or technique
            else:
                return random.choice([2, 3])  # Focus on technique and intensity
    
    async def _generate_single_quest(
        self,
        tier: int,
        user_level: int,
        readiness_effects: ReadinessEffects,
        user_data: Dict
    ) -> Dict:
        """Generate a single quest with readiness modifications"""
        
        # Select theme based on readiness preferences
        available_themes = list(QUEST_THEMES.keys())
        preferred_themes = readiness_effects.quest_themes
        
        # Weight theme selection based on preferences
        theme_weights = {}
        for theme in available_themes:
            if any(pref in theme.lower() for pref in preferred_themes):
                theme_weights[theme] = 2.0
            else:
                theme_weights[theme] = 1.0
        
        # Select weighted random theme
        theme = random.choices(
            list(theme_weights.keys()),
            weights=list(theme_weights.values())
        )[0]
        
        theme_info = QUEST_THEMES[theme]
        
        # Filter movements by tier and readiness preferences
        possible_movements = [
            m for m, data in MOVEMENT_DATA.items()
            if data['tier'] <= tier and data['stat'] == theme
        ]
        
        if not possible_movements:
            # Fallback to any movement of appropriate tier
            possible_movements = [
                m for m, data in MOVEMENT_DATA.items()
                if data['tier'] <= tier
            ]
        
        # Select movement with readiness weighting
        movement = self._select_weighted_movement(possible_movements, readiness_effects)
        movement_data = MOVEMENT_DATA[movement]
        
        # Calculate reps/sets with readiness modifier
        base_reps = self._calculate_base_reps(tier, user_level)
        base_sets = self._calculate_base_sets(tier, user_level)
        
        # Apply difficulty modifier
        target_reps = max(1, int(base_reps * readiness_effects.difficulty_modifier))
        target_sets = max(1, int(base_sets * readiness_effects.difficulty_modifier))
        
        # Generate quest description with readiness context
        description = self._generate_quest_description(
            movement, target_sets, target_reps, readiness_effects, theme_info
        )
        
        return {
            "title": f"{theme_info['name']} Challenge: {movement}",
            "description": description,
            "tier": tier,
            "movement": movement,
            "target_sets": target_sets,
            "target_reps": target_reps,
            "theme": theme,
            "readiness_level": readiness_effects.description,
            "progress": {
                "current_sets": 0,
                "current_reps": 0,
                "completed": False
            }
        }
    
    def _select_weighted_movement(self, movements: List[str], readiness_effects: ReadinessEffects) -> str:
        """Select movement with readiness preference weighting"""
        if not movements:
            return "Push-ups"  # Fallback
        
        movement_weights = []
        for movement in movements:
            movement_data = MOVEMENT_DATA[movement]
            weight = 1.0
            
            # Apply readiness preferences
            for pref_type, pref_weight in readiness_effects.movement_preferences.items():
                if pref_type.lower() in movement.lower() or pref_type.lower() in movement_data.get('category', '').lower():
                    weight *= pref_weight
            
            movement_weights.append(weight)
        
        return random.choices(movements, weights=movement_weights)[0]
    
    def _calculate_base_reps(self, tier: int, user_level: int) -> int:
        """Calculate base rep count for quest"""
        base_reps = {1: 8, 2: 12, 3: 15}[tier]
        level_bonus = min(user_level // 5, 10)  # +2 reps per 5 levels, max +20
        return base_reps + level_bonus
    
    def _calculate_base_sets(self, tier: int, user_level: int) -> int:
        """Calculate base set count for quest"""
        base_sets = {1: 2, 2: 3, 3: 4}[tier]
        if user_level >= 15:
            base_sets += 1
        return base_sets
    
    def _calculate_base_xp(self, tier: int, user_level: int) -> int:
        """Calculate base XP reward for quest"""
        base_xp = {1: 25, 2: 40, 3: 60}[tier]
        level_multiplier = 1 + (user_level * 0.02)  # +2% per level
        return int(base_xp * level_multiplier)
    
    def _generate_quest_description(
        self,
        movement: str,
        sets: int,
        reps: int,
        readiness_effects: ReadinessEffects,
        theme_info: Dict
    ) -> str:
        """Generate contextual quest description"""
        
        readiness_context = {
            "Low energy - Focus on recovery and gentle movement": "Take it easy today, operative. Your body needs recovery.",
            "Standard energy - Balanced training approach": "Standard protocol, operative. Execute with precision.",
            "High energy - Push limits and embrace intensity": "You're charged up, operative. Time to push your limits!"
        }
        
        context = readiness_context.get(readiness_effects.description, "")
        
        return f"{context}\n\n**{theme_info['description']}**\n\nComplete {sets} sets of {reps} {movement}. Focus on {theme_info.get('focus', 'proper form')}."
    
    async def _update_awakening_stats(
        self,
        user_id: int,
        readiness_level: ReadinessLevel,
        conn: asyncpg.Connection
    ):
        """Update user's awakening statistics"""
        
        user_data = await get_unified_user_data(conn, user_id, self.bot)
        
        awakening_stats = user_data.get("awakening_stats", {
            "total_awakenings": 0,
            "completion_streak": 0,
            "average_readiness": "standard",
            "preferred_readiness": "standard",
            "readiness_history": []
        })
        
        # Update stats
        awakening_stats["total_awakenings"] += 1
        awakening_stats["readiness_history"].append({
            "date": date.today().isoformat(),
            "level": readiness_level.value
        })
        
        # Keep only last 30 days of history
        awakening_stats["readiness_history"] = awakening_stats["readiness_history"][-30:]
        
        # Calculate average readiness
        recent_levels = [entry["level"] for entry in awakening_stats["readiness_history"][-7:]]
        if recent_levels:
            level_counts = {"low": 0, "standard": 0, "high": 0}
            for level in recent_levels:
                level_counts[level] += 1
            awakening_stats["average_readiness"] = max(level_counts, key=level_counts.get)
        
        # Update user data
        user_data["awakening_stats"] = awakening_stats
        await update_user_json_data(conn, user_id, user_data, self.bot)
    
    async def _record_readiness_history(
        self,
        user_id: int,
        readiness_level: ReadinessLevel,
        conn: asyncpg.Connection
    ):
        """Record readiness level in history table"""
        
        today = date.today()
        
        await conn.execute(
            """
            INSERT INTO readiness_history (user_id, date, readiness_level)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, date) 
            DO UPDATE SET readiness_level = $3, created_at = CURRENT_TIMESTAMP
            """,
            user_id, today, readiness_level.value
        )
    
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
            raise ValueError("Quest not found or not owned by user")
        
        if quest["status"] == "completed":
            raise ValueError("Quest already completed")
        
        # Mark quest as completed
        await conn.execute(
            """
            UPDATE awakening_quests 
            SET status = 'completed', completed_at = $1, updated_at = $1
            WHERE id = $2
            """,
            datetime.utcnow(), quest_id
        )
        
        # Update awakening session
        await conn.execute(
            """
            UPDATE awakening_sessions 
            SET completed_quests = array_append(completed_quests, $1),
                total_xp_gained = total_xp_gained + $2,
                updated_at = $3
            WHERE id = $4
            """,
            quest_id, quest["xp_reward"], datetime.utcnow(), quest["awakening_session_id"]
        )
        
        # Check if all quests are completed
        session = await conn.fetchrow(
            """
            SELECT * FROM awakening_sessions WHERE id = $1
            """,
            quest["awakening_session_id"]
        )
        
        if len(session["completed_quests"]) >= len(session["generated_quests"]):
            # All quests completed - mark awakening as completed
            await conn.execute(
                """
                UPDATE awakening_sessions 
                SET status = 'completed', completed_at = $1, updated_at = $1
                WHERE id = $2
                """,
                datetime.utcnow(), quest["awakening_session_id"]
            )
        
        return {
            "quest_id": quest_id,
            "xp_gained": quest["xp_reward"],
            "awakening_completed": len(session["completed_quests"]) + 1 >= len(session["generated_quests"])
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