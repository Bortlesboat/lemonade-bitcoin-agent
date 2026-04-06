"""Bitcoin tools for the Lemonade agent — schemas + execution."""

import json
import os
import requests

API_BASE = os.environ.get("SATOSHI_API_URL", "https://bitcoinsapi.com/api/v1")
_SESSION = requests.Session()
_SESSION.headers["User-Agent"] = "lemonade-bitcoin-agent/1.0"
MAX_RESPONSE_CHARS = 3000


# ── Tool Schemas (OpenAI function-calling format) ────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_bitcoin_price",
            "description": "Get the current Bitcoin price in USD and other currencies.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fee_recommendation",
            "description": "Get a human-readable fee recommendation with estimated rates for different priority levels (fastest, half-hour, hour, economy) in sat/vB.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fee_estimates",
            "description": "Get fee estimates for all standard confirmation targets (1, 3, 6, 25, 144 blocks) in sat/vB.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_block",
            "description": "Analyze the most recent Bitcoin block: transaction count, size, weight, fees, mining pool.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_block_by_height",
            "description": "Analyze a specific Bitcoin block by its height number. Returns tx count, size, weight, fees, mining pool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "height": {
                        "type": "integer",
                        "description": "Block height number (e.g. 0 for genesis, 840000 for latest halving)",
                    }
                },
                "required": ["height"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_block_height",
            "description": "Get the current Bitcoin blockchain tip height (latest block number).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mempool_info",
            "description": "Get raw mempool statistics: transaction count, total size in bytes, memory usage.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mempool_congestion",
            "description": "Get detailed mempool analysis: fee rate buckets, congestion level (low/medium/high), next-block minimum fee, transaction count breakdown.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mining_info",
            "description": "Get Bitcoin mining summary: network hashrate, current difficulty, next retarget estimate.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_network_info",
            "description": "Get Bitcoin network info: protocol version, connected peers count, relay fee.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_supply_info",
            "description": "Get Bitcoin supply data: circulating supply, inflation rate, next halving countdown, current block subsidy.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_difficulty_adjustment",
            "description": "Get difficulty epoch progress: blocks until next adjustment, estimated date, projected difficulty change percentage.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# ── Tool Execution ───────────────────────────────────────────────────────

_ENDPOINTS = {
    "get_bitcoin_price": "/prices",
    "get_fee_recommendation": "/fees/recommended",
    "get_fee_estimates": "/fees",
    "get_latest_block": "/blocks/latest",
    "get_block_height": "/blocks/tip/height",
    "get_mempool_info": "/mempool/info",
    "get_mempool_congestion": "/mempool",
    "get_mining_info": "/mining",
    "get_network_info": "/network",
    "get_supply_info": "/supply",
    "get_difficulty_adjustment": "/network/difficulty",
}


def execute_tool(name: str, arguments: dict) -> str:
    """Call the Satoshi API and return the JSON response as a string."""
    # Special case: block by height needs path parameter
    if name == "get_block_by_height":
        height = arguments.get("height", 0)
        url = f"{API_BASE}/blocks/{height}"
    elif name in _ENDPOINTS:
        url = f"{API_BASE}{_ENDPOINTS[name]}"
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        resp = _SESSION.get(url, timeout=15)
        resp.raise_for_status()
        text = json.dumps(resp.json(), indent=2)
        if len(text) > MAX_RESPONSE_CHARS:
            text = text[:MAX_RESPONSE_CHARS] + "\n... (truncated)"
        return text
    except requests.RequestException as e:
        return json.dumps({"error": str(e)})
