"""
Main client for the Focsec API.
"""

import ipaddress
import requests
from urllib.parse import urljoin

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    ClientError,
    ServerError,
    ValidationError,
    APIError
)
from .models import IP


class FocsecClient:
    """
    Client for interacting with the Focsec IP detection API.
    """
    
    BASE_URL = "https://api.focsec.com/v1/"
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize the Focsec client.
        
        Args:
            api_key: Your Focsec API key
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValidationError("API key is required")
        
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": self.api_key,
            "User-Agent": "focsec-python-sdk/0.1.0"
        })
    
    def _make_request(self, endpoint: str) -> dict:
        """
        Make a request to the Focsec API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            JSON response data
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            APIError: If the API returns an error
        """
        url = urljoin(self.BASE_URL, endpoint)
        
        try:
            response = self._session.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            raise APIError(f"Request failed: {e}")
        
        # Parse error response data if available
        error_data = None
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
        except ValueError:
            pass
        
        error_message = (
            error_data.get("message") if error_data 
            else f"HTTP {response.status_code}"
        )
        
        # Map status codes to specific exceptions
        status_error_map = {
            400: (ClientError, "Bad request"),
            401: (AuthenticationError, "Invalid API key"),
            402: (AuthenticationError, "Subscription expired"),
            404: (ClientError, "Resource not found"),
            405: (ClientError, "Method not allowed"),
            429: (RateLimitError, "Rate limit exceeded"),
            500: (ServerError, "Internal server error"),
            502: (ServerError, "Service temporarily unavailable"),
            503: (ServerError, "Service temporarily unavailable")
        }
        
        if response.status_code in status_error_map:
            exception_class, default_message = status_error_map[response.status_code]
            raise exception_class(
                message=error_message or default_message,
                status_code=response.status_code,
                response_data=error_data
            )
        elif response.status_code != 200:
            raise APIError(
                message=error_message,
                status_code=response.status_code,
                response_data=error_data
            )
        
        try:
            return response.json()
        except ValueError:
            raise APIError("Invalid JSON response from API")
    
    def ip(self, ip: str) -> IP:
        """
        Get information about an IP address.
        
        Args:
            ip: IP address to look up (IPv4 or IPv6)
            
        Returns:
            IP object with IP details
            
        Raises:
            ValidationError: If the IP address is invalid
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            APIError: If the API returns an error
        """
        # Validate IP address
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValidationError(f"Invalid IP address: {ip}")
        
        endpoint = f"ip/{ip}"
        data = self._make_request(endpoint)
        return IP.from_api_response(data)