from fastapi import APIRouter, Depends
import asyncpg
from datetime import datetime
from typing import Optional

from api.dependencies import get_db_pool_optional, get_redis, is_development_mode
from api.models.common import SuccessResponse
from core.redis_cache import RedisCache

router = APIRouter()

@router.get("/", response_model=SuccessResponse)
async def health_check():
    """Basic health check"""
    mode = "development" if is_development_mode() else "production"
    return SuccessResponse(
        message="Realm of Shadows API is running",
        data={
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "mode": mode
        }
    )

@router.get("/detailed", response_model=SuccessResponse)
async def detailed_health_check(
    db_pool: Optional[asyncpg.Pool] = Depends(get_db_pool_optional),
    redis: Optional[RedisCache] = Depends(get_redis)
):
    """Detailed health check including database and Redis"""
    mode = "development" if is_development_mode() else "production"
    health_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "mode": mode,
        "services": {}
    }
    
    # Check database
    if db_pool is None:
        health_data["services"]["database"] = "disabled (development mode)"
    else:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_data["services"]["database"] = "healthy"
        except Exception as e:
            health_data["services"]["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    if redis is None:
        health_data["services"]["redis"] = "disabled (development mode)"
    else:
        try:
            await redis.set("health_check", "ok", expire=60)
            result = await redis.get("health_check")
            if result == "ok":
                health_data["services"]["redis"] = "healthy"
            else:
                health_data["services"]["redis"] = "unhealthy: unexpected response"
        except Exception as e:
            health_data["services"]["redis"] = f"unhealthy: {str(e)}"
    
    return SuccessResponse(
        message="Detailed health check completed",
        data=health_data
    )