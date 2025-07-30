# Focsec Python SDK

Python SDK and CLI tool for the [Focsec](https://focsec.com) Threat Intelligence and VPN Detection API.

Focsec provides comprehensive IP intelligence data, including VPN detection, proxy detection, bot detection, and more. This SDK simplifies integration with the Focsec API, allowing you to easily access IP data and perform various checks in your Python-baed project.

## Installation

```bash
pip install focsec
```

## Quick Start

### SDK

```python
from focsec import FocsecClient

# Initialize the client with your API key
client = FocsecClient(api_key="your-api-key-here")

# Get IP information
result = client.ip("84.118.20.205")
print(f"IP: {result.ip}")
print(f"Is VPN: {result.is_vpn}")
print(f"Is Proxy: {result.is_proxy}")
print(f"Is TOR: {result.is_tor}")
print(f"Is Bot: {result.is_bot}")
print(f"Is Datacenter: {result.is_datacenter}")
# More information available: country, city, iso_code, is_in_european_union, flag, autonomous_system_number, autonomous_system_organization	
```

### Command Line Interface

This package also includes a command line interface (CLI) for quick access to the API without writing any code.

```bash
# Set your API key (or use --api-key flag)
export FOCSEC_API_KEY=your-api-key-here

# Look up an IP address
focsec ip 8.8.8.8

# Output in single line JSON format
focsec ip 8.8.8.8 --json
```

## Error Handling

The SDK provides a simple exception hierarchy:

```
FocsecError (base - catch any SDK error)
├── ClientError (4xx - fixable by user)
│   ├── BadRequestError (400)
│   ├── AuthenticationError (401)
│   ├── PaymentRequiredError (402)
│   ├── NotFoundError (404)
│   └── MethodNotAllowedError (405)
├── ServerError (5xx - server issues)
│   ├── InternalServerError (500)
│   ├── BadGatewayError (502)
│   └── ServiceUnavailableError (503)
├── RateLimitError (429 - rate limit exceeded)
├── ValidationError (client-side validation)
└── APIError (unexpected status codes)
```

## API Documentation

For further API documentation, please visit [docs.focsec.com](https://docs.focsec.com).

## License

MIT License

## Questions?

Contact us at [support@focsec.com](mailto:support@focsec.com) for any questions or issues.

