"""
Configuration file for the price analysis tool.
Contains token configurations, network settings, and DEX mappings.
"""

from typing import Dict, List

# Token Configuration
TOKENS = ["wrapped-bitcoin", "lbtc", "tether"]  # wBTC, LBTC, USDT (CoinGecko IDs)

# Network Configuration
NETWORKS = [
    "ethereum",
    "arbitrum",
    "optimism",
    "base",
    "polygon-pos",
    "avalanche",
    "binance-smart-chain",
    "gnosis",
    "fantom",
    "metis",
    "ronin",
    "okx-chain",
    "zksync",
    "linea",
    "polygon-zkevm",
    "mantle",
    "scroll",
    "blast",
    "telos",
    "celo",
]

# DEX Configuration by Network
DEXES: Dict[str, List[str]] = {
    "ethereum": ["uniswap_v3", "balancer", "sushiswap"],
    "arbitrum": ["gmx", "uniswap_v3", "camelot"],
    "optimism": ["velodrome", "uniswap_v3", "synthetix"],
    "base": ["uniswap_v3", "aerodrome", "leetswap"],
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

# Base Token Configuration
BASE_TOKENS = {
    "ethereum": "weth",
    "arbitrum": "weth",
    "optimism": "weth",
    "base": "weth",
    "polygon-pos": "wmatic",
    "avalanche": "wavax",
    "binance-smart-chain": "wbnb",
    "gnosis": "wxdai",
    "fantom": "wftm",
    "metis": "wmetis",
    "ronin": "wron",
    "okx-chain": "wokt",
    "zksync": "weth",
    "linea": "weth",
    "polygon-zkevm": "weth",
    "mantle": "wmnt",
    "scroll": "weth",
    "blast": "weth",
    "telos": "wtlos",
    "celo": "wcelo",
}

# Base Token Addresses (examples for main networks)
BASE_TOKEN_ADDRESSES = {
    "ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
    "binance-smart-chain": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",  # WBNB
    "polygon-pos": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",  # WMATIC
    # Add more addresses as needed
}

# TVL Data (in billions/millions where available)
TVL_DATA = {
    "ethereum": {
        "uniswap_v3": 1.602,  # $1.602B
        "balancer": 0.802980,  # $802.980M
        "sushiswap": 0.789729,  # $789.729M
    },
    "binance-smart-chain": {
        "pancakeswap_v3": 3.782,  # $3.782B
        "biswap": 0.508456,  # $508.456M
        "gambit": 0.090420,  # $90.420M
    },
    "fantom": {
        "spookyswap": 0.009674,  # $9.674M
        "spiritswap": 0.001537,  # $1.537M
        "hyperswap": 0.001516,  # $1.516M
    },
}

# Rate Limiting Configuration
RATE_LIMIT_CALLS = 30  # Maximum calls per minute
RATE_LIMIT_WAIT = 2  # Seconds to wait between calls
