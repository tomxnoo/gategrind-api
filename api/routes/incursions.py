from fastapi import APIRouter, Depends, HTTPException
from typing import List
import os
from api.dependencies import get_current_user
from api.models.incursion import (
    Incursion, IncursionCreate, IncursionContribution, 
    IncursionLeaderboard, IncursionSummary, IncursionListResponse
)

router = APIRouter()

# Development mode check
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"

@router.get("/active", response_model=IncursionListResponse)
async def get_active_incursions(current_user: dict = Depends(get_current_user)):
    """Get all active incursions"""
    if DEVELOPMENT_MODE:
        # Mock data for development
        return {
            "incursions": [],
            "total": 0
        }
    
    # Production logic would integrate with IncursionManager
    from features.incursions.logic.incursion_manager import IncursionManager
    
    # Get bot instance (this would need to be passed properly in production)
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    incursions = await manager.get_active_incursions()
    
    return {
        "incursions": [
            {
                "incursion_id": inc.incursion_id,
                "title": inc.title,
                "description": inc.description,
                "incursion_type": inc.incursion_type,
                "status": "active" if inc.is_active else "completed",
                "target_exercise": inc.target_exercise,
                "target_reps": inc.target_reps,
                "current_reps": inc.current_reps,
                "reward_type": inc.reward_type,
                "reward_value": inc.reward_value,
                "reward_description": inc.reward_description,
                "created_at": inc.created_at,
                "expires_at": inc.expires_at,
                "progress_percentage": inc.progress_percentage,
                "is_completed": inc.is_completed,
                "is_expired": inc.is_expired,
                "time_remaining": inc.time_remaining
            }
            for inc in incursions
        ],
        "total": len(incursions)
    }

@router.get("/{incursion_id}", response_model=Incursion)
async def get_incursion(incursion_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific incursion by ID"""
    if DEVELOPMENT_MODE:
        # Mock data for development
        raise HTTPException(status_code=404, detail="Incursion not found")
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    incursion = await manager.get_incursion_by_id(incursion_id)
    
    if not incursion:
        raise HTTPException(status_code=404, detail="Incursion not found")
    
    return {
        "incursion_id": incursion.incursion_id,
        "title": incursion.title,
        "description": incursion.description,
        "incursion_type": incursion.incursion_type,
        "status": "active" if incursion.is_active else "completed",
        "target_exercise": incursion.target_exercise,
        "target_reps": incursion.target_reps,
        "current_reps": incursion.current_reps,
        "reward_type": incursion.reward_type,
        "reward_value": incursion.reward_value,
        "reward_description": incursion.reward_description,
        "created_at": incursion.created_at,
        "expires_at": incursion.expires_at,
        "progress_percentage": incursion.progress_percentage,
        "is_completed": incursion.is_completed,
        "is_expired": incursion.is_expired,
        "time_remaining": incursion.time_remaining
    }

@router.post("/{incursion_id}/contribute")
async def contribute_to_incursion(
    incursion_id: str, 
    contribution: IncursionContribution,
    current_user: dict = Depends(get_current_user)
):
    """Contribute reps to an incursion"""
    if DEVELOPMENT_MODE:
        return {"message": "Contribution recorded (development mode)", "new_total": 50}
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    result = await manager.contribute_reps(incursion_id, current_user["discord_id"], contribution.reps)
    
    return {"message": "Contribution recorded", "new_total": result}

@router.get("/{incursion_id}/leaderboard", response_model=IncursionLeaderboard)
async def get_incursion_leaderboard(incursion_id: str, current_user: dict = Depends(get_current_user)):
    """Get incursion leaderboard"""
    if DEVELOPMENT_MODE:
        return {
            "incursion_id": incursion_id,
            "participants": [],
            "total_participants": 0
        }
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    leaderboard = await manager.get_incursion_leaderboard(incursion_id)
    
    return {
        "incursion_id": incursion_id,
        "participants": [
            {
                "discord_id": str(entry["discord_id"]),
                "username": entry["username"],
                "contribution": entry["contribution"],
                "rank": entry["rank"]
            }
            for entry in leaderboard
        ],
        "total_participants": len(leaderboard)
    }

@router.post("/", response_model=Incursion)
async def create_incursion(incursion_data: IncursionCreate, current_user: dict = Depends(get_current_user)):
    """Create a new incursion (admin only)"""
    if DEVELOPMENT_MODE:
        # Mock response for development
        from datetime import datetime, timedelta
        return {
            "incursion_id": "test_incursion_001",
            "title": incursion_data.title,
            "description": incursion_data.description,
            "incursion_type": incursion_data.incursion_type,
            "status": "active",
            "target_exercise": incursion_data.target_exercise,
            "target_reps": incursion_data.target_reps,
            "current_reps": 0,
            "reward_type": incursion_data.reward_type,
            "reward_value": incursion_data.reward_value,
            "reward_description": incursion_data.reward_description,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=2),
            "progress_percentage": 0.0,
            "is_completed": False,
            "is_expired": False,
            "time_remaining": "2:00:00"
        }
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    incursion = await manager.create_incursion(
        incursion_type=incursion_data.incursion_type,
        title=incursion_data.title,
        description=incursion_data.description,
        target_exercise=incursion_data.target_exercise,
        target_reps=incursion_data.target_reps,
        reward_type=incursion_data.reward_type,
        reward_value=incursion_data.reward_value,
        reward_description=incursion_data.reward_description,
        duration_hours=incursion_data.duration_hours
    )
    
    return {
        "incursion_id": incursion.incursion_id,
        "title": incursion.title,
        "description": incursion.description,
        "incursion_type": incursion.incursion_type,
        "status": "active" if incursion.is_active else "completed",
        "target_exercise": incursion.target_exercise,
        "target_reps": incursion.target_reps,
        "current_reps": incursion.current_reps,
        "reward_type": incursion.reward_type,
        "reward_value": incursion.reward_value,
        "reward_description": incursion.reward_description,
        "created_at": incursion.created_at,
        "expires_at": incursion.expires_at,
        "progress_percentage": incursion.progress_percentage,
        "is_completed": incursion.is_completed,
        "is_expired": incursion.is_expired,
        "time_remaining": incursion.time_remaining
    }

@router.post("/{incursion_id}/complete")
async def complete_incursion(incursion_id: str, current_user: dict = Depends(get_current_user)):
    """Complete an incursion (admin only)"""
    if DEVELOPMENT_MODE:
        return {"message": "Incursion completed (development mode)"}
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    await manager.complete_incursion(incursion_id)
    
    return {"message": "Incursion completed successfully"}

@router.post("/cleanup")
async def cleanup_expired_incursions(current_user: dict = Depends(get_current_user)):
    """Clean up expired incursions (admin only)"""
    if DEVELOPMENT_MODE:
        return {"message": "Cleanup completed (development mode)", "cleaned_count": 0}
    
    from features.incursions.logic.incursion_manager import IncursionManager
    
    manager = IncursionManager(None)  # TODO: Pass proper bot instance
    count = await manager.cleanup_expired_incursions()
    
    return {"message": f"Cleanup completed", "cleaned_count": count}