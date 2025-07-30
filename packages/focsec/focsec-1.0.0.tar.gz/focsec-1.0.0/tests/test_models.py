import pytest
from focsec.models import IP


class TestIP:
    def test_from_api_response(self):
        data = {
            "ip": "8.8.8.8",
            "is_vpn": False,
            "is_proxy": False,
            "is_bot": False,
            "is_tor": False,
            "is_datacenter": True,
            "is_in_european_union": False,
            "city": "Mountain View",
            "country": "United States",
            "iso_code": "US",
            "flag": "🇺🇸",
            "autonomous_system_number": 15169,
            "autonomous_system_organization": "Google LLC"
        }
        
        ip = IP.from_api_response(data)
        
        assert ip.ip == "8.8.8.8"
        assert ip.is_datacenter is True
        assert ip.country == "United States"
        assert ip.autonomous_system_number == 15169
        assert ip.autonomous_system_organization == "Google LLC"