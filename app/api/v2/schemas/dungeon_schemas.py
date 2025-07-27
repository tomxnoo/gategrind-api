"""
Pydantic schemas for DungeonKey and DungeonProgress models for V2.
These are simple data containers aligned with our SQLAlchemy models.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime


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


# Dungeon Entry and Trial Schemas
class DungeonEntryRequest(BaseModel):
    """Schema for dungeon entry requests"""
    ascendant_id: int = Field(..., gt=0, description="The ascendant entering the dungeon")
    dungeon_level: int = Field(..., ge=1, description="The dungeon level to enter (infinite progression)")
    
    @field_validator('dungeon_level')
    @classmethod
    def validate_dungeon_level(cls, v):
        if v < 1:
            raise ValueError('Dungeon level must be at least 1')
        return v


class TrialCompletionRequest(BaseModel):
    """Schema for trial completion requests"""
    trial_id: int = Field(..., gt=0, description="The trial being completed")
    progress_data: Dict[str, Any] = Field(..., description="Movement progress data")
    
    @field_validator('progress_data')
    @classmethod
    def validate_progress_data(cls, v):
        required_fields = ['reps', 'duration', 'sets', 'distance']
        if not any(field in v for field in required_fields):
            raise ValueError('Progress data must contain at least one progress field')
        return v


class TrialData(BaseModel):
    """Schema for trial data in dungeon responses"""
    id: int = Field(..., description="Trial identifier")
    movement_id: int = Field(..., description="Movement associated with this trial")
    movement_name: str = Field(..., description="Name of the movement")
    target_type: str = Field(..., description="Type of target (reps, duration, etc.)")
    target_value: int = Field(..., description="Target value to achieve")
    current_progress: int = Field(default=0, description="Current progress towards target")
    is_completed: bool = Field(default=False, description="Whether the trial is completed")
    difficulty_multiplier: float = Field(..., description="Difficulty multiplier for this trial")


class DungeonEntryResponse(BaseModel):
    """Schema for dungeon entry responses"""
    success: bool = Field(..., description="Whether the entry was successful")
    message: str = Field(..., description="Response message")
    session_id: int = Field(..., description="The created dungeon session ID")
    dungeon_level: int = Field(..., description="The dungeon level entered")
    shadow_keys_spent: int = Field(..., description="Number of shadow keys spent")
    trials: List[TrialData] = Field(..., description="List of trials for this session")
    daily_modifier: Optional[Dict[str, Any]] = Field(None, description="Active daily modifier")
    expires_at: datetime = Field(..., description="When the session expires")


class TrialCompletionResponse(BaseModel):
    """Schema for trial completion responses"""
    success: bool = Field(..., description="Whether the completion was successful")
    message: str = Field(..., description="Response message")
    trial_completed: bool = Field(..., description="Whether the trial was completed")
    session_completed: bool = Field(..., description="Whether the entire session was completed")
    rewards_earned: List[Dict[str, Any]] = Field(..., description="Rewards earned from completion")
    next_trial_available: bool = Field(..., description="Whether another trial is available")