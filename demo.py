#!/usr/bin/env python3
"""Automated demo — runs preset queries with typewriter effect for screen recording."""

import json
import os
import sys
import time

import requests

from tools import TOOLS, execute_tool

LEMONADE_URL = os.environ.get("LEMONADE_URL", "http://localhost:13305/api/v1")
MODEL = os.environ.get("LEMONADE_MODEL", "Llama-3.2-3B-Instruct-GGUF")

SYSTEM = (
    "You are a Bitcoin network analyst. Call ONE tool at a time. Never guess. "
    "After receiving tool data, summarize it clearly and concisely. "
    "Format numbers with commas. Keep answers under 100 words."
)

# ANSI
CYAN = "\033[36m"
GREEN = "\033[32m"
DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[33m"

QUERIES = [
    "What's the current Bitcoin price?",
    "What are transaction fees like? Should I send now or wait?",
    "Analyze the latest block that was mined.",
    "How congested is the mempool right now?",
    "Tell me about the genesis block — block 0.",
]


def typewriter(text, delay=0.03):
    """Print text character by character for demo effect."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)


def run_query(question):
    """Run one query through the agent, return (answer, tools_called, perf)."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    tool_rounds = 0
    tools_called = []
    t0 = time.time()

    for _ in range(5):
        kwargs = {"model": MODEL, "messages": messages, "temperature": 0.1}
        if tool_rounds == 0:
            kwargs["tools"] = TOOLS

        try:
            r = requests.post(
                f"{LEMONADE_URL}/chat/completions", json=kwargs, timeout=120
            )
            d = r.json()
        except Exception as e:
            return f"Error: {e}", [], {}

        if "error" in d:
            if tool_rounds > 0:
                kwargs.pop("tools", None)
                r = requests.post(
                    f"{LEMONADE_URL}/chat/completions", json=kwargs, timeout=120
                )
                d = r.json()
            else:
                return f"Error: {d['error']}", [], {}

        if not d.get("choices"):
            if tool_rounds > 0:
                kwargs.pop("tools", None)
                r = requests.post(
                    f"{LEMONADE_URL}/chat/completions", json=kwargs, timeout=120
                )
                d = r.json()
            if not d.get("choices"):
                return "(no response)", [], {}

        msg = d["choices"][0]["message"]

        if msg.get("tool_calls"):
            messages.append(msg)
            for tc in msg["tool_calls"]:
                name = tc["function"]["name"]
                args = json.loads(tc["function"].get("arguments", "{}") or "{}")
                tools_called.append(name)
                result = execute_tool(name, args)
                messages.append(
                    {"role": "tool", "tool_call_id": tc["id"], "content": result}
                )
            tool_rounds += 1
        else:
            elapsed = time.time() - t0
            timings = d.get("timings", {})
            perf = {
                "elapsed": round(elapsed, 1),
                "tok_s": timings.get("predicted_per_second", 0),
                "prompt_tok_s": timings.get("prompt_per_second", 0),
            }
            return msg.get("content", ""), tools_called, perf

    return "(max iterations)", tools_called, {}


def main():
    print()
    print(f"  {BOLD}Bitcoin Agent, Locally{RESET}")
    print(f"  {DIM}Powered by AMD Lemonade + Satoshi API{RESET}")
    print(f"  {DIM}Model: {MODEL} @ {LEMONADE_URL}{RESET}")
    print()
    time.sleep(1.5)

    for i, q in enumerate(QUERIES):
        # Typewriter the question
        sys.stdout.write(f"  {GREEN}you > {RESET}")
        typewriter(q, delay=0.04)
        print()
        time.sleep(0.5)

        answer, tools, perf = run_query(q)

        # Show tool calls
        for t in tools:
            print(f"  {DIM}  [tool] {t}(){RESET}")
            time.sleep(0.3)

        # Typewriter the answer
        print()
        sys.stdout.write(f"  {CYAN}agent > {RESET}")
        typewriter(answer, delay=0.015)
        print()

        # Performance stats
        if perf.get("tok_s"):
            print(
                f"  {DIM}  [{perf['elapsed']}s | "
                f"{perf['tok_s']:.0f} tok/s generation | "
                f"{perf['prompt_tok_s']:.0f} tok/s prompt]{RESET}"
            )

        print()
        time.sleep(2.0)

    print(f"  {DIM}All queries answered using real-time Bitcoin data.{RESET}")
    print(f"  {DIM}No cloud LLM. No API keys. Everything runs locally.{RESET}")
    print()


if __name__ == "__main__":
    main()
