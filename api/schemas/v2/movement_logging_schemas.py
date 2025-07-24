"""
API schemas for movement logging endpoints.

These schemas define the request and response models for the movement logging API,
including validation rules and documentation.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LogMovementRequest(BaseModel):
    """
    Request model for logging movement reps.
    
    This model validates the input for the POST /v2/events/log-movement endpoint.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movement_id": 1,
                "reps": 10,
                "session_id": "workout_session_123"
            }
        }
    )
    
    movement_id: int = Field(
        ..., 
        gt=0, 
        description="ID of the movement being logged (must be positive)"
    )
    
    reps: int = Field(
        ..., 
        gt=0, 
        le=10000,  # Reasonable upper limit
        description="Number of repetitions performed (1-10000)"
    )
    
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional session tracking ID for analytics"
    )
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        """Validate session_id format if provided."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class MovementInfo(BaseModel):
    """Movement information in the response."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Push-ups"
            }
        }
    )
    
    id: int = Field(..., description="Movement ID")
    name: str = Field(..., description="Movement name")


class LevelUpInfo(BaseModel):
    """Information about a level-up that occurred."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "strength",
                "new_level": 5,
                "points_earned": 2
            }
        }
    )
    
    type: str = Field(..., description="Type of level-up (global, strength, endurance, technique)")
    new_level: int = Field(..., description="New level achieved")
    points_earned: int = Field(..., description="Stat points earned from level-up")


class AuraUpdateInfo(BaseModel):
    """Information about aura changes."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "previous_aura": 1250,
                "new_aura": 1275,
                "change": 25,
                "reason": "Strength progression"
            }
        }
    )
    
    previous_aura: int = Field(..., description="Previous aura value")
    new_aura: int = Field(..., description="New aura value")
    change: int = Field(..., description="Aura change amount")
    reason: str = Field(..., description="Reason for aura change")


class LogMovementResponse(BaseModel):
    """
    Response model for successful movement logging.
    
    Contains all information about what happened during the movement log,
    including XP earned, level-ups, and aura changes.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movement": {
                    "id": 1,
                    "name": "Push-ups"
                },
                "reps_logged": 10,
                "xp_earned": {
                    "global": 50,
                    "strength": 37
                },
                "level_ups": [
                    {
                        "type": "strength",
                        "new_level": 5,
                        "points_earned": 2
                    }
                ],
                "aura_update": {
                    "previous_aura": 1250,
                    "new_aura": 1275,
                    "change": 25,
                    "reason": "Strength progression"
                },
                "session_id": "workout_session_123"
            }
        }
    )
    
    movement: MovementInfo = Field(..., description="Information about the logged movement")
    
    reps_logged: int = Field(..., description="Number of reps that were logged")
    
    xp_earned: Dict[str, int] = Field(
        ..., 
        description="XP earned by category (global, strength, endurance, technique)"
    )
    
    level_ups: List[LevelUpInfo] = Field(
        default_factory=list,
        description="List of level-ups that occurred"
    )
    
    aura_update: Optional[AuraUpdateInfo] = Field(
        None,
        description="Aura update information if aura changed"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Session ID if provided in request"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Movement not found",
                "detail": "Movement with ID 999 does not exist"
            }
        }
    )
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")