"""
Health check and monitoring endpoints for the API.

This module provides comprehensive health monitoring including:
- Database connectivity checks
- Redis connectivity checks
- Service health status
- Performance metrics
"""
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.core.config import get_settings
from app.core.response_handlers import APIResponseHandler
from app.core.cache_manager import get_cache_manager
from app.infrastructure.database.session import get_async_session
from app.infrastructure.database.models.v2.ascendants import Ascendant

router = APIRouter(prefix="/health", tags=["Health"])
settings = get_settings()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return APIResponseHandler.success(
        data={
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.api_version,
            "environment": settings.environment
        },
        message="Service is healthy"
    )


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_async_session)
):
    """Detailed health check with all system components."""
    start_time = time.time()
    health_status = {
        "overall_status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.api_version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Database health check
    try:
        db_start = time.time()
        result = await db.execute(text("SELECT 1"))
        db_response_time = (time.time() - db_start) * 1000  # Convert to ms
        
        # Test a simple query on our main model
        count_result = await db.execute(select(Ascendant).limit(1))
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(db_response_time, 2),
            "details": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "details": "Database connection failed"
        }
        health_status["overall_status"] = "unhealthy"
    
    # Redis/Cache health check
    try:
        cache_start = time.time()
        cache_manager = get_cache_manager()
        
        # Test cache operations
        test_key = "health_check_test"
        test_value = {"timestamp": datetime.now(timezone.utc).isoformat()}
        
        await cache_manager.set(test_key, test_value, ttl=60)
        retrieved_value = await cache_manager.get(test_key)
        await cache_manager.delete(test_key)
        
        cache_response_time = (time.time() - cache_start) * 1000
        
        cache_stats = await cache_manager.get_stats()
        
        health_status["checks"]["cache"] = {
            "status": "healthy",
            "response_time_ms": round(cache_response_time, 2),
            "redis_available": cache_stats.get("redis_available", False),
            "memory_cache_size": cache_stats.get("memory_cache_size", 0),
            "hit_rate": cache_stats.get("stats", {}).get("hit_rate", 0),
            "details": "Cache operations successful"
        }
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "degraded",
            "error": str(e),
            "details": "Cache operations failed, using fallback"
        }
        # Cache failure is not critical, mark as degraded
        if health_status["overall_status"] == "healthy":
            health_status["overall_status"] = "degraded"
    
    # System metrics
    try:
        import psutil
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "details": "System metrics collected"
        }
        
        # Check for resource issues
        if (psutil.virtual_memory().percent > 90 or 
            psutil.disk_usage('/').percent > 95):
            health_status["checks"]["system"]["status"] = "warning"
            health_status["checks"]["system"]["details"] = "High resource usage detected"
            
    except ImportError:
        health_status["checks"]["system"] = {
            "status": "unavailable",
            "details": "psutil not available for system metrics"
        }
    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "error",
            "error": str(e),
            "details": "Failed to collect system metrics"
        }
    
    # Response time
    total_response_time = (time.time() - start_time) * 1000
    health_status["total_response_time_ms"] = round(total_response_time, 2)
    
    # Determine HTTP status code
    if health_status["overall_status"] == "healthy":
        status_code = status.HTTP_200_OK
    elif health_status["overall_status"] == "degraded":
        status_code = status.HTTP_200_OK  # Still functional
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return APIResponseHandler.success(
        data=health_status,
        message=f"Health check completed - {health_status['overall_status']}",
        status_code=status_code
    )


@router.get("/database")
async def database_health_check(
    db: AsyncSession = Depends(get_async_session)
):
    """Dedicated database health check."""
    try:
        start_time = time.time()
        
        # Basic connectivity test
        await db.execute(text("SELECT 1"))
        
        # Test main tables
        ascendant_count = await db.execute(
            text("SELECT COUNT(*) FROM ascendants")
        )
        
        response_time = (time.time() - start_time) * 1000
        
        return APIResponseHandler.success(
            data={
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "ascendant_count": ascendant_count.scalar(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            message="Database is healthy"
        )
        
    except Exception as e:
        return APIResponseHandler.error(
            message="Database health check failed",
            error_code="DATABASE_UNHEALTHY",
            details={"error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/cache")
async def cache_health_check():
    """Dedicated cache health check."""
    try:
        start_time = time.time()
        cache_manager = get_cache_manager()
        
        # Test cache operations
        test_key = "cache_health_test"
        test_value = {"test": True, "timestamp": time.time()}
        
        # Test set/get/delete cycle
        await cache_manager.set(test_key, test_value, ttl=60)
        retrieved = await cache_manager.get(test_key)
        await cache_manager.delete(test_key)
        
        response_time = (time.time() - start_time) * 1000
        stats = await cache_manager.get_stats()
        
        return APIResponseHandler.success(
            data={
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "operations_successful": retrieved is not None,
                "stats": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            message="Cache is healthy"
        )
        
    except Exception as e:
        return APIResponseHandler.error(
            message="Cache health check failed",
            error_code="CACHE_UNHEALTHY",
            details={"error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    try:
        cache_manager = get_cache_manager()
        cache_stats = await cache_manager.get_stats()
        
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache": cache_stats,
            "api": {
                "version": settings.api_version,
                "environment": settings.environment,
                "uptime_seconds": time.time() - getattr(get_metrics, '_start_time', time.time())
            }
        }
        
        # Add system metrics if available
        try:
            import psutil
            metrics["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "available_mb": psutil.virtual_memory().available // (1024 * 1024)
                },
                "disk": {
                    "percent": psutil.disk_usage('/').percent,
                    "free_gb": psutil.disk_usage('/').free // (1024 * 1024 * 1024)
                }
            }
        except ImportError:
            pass
        
        return APIResponseHandler.success(
            data=metrics,
            message="Metrics retrieved successfully"
        )
        
    except Exception as e:
        return APIResponseHandler.error(
            message="Failed to retrieve metrics",
            error_code="METRICS_ERROR",
            details={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/readiness")
async def readiness_check(
    db: AsyncSession = Depends(get_async_session)
):
    """Kubernetes-style readiness probe."""
    try:
        # Check if we can handle requests
        await db.execute(text("SELECT 1"))
        
        return APIResponseHandler.success(
            data={"ready": True},
            message="Service is ready to handle requests"
        )
        
    except Exception as e:
        return APIResponseHandler.error(
            message="Service is not ready",
            error_code="SERVICE_NOT_READY",
            details={"error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe."""
    return APIResponseHandler.success(
        data={"alive": True},
        message="Service is alive"
    )


# Initialize start time for uptime calculation
if not hasattr(get_metrics, '_start_time'):
    get_metrics._start_time = time.time()