"""
Examples of using the Universal Error Recovery System
"""

from shared.utils.error_recovery import (
    ErrorRecoveryBuilder, ErrorSeverity, ErrorCategory,
    create_api_error, create_database_error, create_network_error,
    create_validation_error, create_permission_error
)

# Example 1: Simple API error with retry
async def handle_api_failure(user, panel_name, error_msg, retry_func):
    """Handle a simple API failure with retry option"""
    return create_api_error(user, panel_name, error_msg, retry_func)

# Example 2: Custom error with specific recovery options
async def handle_quest_generation_error(user, error_msg, retry_func):
    """Handle quest generation errors with specific recovery options"""
    return (ErrorRecoveryBuilder(user, "quests")
            .with_error(error_msg)
            .with_category(ErrorCategory.QUEST)
            .with_severity(ErrorSeverity.MAJOR)
            .with_recovery_option("Check quest parameters")
            .with_recovery_option("Verify user level requirements")
            .with_recovery_option("Try different quest type")
            .with_recovery_option("Contact support if persistent")
            .with_technical_detail("Quest engine failed to generate valid quests")
            .with_technical_detail("User preferences may be incompatible")
            .with_retry_callback(retry_func)
            .build())

# Example 3: Critical system error
async def handle_critical_system_error(user, panel_name, error_msg):
    """Handle critical system errors that require immediate attention"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(error_msg)
            .with_category(ErrorCategory.SYSTEM)
            .with_severity(ErrorSeverity.CRITICAL)
            .with_custom_title("System Critical Failure")
            .with_custom_status("🚨 SYSTEM ALERT")
            .with_recovery_option("Contact system administrator immediately")
            .with_recovery_option("Check system status page")
            .with_recovery_option("Wait for emergency maintenance")
            .with_technical_detail("Critical system component failure detected")
            .with_technical_detail("Automatic recovery protocols initiated")
            .build())

# Example 4: Database connection error
async def handle_database_connection_error(user, panel_name, retry_func):
    """Handle database connection errors"""
    return create_database_error(
        user=user,
        panel_name=panel_name,
        error_msg="Database connection lost",
        retry_callback=retry_func
    )

# Example 5: Permission denied error
async def handle_permission_denied(user, panel_name, required_permission):
    """Handle permission denied errors"""
    return create_permission_error(
        user=user,
        panel_name=panel_name,
        error_msg=f"Missing required permission: {required_permission}"
    )

# Example 6: Validation error with custom details
async def handle_input_validation_error(user, panel_name, field_name, expected_format):
    """Handle input validation errors with specific guidance"""
    return (ErrorRecoveryBuilder(user, panel_name)
            .with_error(f"Invalid {field_name} format")
            .with_category(ErrorCategory.VALIDATION)
            .with_severity(ErrorSeverity.MINOR)
            .with_recovery_option(f"Use format: {expected_format}")
            .with_recovery_option("Check input requirements")
            .with_recovery_option("Try again with correct format")
            .with_technical_detail(f"Field '{field_name}' validation failed")
            .with_technical_detail(f"Expected format: {expected_format}")
            .build())