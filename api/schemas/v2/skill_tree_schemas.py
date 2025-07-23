"""
Pydantic schemas for SkillTreeNode and UserSkillProgress models for V2.
These are simple data containers aligned with our SQLAlchemy models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Schemas for SkillTreeNode
class SkillTreeNodeBase(BaseModel):
    """Base schema for SkillTreeNode"""
    category_id: str = Field(description="Foreign key to MovementCategory")
    level: int = Field(description="Progression level within the category (1-5)")
    name: str = Field(description="Display name for this progression level")
    description: Optional[str] = Field(None, description="Detailed description of this progression level")
    required_ascendant_level: int = Field(default=1, description="Minimum Ascendant level required to unlock")
    required_str_points: int = Field(default=0, description="Strength points cost to unlock this node")
    required_end_points: int = Field(default=0, description="Endurance points cost to unlock this node")
    required_tech_points: int = Field(default=0, description="Technique points cost to unlock this node")

class SkillTreeNodeCreate(SkillTreeNodeBase):
    """Schema for creating a new SkillTreeNode"""
    pass

class SkillTreeNodeUpdate(BaseModel):
    """Schema for updating a SkillTreeNode (all fields optional)"""
    category_id: Optional[str] = Field(None, description="Foreign key to MovementCategory")
    level: Optional[int] = Field(None, description="Progression level within the category (1-5)")
    name: Optional[str] = Field(None, description="Display name for this progression level")
    description: Optional[str] = Field(None, description="Detailed description of this progression level")
    required_ascendant_level: Optional[int] = Field(None, description="Minimum Ascendant level required to unlock")
    required_str_points: Optional[int] = Field(None, description="Strength points cost to unlock this node")
    required_end_points: Optional[int] = Field(None, description="Endurance points cost to unlock this node")
    required_tech_points: Optional[int] = Field(None, description="Technique points cost to unlock this node")

class SkillTreeNodeResponse(SkillTreeNodeBase):
    """Schema for SkillTreeNode API responses"""
    model_config = ConfigDict(from_attributes=True)
    id: int

# Schemas for UserSkillProgress
class UserSkillProgressBase(BaseModel):
    """Base schema for UserSkillProgress"""
    ascendant_id: int = Field(description="Foreign key to Ascendant who unlocked the node")
    node_id: int = Field(description="Foreign key to the SkillTreeNode that was unlocked")
    unlocked_at: datetime = Field(description="Timestamp when the node was unlocked")

class UserSkillProgressCreate(BaseModel):
    """Schema for creating a new UserSkillProgress"""
    ascendant_id: int = Field(description="Foreign key to Ascendant who unlocked the node")
    node_id: int = Field(description="Foreign key to the SkillTreeNode that was unlocked")

class UserSkillProgressResponse(UserSkillProgressBase):
    """Schema for UserSkillProgress API responses"""
    model_config = ConfigDict(from_attributes=True)
    id: int