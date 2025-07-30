# Search API Python Client

A Python client library for the Search API, providing easy access to email, phone, and domain search functionality.
Acquire your API key through @ADSearchEngine_bot on Telegram.

## Installation

    pip install AD-SearchAPI

## Quick Start

    from search_api import SearchAPI

    # Initialize the client with your API key
    client = SearchAPI(api_key="your_api_key")

    # Search by email
    result = client.search_email("example@domain.com", include_house_value=True, include_extra_info=True, phone_format="international")
    print(result)

    # Search by phone
    result = client.search_phone("+1234567890", include_house_value=True, include_extra_info=True, phone_format="international")
    print(result)

    # Search by domain
    result = client.search_domain("example.com")
    print(result)

## Features

- Email search with optional house value, extra info, and phone number formatting
- Phone number search with validation, formatting, and property details
- Domain search with comprehensive results
- Rate limiting and retry handling
- Type hints and comprehensive documentation
- Enhanced address model with property details (bedrooms, bathrooms, living area, home status)

## Advanced Usage

### Configuration

    from search_api import SearchAPI, SearchAPIConfig

    config = SearchAPIConfig(
        api_key="your_api_key",
        max_retries=3,
        timeout=30,
        base_url="https://search-api.dev",
        debug_mode=False,  # Enable debug logging
        proxy=None  # Optional proxy configuration
    )

    client = SearchAPI(config=config)

### Error Handling

    from search_api.exceptions import SearchAPIError

    try:
        result = client.search_email("example@domain.com")
    except SearchAPIError as e:
        print(f"Error: {e}")

### Address Model

The `Address` model includes detailed property information when `include_house_value` is enabled:

- `street: str` - Street address
- `city: Optional[str]` - City name
- `state: Optional[str]` - State abbreviation
- `postal_code: Optional[str]` - Postal code
- `country: Optional[str]` - Country name
- `zestimate: Optional[Decimal]` - Estimated property value
- `zpid: Optional[str]` - Zillow Property ID
- `bedrooms: Optional[int]` - Number of bedrooms
- `bathrooms: Optional[float]` - Number of bathrooms (supports half-baths)
- `living_area: Optional[int]` - Square footage
- `home_status: Optional[str]` - Property status (e.g., "For Sale", "Sold")

## API Reference

### SearchAPI

Main client class for interacting with the Search API.

#### Methods

- `search_email(email: str, include_house_value: bool = False, include_extra_info: bool = False, phone_format: str = "international") -> EmailSearchResult`
  - Search by email address. Returns an `EmailSearchResult` with name, date of birth, addresses, phone numbers, and optional extra info.
  - `phone_format`: Use "international" for E.164 format or "local" for national format.

- `search_phone(phone: str, include_house_value: bool = False, include_extra_info: bool = False, phone_format: str = "international") -> List[PhoneSearchResult]`
  - Search by phone number. Returns a list of `PhoneSearchResult` objects with name, date of birth, addresses, emails, and optional extra info.
  - `phone_format`: Use "international" for E.164 format or "local" for national format.

- `search_domain(domain: str) -> DomainSearchResult`
  - Search by domain name. Returns a `DomainSearchResult` with a list of associated email results.

### SearchAPIConfig

Configuration class for customizing client behavior.

#### Parameters

- `api_key: str` - Your API key (required)
- `cache_ttl: int` - Cache time-to-live in seconds (default: 3600)
- `max_retries: int` - Maximum number of retry attempts (default: 3)
- `timeout: int` - Request timeout in seconds (default: 30)
- `base_url: str` - API base URL (default: "https://search-api.dev")
- `debug_mode: bool` - Enable debug logging (default: False)
- `proxy: Optional[Dict]` - Proxy configuration (default: None)

## Contributing

Contributions are welcome! Please submit a Pull Request with your changes or open an issue for discussion.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
