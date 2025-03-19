Here’s the revised plan and example code structured as a Markdown (`.md`) file:

````markdown
# Price Analysis Tool for wBTC, LBTC, and USDT Across DEXs

This document outlines a revised plan and example code for analyzing price differences of Wrapped Bitcoin (wBTC), Liquid Bitcoin (LBTC), and Tether (USDT) across decentralized exchanges (DEXs) on multiple blockchain networks. The structure, steps, and best practices remain unchanged, with the token selection updated from USDC to wBTC, LBTC, and USDT.

## Research on Price Sources

To analyze price differences across DEXs on different chains, we need reliable, accessible, and up-to-date price data for the same token. Here’s an evaluation of potential sources:

### Direct Blockchain Data

- **Description**: Querying smart contract data (e.g., pool reserves) directly from blockchain nodes using libraries like `web3.py`.
- **Pros**: Provides raw, unprocessed data directly from the source.
- **Cons**: Requires running a node or using an RPC provider (e.g., Infura), complex to implement, slow for real-time analysis, and needs chain-specific handling (e.g., Ethereum vs. Solana).

### DEX-Specific APIs/Subgraphs

- **Description**: Many DEXs offer APIs or GraphQL subgraphs (e.g., Uniswap’s Subgraph, PancakeSwap’s API).
- **Pros**: Accurate and DEX-specific data, often includes pool reserves and prices.
- **Cons**: Requires integration with multiple DEX-specific endpoints, inconsistent data formats, and additional effort to handle cross-chain differences.

### Data Aggregators (e.g., CoinGecko API)

- **Description**: CoinGecko provides a unified API with endpoints for on-chain DEX data, including pool reserves and prices across multiple networks (e.g., `/onchain/networks/{network}/dexes/{dex}/pools`).
- **Pros**: Aggregates data from multiple DEXs and chains, simplifies implementation with a single API, offers both DEX-specific and general price data (e.g., `/simple/price`), free Demo tier available (30 calls/min, 10,000 calls/month).
- **Cons**: Slight delay in data updates (not real-time), relies on CoinGecko’s aggregation methodology, requires an API key for on-chain endpoints.

### Price Oracles (e.g., Chainlink)

- **Description**: Chainlink provides on-chain price feeds for tokens across multiple networks.
- **Pros**: Reliable reference prices, widely used in DeFi.
- **Cons**: Reflects oracle data rather than actual DEX trading prices, not suitable for arbitrage analysis, requires on-chain interaction.

### Chosen Source: CoinGecko API

For this project, the **CoinGecko API** is the best choice due to its simplicity, aggregation across DEXs and chains, and free tier availability. It provides:

- **Token Contract Addresses**: Via `/coins/{id}` (e.g., wBTC, LBTC, USDT addresses on Ethereum, BSC, etc.).
- **DEX Pool Data**: Via `/onchain/networks/{network}/dexes/{dex}/pools` (reserves, liquidity).
- **Base Token USD Prices**: Via `/simple/price` (e.g., WETH in USD).

This allows us to calculate implied token prices without needing direct blockchain access or multiple DEX integrations, keeping the scope small and implementation straightforward.

## Structured Plan: Step-by-Step Guide

Below is a step-by-step plan broken into small, atomic steps for building the Python script.

### Step 1: Define the Token and Configuration

- **Objective**: Set up the token to analyze and the networks/DEXs to compare.
- **Tasks**:
  - Choose cross-chain tokens (e.g., wBTC, LBTC, USDT).
  - Define networks (e.g., Ethereum, Binance Smart Chain, Polygon).
  - List DEXs per network (e.g., Uniswap and Sushiswap for Ethereum).
  - Specify base tokens per network (e.g., WETH, WBNB, WMATIC).
- **Output**: A configuration dictionary in Python.

### Step 2: Set Up Environment and API Access

- **Objective**: Prepare the Python environment and API connectivity.
- **Tasks**:
  - Install libraries: `pip install requests pandas`.
  - Sign up for CoinGecko and get a Demo API key.
  - Define the API key and headers in the script.
- **Output**: Working environment with API access.

### Step 3: Fetch Token Contract Addresses

- **Objective**: Get the token’s contract addresses on each network.
- **Tasks**:
  - Use `/coins/{id}` to fetch wBTC, LBTC, and USDT’s `platforms` field (e.g., Ethereum: wBTC `0x2260fac5e5542a773aa44fbcfedf7c193bc2c599`).
  - Hardcode base token addresses (e.g., WETH: `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2`).
- **Output**: Dictionary mapping networks to token and base token addresses.

### Step 4: Fetch Base Token USD Prices

- **Objective**: Get USD prices for base tokens to convert pool prices to USD.
- **Tasks**:
  - Use `/simple/price?ids=weth,wbnb,wmatic&vs_currencies=usd` to fetch prices.
  - Store prices in a dictionary (e.g., `{'weth': 2000, 'wbnb': 300, 'wmatic': 0.8}`).
- **Output**: USD prices for WETH, WBNB, WMATIC.

### Step 5: Retrieve Pool Data for Each DEX

- **Objective**: Get pool data to calculate token prices.
- **Tasks**:
  - For each network and DEX:
    - Call `/onchain/networks/{network}/dexes/{dex}/pools`.
    - Filter pools containing both the token (wBTC, LBTC, or USDT) and the base token (e.g., WETH).
    - Select the pool with the highest `reserve_usd` (liquidity).
- **Output**: One pool per DEX with reserves data.

### Step 6: Calculate Implied USD Price

- **Objective**: Compute the token’s USD price from pool reserves.
- **Tasks**:
  - For each selected pool:
    - Identify reserves (e.g., `reserve0` for wBTC, `reserve1` for WETH, or vice versa).
    - Calculate price of token in base token: `P_token_base = R_base / R_token`.
    - Calculate USD price: `P_token_USD = P_token_base * P_base_USD`.
- **Output**: List of USD prices per DEX/network.

### Step 7: Collect and Analyze Results

- **Objective**: Compare prices and present findings.
- **Tasks**:
  - Store results in a list (e.g., `{'network': 'ethereum', 'dex': 'uniswap_v2', 'P_wBTC_USD': 60000.50}`).
  - Create a pandas DataFrame.
  - Print the table and calculate basic stats (e.g., mean, max/min difference).
- **Output**: Table of prices and summary statistics.

## Example Implementation

Here’s a simplified example of the Python script based on the plan, updated for wBTC, LBTC, and USDT:

```python
import requests
import pandas as pd

# Step 1: Configuration
tokens = ['wbtc', 'lbtc', 'tether']  # wBTC, LBTC, USDT (CoinGecko IDs)
networks = ['ethereum', 'binance-smart-chain', 'polygon']
dexes = {
    'ethereum': ['uniswap_v2', 'sushiswap'],
    'binance-smart-chain': ['pancakeswap_v2'],
    'polygon': ['quickswap']
}
base_tokens = {
    'ethereum': 'weth',
    'binance-smart-chain': 'wbnb',
    'polygon': 'wmatic'
}
base_token_addresses = {
    'ethereum': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',  # WETH
    'binance-smart-chain': '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',  # WBNB
    'polygon': '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270'  # WMATIC
}

# Step 2: API Setup
api_key = 'your_demo_api_key'  # Replace with your CoinGecko Demo API key
headers = {'x-cg-demo-api-key': api_key}

# Step 3: Fetch Token Addresses
def get_token_address(token, network):
    response = requests.get(f'https://api.coingecko.com/api/v3/coins/{token}', headers=headers)
    return response.json()['platforms'].get(network)

# Step 4: Fetch Base Token USD Prices
base_token_ids = list(base_tokens.values())
response = requests.get(
    f'https://api.coingecko.com/api/v3/simple/price?ids={",".join(base_token_ids)}&vs_currencies=usd',
    headers=headers
)
base_token_usd = response.json()

# Step 5 & 6: Get Pool Data and Calculate Prices
results = []
for token in tokens:
    for network in networks:
        token_address = get_token_address(token, network)
        if not token_address:  # Skip if token not available on network
            continue
        base_token = base_tokens[network]
        base_address = base_token_addresses[network]
        base_usd_price = base_token_usd[base_token]['usd']

        for dex in dexes[network]:
            # Fetch pools
            response = requests.get(
                f'https://api.coingecko.com/api/v3/onchain/networks/{network}/dexes/{dex}/pools',
                headers=headers
            )
            pools = response.json()['data']

            # Filter relevant pools
            relevant_pools = [
                p for p in pools
                if token_address.lower() in [p['token0']['address'], p['token1']['address']] and
                   base_address.lower() in [p['token0']['address'], p['token1']['address']]
            ]

            if relevant_pools:
                # Select highest liquidity pool
                pool = max(relevant_pools, key=lambda p: float(p['reserve_usd']))
                r_token = float(pool['reserve0']) if pool['token0']['address'] == token_address.lower() else float(pool['reserve1'])
                r_base = float(pool['reserve1']) if pool['token1']['address'] == base_address.lower() else float(pool['reserve0'])

                # Calculate price
                p_token_base = r_base / r_token
                p_token_usd = p_token_base * base_usd_price
                results.append({'token': token, 'network': network, 'dex': dex, 'P_USD': p_token_usd})

# Step 7: Analyze Results
df = pd.DataFrame(results)
print(df)
for token in tokens:
    token_df = df[df['token'] == token]
    if not token_df.empty:
        print(f"{token} - Mean Price: {token_df['P_USD'].mean():.4f}")
        print(f"{token} - Max Difference: {(token_df['P_USD'].max() - token_df['P_USD'].min()):.4f}")
```
````

### Example Output

```
    token         network           dex     P_USD
0    wbtc       ethereum    uniswap_v2  60000.50
1    wbtc       ethereum     sushiswap  59998.75
2    wbtc  binance-smart-chain  pancakeswap_v2  60002.10
3    wbtc        polygon     quickswap  60001.20
4    lbtc       ethereum    uniswap_v2  59800.30
5    lbtc        polygon     quickswap  59802.50
6  tether       ethereum    uniswap_v2      1.001
7  tether  binance-smart-chain  pancakeswap_v2      0.999

wbtc - Mean Price: 60000.6375
wbtc - Max Difference: 3.3500
lbtc - Mean Price: 59801.4000
lbtc - Max Difference: 2.2000
tether - Mean Price: 1.0000
tether - Max Difference: 0.0020
```

## Best Practices for AI Implementation

### Modular Design

- Break code into functions (e.g., `get_token_address`, `calculate_price`) for readability and reuse.
- **Example**: Separate API calls and price calculations.

### Error Handling

- Check API response status (`response.raise_for_status()`) and handle missing pools gracefully.
- **Example**: `if not relevant_pools: continue`.

### Rate Limiting

- Add delays (`time.sleep(2)`) if testing extensively to avoid hitting CoinGecko’s 30 calls/min limit.
- Cache responses during development (e.g., save JSON to a file).

### Data Validation

- Ensure reserves are non-zero before division (`if r_token == 0: continue`).
- Verify API responses contain expected fields (e.g., `reserve_usd`).

### Comments and Logging

- Use inline comments to explain logic (e.g., `# Calculate price from reserves`).
- Optionally, use `logging` for debugging instead of `print`.

### Keep Scope Small

- Focus on a few tokens and networks/DEXs to avoid complexity.
- Avoid real-time trading or blockchain interaction unless explicitly required.

## Additional Features (Optional)

These can be built on top of the script later without bloating the initial scope:

- **Multiple Tokens**: Extend to a list of tokens (already included: wBTC, LBTC, USDT) by looping over `token_ids`.
- **Historical Analysis**: Run periodically and store data in a CSV for trend analysis.
- **Arbitrage Detection**: Calculate potential profits by comparing max/min prices, factoring in gas fees.
- **Visualization**: Use `matplotlib` to plot prices (e.g., bar chart of `P_USD` by DEX).
- **Broader Network Support**: Add non-EVM chains (e.g., Solana) if CoinGecko supports their DEXs.

## Design Considerations and Scope Management

- **Simplicity**: Using CoinGecko avoids the complexity of direct blockchain queries or multiple DEX integrations.
- **Scalability**: The modular structure supports adding more tokens/networks later.
- **Accuracy**: Selecting high-liquidity pools ensures prices reflect market conditions.
- **Scope**: Limited to a one-time snapshot of prices for wBTC, LBTC, and USDT across a few EVM-compatible chains, avoiding real-time or trading features.
