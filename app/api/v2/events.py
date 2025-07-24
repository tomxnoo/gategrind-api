"""
Events API endpoints for logging user activities.

This module contains endpoints for logging various user events,
starting with movement logging functionality.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_async_session
from app.application.services.movement_logging_service import MovementLoggingService
from api.schemas.v2.movement_logging_schemas import (
    LogMovementRequest,
    LogMovementResponse,
    ErrorResponse
)
from api.dependencies.auth import get_current_user_id


logger = logging.getLogger(__name__)
router = APIRouter(tags=["events"])


@router.post(
    "/log-movement",
    response_model=LogMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log movement reps and calculate XP",
    description="""
    Log completed exercise reps and receive XP rewards.
    
    This endpoint:
    - Validates the movement exists
    - Calculates XP based on movement type and reps
    - Updates user progression (levels, stats, aura)
    - Returns detailed progression information
    
    Enhanced from V1 with:
    - Better validation and error handling
    - Real-time aura updates
    - Improved XP calculation logic
    - Session tracking support
    """,
    responses={
        201: {
            "description": "Movement logged successfully",
            "model": LogMovementResponse
        },
        400: {
            "description": "Invalid request data",
            "model": ErrorResponse
        },
        404: {
            "description": "Movement not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def log_movement(
    request: LogMovementRequest,
    user_id: int = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_async_session)
) -> LogMovementResponse:
    """
    Log movement reps and calculate XP rewards.
    
    Args:
        request: Movement logging request data
        user_id: Current user ID from authentication
        db_session: Database session
        
    Returns:
        LogMovementResponse: Complete movement logging results
        
    Raises:
        HTTPException: If movement not found or validation fails
    """
    try:
        # Initialize movement logging service
        movement_service = MovementLoggingService(session=db_session)
        
        # Log the movement and get results
        result = await movement_service.log_movement(
            user_id=user_id,
            movement_id=request.movement_id,
            reps=request.reps,
            session_id=request.session_id
        )
        
        # Convert result to response format
        response_data = result.to_dict()
        
        # Log successful operation
        logger.info(
            f"Movement logged successfully: user_id={user_id}, "
            f"movement_id={request.movement_id}, reps={request.reps}, "
            f"xp_earned={response_data['xp_earned']}"
        )
        
        return LogMovementResponse(**response_data)
        
    except ValueError as e:
        # Handle validation errors
        logger.warning(f"Validation error in log_movement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid request data", "detail": str(e)}
        )
        
    except Exception as e:
        # Handle movement not found and other errors
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            logger.warning(f"Movement not found: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Movement not found", "detail": error_msg}
            )
        
        # Handle unexpected errors
        logger.error(f"Unexpected error in log_movement: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "detail": "An unexpected error occurred"}
        )


@router.get(
    "/health",
    summary="Health check for events service",
    description="Check the health status of the events service and its dependencies.",
    response_model=Dict[str, Any]
)
async def health_check(
    db_session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Perform a health check for the events service.
    
    Args:
        db_session: Database session
        
    Returns:
        Dict[str, Any]: Health check results
    """
    try:
        # Initialize movement logging service for health check
        movement_service = MovementLoggingService(session=db_session)
        health_result = await movement_service.health_check()
        
        # Add timestamp
        from datetime import datetime, UTC
        health_result["timestamp"] = datetime.now(UTC).isoformat()
        
        return health_result
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return {
            "service": "EventsService",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }