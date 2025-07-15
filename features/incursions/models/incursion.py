from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class IncursionType(Enum):
    SURGE = "surge"
    CHALLENGE = "challenge" 
    ANOMALY = "anomaly"

class RewardType(Enum):
    XP = "xp"
    BUFF = "buff"
    ITEM = "item"

@dataclass
class Incursion:
    """Core data model for Shadow Incursions"""
    id: int
    incursion_id: str
    incursion_type: IncursionType
    title: str
    description: str
    target_exercise: str
    target_reps: int
    current_reps: int
    reward_type: RewardType
    reward_value: int
    reward_description: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    metadata: Dict[str, Any]
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.target_reps == 0:
            return 0.0
        return min(100.0, (self.current_reps / self.target_reps) * 100)
    
    @property
    def is_completed(self) -> bool:
        """Check if incursion is completed"""
        return self.current_reps >= self.target_reps
    
    @property
    def is_expired(self) -> bool:
        """Check if incursion has expired"""
        return datetime.now() > self.expires_at
    
    @property
    def time_remaining(self) -> Optional[str]:
        """Get human-readable time remaining"""
        if self.is_expired:
            return None
        
        delta = self.expires_at - datetime.now()
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        else:
            return f"{int(minutes)}m"