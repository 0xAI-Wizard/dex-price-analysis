"""
Configuration file for the price analysis tool.
Contains token configurations, network settings, and DEX mappings.
"""

from typing import Dict, List

# Token Configuration
TOKENS = [
    "wrapped-bitcoin",  # Wrapped Bitcoin
    "lombard-staked-btc",  # LBTC (Lombard)
    "ethereum",  # Ethereum
    "tether",
    "usd-coin",
]  # wBTC, LBTC, USDT (CoinGecko IDs)

# Network Configuration
NETWORKS = [
    "ethereum",
    "arbitrum",
    "optimism",
    "base",
    "bob-network",
    # "polygon-pos",
    # "avalanche",
    # "binance-smart-chain",
    # "gnosis",
    # "fantom",
    # "metis",
    # "ronin",
    # "okx-chain",
    # "zksync",
    # "linea",
    # "polygon-zkevm",
    # "mantle",
    # "scroll",
    # "blast",
    # "telos",
    # "celo",
]

# DEX Configuration by Network
DEXES: Dict[str, List[str]] = {
    "bob-network": ["uniswap-v3"],
    "ethereum": ["uniswap-v3", "balancer", "sushiswap"],
    "arbitrum": ["gmx", "uniswap-v3", "camelot"],
    "optimism": ["velodrome", "uniswap-v3", "synthetix"],
    "base": ["uniswap-v3", "aerodrome", "leetswap"],
    "polygon-pos": ["quickswap_v3", "sushiswap_v3", "apeswap"],
    "avalanche": ["trader_joe", "pangolin", "platypus"],
    "binance-smart-chain": ["pancakeswap_v3", "biswap", "gambit"],
    "gnosis": ["paraswap", "matcha", "oneinch"],
    "fantom": ["spookyswap", "spiritswap", "hyperswap"],
    "metis": ["metisswap", "alchemist", "metisdao"],
    "ronin": ["katana", "cow_protocol", "sky_mavis"],
    "okx-chain": ["okx_dex", "mdex", "dodo"],
    "zksync": ["syncswap", "mute", "pento"],
    "linea": ["linea_dex", "uniswap_v3", "curve"],
    "polygon-zkevm": ["balancer", "uniswap_v3", "sushiswap_v3"],
    "mantle": ["mantle_dex", "curve", "balancer"],
    "scroll": ["scroll_dex", "uniswap_v3", "sushiswap_v3"],
    "blast": ["blast_dex", "uniswap_v3", "curve"],
    "telos": ["telos_dex", "alcor", "dexalot"],
    "celo": ["ubeswap", "curve", "sushiswap_v3"],
}

# Rate Limiting Configuration
RATE_LIMIT_CALLS = 30  # Maximum calls per minute
RATE_LIMIT_WAIT = 2  # Seconds to wait between calls
