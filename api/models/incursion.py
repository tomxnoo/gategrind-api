from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class IncursionType(str, Enum):
    """Incursion type enumeration"""
    SURGE = "surge"        # System-wide buffs
    CHALLENGE = "challenge"  # Specific tasks
    ANOMALY = "anomaly"    # Rule-changing modifiers

class IncursionStatus(str, Enum):
    """Incursion status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class IncursionBase(BaseModel):
    """Base incursion model"""
    title: str
    description: str
    incursion_type: IncursionType
    objective: Dict[str, Any]
    rewards: Dict[str, Any]
    duration_minutes: int

class IncursionCreate(IncursionBase):
    """Incursion creation model"""
    pass

class Incursion(IncursionBase):
    """Complete incursion model"""
    id: int
    status: IncursionStatus = IncursionStatus.ACTIVE
    participants: List[int] = Field(default_factory=list)
    created_at: datetime
    expires_at: datetime
    message_id: Optional[str] = None  # Discord message ID
    
    class Config:
        from_attributes = True

class IncursionParticipation(BaseModel):
    """Incursion participation model"""
    incursion_id: int
    user_id: int
    progress: Dict[str, Any] = Field(default_factory=dict)
    completed: bool = False
    rewards_claimed: bool = False
    participated_at: datetime

class IncursionSummary(BaseModel):
    """Incursion summary for lists"""
    id: int
    title: str
    incursion_type: IncursionType
    status: IncursionStatus
    participants_count: int
    time_remaining: Optional[int] = None  # minutes
    expires_at: datetime