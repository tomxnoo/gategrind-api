"""
API routes for the Realm of Shadows API
"""

from .health import router as health_router
from .users import router as users_router
from .quests import router as quests_router
from .logging import router as logging_router
from .auth import router as auth_router

# TODO: Add these imports as we create the corresponding route files
# from .buffs import router as buffs_router
# from .incursions import router as incursions_router