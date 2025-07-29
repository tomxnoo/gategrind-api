from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class BuffType(str, Enum):
    """Buff type enumeration"""
    TEMPORARY = "temporary"
    CONSUMABLE = "consumable"
    PERMANENT = "permanent"

class BuffRarity(str, Enum):
    """Buff rarity enumeration"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class BuffBase(BaseModel):
    """Base buff model"""
    name: str
    description: str
    buff_type: BuffType
    rarity: BuffRarity
    effects: Dict[str, Any]
    duration_minutes: Optional[int] = None

class BuffCreate(BuffBase):
    """Buff creation model"""
    user_id: int

class Buff(BuffBase):
    """Complete buff model"""
    id: int
    user_id: int
    active: bool = True
    stacks: int = 1
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ActiveBuff(BaseModel):
    """Active buff summary"""
    buff_id: int
    name: str
    description: str
    effects: Dict[str, Any]
    stacks: int
    expires_at: Optional[datetime] = None
    time_remaining: Optional[int] = None  # minutes

class BuffInventory(BaseModel):
    """User's buff inventory"""
    consumable_buffs: List[Buff]
    active_buffs: List[ActiveBuff]
    total_active_effects: Dict[str, float]

class BuffData(BaseModel):
    """Buff data model for API responses"""
    id: int
    name: str
    description: str
    buff_type: BuffType
    rarity: BuffRarity
    effects: Dict[str, Any]
    duration_minutes: Optional[int] = None
    active: bool = True
    stacks: int = 1
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class BuffResponse(BaseModel):
    """Buff response model for API endpoints"""
    success: bool
    message: str
    data: Optional[BuffData] = None
    error: Optional[str] = None