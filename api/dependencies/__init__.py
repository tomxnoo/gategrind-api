"""
API dependencies package.

This package contains dependency injection utilities for the API,
including authentication, database sessions, and other common dependencies.
"""
from .auth import get_current_user_id, get_current_user_profile

__all__ = [
    "get_current_user_id",
    "get_current_user_profile"
]