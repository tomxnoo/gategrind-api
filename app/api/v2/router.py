"""
API V2 Router Configuration.

This module configures and exports the main API v2 router that includes
all v2 endpoints. It provides a centralized way to manage API versioning
and endpoint organization.
"""
from fastapi import APIRouter
from .movements import router as movements_router
from .progression import router as progression_router
from .events import router as events_router
from .incursions import router as incursions_router
from .awakening import router as awakening_router
from .dungeons import router as dungeons_router
from .profiles import router as profiles_router

# Import admin router
from .admin.skill_requirements import router as admin_skill_requirements_router

# Create the main v2 router
api_v2_router = APIRouter(prefix="/api/v2")

# Include all sub-routers
api_v2_router.include_router(movements_router)
api_v2_router.include_router(progression_router)
api_v2_router.include_router(events_router)
api_v2_router.include_router(incursions_router)
api_v2_router.include_router(awakening_router)
api_v2_router.include_router(dungeons_router)
api_v2_router.include_router(profiles_router)
api_v2_router.include_router(admin_skill_requirements_router)

# Export for easy import
__all__ = ["api_v2_router"]