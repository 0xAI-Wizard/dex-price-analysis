# DEX Price Analysis Tool

This tool analyzes price differences of wBTC, LBTC, and USDT across decentralized exchanges (DEXs) on multiple blockchain networks (Ethereum, Binance Smart Chain, and Polygon).

## Features

- Fetches and compares token prices across multiple DEXs and networks
- Calculates price statistics (mean price and maximum difference)
- Implements rate limiting and error handling
- Provides detailed logging for troubleshooting

## Prerequisites

- Python 3.8 or higher
- CoinGecko API Demo key (get one at https://www.coingecko.com/en/api)

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the project root (or copy the template)
   - Add your CoinGecko API key to the `.env` file:
     ```
     COINGECKO_API_KEY=your_demo_api_key
     ```

## Configuration

The script uses environment variables for sensitive information like API keys. The `.env` file is included in `.gitignore` to prevent accidental exposure of your API key.

## Usage

Run the script:

```bash
python price_analysis.py
```

The script will:

1. Fetch token addresses and base token prices
2. Query pool data from various DEXs
3. Calculate and display price analysis results
4. Show statistics for each token

## Output Example

```
Price Analysis Results:
   token         network           dex     price_usd
    wbtc       ethereum    uniswap_v2     60000.50
    wbtc       ethereum     sushiswap     59998.75
    wbtc  binance-smart-chain  pancakeswap_v2     60002.10
    wbtc        polygon     quickswap     60001.20
    lbtc       ethereum    uniswap_v2     59800.30
    lbtc        polygon     quickswap     59802.50
  tether       ethereum    uniswap_v2         1.001
  tether  binance-smart-chain  pancakeswap_v2         0.999

Price Statistics:
WBTC:
Mean Price: $60000.6375
Max Difference: $3.3500

LBTC:
Mean Price: $59801.4000
Max Difference: $2.2000

TETHER:
Mean Price: $1.0000
Max Difference: $0.0020
```

## Rate Limiting

The script implements rate limiting to comply with CoinGecko's Demo API limits:

- Maximum 30 calls per minute
- 2-second delay between API calls

## Error Handling

The script includes comprehensive error handling:

- API request failures
- Invalid responses
- Missing or invalid pool data
- Zero/negative reserves

Errors are logged with context for easy troubleshooting.

## Notes

- This is a one-time snapshot tool and does not provide real-time price updates
- Price calculations use the highest liquidity pools for accuracy
- All timestamps are in UTC
