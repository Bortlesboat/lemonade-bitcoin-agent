# Bitcoin Agent, Locally

A fully local AI agent that answers Bitcoin questions using real-time network data — powered by [AMD Lemonade](https://github.com/lemonade-sdk/lemonade) and the [Satoshi API](https://bitcoinsapi.com).

No cloud LLM. No API keys. Your Bitcoin questions stay on your machine.

## Demo

[![Demo Video](https://img.youtube.com/vi/OBSauHpRmyg/maxresdefault.jpg)](https://www.youtube.com/watch?v=OBSauHpRmyg)

Real output from a live session running Llama 3.2 3B on AMD Lemonade (Vulkan backend, RTX 3060):

```
you > What's the current Bitcoin price?
  [tool] get_bitcoin_price()

agent > The current Bitcoin price is approximately $69.9K USD, with prices
        in other currencies: 60.5K EUR, 52.8K GBP, 97.2K CAD, 101K AUD.
        The price has increased by 3.35% over the past 24 hours.

  [2.8s | 88 tok/s generation | 2622 tok/s prompt]
```

```
you > What are transaction fees like? Should I send now or wait?
  [tool] get_fee_recommendation()

agent > The current transaction fees are very low, with an estimated fee of
        1.0 sat/vB, which should confirm within a day. This is a good time
        to send transactions — fees are at the minimum relay rate.

  [8.9s | 94 tok/s generation | 2881 tok/s prompt]
```

```
you > Analyze the latest block that was mined.
  [tool] get_latest_block()

agent > Block 943,959 — 4,367 transactions, weight 3,993,957 (99.8% full).
        Total fees collected: 0.016 BTC. The top fee transactions paid
        100 sat/vB, while the median fee rate was 0.14 sat/vB.

  [5.8s | 89 tok/s generation | 3516 tok/s prompt]
```

```
you > How congested is the mempool?
  [tool] get_mempool_congestion()

agent > The mempool is "low" congestion — 370 transactions, 115,853 bytes.
        Most transactions are paying 1-5 sat/vB. The next block's minimum
        fee is 0.0 sat/vB. Great conditions for sending.

  [5.6s | 92 tok/s generation | 1435 tok/s prompt]
```

```
you > Tell me about the genesis block — block 0.
  [tool] get_block_by_height()

agent > The genesis block was created on January 3, 2009 by Satoshi Nakamoto.
        It contains a single transaction transferring 50 BTC. Its hash:
        000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f

  [8.9s | 89 tok/s generation | 1097 tok/s prompt]
```

The agent autonomously picks which tool to call, fetches live data from the Bitcoin network, and synthesizes a human-readable response — all running locally.

## How It Works

```
┌──────────┐     ┌──────────────────────┐     ┌──────────────┐     ┌─────────────┐
│  You     │────▶│  AMD Lemonade        │────▶│  tools.py    │────▶│ Satoshi API │
│  (CLI)   │◀────│  (local LLM)         │◀────│  (executor)  │◀────│ (live data) │
└──────────┘     │  localhost:13305     │     └──────────────┘     └─────────────┘
                 │  OpenAI-compatible   │                                │
                 └──────────────────────┘                          Bitcoin Network
```

The entire agent is **~130 lines of Python** using the standard `openai` library. Since Lemonade exposes an OpenAI-compatible API, we just point the client at `localhost:13305`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:13305/api/v1", api_key="lemonade")

response = client.chat.completions.create(
    model="Llama-3.2-3B-Instruct-GGUF",
    messages=messages,
    tools=TOOLS,          # 12 Bitcoin data tools
    temperature=0.1,
)
```

When the model decides it needs data, it returns `tool_calls` instead of text. We execute those against the [Satoshi API](https://bitcoinsapi.com), feed the results back, and the model synthesizes a final answer.

No frameworks. No LangChain. No abstractions. Just the OpenAI client + requests.

## Setup

### 1. Install AMD Lemonade

Download from [lemonade-server.ai](https://lemonade-server.ai) and install. It runs as a local service.

### 2. Pull a model

```bash
lemonade-server pull Llama-3.2-3B-Instruct-GGUF
```

Any GGUF model that supports tool calling will work. The 3B model runs at ~90 tok/s on Vulkan.

If you're starting on a CPU-first AMD box, `Llama-3.2-1B-Instruct-GGUF` is a safer first pull for a quick validation pass:

```bash
lemonade-server pull Llama-3.2-1B-Instruct-GGUF
```

### 3. Install and run

```bash
git clone https://github.com/Bortlesboat/lemonade-bitcoin-agent.git
cd lemonade-bitcoin-agent
pip install -r requirements.txt
python main.py
```

### Run the automated demo

```bash
python demo.py
```

This runs 5 preset queries with typewriter effect — perfect for screen recording.

## Available Tools

| Tool | What it returns |
|------|----------------|
| `get_bitcoin_price` | BTC/USD + 5 currencies, 24h change |
| `get_fee_recommendation` | Human-readable fee advice with priority rates |
| `get_fee_estimates` | Fee rates for 1/3/6/25/144 block targets |
| `get_latest_block` | Tx count, size, weight, fees, top transactions |
| `get_block_by_height` | Any historical block by height number |
| `get_block_height` | Current chain tip height |
| `get_mempool_info` | Mempool size, bytes, memory usage |
| `get_mempool_congestion` | Fee buckets, congestion level, next-block min fee |
| `get_mining_info` | Network hashrate, difficulty, next retarget |
| `get_network_info` | Peers, protocol version, relay fee |
| `get_supply_info` | Circulating supply, inflation rate, halving countdown |
| `get_difficulty_adjustment` | Blocks until next adjustment, projected change |

## Performance

Tested on AMD Ryzen 7 5800X3D + RTX 3060 12GB (Vulkan backend):

| Metric | Value |
|--------|-------|
| Model | Llama 3.2 3B Instruct (Q4_K_XL, 1.97 GB) |
| Generation speed | **88-94 tok/s** |
| Prompt processing | **1,097-3,516 tok/s** |
| Typical query time | **3-9 seconds** end-to-end |
| VRAM usage | ~3 GB |

Larger models (8B, 13B) work too - just set `LEMONADE_MODEL` to your preferred model name.

## AMD Validation

Additional validation on April 7, 2026 confirmed the agent flow on a second AMD machine end to end:

- Host: HP Pavilion Desktop TP01-2xxx
- CPU: AMD Ryzen 7 5700G with Radeon Graphics
- Runtime: Lemonade 10.0.1
- Backend: `llamacpp:cpu`
- Model: `Llama-3.2-1B-Instruct-GGUF`

Verified local proof:

```
tool call: get_bitcoin_price
answer: The current Bitcoin price is $68,513.
[24.5 tok/s generation | 268.5 tok/s prompt]
```

This shows the Bitcoin tool-calling loop works on an AMD client machine, not just on the original RTX 3060 demo box.

One caveat: on this specific Ryzen 7 5700G CPU setup, `Llama-3.2-3B-Instruct-GGUF` produced corrupted `GGGG` output on the CPU backend, while the 1B model was stable. So the current AMD-silicon proof uses the working 1B model, and the higher-throughput 3B numbers above remain the Vulkan demo from the main submission machine.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LEMONADE_URL` | `http://localhost:13305/api/v1` | Lemonade API endpoint |
| `LEMONADE_MODEL` | `Llama-3.2-3B-Instruct-GGUF` | Model to use |
| `SATOSHI_API_URL` | `https://bitcoinsapi.com/api/v1` | Bitcoin data source |

## Why Local Matters for Bitcoin

Bitcoin users care about privacy. If you're checking fees before a transaction or analyzing your wallet activity, sending those questions to a cloud LLM means sharing your financial intent with a third party.

Running locally means:

- **Privacy** — your financial questions never leave your machine
- **Speed** — no network round-trip to a cloud LLM, just local inference
- **Cost** — no per-token charges, unlimited queries
- **Sovereignty** — you own your stack, just like you own your keys

## Why Lemonade

[AMD Lemonade](https://github.com/lemonade-sdk/lemonade) made this project trivial to build:

1. **One-line install** — MSI on Windows, snap/deb/rpm on Linux. No CUDA toolkit, no compile flags.
2. **OpenAI-compatible API** — existing code just works. Change the `base_url` and you're local.
3. **Tool calling works** — function calling out of the box, which is the entire backbone of this agent.
4. **Hardware-agnostic** — Vulkan runs on any GPU. ROCm for AMD. CPU fallback. No vendor lock-in.
5. **Model management** — `lemonade pull`, auto-caching, LRU eviction. No manual GGUF wrangling.

The total integration effort was pointing an OpenAI client at `localhost:13305` instead of `api.openai.com`. That's it.

## Project Structure

```
lemonade-bitcoin-agent/
├── main.py           # Interactive CLI agent (~130 lines)
├── demo.py           # Automated demo with typewriter effect
├── tools.py          # 12 Bitcoin tool schemas + API executor
├── requirements.txt  # openai, requests
├── LICENSE           # MIT
└── README.md
```

## Credits

- [AMD Lemonade](https://github.com/lemonade-sdk/lemonade) — local AI runtime
- [Satoshi API](https://bitcoinsapi.com) — real-time Bitcoin network data ([bitcoin-mcp](https://github.com/Bortlesboat/bitcoin-mcp))

## License

MIT
