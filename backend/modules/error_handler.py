"""
Error Handler Module
Provides centralized error handling and logging for the API
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from logger import setup_logger

logger = setup_logger(__name__)


class ErrorResponse(BaseModel):
    """Standardized error response format"""
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


def create_error_response(
    error_message: str,
    error_code: str = "INTERNAL_ERROR",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict] = None
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        error_message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details (optional)
        
    Returns:
        JSONResponse with standardized error format
    """
    error_data = ErrorResponse(
        error=error_message,
        error_code=error_code,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )
    
    logger.error(f"{error_code}: {error_message}", extra={"details": details})
    
    return JSONResponse(
        status_code=status_code,
        content=error_data.dict(exclude_none=True)
    )


# Common error creators
def not_found_error(resource: str, resource_id: str) -> JSONResponse:
    """Standard 404 error"""
    return create_error_response(
        error_message=f"{resource} not found",
        error_code="NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND,
        details={"resource": resource, "id": resource_id}
    )


def validation_error(message: str, field: Optional[str] = None) -> JSONResponse:
    """Standard validation error"""
    details = {"field": field} if field else None
    return create_error_response(
        error_message=message,
        error_code="VALIDATION_ERROR",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details
    )


def server_error(message: str, exception: Optional[Exception] = None) -> JSONResponse:
    """Standard 500 error"""
    details = {"exception": str(exception)} if exception else None
    return create_error_response(
        error_message=message,
        error_code="SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details
    )


# Error codes reference
ERROR_CODES = {
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Invalid input data",
    "SERVER_ERROR": "Internal server error",
    "DATABASE_ERROR": "Database operation failed",
    "EXTERNAL_API_ERROR": "External API call failed",
    "ANALYSIS_FAILED": "Analysis processing failed",
    "CACHE_ERROR": "Cache operation failed",
    "SCORING_ERROR": "Content scoring failed"
}
