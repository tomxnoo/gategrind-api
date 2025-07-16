from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class QuestTier(int, Enum):
    """Quest tier enumeration"""
    PRACTICE = 1  # Volume/Practice (Common)
    TECHNIQUE = 2  # Technique/Endurance (Uncommon)
    INTENSITY = 3  # Intensity/Hypertrophy (Rare)

class QuestStatus(str, Enum):
    """Quest status enumeration"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"

class QuestProgress(BaseModel):
    """Quest progress tracking"""
    movement: str
    current_sets: int = 0
    target_sets: int
    current_reps: int = 0
    target_reps: int
    completed: bool = False

class QuestBase(BaseModel):
    """Base quest model"""
    title: str
    description: str
    tier: QuestTier
    xp_reward: int
    movements: List[str]
    target: Dict[str, Any]

class QuestCreate(QuestBase):
    """Quest creation model"""
    user_id: int
    expires_at: Optional[datetime] = None

class Quest(QuestBase):
    """Complete quest model"""
    id: int
    user_id: int
    status: QuestStatus = QuestStatus.AVAILABLE
    progress: Dict[str, QuestProgress] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class QuestCompletion(BaseModel):
    """Quest completion model"""
    quest_id: int
    completed_at: datetime
    xp_gained: int
    bonus_rewards: Optional[Dict[str, Any]] = None

class DailyQuestSummary(BaseModel):
    """Daily quest summary"""
    date: datetime
    total_quests: int
    completed_quests: int
    total_xp_gained: int
    completion_rate: float