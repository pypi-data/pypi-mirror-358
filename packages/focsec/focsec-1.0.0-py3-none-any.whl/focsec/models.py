"""
Data models for the Focsec SDK.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IP:
    """
    Information about an IP address from the Focsec API.
    """
    ip: str
    is_vpn: bool = False
    is_proxy: bool = False
    is_bot: bool = False
    is_tor: bool = False
    is_datacenter: bool = False
    is_in_european_union: bool = False
    city: Optional[str] = None
    country: Optional[str] = None
    iso_code: Optional[str] = None
    flag: Optional[str] = None
    autonomous_system_number: Optional[int] = None
    autonomous_system_organization: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: dict) -> "IP":
        """Create an IP instance from API response data."""
        return cls(**data)