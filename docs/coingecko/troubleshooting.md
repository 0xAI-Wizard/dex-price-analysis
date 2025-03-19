# CoinGecko API Troubleshooting Guide

## Common Issues and Solutions

### 1. Rate Limit Exceeded (429 Error)

**Problem**: Too many requests made within the rate limit window.

**Solution**:

- Implement rate limiting in your code
- Use caching for frequently accessed data
- Consider upgrading to a higher API tier
- Add exponential backoff for retries

**Example Implementation**:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_cached_price(coin_id, vs_currency):
    # Cache price data for 60 seconds
    return fetch_price(coin_id, vs_currency)
```

### 2. Invalid API Key (401 Error)

**Problem**: API key is missing, invalid, or expired.

**Solution**:

- Verify API key in environment variables
- Check if API key is properly set in request headers
- Ensure API key has not expired
- Validate API key format

**Debugging Steps**:

1. Check `.env` file configuration
2. Verify API key in request headers
3. Test API key with simple endpoint
4. Check API key status in CoinGecko dashboard

### 3. Missing Token Data

**Problem**: No data returned for specific tokens.

**Solution**:

- Verify token ID is correct
- Check if token is supported by CoinGecko
- Use alternative token identifiers
- Implement fallback data sources

### 4. Pool Data Issues

**Problem**: Incomplete or missing DEX pool data.

**Solution**:

- Verify network and DEX identifiers
- Check pool address format
- Implement pagination for large datasets
- Add error handling for missing data

## Debugging Tips

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_request(url, params):
    try:
        logger.info(f"Making request to {url}")
        response = requests.get(url, params=params)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
```

### Request Validation

```python
def validate_request_params(params):
    required = ["ids", "vs_currencies"]
    missing = [param for param in required if param not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")
```

### Error Prevention

1. Always validate input parameters
2. Use type hints and docstrings
3. Implement proper error handling
4. Add request/response logging
5. Monitor API usage and errors

## Support Resources

- [CoinGecko API Documentation](https://www.coingecko.com/api/documentation)
- [API Status Page](https://status.coingecko.com/)
- Support Email: api@coingecko.com
- [API Discord Community](https://discord.gg/EhrkaCH)

## Common Error Messages

```python
ERROR_MESSAGES = {
    401: "Invalid API key. Please check your credentials.",
    403: "Access forbidden. Please check your API plan limits.",
    429: "Rate limit exceeded. Please wait before making more requests.",
    500: "CoinGecko API internal error. Please try again later.",
    502: "Bad gateway. The API is temporarily unavailable.",
    504: "Gateway timeout. The API request timed out."
}
```
