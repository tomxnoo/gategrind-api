"""
Pydantic schemas for Ascendant-related API operations in V2.
These models define the data contracts for our API and are used for
request validation and response serialization. They are simple data
containers with no business logic.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# First, we need a schema for the related stats model
class AscendantStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    str_level: int
    str_xp: float
    end_level: int
    end_xp: float
    tech_level: int
    tech_xp: float

# Base schema with fields common to most Ascendant operations
class AscendantBase(BaseModel):
    username: str = Field(min_length=1, max_length=100)

# Schema for creating a new Ascendant (used by the service layer)
class AscendantCreate(AscendantBase):
    discord_id: str = Field(min_length=1, max_length=20)

# Schema for updating an Ascendant (all fields are optional)
class AscendantUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)

# The main, comprehensive response model for an Ascendant's profile
class AscendantProfile(AscendantBase):
    model_config = ConfigDict(from_attributes=True)
    
    # Core progression fields
    id: int
    discord_id: str
    level: int
    global_xp: int
    aura: int
    
    # Spendable resource points
    strength_points: int
    endurance_points: int
    technique_points: int
    
    # Related data
    stats: AscendantStatsSchema
    
    # Timestamps
    created_at: datetime
    updated_at: datetime