from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class IncursionType(str, Enum):
    """Incursion type enumeration"""
    SURGE = "surge"        # System-wide buffs
    CHALLENGE = "challenge"  # Specific tasks
    ANOMALY = "anomaly"    # Rule-changing modifiers

class RewardType(str, Enum):
    """Reward type enumeration"""
    XP = "xp"
    BUFF = "buff"
    ITEM = "item"

class IncursionStatus(str, Enum):
    """Incursion status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class IncursionBase(BaseModel):
    """Base incursion model"""
    incursion_id: str
    title: str
    description: str
    incursion_type: IncursionType
    target_exercise: str
    target_reps: int
    reward_type: RewardType
    reward_value: int
    reward_description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IncursionCreate(BaseModel):
    """Incursion creation model"""
    title: str
    description: str
    incursion_type: IncursionType
    target_exercise: str
    target_reps: int
    reward_type: RewardType
    reward_value: int
    reward_description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    duration_hours: float = 24.0

class Incursion(IncursionBase):
    """Complete incursion model"""
    id: int
    current_reps: int = 0
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)

class IncursionContribution(BaseModel):
    """Model for contributing reps to an incursion"""
    incursion_id: str
    reps: int

class IncursionParticipation(BaseModel):
    """Incursion participation model"""
    incursion_id: str
    user_id: int
    reps_contributed: int
    participated_at: datetime

class IncursionLeaderboard(BaseModel):
    """Incursion leaderboard entry"""
    username: str
    total_reps: int
    sessions: int

class IncursionSummary(BaseModel):
    """Incursion summary for lists"""
    id: int
    incursion_id: str
    title: str
    incursion_type: IncursionType
    target_exercise: str
    current_reps: int
    target_reps: int
    progress_percentage: float
    participants_count: int
    time_remaining: Optional[int] = None  # minutes
    expires_at: datetime
    is_active: bool
    reward_description: str

class IncursionListResponse(BaseModel):
    """Response model for listing incursion summaries"""
    incursions: List[IncursionSummary]
    total_count: int

class IncursionFullListResponse(BaseModel):
    """Response model for listing full incursion objects"""
    active_incursions: List[Incursion]
    total_count: int