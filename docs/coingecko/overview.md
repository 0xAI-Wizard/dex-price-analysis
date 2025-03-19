# CoinGecko API Overview

## Base URL

```
https://api.coingecko.com/api/v3
```

## Authentication

The CoinGecko API requires an API key for most endpoints. The key should be included in the request headers:

```
x-cg-demo-api-key: YOUR_API_KEY
```

## Rate Limits

- Free API: 10-30 calls/minute
- Pro API: Higher limits based on subscription tier
- Rate limit headers are included in responses:
  - `x-ratelimit-limit`: Total requests allowed per minute
  - `x-ratelimit-remaining`: Remaining requests for the current minute

## Common Response Codes

- 200: Success
- 400: Bad Request
- 401: Unauthorized (Invalid API key)
- 403: Forbidden
- 429: Too Many Requests (Rate limit exceeded)
- 500: Internal Server Error

## Implementation Notes

1. Always check rate limits before making requests
2. Implement exponential backoff for rate limit handling
3. Cache responses when possible to minimize API calls
4. Handle API errors gracefully with appropriate error messages

## Best Practices

1. Store API key securely in environment variables
2. Implement request retries with backoff
3. Log API responses for debugging
4. Monitor rate limit usage
5. Use appropriate error handling for different response codes

## API Versioning

The current version (v3) is stable. Check the [CoinGecko API documentation](https://www.coingecko.com/api/documentation) for updates.
