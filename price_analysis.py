import requests
import pandas as pd
import time
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Step 1: Configuration
TOKENS = ["wbtc", "lbtc", "tether"]  # wBTC, LBTC, USDT (CoinGecko IDs)
NETWORKS = ["ethereum", "binance-smart-chain", "polygon"]
DEXES = {
    "ethereum": ["uniswap_v2", "sushiswap"],
    "binance-smart-chain": ["pancakeswap_v2"],
    "polygon": ["quickswap"],
}
BASE_TOKENS = {"ethereum": "weth", "binance-smart-chain": "wbnb", "polygon": "wmatic"}
BASE_TOKEN_ADDRESSES = {
    "ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
    "binance-smart-chain": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",  # WBNB
    "polygon": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  # WMATIC
}

# Load API key from environment variables
API_KEY = os.getenv("COINGECKO_API_KEY")
HEADERS = {"x-cg-demo-api-key": API_KEY}
BASE_URL = "https://api.coingecko.com/api/v3"

# Validate API key
if not API_KEY:
    logger.error("API key not found. Please set COINGECKO_API_KEY in your .env file.")
    raise ValueError("API key not found")

# Rate limiting configuration
RATE_LIMIT_CALLS = 30  # Maximum calls per minute
RATE_LIMIT_WAIT = 2  # Seconds to wait between calls


class PriceAnalysisError(Exception):
    """Custom exception for price analysis errors"""

    pass


def handle_api_response(response: requests.Response, context: str = "") -> dict:
    """
    Handle API response with proper error checking

    Args:
        response: The API response object
        context: Additional context for error messages

    Returns:
        dict: The JSON response data

    Raises:
        PriceAnalysisError: If the API request fails
    """
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed ({context}): {str(e)}"
        logger.error(error_msg)
        raise PriceAnalysisError(error_msg)
    except ValueError as e:
        error_msg = f"Invalid JSON response ({context}): {str(e)}"
        logger.error(error_msg)
        raise PriceAnalysisError(error_msg)


def get_token_address(token: str, network: str) -> Optional[str]:
    """
    Fetch token contract address for a given network

    Args:
        token: Token ID (e.g., 'wbtc')
        network: Network ID (e.g., 'ethereum')

    Returns:
        Optional[str]: Token contract address if available, None otherwise
    """
    logger.info(f"Fetching {token} address for {network}")
    time.sleep(RATE_LIMIT_WAIT)  # Rate limiting

    response = requests.get(f"{BASE_URL}/coins/{token}", headers=HEADERS)
    data = handle_api_response(response, f"get_token_address({token}, {network})")
    return data.get("platforms", {}).get(network)


def get_base_token_prices() -> Dict[str, float]:
    """
    Fetch USD prices for base tokens (WETH, WBNB, WMATIC)

    Returns:
        Dict[str, float]: Mapping of base token IDs to their USD prices
    """
    logger.info("Fetching base token USD prices")
    time.sleep(RATE_LIMIT_WAIT)  # Rate limiting

    base_token_ids = list(BASE_TOKENS.values())
    response = requests.get(
        f"{BASE_URL}/simple/price",
        params={"ids": ",".join(base_token_ids), "vs_currencies": "usd"},
        headers=HEADERS,
    )
    data = handle_api_response(response, "get_base_token_prices")
    return {token: prices["usd"] for token, prices in data.items()}


def get_pool_data(
    network: str, dex: str, token_address: str, base_address: str
) -> Optional[Dict]:
    """
    Fetch and filter pool data for a specific DEX and token pair

    Args:
        network: Network ID
        dex: DEX name
        token_address: Token contract address
        base_address: Base token contract address

    Returns:
        Optional[Dict]: Pool data with highest liquidity if found, None otherwise
    """
    logger.info(f"Fetching pool data for {dex} on {network}")
    time.sleep(RATE_LIMIT_WAIT)  # Rate limiting

    response = requests.get(
        f"{BASE_URL}/onchain/networks/{network}/dexes/{dex}/pools", headers=HEADERS
    )
    data = handle_api_response(response, f"get_pool_data({network}, {dex})")

    # Filter relevant pools
    relevant_pools = [
        p
        for p in data.get("data", [])
        if (
            token_address.lower()
            in [p["token0"]["address"].lower(), p["token1"]["address"].lower()]
            and base_address.lower()
            in [p["token0"]["address"].lower(), p["token1"]["address"].lower()]
        )
    ]

    if not relevant_pools:
        logger.warning(f"No relevant pools found for {dex} on {network}")
        return None

    # Return pool with highest liquidity
    return max(relevant_pools, key=lambda p: float(p.get("reserve_usd", 0)))


def calculate_price(
    pool: Dict, token_address: str, base_address: str, base_usd_price: float
) -> Optional[float]:
    """
    Calculate token USD price from pool data

    Args:
        pool: Pool data
        token_address: Token contract address
        base_address: Base token contract address
        base_usd_price: Base token USD price

    Returns:
        Optional[float]: Calculated USD price if valid, None otherwise
    """
    try:
        is_token0 = pool["token0"]["address"].lower() == token_address.lower()
        r_token = float(pool["reserve0"] if is_token0 else pool["reserve1"])
        r_base = float(pool["reserve1"] if not is_token0 else pool["reserve0"])

        if r_token <= 0:
            logger.warning("Invalid token reserve (zero or negative)")
            return None

        p_token_base = r_base / r_token
        return p_token_base * base_usd_price
    except (KeyError, ValueError, ZeroDivisionError) as e:
        logger.error(f"Error calculating price: {str(e)}")
        return None


def analyze_prices() -> pd.DataFrame:
    """
    Main function to analyze token prices across DEXs and networks

    Returns:
        pd.DataFrame: Results containing token prices across different DEXs and networks
    """
    results = []
    base_token_usd = get_base_token_prices()

    for token in TOKENS:
        for network in NETWORKS:
            token_address = get_token_address(token, network)
            if not token_address:
                logger.info(f"{token} not available on {network}")
                continue

            base_token = BASE_TOKENS[network]
            base_address = BASE_TOKEN_ADDRESSES[network]
            base_usd_price = base_token_usd.get(base_token)

            if not base_usd_price:
                logger.warning(f"No USD price found for {base_token}")
                continue

            for dex in DEXES[network]:
                pool = get_pool_data(network, dex, token_address, base_address)
                if not pool:
                    continue

                price_usd = calculate_price(
                    pool, token_address, base_address, base_usd_price
                )
                if price_usd is not None:
                    results.append(
                        {
                            "token": token,
                            "network": network,
                            "dex": dex,
                            "price_usd": price_usd,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

    return pd.DataFrame(results)


def main():
    """Main entry point of the script"""
    try:
        logger.info("Starting price analysis")
        df = analyze_prices()

        if df.empty:
            logger.warning("No price data found")
            return

        # Display results
        print("\nPrice Analysis Results:")
        print(df.to_string(index=False))

        # Calculate and display statistics
        print("\nPrice Statistics:")
        for token in df["token"].unique():
            token_df = df[df["token"] == token]
            if not token_df.empty:
                mean_price = token_df["price_usd"].mean()
                max_diff = token_df["price_usd"].max() - token_df["price_usd"].min()
                print(f"\n{token.upper()}:")
                print(f"Mean Price: ${mean_price:.4f}")
                print(f"Max Difference: ${max_diff:.4f}")

    except PriceAnalysisError as e:
        logger.error(f"Price analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
