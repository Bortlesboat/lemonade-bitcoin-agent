# Bitcoin Agent, Locally

A fully local AI agent that answers Bitcoin questions using real-time network data — powered by [AMD Lemonade](https://github.com/lemonade-sdk/lemonade) and the [Satoshi API](https://bitcoinsapi.com).

No cloud LLM. No API keys. Your Bitcoin questions stay on your machine.

## What It Does

Ask natural language questions about Bitcoin and get answers backed by live data:

```
you > What are fees like right now?
  [tool] get_fee_recommendation()
  [tool] get_mempool_congestion()
agent > Fees are very low right now. A standard transaction at 1.0 sat/vB
        should confirm within a few blocks. The mempool has only 2,300 transactions
        — well below congestion levels. Great time to send.

you > Analyze the latest block
  [tool] get_latest_block()
agent > Block 943,955 was mined by Foundry USA. It contains 1,847 transactions
        with a total weight of 3.99 MWU (99.8% full). Median fee rate: 2.1 sat/vB.
        Total fees collected: 0.028 BTC.

you > Should I send a transaction now or wait?
  [tool] get_fee_recommendation()
  [tool] get_mempool_congestion()
  [tool] get_bitcoin_price()
agent > Send now. Fees are at 1.0 sat/vB — the minimum relay fee. A typical
        2-input, 2-output transaction would cost ~140 sats ($0.10). The mempool
        is nearly empty. You won't find cheaper fees than this.
```

The agent decides which tools to call, fetches live data, and synthesizes a response — all running locally on your hardware.

## Architecture

```
┌──────────┐     ┌──────────────────────┐     ┌──────────────┐     ┌─────────────┐
│  You     │────▶│  AMD Lemonade        │────▶│  tools.py    │────▶│ Satoshi API │
│  (CLI)   │◀────│  (local LLM)         │◀────│  (executor)  │◀────│ (live data) │
└──────────┘     │  localhost:13305     │     └──────────────┘     └─────────────┘
                 │  OpenAI-compatible   │                                │
                 └──────────────────────┘                          Bitcoin Network
```

- **LLM**: Lemonade runs the model locally (Vulkan for any GPU, ROCm for AMD, or CPU)
- **Tools**: 12 Bitcoin tools defined as OpenAI function-calling schemas
- **Data**: [Satoshi API](https://bitcoinsapi.com) provides real-time Bitcoin network data
- **Privacy**: Nothing leaves your machine except the API data calls

## Setup

### 1. Install AMD Lemonade

Download from [lemonade-server.ai](https://lemonade-server.ai) and install. It runs as a local service on port 13305.

### 2. Pull a model

```bash
lemonade pull llama-3.1-8b-instruct
```

Any model that supports tool/function calling will work. Larger models (13B+) give better results if you have the VRAM.

### 3. Install dependencies

```bash
git clone https://github.com/Bortlesboat/lemonade-bitcoin-agent.git
cd lemonade-bitcoin-agent
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

## Available Tools

The agent has access to 12 real-time Bitcoin data tools:

| Tool | What it does |
|------|-------------|
| `get_bitcoin_price` | Current BTC price in USD and other currencies |
| `get_fee_recommendation` | Human-readable fee advice with priority rates |
| `get_fee_estimates` | Fee rates for 1/3/6/25/144 block targets |
| `get_latest_block` | Analysis of the most recent block |
| `get_block_by_height` | Analyze any historical block |
| `get_block_height` | Current chain tip height |
| `get_mempool_info` | Mempool size and memory usage |
| `get_mempool_congestion` | Fee buckets and congestion level |
| `get_mining_info` | Hashrate, difficulty, next retarget |
| `get_network_info` | Peers, protocol version, relay fee |
| `get_supply_info` | Circulating supply, inflation, halving countdown |
| `get_difficulty_adjustment` | Next difficulty change estimate |

The agent autonomously decides which tools to call based on your question, and can chain multiple tools together for complex analysis.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LEMONADE_URL` | `http://localhost:13305/api/v1` | Lemonade API endpoint |
| `LEMONADE_MODEL` | `llama-3.1-8b-instruct` | Model to use |
| `SATOSHI_API_URL` | `https://bitcoinsapi.com/api/v1` | Bitcoin data API |

## How It Works

The agent is ~120 lines of Python using the standard OpenAI client library. Since Lemonade exposes an OpenAI-compatible API, we just point the client at `localhost:13305`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:13305/api/v1", api_key="lemonade")

response = client.chat.completions.create(
    model="llama-3.1-8b-instruct",
    messages=messages,
    tools=TOOLS,          # 12 Bitcoin data tools
    temperature=0.1,
)
```

When the model decides it needs data, it returns `tool_calls` instead of text. We execute those calls against the Satoshi API, feed the results back, and let the model synthesize a final answer. This loop repeats until the model has all the data it needs.

No frameworks. No LangChain. No abstractions. Just the OpenAI client + requests.

## Why Lemonade?

[AMD Lemonade](https://github.com/lemonade-sdk/lemonade) makes local AI dead simple:

- **One install, one API**: MSI on Windows, deb/rpm/snap on Linux. It just works.
- **OpenAI-compatible**: Any code written for the OpenAI API works with zero changes.
- **Hardware-agnostic**: Vulkan backend runs on any GPU. ROCm for AMD. Metal for Mac. CPU fallback.
- **Tool calling support**: Function calling works out of the box — critical for agentic workflows.
- **Auto-managed**: Runs as a system service, handles model loading/caching automatically.

For this project, Lemonade meant we could focus entirely on the Bitcoin agent logic without touching model serving, quantization, or GPU configuration.

## Why Local?

Running your Bitcoin analysis agent locally means:

- **Privacy**: Your financial questions never leave your machine
- **Speed**: No network round-trip to a cloud LLM — just local inference
- **Cost**: No per-token charges — run as many queries as you want
- **Reliability**: Works offline (except for the Bitcoin data API calls)
- **Control**: Choose your model, tune your prompts, own your stack

## Credits

- [AMD Lemonade](https://github.com/lemonade-sdk/lemonade) — local AI runtime
- [Satoshi API](https://bitcoinsapi.com) — real-time Bitcoin network data
- [bitcoin-mcp](https://github.com/Bortlesboat/bitcoin-mcp) — the MCP server that inspired the tool set

## License

MIT
