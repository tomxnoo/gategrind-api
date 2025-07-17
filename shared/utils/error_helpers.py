"""
Simple error handling helpers for quick integration
"""

from shared.utils.error_handler import handle_panel_errors, quick_error_recovery, PanelErrorContext
from shared.utils.error_recovery import (
    create_api_error, create_database_error, create_network_error,
    create_validation_error, create_permission_error, ErrorCategory
)

# Re-export for convenience
__all__ = [
    'handle_panel_errors',
    'quick_error_recovery', 
    'PanelErrorContext',
    'create_api_error',
    'create_database_error',
    'create_network_error',
    'create_validation_error',
    'create_permission_error',
    'ErrorCategory'
]

# Common error patterns for different panels
AWAKENING_ERRORS = {
    'api': lambda user, error, retry: create_api_error(user, "awakening", str(error), retry),
    'quest': lambda user, error, retry: quick_error_recovery(user, "awakening", error, "quest", retry),
}

INCURSION_ERRORS = {
    'api': lambda user, error, retry: create_api_error(user, "incursions", str(error), retry),
    'database': lambda user, error, retry: create_database_error(user, "incursions", str(error), retry),
}

LOGGING_ERRORS = {
    'validation': lambda user, error, retry: create_validation_error(user, "logging", str(error), retry),
    'api': lambda user, error, retry: create_api_error(user, "logging", str(error), retry),
}

QUEST_ERRORS = {
    'generation': lambda user, error, retry: quick_error_recovery(user, "quests", error, "quest", retry),
    'api': lambda user, error, retry: create_api_error(user, "quests", str(error), retry),
}