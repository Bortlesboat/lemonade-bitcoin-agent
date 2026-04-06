#!/usr/bin/env python3
"""Bitcoin Agent, Locally — AI-powered Bitcoin analysis with AMD Lemonade."""

import json
import os
import sys

from openai import OpenAI

from tools import TOOLS, execute_tool

# ── Configuration ────────────────────────────────────────────────────────

LEMONADE_URL = os.environ.get("LEMONADE_URL", "http://localhost:13305/api/v1")
MODEL = os.environ.get("LEMONADE_MODEL", "llama-3.1-8b-instruct")
MAX_ITERATIONS = 10

SYSTEM_PROMPT = """\
You are a Bitcoin network analyst with access to real-time Bitcoin data.

Rules:
- ALWAYS use your tools to get current data before answering Bitcoin questions.
- Never guess or make up numbers — call a tool first.
- Be concise. Lead with the data, then add brief analysis.
- When a question needs multiple data points, call multiple tools.
- Format numbers clearly: use commas for large numbers, 2 decimal places for prices.
"""

# ── ANSI colors ──────────────────────────────────────────────────────────

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_tool_call(name: str, args: dict):
    """Show the tool call in the terminal."""
    args_str = json.dumps(args) if args else ""
    print(f"  {DIM}[tool] {name}({args_str}){RESET}")


def run_agent(client: OpenAI, messages: list) -> str:
    """Run the agentic loop: send → tool calls → execute → repeat."""
    for _ in range(MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                temperature=0.1,
            )
        except Exception as e:
            return f"Error calling Lemonade: {e}"

        choice = response.choices[0]
        msg = choice.message

        # If the model wants to call tools
        if msg.tool_calls:
            # Append the assistant message with tool calls
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
            continue

        # No tool calls — return the text response
        return msg.content or "(no response)"

    return "(max iterations reached — the agent got stuck in a tool-calling loop)"


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
