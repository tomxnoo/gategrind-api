"""
V2 Incursions API - Modern FastAPI endpoints for incursion management

This module provides:
- RESTful API endpoints for incursion operations
- Integration with the new IncursionService
- Proper error handling and validation
- Scheduler management endpoints
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.application.services.incursion_service import IncursionService
from app.application.services.incursion_scheduler import IncursionScheduler, SpawnCooldownConfig
from app.infrastructure.database.models.v2.incursions import (
    IncursionType, RewardType, IncursionStatus
)


# Pydantic models for API requests/responses
class IncursionCreateRequest(BaseModel):
    """Request model for creating an incursion."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    incursion_type: IncursionType
    target_exercise: str = Field(..., min_length=1, max_length=100)
    target_reps: int = Field(..., gt=0)
    reward_type: RewardType
    reward_value: int = Field(..., gt=0)
    reward_description: str = Field(..., min_length=1, max_length=200)
    duration_hours: float = Field(default=24.0, gt=0, le=168)  # Max 1 week
    metadata: Optional[Dict[str, Any]] = None


class IncursionResponse(BaseModel):
    """Response model for incursion data."""
    id: int
    incursion_id: str
    title: str
    description: str
    incursion_type: IncursionType
    target_exercise: str
    target_reps: int
    current_reps: int
    reward_type: RewardType
    reward_value: int
    reward_description: str
    status: IncursionStatus
    is_active: bool
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    progress_percentage: float
    is_completed: bool
    participant_count: int
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class ParticipantContributionRequest(BaseModel):
    """Request model for adding participant contribution."""
    user_id: int = Field(..., gt=0)
    reps: int = Field(..., gt=0)


class ParticipantContributionResponse(BaseModel):
    """Response model for contribution result."""
    success: bool
    message: str
    incursion_completed: bool = False


class IncursionStatsResponse(BaseModel):
    """Response model for incursion statistics."""
    status_counts: Dict[str, int]
    type_counts: Dict[str, int]
    total_participants: int
    timestamp: str


class SchedulerStatusResponse(BaseModel):
    """Response model for scheduler status."""
    is_running: bool
    last_spawn_time: Optional[str]
    global_cooldown_remaining: Optional[int]
    type_cooldowns: Dict[str, Dict[str, Any]]
    config: Dict[str, Any]


class ForceSpawnRequest(BaseModel):
    """Request model for force spawning an incursion."""
    incursion_type: Optional[IncursionType] = None


# Router setup
router = APIRouter(prefix="/api/v2/incursions", tags=["incursions"])

# Global scheduler instance (will be initialized by the application)
_scheduler: Optional[IncursionScheduler] = None


def get_incursion_service() -> IncursionService:
    """Dependency to get IncursionService instance."""
    return IncursionService()


def get_scheduler() -> IncursionScheduler:
    """Dependency to get IncursionScheduler instance."""
    if _scheduler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Incursion scheduler not initialized"
        )
    return _scheduler


def set_scheduler(scheduler: IncursionScheduler) -> None:
    """Set the global scheduler instance."""
    global _scheduler
    _scheduler = scheduler


# API Endpoints
@router.get("/", response_model=List[IncursionResponse])
async def get_active_incursions(
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Get all currently active incursions.
    
    Returns:
        List[IncursionResponse]: List of active incursions
    """
    try:
        incursions = await service.get_active_incursions()
        
        # Convert to response models
        response_data = []
        for incursion in incursions:
            response_data.append(IncursionResponse(
                id=incursion.id,
                incursion_id=incursion.incursion_id,
                title=incursion.title,
                description=incursion.description,
                incursion_type=incursion.incursion_type,
                target_exercise=incursion.target_exercise,
                target_reps=incursion.target_reps,
                current_reps=incursion.current_reps,
                reward_type=incursion.reward_type,
                reward_value=incursion.reward_value,
                reward_description=incursion.reward_description,
                status=incursion.status,
                is_active=incursion.is_active,
                expires_at=incursion.expires_at,
                created_at=incursion.created_at,
                updated_at=incursion.updated_at,
                progress_percentage=incursion.progress_percentage,
                is_completed=incursion.is_completed,
                participant_count=len(incursion.participants),
                metadata=incursion.metadata
            ))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active incursions: {str(e)}"
        )


@router.get("/{incursion_id}", response_model=IncursionResponse)
async def get_incursion_by_id(
    incursion_id: str,
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Get a specific incursion by ID.
    
    Args:
        incursion_id: The incursion identifier
        
    Returns:
        IncursionResponse: The incursion data
    """
    try:
        incursion = await service.get_incursion_by_id(incursion_id)
        
        if not incursion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incursion {incursion_id} not found"
            )
        
        return IncursionResponse(
            id=incursion.id,
            incursion_id=incursion.incursion_id,
            title=incursion.title,
            description=incursion.description,
            incursion_type=incursion.incursion_type,
            target_exercise=incursion.target_exercise,
            target_reps=incursion.target_reps,
            current_reps=incursion.current_reps,
            reward_type=incursion.reward_type,
            reward_value=incursion.reward_value,
            reward_description=incursion.reward_description,
            status=incursion.status,
            is_active=incursion.is_active,
            expires_at=incursion.expires_at,
            created_at=incursion.created_at,
            updated_at=incursion.updated_at,
            progress_percentage=incursion.progress_percentage,
            is_completed=incursion.is_completed,
            participant_count=len(incursion.participants),
            metadata=incursion.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve incursion: {str(e)}"
        )


@router.post("/", response_model=IncursionResponse, status_code=status.HTTP_201_CREATED)
async def create_incursion(
    request: IncursionCreateRequest,
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Create a new incursion.
    
    Args:
        request: Incursion creation data
        
    Returns:
        IncursionResponse: The created incursion
    """
    try:
        incursion = await service.create_incursion(
            title=request.title,
            description=request.description,
            incursion_type=request.incursion_type,
            target_exercise=request.target_exercise,
            target_reps=request.target_reps,
            reward_type=request.reward_type,
            reward_value=request.reward_value,
            reward_description=request.reward_description,
            duration_hours=request.duration_hours,
            metadata=request.metadata
        )
        
        return IncursionResponse(
            id=incursion.id,
            incursion_id=incursion.incursion_id,
            title=incursion.title,
            description=incursion.description,
            incursion_type=incursion.incursion_type,
            target_exercise=incursion.target_exercise,
            target_reps=incursion.target_reps,
            current_reps=incursion.current_reps,
            reward_type=incursion.reward_type,
            reward_value=incursion.reward_value,
            reward_description=incursion.reward_description,
            status=incursion.status,
            is_active=incursion.is_active,
            expires_at=incursion.expires_at,
            created_at=incursion.created_at,
            updated_at=incursion.updated_at,
            progress_percentage=incursion.progress_percentage,
            is_completed=incursion.is_completed,
            participant_count=0,  # New incursion has no participants
            metadata=incursion.metadata
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incursion: {str(e)}"
        )


@router.post("/{incursion_id}/contribute", response_model=ParticipantContributionResponse)
async def add_contribution(
    incursion_id: str,
    request: ParticipantContributionRequest,
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Add a user's contribution to an incursion.
    
    Args:
        incursion_id: The incursion identifier
        request: Contribution data
        
    Returns:
        ParticipantContributionResponse: Result of the contribution
    """
    try:
        # Get incursion before contribution to check completion status
        incursion_before = await service.get_incursion_by_id(incursion_id)
        if not incursion_before:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incursion {incursion_id} not found"
            )
        
        was_completed = incursion_before.is_completed
        
        # Add contribution
        success = await service.add_participant_contribution(
            incursion_id=incursion_id,
            user_id=request.user_id,
            reps=request.reps
        )
        
        if not success:
            return ParticipantContributionResponse(
                success=False,
                message="Failed to add contribution. Incursion may be inactive or expired."
            )
        
        # Check if incursion was completed by this contribution
        incursion_after = await service.get_incursion_by_id(incursion_id)
        incursion_completed = not was_completed and incursion_after.is_completed
        
        message = f"Successfully contributed {request.reps} reps"
        if incursion_completed:
            message += ". Incursion completed!"
        
        return ParticipantContributionResponse(
            success=True,
            message=message,
            incursion_completed=incursion_completed
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add contribution: {str(e)}"
        )


@router.delete("/{incursion_id}")
async def end_incursion(
    incursion_id: str,
    reason: str = "manual",
    service: IncursionService = Depends(get_incursion_service)
):
    """
    End an incursion manually.
    
    Args:
        incursion_id: The incursion identifier
        reason: Reason for ending the incursion
        
    Returns:
        dict: Success message
    """
    try:
        success = await service.end_incursion(incursion_id, reason)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incursion {incursion_id} not found"
            )
        
        return {"message": f"Incursion {incursion_id} ended successfully", "reason": reason}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end incursion: {str(e)}"
        )


@router.get("/stats/overview", response_model=IncursionStatsResponse)
async def get_incursion_statistics(
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Get incursion statistics and overview.
    
    Returns:
        IncursionStatsResponse: Statistics about incursions
    """
    try:
        stats = await service.get_incursion_statistics()
        return IncursionStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


# Scheduler management endpoints
@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    scheduler: IncursionScheduler = Depends(get_scheduler)
):
    """
    Get the current status of the incursion scheduler.
    
    Returns:
        SchedulerStatusResponse: Scheduler status and cooldown information
    """
    try:
        status = scheduler.get_cooldown_status()
        return SchedulerStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


@router.post("/scheduler/start")
async def start_scheduler(
    scheduler: IncursionScheduler = Depends(get_scheduler)
):
    """
    Start the incursion scheduler.
    
    Returns:
        dict: Success message
    """
    try:
        await scheduler.start()
        return {"message": "Incursion scheduler started successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler(
    scheduler: IncursionScheduler = Depends(get_scheduler)
):
    """
    Stop the incursion scheduler.
    
    Returns:
        dict: Success message
    """
    try:
        await scheduler.stop()
        return {"message": "Incursion scheduler stopped successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop scheduler: {str(e)}"
        )


@router.post("/scheduler/force-spawn")
async def force_spawn_incursion(
    request: ForceSpawnRequest,
    scheduler: IncursionScheduler = Depends(get_scheduler)
):
    """
    Force spawn an incursion, bypassing cooldowns.
    
    Args:
        request: Force spawn parameters
        
    Returns:
        dict: Success message
    """
    try:
        success = await scheduler.force_spawn_incursion(request.incursion_type)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to spawn incursion. Check scheduler status and available templates."
            )
        
        return {"message": "Incursion spawned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force spawn incursion: {str(e)}"
        )


@router.get("/health")
async def health_check(
    service: IncursionService = Depends(get_incursion_service)
):
    """
    Health check endpoint for the incursions API.
    
    Returns:
        dict: Health status
    """
    try:
        health_result = await service.health_check()
        
        if health_result.get("status") == "healthy":
            return health_result
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )