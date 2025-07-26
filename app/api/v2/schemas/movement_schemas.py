"""
Pydantic schemas for Movement and MovementCategory models for V2.
These are simple data containers aligned with our SQLAlchemy models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

# Enum for stat types, can be moved to a shared /enums file later
class StatType(str, Enum):
    STR = "STR"
    END = "END"
    TECH = "TECH"

# Schemas for MovementCategory
class MovementCategoryBase(BaseModel):
    """Base schema for MovementCategory"""
    id: str = Field(description="Category identifier (e.g., 'PULL_VERTICAL')")
    name: str = Field(description="Human-readable category name")
    primary_stat: StatType = Field(description="Primary stat for this category")

class MovementCategoryResponse(MovementCategoryBase):
    """Schema for MovementCategory API responses"""
    model_config = ConfigDict(from_attributes=True)

# Schemas for Movement
class MovementBase(BaseModel):
    """Base schema for Movement"""
    name: str = Field(description="Movement name")
    xp_per_rep: float = Field(description="XP earned per repetition")
    stat_reward_type: StatType = Field(description="Stat type rewarded by this movement")

class MovementCreate(MovementBase):
    """Schema for creating a new Movement"""
    node_id: int = Field(description="The ID of the SkillTreeNode it belongs to")

class MovementUpdate(BaseModel):
    """Schema for updating a Movement (all fields optional)"""
    name: Optional[str] = Field(None, description="Movement name")
    xp_per_rep: Optional[float] = Field(None, description="XP earned per repetition")
    stat_reward_type: Optional[StatType] = Field(None, description="Stat type rewarded")

class MovementResponse(MovementBase):
    """Schema for Movement API responses"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    node_id: int