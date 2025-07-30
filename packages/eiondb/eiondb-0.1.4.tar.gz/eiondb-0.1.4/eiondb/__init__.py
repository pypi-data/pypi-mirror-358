"""
Eion Python SDK

A Python SDK for Eion - Shared memory storage and collaborative intelligence for AI agent systems.
"""

__version__ = "0.1.2"

from .client import EionClient
from .exceptions import (
    EionError,
    EionAuthenticationError,
    EionValidationError,
    EionNotFoundError,
    EionServerError,
    EionConnectionError,
    EionTimeoutError,
    EionSetupError
)

__all__ = [
    "EionClient",
    "EionError",
    "EionAuthenticationError", 
    "EionValidationError",
    "EionNotFoundError",
    "EionServerError",
    "EionConnectionError",
    "EionTimeoutError",
    "EionSetupError"
] 