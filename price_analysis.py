import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
from datetime import datetime
import os
import requests
import pandas as pd
import time
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import os
import json
from functools import lru_cache
from dotenv import load_dotenv
from config import (
    TOKENS,
    NETWORKS,
    DEXES,
    RATE_LIMIT_CALLS,
    RATE_LIMIT_WAIT,
)
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="price_analysis.log",  # Save logs to file
    filemode="a",  # Append to log file
)
# Add console handler to display logs in console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

logger = logging.getLogger(__name__)

# directory constants
VIZ_DIR = "visualizations"
REPORT_DIR = "reports"
os.makedirs(VIZ_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Load API key from environment variables
API_KEY = os.getenv("COINGECKO_API_KEY_PRO")
HEADERS = {"x-cg-pro-api-key": API_KEY}  # Header for Pro API
BASE_URL = "https://pro-api.coingecko.com/api/v3"

# Cache file paths
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
RESULTS_FILE = os.path.join(CACHE_DIR, "price_analysis_results.csv")
REQUEST_COUNT_FILE = os.path.join(CACHE_DIR, "request_count.json")
CACHE_FILE = os.path.join(CACHE_DIR, "api_cache.json")

# Error message mapping
ERROR_MESSAGES = {
    400: "Bad request. Please check your parameters.",
    401: "Invalid API key. Please check your credentials.",
    403: "Access forbidden. Please check your API plan limits.",
    429: "Rate limit exceeded. Please wait before making more requests.",
    500: "CoinGecko API internal error. Please try again later.",
    502: "Bad gateway. The API is temporarily unavailable.",
    504: "Gateway timeout. The API request timed out.",
}

# Request counter
request_counter = 0

# Cache for API responses
api_cache = {}

# Validate API key
if not API_KEY:
    logger.error(
        "API key not found. Please set COINGECKO_API_KEY_PRO in your .env file."
    )
    raise ValueError("API key not found")


class PriceAnalysisError(Exception):
    """Custom exception for price analysis errors"""

    pass


def load_cache() -> None:
    """Load API cache from file if it exists"""
    global api_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                # Only use cache entries that are less than 5 minutes old
                current_time = datetime.utcnow().timestamp()
                api_cache = {
                    k: v
                    for k, v in cache_data.items()
                    if current_time - v.get("timestamp", 0) < 300  # 5 minutes
                }
            logger.info(f"Loaded {len(api_cache)} cached API responses")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache: {str(e)}")
            api_cache = {}


def save_cache() -> None:
    """Save API cache to file"""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(api_cache, f)
        logger.info(f"Saved {len(api_cache)} API responses to cache")
    except (IOError, TypeError) as e:
        logger.warning(f"Failed to save cache: {str(e)}")


def track_request() -> None:
    """
    Track API request and update counter
    """
    global request_counter
    request_counter += 1
    # Save counter to file
    with open(REQUEST_COUNT_FILE, "w") as f:
        json.dump(
            {"count": request_counter, "last_updated": datetime.utcnow().isoformat()}, f
        )
    logger.debug(f"API requests made: {request_counter}")


def handle_rate_limit(response: requests.Response) -> bool:
    """
    Handle rate limiting based on response headers

    Args:
        response: API response

    Returns:
        bool: True if rate limited and should retry, False otherwise
    """
    if response.status_code == 429:
        retry_after = int(response.headers.get("retry-after", RATE_LIMIT_WAIT * 5))
        logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds")
        time.sleep(retry_after)
        return True

    # Check remaining rate limit
    remaining = int(response.headers.get("x-ratelimit-remaining", RATE_LIMIT_CALLS))
    if remaining < 5:
        logger.warning(f"Rate limit nearly exceeded ({remaining} left). Adding delay")
        time.sleep(RATE_LIMIT_WAIT * 2)  # Double the wait time when close to limit

    return False


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
        # Check for error codes and return appropriate message
        if response.status_code != 200:
            error_msg = ERROR_MESSAGES.get(
                response.status_code, f"Unknown error: {response.status_code}"
            )
            error_detail = f"API request failed ({context}): {error_msg}"
            logger.error(error_detail)
            raise PriceAnalysisError(error_detail)

        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed ({context}): {str(e)}"
        logger.error(error_msg)
        raise PriceAnalysisError(error_msg)
    except ValueError as e:
        error_msg = f"Invalid JSON response ({context}): {str(e)}"
        logger.error(error_msg)
        raise PriceAnalysisError(error_msg)


def make_api_request(
    url: str, params: Optional[Dict[str, Any]] = None, context: str = ""
) -> Dict:
    """
    Make API request with retry logic and caching

    Args:
        url: API endpoint URL
        params: Query parameters
        context: Context for error messages

    Returns:
        Dict: JSON response data
    """
    # Generate cache key
    cache_key = f"{url}_{json.dumps(params or {})}"

    # Check cache first
    if cache_key in api_cache:
        cache_entry = api_cache[cache_key]
        logger.debug(f"Using cached response for {url}")
        return cache_entry["data"]

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.debug(f"Making API request to {url}")
            time.sleep(RATE_LIMIT_WAIT)  # Rate limiting
            response = requests.get(url, params=params, headers=HEADERS)
            track_request()

            # Handle rate limiting
            if handle_rate_limit(response):
                retry_count += 1
                continue

            # Process response
            data = handle_api_response(response, context)

            # Cache the successful response
            api_cache[cache_key] = {
                "data": data,
                "timestamp": datetime.utcnow().timestamp(),
            }

            return data
        except (requests.exceptions.RequestException, PriceAnalysisError) as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Failed after {max_retries} retries: {str(e)}")
                raise PriceAnalysisError(
                    f"API request failed after {max_retries} retries: {str(e)}"
                )

            # Exponential backoff
            wait_time = RATE_LIMIT_WAIT * (2**retry_count)
            logger.warning(
                f"Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(wait_time)


@lru_cache(maxsize=50)
def get_token_price(token: str) -> Optional[float]:
    """
    Fetch token's USD price directly from CoinGecko

    Args:
        token: Token ID (e.g., 'wrapped-bitcoin')

    Returns:
        Optional[float]: Token's USD price if available, None otherwise
    """
    logger.info(f"Fetching USD price for {token}")

    try:
        data = make_api_request(
            f"{BASE_URL}/simple/price",
            params={"ids": token, "vs_currencies": "usd"},
            context=f"get_token_price({token})",
        )
        return data.get(token, {}).get("usd")
    except PriceAnalysisError as e:
        logger.error(f"Failed to fetch token price: {str(e)}")
        return None


@lru_cache(maxsize=100)
def get_token_address(token: str, network: str) -> Optional[str]:
    """
    Get the contract address for a token on a specific network

    Args:
        token: Token ID (e.g., 'wrapped-bitcoin')
        network: Network ID (e.g., 'ethereum')

    Returns:
        Optional[str]: Token contract address if available, None otherwise
    """
    logger.info(f"Fetching contract address for {token} on {network}")

    try:
        data = make_api_request(
            f"{BASE_URL}/coins/{token}",
            context=f"get_token_address({token}, {network})",
        )

        # Extract contract address for the specified network
        platforms = data.get("platforms", {})
        contract_address = platforms.get(network)

        if not contract_address:
            logger.warning(f"No contract address found for {token} on {network}")
            return None

        return contract_address
    except PriceAnalysisError as e:
        logger.error(f"Failed to fetch token address: {str(e)}")
        return None


def get_onchain_token_price(token_address: str, network: str) -> Optional[float]:
    """
    Fetch token's USD price directly through the onchain simple token price endpoint

    Args:
        token_address: Token contract address
        network: Network ID (using CoinGecko network IDs)

    Returns:
        Optional[float]: Token's USD price if available, None otherwise
    """
    logger.info(f"Fetching onchain price for token {token_address} on {network}")

    # Map network names to CoinGecko's network identifiers if needed
    network_id_mapping = {
        "ethereum": "eth",
        "arbitrum": "arbitrum-one",
        "optimism": "optimistic-ethereum",
        "base": "base",
        "polygon-pos": "polygon-pos",
        "avalanche": "avalanche",
        "binance-smart-chain": "bsc",
        # Add more mappings as needed
    }

    network_id = network_id_mapping.get(network, network)

    try:
        data = make_api_request(
            f"{BASE_URL}/onchain/simple/networks/{network_id}/token_price/{token_address}",
            context=f"get_onchain_token_price({token_address}, {network})",
        )

        # Response format: {"0x...address": {"usd": price}}
        if token_address in data:
            return data.get(token_address, {}).get("usd")
        return None
    except PriceAnalysisError as e:
        logger.error(f"Failed to fetch onchain token price: {str(e)}")
        return None


def get_dex_price(network: str, dex: str, token: str) -> Optional[float]:
    """
    Fetch token's USD price from a specific DEX using available endpoints
    First attempts to get price from simple token price endpoint, falls back to other methods

    Args:
        network: Network ID
        dex: DEX name
        token: Token ID

    Returns:
        Optional[float]: Token's USD price if available, None otherwise
    """
    logger.info(f"Fetching {token} price from {dex} on {network}")

    # Step 1: Get token contract address
    token_address = get_token_address(token, network)
    if not token_address:
        return None

    # Step 2: Try the onchain simple token price endpoint
    price = get_onchain_token_price(token_address, network)
    if price is not None:
        return price

    # If we couldn't get price from the simple endpoint, we can't proceed
    # as the pool endpoints appear to be unavailable or different
    logger.warning(
        f"Could not get price for {token} on {network}/{dex} through available endpoints"
    )
    return None


def analyze_prices() -> pd.DataFrame:
    """
    Analyze token prices across DEXs and networks, focusing on USD price discrepancies

    Returns:
        pd.DataFrame: Results containing token prices across different DEXs and networks
    """
    results = []

    for token in TOKENS:
        # Get reference price from CoinGecko
        reference_price = get_token_price(token)
        if not reference_price:
            logger.warning(f"Could not get reference price for {token}")
            continue

        for network in NETWORKS:
            if network not in DEXES:
                logger.warning(f"No DEXes configured for network {network}")
                continue

            for dex in DEXES[network]:
                dex_price = get_dex_price(network, dex, token)
                if dex_price is not None:
                    price_diff = ((dex_price - reference_price) / reference_price) * 100
                    results.append(
                        {
                            "token": token,
                            "network": network,
                            "dex": dex,
                            "price_usd": dex_price,
                            "reference_price": reference_price,
                            "price_difference_percent": price_diff,
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

    return pd.DataFrame(results)


def save_results(df: pd.DataFrame) -> None:
    """
    Save analysis results to CSV file

    Args:
        df: DataFrame with analysis results
    """
    if df.empty:
        logger.warning("No data to save")
        return

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

    # Save to CSV
    df.to_csv(RESULTS_FILE, index=False)
    logger.info(f"Results saved to {RESULTS_FILE}")


def main():
    """Main entry point of the script"""
    global request_counter

    # Initialize or load request counter
    if os.path.exists(REQUEST_COUNT_FILE):
        try:
            with open(REQUEST_COUNT_FILE, "r") as f:
                request_counter = json.load(f).get("count", 0)
        except (json.JSONDecodeError, IOError):
            request_counter = 0

    # Load API cache
    load_cache()

    try:
        logger.info("Starting price analysis")
        df = analyze_prices()

        if df.empty:
            logger.warning("No price data found")
            return

        # Save results to file
        save_results(df)

        # Save cache for future runs
        save_cache()

        # Display results
        print("\nPrice Analysis Results:")
        print(df.to_string(index=False))

        # Calculate and display statistics
        print("\nPrice Discrepancy Analysis:")
        for token in df["token"].unique():
            token_df = df[df["token"] == token]
            if not token_df.empty:
                max_diff = token_df["price_difference_percent"].abs().max()
                avg_diff = token_df["price_difference_percent"].abs().mean()
                print(f"\n{token.upper()}:")
                print(f"Average Price Difference: {avg_diff:.2f}%")
                print(f"Maximum Price Difference: {max_diff:.2f}%")

                # Find the DEXs with the largest price difference
                max_diff_row = token_df.loc[
                    token_df["price_difference_percent"].abs().idxmax()
                ]
                print(f"Largest difference found between:")
                print(f"  - Reference price: ${max_diff_row['reference_price']:.2f}")
                print(
                    f"  - {max_diff_row['dex']} on {max_diff_row['network']}: ${max_diff_row['price_usd']:.2f}"
                )

        print(f"\nTotal API requests made: {request_counter}")

    except PriceAnalysisError as e:
        logger.error(f"Price analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        # Always save the cache and request count when done
        save_cache()


def find_arbitrage_opportunities(
    df: pd.DataFrame, min_profit_percent: float = 0.5
) -> pd.DataFrame:
    """
    Find arbitrage opportunities across DEXs and networks.

    Args:
        df: DataFrame with price analysis results
        min_profit_percent: Minimum profit percentage to consider

    Returns:
        DataFrame with arbitrage opportunities
    """
    opportunities = []

    for token in df["token"].unique():
        token_data = df[df["token"] == token].copy()

        # Find min and max prices for each token
        min_price_row = token_data.loc[token_data["price_usd"].idxmin()]
        max_price_row = token_data.loc[token_data["price_usd"].idxmax()]

        price_diff_percent = (
            (max_price_row["price_usd"] - min_price_row["price_usd"])
            / min_price_row["price_usd"]
            * 100
        )

        if price_diff_percent >= min_profit_percent:
            opportunities.append(
                {
                    "token": token,
                    "buy_network": min_price_row["network"],
                    "buy_dex": min_price_row["dex"],
                    "buy_price": min_price_row["price_usd"],
                    "sell_network": max_price_row["network"],
                    "sell_dex": max_price_row["dex"],
                    "sell_price": max_price_row["price_usd"],
                    "profit_percent": price_diff_percent,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    return pd.DataFrame(opportunities)


def generate_visualizations(df: pd.DataFrame) -> None:
    """
    Generate visualizations for price analysis results.
    Uses direct matplotlib plotting instead of seaborn for better compatibility.
    """
    # 1. Price comparison plots for each token
    for token in df["token"].unique():
        token_data = df[df["token"] == token]

        # Get unique networks for this token
        networks = token_data["network"].unique()
        dexes = token_data["dex"].unique()

        plt.figure(figsize=(12, 6))

        # Create grouped bar chart
        bar_width = 0.8 / len(networks)
        x = np.arange(len(dexes))

        for i, network in enumerate(networks):
            network_data = token_data[token_data["network"] == network]
            heights = []

            for dex in dexes:
                dex_data = network_data[network_data["dex"] == dex]
                if len(dex_data) > 0:
                    heights.append(dex_data["price_usd"].values[0])
                else:
                    heights.append(0)

            plt.bar(
                x + i * bar_width - (len(networks) - 1) * bar_width / 2,
                heights,
                width=bar_width,
                label=network,
            )

        plt.xlabel("DEX")
        plt.ylabel("Price (USD)")
        plt.title(f"{token} Prices Across DEXs and Networks")
        plt.xticks(x, dexes, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(VIZ_DIR, f"{token}_price_comparison.png"))
        plt.close()

    # 2. Price differences boxplot using matplotlib
    plt.figure(figsize=(10, 6))

    # Group data by token
    tokens = df["token"].unique()
    data_by_token = [
        df[df["token"] == token]["price_difference_percent"].values for token in tokens
    ]

    plt.boxplot(data_by_token, labels=tokens)
    plt.title("Price Differences Distribution by Token")
    plt.xlabel("Token")
    plt.ylabel("Price Difference (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "price_differences_boxplot.png"))
    plt.close()


def generate_html_report(
    price_data: pd.DataFrame, arb_opportunities: pd.DataFrame
) -> str:
    """
    Generate an HTML report with analysis results.

    Returns:
        str: Path to generated report
    """
    template_str = """
    <html>
    <head>
        <title>Price Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f5f5f5; }
            .visualization { margin: 20px 0; }
            h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Price Analysis Report</h1>
        <p>Generated on: {{ timestamp }}</p>
        
        <h2>Price Analysis Results</h2>
        {{ price_table }}
        
        <h2>Arbitrage Opportunities</h2>
        {{ arb_table }}
        
        <h2>Visualizations</h2>
        <div class="visualization">
            {% for viz in visualizations %}
            <img src="{{ viz }}" style="max-width: 100%; margin: 10px 0;">
            {% endfor %}
        </div>
    </body>
    </html>
    """

    template = Template(template_str)

    # Get list of visualization files
    viz_files = [
        os.path.join("..", VIZ_DIR, f)
        for f in os.listdir(VIZ_DIR)
        if f.endswith(".png")
    ]

    # Generate HTML
    html_content = template.render(
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        price_table=price_data.to_html(classes="dataframe"),
        arb_table=arb_opportunities.to_html(classes="dataframe"),
        visualizations=viz_files,
    )

    # Save report
    report_path = os.path.join(
        REPORT_DIR,
        f'price_analysis_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.html',
    )
    with open(report_path, "w") as f:
        f.write(html_content)

    return report_path


def main():
    """Main entry point of the script"""
    try:
        logger.info("Starting price analysis")

        # Get price data (using existing functionality)
        df = analyze_prices()

        if df.empty:
            logger.warning("No price data found")
            return

        # Save results
        save_results(df)

        # Find arbitrage opportunities
        opportunities = find_arbitrage_opportunities(df)

        # Generate visualizations
        generate_visualizations(df)

        # Generate report
        report_path = generate_html_report(df, opportunities)

        # Display summary
        print("\nAnalysis Summary:")
        print(
            f"- Analyzed {len(df)} price points across {len(df['token'].unique())} tokens"
        )
        print(f"- Found {len(opportunities)} potential arbitrage opportunities")
        print(f"- Report generated at: {report_path}")
        print("\nArbitrage Opportunities:")
        if not opportunities.empty:
            print(opportunities.to_string(index=False))
        else:
            print("No significant arbitrage opportunities found")

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
    finally:
        save_cache()


if __name__ == "__main__":
    main()
