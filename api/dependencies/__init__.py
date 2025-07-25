"""
API dependencies package.

This package contains dependency injection utilities for the API,
including authentication, database sessions, and other common dependencies.
"""
from .auth import get_current_user_id, get_current_user_profile

# Import functions from the main deps module
from ..deps import (
    get_db_pool_optional,
    require_db_pool,
    get_redis,
    get_current_user_with_optional_db,
    get_current_user,
    get_optional_user,
    is_development_mode
)

__all__ = [
    "get_current_user_id",
    "get_current_user_profile",
    "get_db_pool_optional",
    "require_db_pool", 
    "get_redis",
    "get_current_user_with_optional_db",
    "get_current_user",
    "get_optional_user",
    "is_development_mode"
]