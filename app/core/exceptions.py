"""
Custom exception classes for the application.

This module provides a hierarchy of custom exceptions that enable
precise error handling throughout the application layers.
"""
from typing import Optional, Dict, Any


class RoSBaseException(Exception):
    """Base exception for all RoS application errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}


class ValidationError(RoSBaseException):
    """Raised when input validation fails."""
    pass


class BusinessLogicError(RoSBaseException):
    """Raised when business rules are violated."""
    pass


class ResourceNotFoundError(RoSBaseException):
    """Raised when a requested resource is not found."""
    pass


class InsufficientPermissionsError(RoSBaseException):
    """Raised when user lacks required permissions."""
    pass


class ExternalServiceError(RoSBaseException):
    """Raised when external service calls fail."""
    pass


class DatabaseError(RoSBaseException):
    """Raised when database operations fail."""
    pass


class CacheError(RoSBaseException):
    """Raised when cache operations fail."""
    pass


# Game-specific exceptions
class DungeonError(BusinessLogicError):
    """Base class for dungeon-related errors."""
    pass


class DungeonLevelLockedError(DungeonError):
    """Raised when trying to access a locked dungeon level."""
    pass


class InsufficientRequirementsError(DungeonError):
    """Raised when player doesn't meet dungeon requirements."""
    pass


class ActiveSessionError(DungeonError):
    """Raised when player already has an active dungeon session."""
    pass


class SkillTreeError(BusinessLogicError):
    """Base class for skill tree errors."""
    pass


class IncursionError(BusinessLogicError):
    """Base class for incursion system errors."""
    pass


class QuestError(BusinessLogicError):
    """Base class for quest system errors."""
    pass