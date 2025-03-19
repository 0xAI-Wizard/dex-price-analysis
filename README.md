# Crypto Price Analysis Tool

A Python-based tool for analyzing cryptocurrency price discrepancies across different exchanges and networks. This tool leverages the CoinGecko Pro API to fetch real-time price data.

## Features

- Fetches token prices from CoinGecko's official API
- Analyzes price differences across multiple networks and DEXs
- Calculates statistics on price discrepancies
- Saves results to CSV for further analysis
- Tracks API request usage

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the root directory with your CoinGecko Pro API key:

```
COINGECKO_API_KEY_PRO=your_api_key_here
```

You can get a CoinGecko Pro API key by subscribing to one of their paid plans.

### 3. Configure Tokens and Networks

Edit the `config.py` file to specify:

- Tokens you want to analyze
- Networks to check
- DEXs per network

## Usage

Run the script with:

```bash
python price_analysis.py
```

The script will:

1. Fetch current token prices from CoinGecko
2. Check prices across configured networks and DEXs
3. Calculate price differences
4. Display results in the console
5. Save results to `cache/price_analysis_results.csv`

## Data Storage

- All results are saved to `cache/price_analysis_results.csv`
- API request count is tracked in `cache/request_count.json`

## Troubleshooting

- Check your API key is valid and has sufficient credits
- Ensure you're not exceeding rate limits
- For network or DEX-specific issues, check if they are supported by CoinGecko

## Notes

- The tool uses CoinGecko's new onchain endpoints which may have different access requirements based on your subscription plan
- Some networks may require specific identifiers that differ from their common names
