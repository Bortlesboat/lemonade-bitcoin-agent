#!/usr/bin/env python3
"""Bitcoin Agent, Locally — AI-powered Bitcoin analysis with AMD Lemonade."""

import json
import os
import sys

from openai import OpenAI

from tools import TOOLS, execute_tool

# ── Configuration ────────────────────────────────────────────────────────

LEMONADE_URL = os.environ.get("LEMONADE_URL", "http://localhost:13305/api/v1")
MODEL = os.environ.get("LEMONADE_MODEL", "Llama-3.2-3B-Instruct-GGUF")
MAX_ITERATIONS = 10

SYSTEM_PROMPT = """\
You are a Bitcoin network analyst with access to real-time Bitcoin data.

Rules:
- ALWAYS call a tool before answering any Bitcoin question. Never guess.
- Call ONE tool at a time. After receiving results, either call another tool or answer.
- Be concise. Lead with the data, then add brief analysis.
- Format numbers clearly: use commas for large numbers, 2 decimal places for prices.
"""

# ── ANSI colors ──────────────────────────────────────────────────────────

CYAN = "\033[36m"
GREEN = "\033[32m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_tool_call(name: str, args: dict):
    """Show the tool call in the terminal."""
    args_str = json.dumps(args) if args else ""
    print(f"  {DIM}[tool] {name}({args_str}){RESET}")


def run_agent(client: OpenAI, messages: list) -> str:
    """Run the agentic loop: send → tool calls → execute → repeat.

    After tool data is collected, the next call omits the tools parameter
    so the model produces a text summary instead of more tool calls.
    Small local models generate much better responses this way.
    """
    tool_rounds = 0

    for _ in range(MAX_ITERATIONS):
        kwargs = {"model": MODEL, "messages": messages, "temperature": 0.1}

        # Offer tools only on the first call. After collecting tool data,
        # omit tools to force the model to produce a text summary.
        # Small models get stuck in loops if tools stay available.
        if tool_rounds == 0:
            kwargs["tools"] = TOOLS

        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as e:
            err_msg = str(e)
            if "Failed to parse" in err_msg and tool_rounds > 0:
                # Model tried parallel tool calls and the backend choked.
                # Drop tools and ask for a text summary instead.
                kwargs.pop("tools", None)
                try:
                    response = client.chat.completions.create(**kwargs)
                except Exception as e2:
                    return f"Error: {e2}"
            else:
                return f"Error calling Lemonade: {e}"

        if not response.choices:
            if tool_rounds > 0:
                # Model returned empty after tools — retry without tools
                kwargs.pop("tools", None)
                try:
                    response = client.chat.completions.create(**kwargs)
                except Exception as e:
                    return f"Error: {e}"
                if not response.choices:
                    return "(no response from model)"
            else:
                return "(no response from model)"

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                except json.JSONDecodeError:
                    args = {}

                print_tool_call(name, args)
                result = execute_tool(name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            tool_rounds += 1
            continue

        return msg.content or "(no response)"

    return "(max iterations reached)"


def main():
    print(f"{BOLD}Bitcoin Agent, Locally{RESET}")
    print(f"{DIM}Powered by AMD Lemonade + Satoshi API{RESET}")
    print(f"{DIM}Model: {MODEL} @ {LEMONADE_URL}{RESET}")
    print(f"{DIM}Type 'quit' to exit.{RESET}\n")

    client = OpenAI(base_url=LEMONADE_URL, api_key="lemonade")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input(f"{GREEN}you > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        messages.append({"role": "user", "content": user_input})
        print(f"{CYAN}agent > {RESET}", end="", flush=True)

        answer = run_agent(client, messages)
        print(f"{answer}\n")

        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
