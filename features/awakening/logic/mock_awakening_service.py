"""
Mock Awakening Service for development mode
"""
from datetime import date, datetime
from typing import Dict, List, Any
from api.models.awakening import ReadinessLevel

class MockAwakeningService:
    """Mock service for awakening system functionality in development mode"""

    def __init__(self):
        # In-memory storage for mock data
        self._sessions = {}
        self._quests = {}

    async def get_awakening_status(self, user_id: int, include_quests: bool = False) -> Dict:
        """Get mock awakening status"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        if session_key not in self._sessions:
            return {
                "status": "pending",
                "awakened": False,
                "quests_available": False,
                "readiness_level": None,
                "quests": [],
                "active_session": None,
            }

        session = self._sessions[session_key]
        quests = []
        
        if include_quests and session_key in self._quests:
            quests = self._quests[session_key]

        return {
            "status": session["status"],
            "awakened": session["status"] != "pending",
            "quests_available": len(quests) > 0,
            "readiness_level": session["readiness_level"],
            "quest_count": session["quest_count"],
            "completed_quests": session.get("completed_quests", 0),
            "total_xp_gained": session.get("total_xp_gained", 0),
            "session_theme": "Shadow Training (Mock)",
            "quests": quests,
            "active_session": session,
        }

    async def process_awakening(self, user_id: int, readiness_level: ReadinessLevel) -> Dict:
        """Process mock awakening"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        # Create mock session
        quest_count = self._get_quest_count_for_readiness(readiness_level)
        
        self._sessions[session_key] = {
            "user_id": user_id,
            "awakening_date": today,
            "readiness_level": readiness_level.value,
            "status": "awakened",
            "quest_count": quest_count,
            "completed_quests": 0,
            "total_xp_gained": 0,
            "awakened_at": datetime.now().isoformat(),
        }
        
        # Generate mock quests
        self._quests[session_key] = self._generate_mock_quests(quest_count, readiness_level)
        
        return await self.get_awakening_status(user_id, include_quests=True)

    async def complete_quest(self, user_id: int, quest_id: int) -> Dict:
        """Complete mock quest"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        if session_key in self._quests:
            for quest in self._quests[session_key]:
                if quest["id"] == quest_id:
                    quest["status"] = "completed"
                    quest["completed_at"] = datetime.now().isoformat()
                    
                    # Update session progress
                    if session_key in self._sessions:
                        session = self._sessions[session_key]
                        session["completed_quests"] += 1
                        session["total_xp_gained"] += quest["xp_reward"]
                        
                        # Check if all quests completed
                        completed_count = sum(1 for q in self._quests[session_key] 
                                            if q["status"] == "completed")
                        if completed_count >= session["quest_count"]:
                            session["status"] = "completed"
                            session["completed_at"] = datetime.now().isoformat()
                    break
        
        return await self.get_awakening_status(user_id, include_quests=True)

    async def get_awakening_history(self, user_id: int, limit: int = 10) -> Dict:
        """Get mock awakening history"""
        # Return mock history data
        sessions = []
        for i in range(min(3, limit)):  # Mock 3 previous sessions
            past_date = date.today().replace(day=date.today().day - i - 1)
            sessions.append({
                "awakening_date": past_date.isoformat(),
                "readiness_level": "standard",
                "status": "completed",
                "quest_count": 3,
                "completed_quests": 3,
                "total_xp_gained": 150,
                "awakened_at": f"{past_date}T08:00:00",
                "completed_at": f"{past_date}T20:00:00",
            })
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
        }

    async def recover_session(self, user_id: int) -> Dict:
        """Recover mock session"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        # Clear today's session
        if session_key in self._sessions:
            del self._sessions[session_key]
        if session_key in self._quests:
            del self._quests[session_key]
        
        return await self.get_awakening_status(user_id)

    def _get_quest_count_for_readiness(self, readiness_level: ReadinessLevel) -> int:
        """Determine quest count based on readiness level"""
        if readiness_level == ReadinessLevel.LOW:
            return 2
        elif readiness_level == ReadinessLevel.STANDARD:
            return 3
        else:  # HIGH
            return 4

    def _generate_mock_quests(self, quest_count: int, readiness_level: ReadinessLevel) -> List[Dict]:
        """Generate mock quests"""
        quests = []
        quest_types = ["practice", "technique", "intensity"]
        
        for i in range(quest_count):
            quest_type = quest_types[i % len(quest_types)]
            tier = (i % 3) + 1
            
            quests.append({
                "id": i + 1,
                "quest_data": {
                    "title": f"Mock {quest_type.title()} Quest {i+1}",
                    "description": f"Complete mock {quest_type} exercise",
                    "type": quest_type,
                    "difficulty": readiness_level.value,
                },
                "tier": tier,
                "xp_reward": 50 * tier,
                "status": "available",
                "progress": {},
                "completed_at": None,
                "created_at": datetime.now().isoformat(),
            })
        
        return quests