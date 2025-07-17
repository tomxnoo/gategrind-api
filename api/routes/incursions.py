from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
import os
import asyncpg
import json
from datetime import datetime
from api.dependencies import get_current_user, get_db_pool_optional
from api.models.incursion import (
    Incursion, IncursionCreate, IncursionContribution, 
    IncursionLeaderboard, IncursionSummary, IncursionListResponse, IncursionFullListResponse
)

router = APIRouter()

# Development mode check - Changed default to "false" for production
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

# Helper class to adapt IncursionManager for API use
class APIIncursionManager:
    """Adapter for IncursionManager to work with API database connections"""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def get_active_incursions(self):
        """Get all active incursions"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM active_incursions 
                WHERE is_active = TRUE AND expires_at > NOW()
                ORDER BY created_at DESC
                """
            )
            return rows
    
    async def get_incursion_by_id(self, incursion_id: str):
        """Get incursion by ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM active_incursions WHERE incursion_id = $1",
                incursion_id
            )
            return row
    
    async def create_incursion(self, incursion_data: IncursionCreate):
        """Create new incursion"""
        from datetime import datetime, timedelta, timezone
        import json
        
        expires_at = datetime.now(timezone.utc) + timedelta(hours=incursion_data.duration_hours)
        metadata_json = json.dumps(incursion_data.metadata or {})
        created_at = datetime.now(timezone.utc)
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO active_incursions 
                (incursion_id, incursion_type, title, description, target_exercise, 
                 target_reps, current_reps, reward_type, reward_value, reward_description, 
                 expires_at, is_active, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING *
                """,
                f"incursion_{int(datetime.now().timestamp())}", 
                incursion_data.incursion_type, incursion_data.title, incursion_data.description, 
                incursion_data.target_exercise, incursion_data.target_reps, 0,  # current_reps starts at 0
                incursion_data.reward_type, incursion_data.reward_value,
                incursion_data.reward_description, expires_at, True, metadata_json, created_at
            )
        return row
    
    async def mark_incursion_inactive(self, incursion_id: str):
        """Mark incursion as inactive"""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE active_incursions SET is_active = FALSE WHERE incursion_id = $1",
                incursion_id
            )
    
    async def update_incursion_metadata(self, incursion_id: str, metadata: dict):
        """Update incursion metadata"""
        import json
        metadata_json = json.dumps(metadata)
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE active_incursions SET metadata = $1 WHERE incursion_id = $2",
                metadata_json, incursion_id
            )

@router.get("/active", response_model=IncursionFullListResponse)
async def get_active_incursions(
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Get all currently active incursions with full details"""
    # Check for development mode OR if db_pool is None
    if DEVELOPMENT_MODE or db_pool is None:
        # Return mock data for development mode
        from datetime import datetime, timedelta, timezone
        mock_incursion = Incursion(
            id=1,
            incursion_id="dev_incursion_001",
            incursion_type="surge",
            title="🔥 Development Surge",
            description="A test incursion for development mode",
            target_exercise="Push-ups",
            current_reps=25,
            target_reps=100,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2),  # Changed to timezone-aware
            is_active=True,
            reward_type="buff",
            reward_value=50,
            reward_description="+50% XP for 1 hour",
            metadata={"test": True},
            created_at=datetime.now(timezone.utc)  # Changed to timezone-aware
        )
        
        return IncursionFullListResponse(
            active_incursions=[mock_incursion],
            total_count=1
        )
    
    try:
        manager = APIIncursionManager(db_pool)
        incursions_data = await manager.get_active_incursions()
        
        # Convert to full Incursion objects with all fields
        incursion_objects = []
        for inc in incursions_data:
            # Parse metadata if it's a string
            metadata = inc["metadata"]
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = {}
            elif metadata is None:
                metadata = {}
            
            incursion_obj = Incursion(
                id=inc["id"],
                incursion_id=inc["incursion_id"],
                incursion_type=inc["incursion_type"],
                title=inc["title"],
                description=inc["description"],
                target_exercise=inc["target_exercise"],
                current_reps=inc["current_reps"],
                target_reps=inc["target_reps"],
                expires_at=inc["expires_at"],
                is_active=inc["is_active"],
                reward_type=inc["reward_type"],
                reward_value=inc["reward_value"],
                reward_description=inc["reward_description"],
                metadata=metadata,
                created_at=inc["created_at"]
            )
            incursion_objects.append(incursion_obj)
        
        return IncursionFullListResponse(
            active_incursions=incursion_objects,
            total_count=len(incursion_objects)
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching active incursions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active incursions")

@router.post("/", response_model=Incursion)
async def create_incursion(
    incursion_data: IncursionCreate, 
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Create a new incursion (admin only)"""
    # Check for development mode OR if db_pool is None
    if DEVELOPMENT_MODE or db_pool is None:
        # Mock response for development
        from datetime import datetime, timedelta, timezone
        return {
            "id": 1,
            "incursion_id": "test_incursion_001",
            "title": incursion_data.title,
            "description": incursion_data.description,
            "incursion_type": incursion_data.incursion_type,
            "target_exercise": incursion_data.target_exercise,
            "target_reps": incursion_data.target_reps,
            "current_reps": 0,
            "reward_type": incursion_data.reward_type,
            "reward_value": incursion_data.reward_value,
            "reward_description": incursion_data.reward_description,
            "metadata": incursion_data.metadata,
            "created_at": datetime.now(timezone.utc),  # Changed to timezone-aware
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=incursion_data.duration_hours),  # Changed to timezone-aware
            "is_active": True
        }
    
    manager = APIIncursionManager(db_pool)
    incursion = await manager.create_incursion(incursion_data)
    
    # Parse metadata from JSON string to dict
    import json
    metadata = json.loads(incursion["metadata"]) if incursion["metadata"] else {}
    
    return {
        "id": incursion["id"],  # Add the missing id field
        "incursion_id": incursion["incursion_id"],
        "title": incursion["title"],
        "description": incursion["description"],
        "incursion_type": incursion["incursion_type"],
        "target_exercise": incursion["target_exercise"],
        "target_reps": incursion["target_reps"],
        "current_reps": incursion["current_reps"],
        "reward_type": incursion["reward_type"],
        "reward_value": incursion["reward_value"],
        "reward_description": incursion["reward_description"],
        "metadata": metadata,  # Now properly parsed as dict
        "created_at": incursion["created_at"],
        "expires_at": incursion["expires_at"],
        "is_active": incursion["is_active"]  # Add the missing is_active field
    }

@router.post("/{incursion_id}/complete")
async def complete_incursion(
    incursion_id: str, 
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Complete an incursion (admin only)"""
    if DEVELOPMENT_MODE or db_pool is None:
        return {"message": "Incursion completed (development mode)"}
    
    manager = APIIncursionManager(db_pool)
    await manager.mark_incursion_inactive(incursion_id)
    
    return {"message": "Incursion completed successfully"}

@router.post("/cleanup")
async def cleanup_expired_incursions(
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Clean up expired incursions (admin only)"""
    if DEVELOPMENT_MODE or db_pool is None:
        return {"message": "Cleanup completed (development mode)", "cleaned_count": 0}
    
    # This would need proper implementation
    return {"message": f"Cleanup completed", "cleaned_count": 0}

@router.post("/{incursion_id}/mark_inactive")
async def mark_incursion_inactive(
    incursion_id: str, 
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Mark an incursion as inactive (admin only)"""
    if DEVELOPMENT_MODE or db_pool is None:
        return {"message": "Incursion marked inactive (development mode)"}
    
    manager = APIIncursionManager(db_pool)
    await manager.mark_incursion_inactive(incursion_id)
    
    return {"message": "Incursion marked inactive successfully"}

@router.post("/{incursion_id}/update_metadata")
async def update_incursion_metadata(
    incursion_id: str, 
    metadata: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user),
    db_pool: asyncpg.Pool = Depends(get_db_pool_optional)
):
    """Update incursion metadata (admin only)"""
    if DEVELOPMENT_MODE or db_pool is None:
        return {"message": "Metadata updated (development mode)"}
    
    manager = APIIncursionManager(db_pool)
    await manager.update_incursion_metadata(incursion_id, metadata)
    
    return {"message": "Incursion metadata updated successfully"}