# Lemonade Bitcoin Agent Copilot Instructions

This repo is a local Bitcoin agent powered by AMD Lemonade and Satoshi API.

## Rules

- Keep the agent local-first: the LLM runs through Lemonade, and Bitcoin data comes from Satoshi API.
- Use `tools.py` for Bitcoin data access instead of adding ad hoc HTTP calls in the agent loop.
- Keep `SATOSHI_API_URL` configurable; default hosted API is `https://bitcoinsapi.com/api/v1`.
- When adding new Bitcoin tools, prefer stable Satoshi API `/api/v1` paths.
- For broader agent integrations, use the Satoshi API guide: https://github.com/Bortlesboat/bitcoin-api/blob/main/docs/AGENT_INTEGRATION.md

## Useful Satoshi API Links

- Docs: https://bitcoinsapi.com/docs
- Agent overview: https://bitcoinsapi.com/llms.txt
- MCP setup: https://bitcoinsapi.com/mcp-setup
- x402 first paid call: https://bitcoinsapi.com/x402/start
