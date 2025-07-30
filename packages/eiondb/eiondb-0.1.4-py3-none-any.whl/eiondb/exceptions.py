"""
Eion SDK Exception Classes

Custom exceptions for different types of errors that can occur
when using the Eion SDK.
"""

from typing import Optional, Dict, Any


class EionError(Exception):
    """Base exception for all Eion-related errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class EionConnectionError(EionError):
    """Raised when there are connection issues with the Eion server"""
    pass


class EionTimeoutError(EionError):
    """Raised when requests to the Eion server timeout"""
    pass


class EionAuthenticationError(EionError):
    """Raised when authentication with the Eion server fails"""
    pass


class EionValidationError(EionError):
    """Raised when request data fails validation"""
    pass


class EionNotFoundError(EionError):
    """Raised when a requested resource is not found"""
    pass


class EionServerError(EionError):
    """Raised when the Eion server returns a 5xx error"""
    pass


class EionSetupError(EionError):
    """Raised when Eion server setup fails"""
    pass 