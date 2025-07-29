"""
Standardized API response handling utilities.

This module provides consistent response formatting, error handling,
and status management across all API endpoints.
"""
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    RoSBaseException,
    ValidationError,
    BusinessLogicError,
    ResourceNotFoundError,
    InsufficientPermissionsError,
    ExternalServiceError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class APIResponseHandler:
    """Handles standardized API responses and error formatting."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Create a successful API response."""
        response_data = {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        return JSONResponse(content=response_data, status_code=status_code)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> JSONResponse:
        """Create a 201 Created response."""
        return APIResponseHandler.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def error(
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> JSONResponse:
        """Create an error API response."""
        response_data = {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log the error
        logger.error(
            f"API Error {status_code}: {message}",
            extra={
                "error_code": error_code,
                "details": details
            }
        )
        
        return JSONResponse(content=response_data, status_code=status_code)
    
    @staticmethod
    def validation_error(
        message: str,
        field_errors: Optional[Dict[str, List[str]]] = None
    ) -> JSONResponse:
        """Create a validation error response."""
        return APIResponseHandler.error(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors} if field_errors else None,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> JSONResponse:
        """Create a 404 Not Found response."""
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        return APIResponseHandler.error(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details if details else None,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        required_permission: Optional[str] = None
    ) -> JSONResponse:
        """Create a 403 Forbidden response."""
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
            
        return APIResponseHandler.error(
            message=message,
            error_code="ACCESS_FORBIDDEN",
            details=details if details else None,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def handle_exception(exception: Exception) -> JSONResponse:
        """Convert exceptions to appropriate HTTP responses."""
        if isinstance(exception, ValidationError):
            return APIResponseHandler.validation_error(
                message=exception.message,
                field_errors=exception.context.get("field_errors")
            )
        
        elif isinstance(exception, ResourceNotFoundError):
            return APIResponseHandler.not_found(
                message=exception.message,
                resource_type=exception.context.get("resource_type"),
                resource_id=exception.context.get("resource_id")
            )
        
        elif isinstance(exception, InsufficientPermissionsError):
            return APIResponseHandler.forbidden(
                message=exception.message,
                required_permission=exception.context.get("required_permission")
            )
        
        elif isinstance(exception, BusinessLogicError):
            return APIResponseHandler.error(
                message=exception.message,
                error_code=exception.error_code or "BUSINESS_LOGIC_ERROR",
                details=exception.context,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        elif isinstance(exception, (DatabaseError, ExternalServiceError)):
            return APIResponseHandler.error(
                message="Service temporarily unavailable",
                error_code=exception.error_code or "SERVICE_ERROR",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        elif isinstance(exception, RoSBaseException):
            return APIResponseHandler.error(
                message=exception.message,
                error_code=exception.error_code,
                details=exception.context,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        else:
            # Log unexpected errors
            logger.exception("Unexpected error occurred", exc_info=exception)
            return APIResponseHandler.error(
                message="An unexpected error occurred",
                error_code="INTERNAL_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaginatedResponseHandler:
    """Handles paginated API responses."""
    
    @staticmethod
    def paginate(
        items: List[Any],
        total: int,
        page: int,
        limit: int,
        message: str = "Data retrieved successfully"
    ) -> JSONResponse:
        """Create a paginated response."""
        pages = (total + limit - 1) // limit  # Ceiling division
        
        response_data = {
            "status": "success",
            "message": message,
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                    "has_next": page < pages,
                    "has_prev": page > 1
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)