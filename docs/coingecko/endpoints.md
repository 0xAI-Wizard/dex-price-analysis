# CoinGecko API Endpoints

## Simple Price Endpoint

```
GET /simple/price
```

### Parameters

- `ids`: Comma-separated cryptocurrency IDs (e.g., bitcoin,ethereum)
- `vs_currencies`: Comma-separated target currencies (e.g., usd,eur)
- `include_24hr_vol`: Include 24h volume data (boolean)
- `include_market_cap`: Include market cap data (boolean)

### Example Request

```python
response = requests.get(
    "https://api.coingecko.com/api/v3/simple/price",
    params={
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd",
        "include_24hr_vol": "true",
        "include_market_cap": "true"
    },
    headers={"x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")}
)
```

### Example Response

```json
{
  "bitcoin": {
    "usd": 65000,
    "usd_24h_vol": 25000000000,
    "usd_market_cap": 1200000000000
  },
  "ethereum": {
    "usd": 3500,
    "usd_24h_vol": 15000000000,
    "usd_market_cap": 400000000000
  }
}
```

## DEX Pools Endpoint

```
GET /onchain/networks/{network}/dexes/{dex}/pools
```

### Parameters

- `network`: Network identifier (e.g., ethereum, binance-smart-chain)
- `dex`: DEX identifier (e.g., uniswap-v2, pancakeswap-v2)
- `page`: Page number for pagination
- `per_page`: Number of results per page

### Example Request

```python
response = requests.get(
    "https://api.coingecko.com/api/v3/onchain/networks/ethereum/dexes/uniswap-v2/pools",
    params={
        "page": 1,
        "per_page": 100
    },
    headers={"x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")}
)
```

### Example Response

```json
{
  "pools": [
    {
      "pool_address": "0x...",
      "token0": {
        "symbol": "WETH",
        "address": "0x..."
      },
      "token1": {
        "symbol": "USDC",
        "address": "0x..."
      },
      "liquidity": {
        "usd": 1000000
      },
      "volume_24h": {
        "usd": 500000
      }
    }
  ]
}
```

## Error Handling

```python
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Check rate limits
    remaining = int(response.headers.get("x-ratelimit-remaining", 0))
    if remaining < 5:
        time.sleep(2)  # Back off if close to limit

    return response.json()
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {str(e)}")
    raise
```

## Rate Limiting Implementation

```python
def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = int(response.headers.get("retry-after", 60))
        time.sleep(retry_after)
        return True
    return False

def make_api_request(url, params=None):
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(url, params=params)
            if handle_rate_limit(response):
                retry_count += 1
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count == max_retries:
                raise
            time.sleep(2 ** retry_count)  # Exponential backoff
```
