"""
Focsec Python SDK

A Python SDK for the Focsec IP information and VPN detection API.
"""

from .client import FocsecClient
from .models import IP
from .exceptions import (
    FocsecError,
    AuthenticationError,
    RateLimitError,
    ClientError,
    ServerError,
    ValidationError,
    APIError
)

__version__ = "0.1.0"
__all__ = [
    "FocsecClient", 
    "IP", 
    "FocsecError",
    "AuthenticationError",
    "RateLimitError",
    "ClientError",
    "ServerError",
    "ValidationError",
    "APIError"
]