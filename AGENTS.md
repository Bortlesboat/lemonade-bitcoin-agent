# Lemonade Bitcoin Agent Instructions

## What This Is

A local Bitcoin question-answering agent using AMD Lemonade for inference and Satoshi API for live Bitcoin data.

## Rules

- Keep the LLM local through Lemonade.
- Keep Bitcoin data access in `tools.py`.
- Use canonical Satoshi API `/api/v1` paths.
- Keep `SATOSHI_API_URL` configurable and default it to the hosted Satoshi API.
- For MCP or x402 expansion, reference the main Satoshi API integration guide: https://github.com/Bortlesboat/bitcoin-api/blob/main/docs/AGENT_INTEGRATION.md
