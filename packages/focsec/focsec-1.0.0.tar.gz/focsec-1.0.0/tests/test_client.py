import pytest
import responses
from focsec import FocsecClient
from focsec.exceptions import ValidationError, AuthenticationError, RateLimitError, ClientError, ServerError, APIError


@pytest.fixture
def client():
    return FocsecClient(api_key="test-key")


@pytest.fixture
def api_response():
    return {
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


class TestFocsecClient:
    def test_init_requires_api_key(self):
        with pytest.raises(ValidationError):
            FocsecClient(api_key="")

    def test_init_sets_timeout(self):
        client = FocsecClient(api_key="key", timeout=60)
        assert client.timeout == 60

    def test_invalid_ip_raises_validation_error(self, client):
        with pytest.raises(ValidationError):
            client.ip("invalid")

    @responses.activate
    def test_successful_ip_lookup(self, client, api_response):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", json=api_response)
        
        result = client.ip("8.8.8.8")
        
        assert result.ip == "8.8.8.8"
        assert result.is_datacenter is True
        assert result.country == "United States"
        assert result.autonomous_system_number == 15169

    @responses.activate
    def test_401_raises_authentication_error(self, client):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", 
                     json={"message": "Invalid API key"}, status=401)
        
        with pytest.raises(AuthenticationError):
            client.ip("8.8.8.8")

    @responses.activate
    def test_429_raises_rate_limit_error(self, client):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", status=429)
        
        with pytest.raises(RateLimitError):
            client.ip("8.8.8.8")

    @responses.activate
    def test_400_raises_client_error(self, client):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", status=400)
        
        with pytest.raises(ClientError):
            client.ip("8.8.8.8")

    @responses.activate
    def test_500_raises_server_error(self, client):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", status=500)
        
        with pytest.raises(ServerError):
            client.ip("8.8.8.8")

    @responses.activate
    def test_unknown_status_raises_api_error(self, client):
        responses.add(responses.GET, "https://api.focsec.com/v1/ip/8.8.8.8", status=418)
        
        with pytest.raises(APIError):
            client.ip("8.8.8.8")