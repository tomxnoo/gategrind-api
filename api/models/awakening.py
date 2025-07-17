from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

class ReadinessLevel(str, Enum):
    """Energy/readiness level for awakening"""
    LOW = "low"           # Low energy - easier quests, recovery focus
    STANDARD = "standard" # Normal energy - balanced quests
    HIGH = "high"         # High energy - challenging quests, intensity focus

class AwakeningStatus(str, Enum):
    """Daily awakening status"""
    PENDING = "pending"       # Not awakened today
    AWAKENED = "awakened"     # Awakened, quests generated
    COMPLETED = "completed"   # All daily quests completed

class AwakeningBase(BaseModel):
    """Base awakening model"""
    readiness_level: ReadinessLevel
    awakening_date: date
    quest_count: int = Field(default=3, ge=1, le=5)  # 1-5 quests per day
    
class AwakeningCreate(AwakeningBase):
    """Awakening creation model"""
    user_id: int

class Awakening(AwakeningBase):
    """Complete awakening model"""
    id: int
    user_id: int
    status: AwakeningStatus = AwakeningStatus.PENDING
    generated_quests: List[int] = Field(default_factory=list)  # Quest IDs
    completed_quests: List[int] = Field(default_factory=list)  # Completed quest IDs
    total_xp_gained: int = 0
    awakened_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True

class AwakeningResponse(BaseModel):
    """Awakening response with quest details"""
    awakening: Awakening
    quests: List[Dict[str, Any]]
    readiness_effects: Dict[str, Any]
    daily_briefing: Dict[str, Any]

class ReadinessEffects(BaseModel):
    """Effects of readiness level on quest generation"""
    difficulty_modifier: float = Field(ge=0.5, le=2.0)  # 0.5x to 2.0x difficulty
    xp_modifier: float = Field(ge=0.8, le=1.5)          # 0.8x to 1.5x XP
    quest_themes: List[str]                              # Preferred quest themes
    movement_preferences: Dict[str, float]               # Movement type weights
    description: str                                     # Human-readable description

class DailyBriefing(BaseModel):
    """Post-awakening daily status briefing"""
    awakening_summary: str
    quest_overview: List[str]
    readiness_impact: str
    motivation_message: str
    progress_highlights: Dict[str, Any]