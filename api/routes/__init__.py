from .health import router as health_router
from .users import router as users_router
from .quests import router as quests_router
from .logging import router as logging_router
from .auth import router as auth_router
from .buffs import router as buffs_router
from .incursions import router as incursions_router
from .awakening import router as awakening_router

__all__ = [
    "health_router",
    "users_router", 
    "quests_router",
    "logging_router",
    "auth_router",
    "buffs_router",
    "incursions_router",
    "awakening_router"
]