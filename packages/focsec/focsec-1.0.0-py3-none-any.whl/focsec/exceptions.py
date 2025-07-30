"""
Exception classes for the Focsec SDK.

This module provides a comprehensive exception hierarchy that maps to HTTP status codes
and client-side validation errors. The hierarchy allows for both fine-grained error
handling and broad exception catching based on error categories.
"""

from typing import Optional, Dict, Any


class FocsecError(Exception):
    """
    Base exception for all Focsec SDK errors.
    
    All SDK exceptions inherit from this class, allowing users to catch
    any SDK error with a single except clause.
    
    Attributes:
        message: Human-readable error description
        status_code: HTTP status code if applicable
        response_data: Raw response data from the API
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


# Client Errors (4xx) - User can fix these
class ClientError(FocsecError):
    """
    Base class for 4xx client errors.
    
    These errors indicate that the request was invalid in some way.
    The client can typically fix these by correcting the request.
    """
    pass


class BadRequestError(ClientError):
    """HTTP 400: The request was malformed or invalid."""
    pass


class AuthenticationError(ClientError):
    """HTTP 401: Authentication credentials are missing or invalid."""
    pass


class PaymentRequiredError(ClientError):
    """HTTP 402: Payment required (subscription expired or quota exceeded)."""
    pass


class NotFoundError(ClientError):
    """HTTP 404: The requested resource was not found."""
    pass


class MethodNotAllowedError(ClientError):
    """HTTP 405: The HTTP method is not allowed for this endpoint."""
    pass


# Server Errors (5xx) - Server issues
class ServerError(FocsecError):
    """
    Base class for 5xx server errors.
    
    These errors indicate issues on the server side.
    Typically these are temporary and may succeed if retried.
    """
    pass


class InternalServerError(ServerError):
    """HTTP 500: An unexpected error occurred on the server."""
    pass


class BadGatewayError(ServerError):
    """HTTP 502: The service is temporarily unavailable."""
    pass


class ServiceUnavailableError(ServerError):
    """HTTP 503: The service is temporarily unavailable."""
    pass


# Special Cases
class RateLimitError(FocsecError):
    """
    HTTP 429: Rate limit exceeded.
    
    This is technically a 4xx error but gets special treatment
    as it's often handled differently (with retries).
    """
    pass


# Client-side Validation
class ValidationError(FocsecError):
    """
    Raised when client-side validation fails.
    
    This error is raised before making an API request when
    the input doesn't meet the required format or constraints.
    """
    pass


# Catch-all for unexpected responses
class APIError(FocsecError):
    """
    Generic API error for unexpected or unhandled status codes.
    
    This exception is raised when the API returns a status code
    that doesn't map to a more specific exception class.
    """
    pass


# HTTP Status Code to Exception Mapping
STATUS_EXCEPTION_MAP = {
    400: BadRequestError,
    401: AuthenticationError,
    402: PaymentRequiredError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    429: RateLimitError,
    500: InternalServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
}


def get_exception_for_status(
    status_code: int, 
    message: str, 
    response_data: Optional[Dict[str, Any]] = None
) -> FocsecError:
    """
    Get the appropriate exception class for an HTTP status code.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Optional response data from the API
    
    Returns:
        An instance of the appropriate FocsecError subclass
    """
    exception_class = STATUS_EXCEPTION_MAP.get(status_code, APIError)
    return exception_class(message, status_code, response_data)