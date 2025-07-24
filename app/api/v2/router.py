"""
API V2 Router Configuration.

This module configures and exports the main API v2 router that includes
all v2 endpoints. It provides a centralized way to manage API versioning
and endpoint organization.
"""
from fastapi import APIRouter

from app.api.v2.movements import router as movements_router
from app.api.v2.progression import router as progression_router


# Create the main v2 API router
api_v2_router = APIRouter(prefix="/api")

# Include all v2 routers
api_v2_router.include_router(movements_router)
api_v2_router.include_router(progression_router)

# Export for easy import
__all__ = ["api_v2_router"]