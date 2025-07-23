"""
Pydantic schemas for Quest and QuestCompletion models for V2.
These are simple data containers aligned with our SQLAlchemy models.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Schemas for Quest
class QuestBase(BaseModel):
    """Base schema for Quest"""
    title: str
    description: Optional[str] = None
    source: str
    status: str


class QuestCreate(QuestBase):
    """Schema for creating a new Quest"""
    ascendant_id: int


class QuestUpdate(BaseModel):
    """Schema for updating a Quest's status"""
    status: Optional[str] = None


class QuestResponse(QuestBase):
    """Schema for Quest API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ascendant_id: int
    created_at: datetime
    updated_at: datetime


# Schemas for QuestCompletion
class QuestCompletionBase(BaseModel):
    """Base schema for QuestCompletion"""
    ascendant_id: int
    quest_id: int


class QuestCompletionCreate(QuestCompletionBase):
    """Schema for creating a new QuestCompletion"""
    pass


class QuestCompletionResponse(QuestCompletionBase):
    """Schema for QuestCompletion API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime  # This serves as the completion timestamp