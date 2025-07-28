"""
Mock Awakening Service for development mode
"""
from datetime import date, datetime
from typing import Dict, List, Any
import json
import os
from api.models.awakening import ReadinessLevel

class MockAwakeningService:
    """Mock service for awakening system functionality in development mode"""
    
    # Class-level storage for true singleton behavior
    _sessions = {}
    _quests = {}
    _initialized = False

    def __init__(self):
        # File-based storage for persistence
        self.data_file = "mock_awakening_data.json"
        if not MockAwakeningService._initialized:
            self._load_data()
            MockAwakeningService._initialized = True
            print(f"[MOCK] Initialized MockAwakeningService with {len(MockAwakeningService._sessions)} sessions")
    
    def _load_data(self):
        """Load data from file if it exists"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    MockAwakeningService._sessions = data.get('sessions', {})
                    MockAwakeningService._quests = data.get('quests', {})
                    print(f"[MOCK] Loaded {len(MockAwakeningService._sessions)} sessions from file")
            except Exception as e:
                print(f"[MOCK] Error loading data: {e}")
                MockAwakeningService._sessions = {}
                MockAwakeningService._quests = {}
        else:
            MockAwakeningService._sessions = {}
            MockAwakeningService._quests = {}
    
    def _save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    'sessions': MockAwakeningService._sessions,
                    'quests': MockAwakeningService._quests
                }, f, indent=2)
                print(f"[MOCK] Saved {len(MockAwakeningService._sessions)} sessions to file")
        except Exception as e:
            print(f"[MOCK] Error saving data: {e}")

    async def get_or_create_daily_session(self, user_id: int, readiness_level: str) -> Dict:
        """Get or create a daily awakening session"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        # Check if session already exists
        if session_key in MockAwakeningService._sessions:
            session = MockAwakeningService._sessions[session_key]
            quests = MockAwakeningService._quests.get(session_key, [])
            return {
                "session": session,
                "quests": quests,
                "awakened": session["status"] != "pending",
                "message": "Existing session retrieved"
            }
        
        # Convert string readiness to ReadinessLevel enum
        readiness_map = {"low": ReadinessLevel.LOW, "medium": ReadinessLevel.STANDARD, "standard": ReadinessLevel.STANDARD, "high": ReadinessLevel.HIGH}
        readiness_enum = readiness_map.get(readiness_level, ReadinessLevel.STANDARD)
        
        # Create new session
        quest_count = self._get_quest_count_for_readiness(readiness_enum)
        
        session = {
            "user_id": user_id,
            "awakening_date": today,
            "readiness_level": readiness_level,
            "status": "awakened",
            "quest_count": quest_count,
            "completed_quests": 0,
            "total_xp_gained": 0,
            "awakened_at": datetime.now().isoformat(),
        }
        
        MockAwakeningService._sessions[session_key] = session
        
        # Generate mock quests
        quests = self._generate_mock_quests(quest_count, readiness_enum)
        MockAwakeningService._quests[session_key] = quests
        
        # Save to file
        self._save_data()
        
        return {
            "session": session,
            "quests": quests,
            "awakened": True,
            "message": f"New session created with {quest_count} quests"
        }

    async def get_awakening_progress(self, user_id: int, include_quests: bool = True) -> Dict:
        """Get mock awakening progress - alias for get_awakening_status"""
        return await self.get_awakening_status(user_id, include_quests)

    async def get_awakening_status(self, user_id: int, include_quests: bool = False) -> Dict:
        """Get mock awakening status"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        # Debug logging to file
        with open("debug_awakening.log", "a") as f:
            f.write(f"[STATUS] user_id={user_id}, session_key={session_key}, include_quests={include_quests}\n")
            f.write(f"[STATUS] instance_id={id(self)}, total_sessions={len(MockAwakeningService._sessions)}\n")
            f.write(f"[STATUS] session_exists={session_key in MockAwakeningService._sessions}\n")
            if MockAwakeningService._sessions:
                f.write(f"[STATUS] available_sessions={list(MockAwakeningService._sessions.keys())}\n")
        
        if session_key not in MockAwakeningService._sessions:
            with open("debug_awakening.log", "a") as f:
                f.write(f"[STATUS] session not found, returning pending\n")
            return {
                "status": "pending",
                "awakened": False,
                "quests_available": False,
                "readiness_level": None,
                "quests": [],
                "active_session": None,
            }

        session = MockAwakeningService._sessions[session_key]
        quests = []
        
        if include_quests and session_key in MockAwakeningService._quests:
            quests = MockAwakeningService._quests[session_key]

        with open("debug_awakening.log", "a") as f:
            f.write(f"[STATUS] returning session with status={session['status']}, quest_count={len(quests)}\n")
            
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
        
        # Debug logging to file
        with open("debug_awakening.log", "a") as f:
            f.write(f"[PROCESS] user_id={user_id}, session_key={session_key}, readiness={readiness_level.value}\n")
            f.write(f"[PROCESS] instance_id={id(self)}, sessions_before={len(MockAwakeningService._sessions)}\n")
        
        # Create mock session
        quest_count = self._get_quest_count_for_readiness(readiness_level)
        
        MockAwakeningService._sessions[session_key] = {
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
        MockAwakeningService._quests[session_key] = self._generate_mock_quests(quest_count, readiness_level)
        
        # Save to file
        self._save_data()
        
        with open("debug_awakening.log", "a") as f:
            f.write(f"[PROCESS] stored session, sessions_after={len(MockAwakeningService._sessions)}, quest_count={quest_count}\n")
        
        return await self.get_awakening_status(user_id, include_quests=True)

    async def complete_quest(self, user_id: int, quest_id: int) -> Dict:
        """Complete mock quest"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        quest_found = False
        xp_awarded = 0
        
        if session_key in MockAwakeningService._quests:
            for quest in MockAwakeningService._quests[session_key]:
                if quest["id"] == quest_id:
                    quest["status"] = "completed"
                    quest["completed"] = True
                    quest["completed_at"] = datetime.now().isoformat()
                    quest_found = True
                    xp_awarded = quest["xp_reward"]
                    
                    # Update session progress
                    if session_key in MockAwakeningService._sessions:
                        session = MockAwakeningService._sessions[session_key]
                        session["completed_quests"] += 1
                        session["total_xp_gained"] += quest["xp_reward"]
                        
                        # Check if all quests completed
                        completed_count = sum(1 for q in MockAwakeningService._quests[session_key] 
                                            if q["status"] == "completed")
                        if completed_count >= session["quest_count"]:
                            session["status"] = "completed"
                            session["completed_at"] = datetime.now().isoformat()
                    
                    # Save to file
                    self._save_data()
                    break
        
        return {
            "success": quest_found,
            "xp_awarded": xp_awarded,
            "message": f"Quest {quest_id} completed successfully" if quest_found else f"Quest {quest_id} not found",
            "session": await self.get_awakening_status(user_id, include_quests=True)
        }

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
        if session_key in MockAwakeningService._sessions:
            del MockAwakeningService._sessions[session_key]
        if session_key in MockAwakeningService._quests:
            del MockAwakeningService._quests[session_key]
        
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
                "title": f"Mock {quest_type.title()} Quest {i+1}",
                "description": f"Complete mock {quest_type} exercise",
                "type": quest_type,
                "difficulty": readiness_level.value,
                "tier": tier,
                "xp_reward": 50 * tier,
                "status": "available",
                "completed": False,
                "movement_name": f"Mock Movement {i+1}",
                "target_reps": 10 + (i * 2),
                "target_sets": 3,
                "progress": {},
                "completed_at": None,
                "created_at": datetime.now().isoformat(),
            })
        
        return quests
    
    async def get_daily_briefing(self, user_id: int) -> Dict:
        """Get mock daily briefing"""
        today = date.today().isoformat()
        session_key = f"{user_id}_{today}"
        
        if session_key in MockAwakeningService._sessions:
            session = MockAwakeningService._sessions[session_key]
            readiness = session.get("readiness_level", "standard")
            quest_count = session.get("quest_count", 0)
            
            return {
                "awakening_summary": f"Your {readiness} intensity session is active with {quest_count} challenges.",
                "quest_summary": f"Complete all {quest_count} quests to maximize your daily XP gains.",
                "readiness_impact": f"Your {readiness} readiness level provides balanced quest difficulty and rewards.",
                "motivation_message": "Push beyond your limits. Every rep counts towards your shadow mastery!"
            }
        
        return {
            "awakening_summary": "No active awakening session. Begin your daily ritual to unlock today's challenges.",
            "quest_summary": "Quests will be generated based on your chosen readiness level.",
            "readiness_impact": "Choose your readiness level wisely - it affects quest difficulty and XP rewards.",
            "motivation_message": "The shadow realm awaits. Are you ready to awaken your true potential?"
        }
    
    async def get_system_health(self) -> Dict:
        """Get mock system health status"""
        return {
            "status": "healthy",
            "uptime": "100%",
            "active_sessions": len(MockAwakeningService._sessions),
            "total_quests": sum(len(q) for q in MockAwakeningService._quests.values()),
            "environment": "development",
            "timestamp": datetime.now().isoformat()
        }