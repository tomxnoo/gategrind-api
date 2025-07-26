"""
Pydantic schemas for DungeonKey and DungeonProgress models for V2.
These are simple data containers aligned with our SQLAlchemy models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# DungeonKey Schemas
class DungeonKeyBase(BaseModel):
    """Base schema for DungeonKey with common fields"""
    ascendant_id: int = Field(..., description="The user who owns these keys")
    key_type: str = Field(default="shadow_key", max_length=50, description="The type of key")
    quantity: int = Field(default=0, ge=0, description="How many keys of this type the user has")


class DungeonKeyCreate(DungeonKeyBase):
    """Schema for creating a new DungeonKey"""
    pass


class DungeonKeyUpdate(BaseModel):
    """Schema for updating a DungeonKey"""
    key_type: Optional[str] = Field(None, max_length=50, description="The type of key")
    quantity: Optional[int] = Field(None, ge=0, description="How many keys of this type the user has")


class DungeonKeyResponse(DungeonKeyBase):
    """Schema for DungeonKey responses"""
    id: int = Field(..., description="Unique identifier for the dungeon key record")
    
    model_config = ConfigDict(from_attributes=True)


# DungeonProgress Schemas
class DungeonProgressBase(BaseModel):
    """Base schema for DungeonProgress with common fields"""
    ascendant_id: int = Field(..., description="The user whose progress is being tracked")
    highest_level_completed: int = Field(default=0, ge=0, description="The highest dungeon level completed")


class DungeonProgressCreate(DungeonProgressBase):
    """Schema for creating a new DungeonProgress"""
    pass


class DungeonProgressUpdate(BaseModel):
    """Schema for updating DungeonProgress"""
    highest_level_completed: Optional[int] = Field(None, ge=0, description="The highest dungeon level completed")


class DungeonProgressResponse(DungeonProgressBase):
    """Schema for DungeonProgress responses"""
    id: int = Field(..., description="Unique identifier for the dungeon progress record")
    
    model_config = ConfigDict(from_attributes=True)