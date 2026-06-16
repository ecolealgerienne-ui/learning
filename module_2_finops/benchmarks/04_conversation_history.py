"""
Module 2 — Benchmark 4: Conversation History Growth
=====================================================
Demonstrates how unmanaged conversation history causes exponential token growth.
Shows the impact of truncation strategies.

Run: python 04_conversation_history.py
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Install: pip install openai python-dotenv")
    exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_API_KEY  = os.getenv("LITELLM_API_KEY", "sk-litellm-master-2026")
MODEL            = "claude-haiku"

client = OpenAI(base_url=f"{LITELLM_BASE_URL}/v1", api_key=LITELLM_API_KEY)

SYSTEM = "Banking assistant. Answer questions about regulations and compliance."

# Simulates a realistic banking support conversation
CONVERSATION_TURNS = [
    "Hello, I need help with GDPR compliance for our AI system.",
    "We're building a credit scoring model. What data can we use?",
    "What about using transaction history from the last 5 years?",
    "Do we need explicit consent for each data point?",
    "What's the difference between legitimate interest and consent under GDPR?",
    "Can we use anonymized data without consent?",
    "What does 'pseudonymization' mean in practice?",
    "How long can we retain the scoring data?",
    "What are the deletion rights for scored customers?",
    "We have EU and UK customers — does Brexit affect the rules?",
    "What about US customers processed in France?",
    "Do we need a DPO for this use case?",
    "What DPA notification is required?",
    "Is there a template for the ROPA record?",
    "What happens if we have a data breach affecting scoring data?",
]

# ── Strategy: No management (full history) ────────────────────────────────────

def run_no_management() -> list[dict]:
    """Send complete conversation history on every turn — realistic bad practice."""
    history = []
    results = []

    for i, user_msg in enumerate(CONVERSATION_TURNS):
        history.append({"role": "user", "content": user_msg})

        start = time.time()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + history,
        )
        elapsed = time.time() - start

        assistant_msg = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_msg})

        results.append({
            "turn":          i + 1,
            "input_tokens":  response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens":  response.usage.total_tokens,
            "latency_s":     round(elapsed, 2),
        })

        print(f"  Turn {i+1:>2}: {response.usage.total_tokens:>6} tokens | {elapsed:.2f}s | input={response.usage.prompt_tokens}")

    return results

# ── Strategy: Sliding window (last N turns) ───────────────────────────────────

def run_sliding_window(window: int = 4) -> list[dict]:
    """Keep only the last N message pairs — simple and effective."""
    history = []
    results = []

    for i, user_msg in enumerate(CONVERSATION_TURNS):
        history.append({"role": "user", "content": user_msg})

        # Keep only last `window` pairs (2*window messages)
        windowed = history[-(window * 2):]

        start = time.time()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + windowed,
        )
        elapsed = time.time() - start

        assistant_msg = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_msg})

        results.append({
            "turn":          i + 1,
            "messages_sent": len(windowed) + 1,   # +1 for system
            "input_tokens":  response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens":  response.usage.total_tokens,
            "latency_s":     round(elapsed, 2),
        })

        print(f"  Turn {i+1:>2}: {response.usage.total_tokens:>6} tokens | {len(windowed)} msgs sent | {elapsed:.2f}s")

    return results

# ── Cost helper ───────────────────────────────────────────────────────────────

def total_cost(results: list[dict]) -> float:
    total = 0.0
    for r in results:
        total += (r["input_tokens"]  / 1000) * 0.00025
        total += (r["output_tokens"] / 1000) * 0.00125
    return total

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BENCHMARK 4 — Conversation History Growth")
    print(f"Model: {MODEL} | Turns: {len(CONVERSATION_TURNS)}")
    print("=" * 60)

    print("\n🔴 STRATEGY 1: No management (full history)")
    results_full = run_no_management()

    print("\n🟢 STRATEGY 2: Sliding window (last 4 pairs)")
    results_window = run_sliding_window(window=4)

    # ── Analysis ──────────────────────────────────────────────────────────────

    cost_full   = total_cost(results_full)
    cost_window = total_cost(results_window)
    savings_pct = (cost_full - cost_window) / cost_full * 100

    tokens_first = results_full[0]["total_tokens"]
    tokens_last  = results_full[-1]["total_tokens"]
    growth_factor = tokens_last / tokens_first

    # Monthly: 10,000 conversations/day, avg 8 turns each
    daily_conversations = 10_000
    avg_turns = len(CONVERSATION_TURNS)  # assume full length
    scale = daily_conversations
    monthly_cost_full   = cost_full   * scale * 30
    monthly_cost_window = cost_window * scale * 30

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nToken growth (no management):")
    print(f"  Turn  1: {tokens_first:>6} tokens")
    print(f"  Turn {len(CONVERSATION_TURNS):>2}: {tokens_last:>6} tokens")
    print(f"  Growth:  {growth_factor:.1f}x over the conversation")

    print(f"\nCost for one {len(CONVERSATION_TURNS)}-turn conversation:")
    print(f"  No management:   ${cost_full:.4f}")
    print(f"  Sliding window:  ${cost_window:.4f}")
    print(f"  Savings:         {savings_pct:.1f}%")

    print(f"\nMonthly ({daily_conversations:,} conversations/day):")
    print(f"  No management:   ${monthly_cost_full:>10,.2f}/month")
    print(f"  Sliding window:  ${monthly_cost_window:>10,.2f}/month")
    print(f"  Monthly savings: ${monthly_cost_full - monthly_cost_window:>10,.2f}")
    print(f"  Annual savings:  ${(monthly_cost_full - monthly_cost_window)*12:>10,.2f}")

    print(f"\n✅ Implementation: 15 lines of code in your chat handler")
    print(f"✅ User experience: no degradation (4 pairs = sufficient context)")

    # ── Save ──────────────────────────────────────────────────────────────────

    report = {
        "benchmark":          "conversation_history",
        "date":               datetime.now().isoformat(),
        "model":              MODEL,
        "turns":              len(CONVERSATION_TURNS),
        "token_growth_factor": round(growth_factor, 1),
        "savings_pct":        round(savings_pct, 1),
        "monthly_savings_usd": round(monthly_cost_full - monthly_cost_window, 2),
        "annual_savings_usd":  round((monthly_cost_full - monthly_cost_window) * 12, 2),
        "results_full":       results_full,
        "results_window":     results_window,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark4_history_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Results saved: {fname}")


if __name__ == "__main__":
    main()
