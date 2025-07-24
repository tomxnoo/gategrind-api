from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class UserStats(BaseModel):
    """User statistics model"""
    STR: Dict[str, Any] = Field(default_factory=lambda: {"level": 1, "xp": 0, "xp_max": 100})
    END: Dict[str, Any] = Field(default_factory=lambda: {"level": 1, "xp": 0, "xp_max": 100})
    TECH: Dict[str, Any] = Field(default_factory=lambda: {"level": 1, "xp": 0, "xp_max": 100})

class UserBase(BaseModel):
    """Base user model"""
    username: str
    level: int = 1
    xp: int = 0
    xp_max: int = 100

class UserCreate(UserBase):
    """User creation model"""
    user_id: int
    discord_id: str

class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    xp: Optional[int] = None
    level: Optional[int] = None
    stats: Optional[UserStats] = None

class UserProfile(UserBase):
    """Complete user profile model"""
    user_id: int
    discord_id: str
    stats: UserStats
    active_buffs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserSummary(BaseModel):
    """Simplified user model for lists"""
    user_id: int
    username: str
    level: int
    discord_id: str