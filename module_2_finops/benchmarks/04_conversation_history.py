"""
Benchmark 4 — Conversation History Growth
==========================================
Shows how unmanaged history causes exponential token cost.
Compares full-history vs sliding-window strategies.
Uses MODEL_DEFAULT from .env.

Run: python 04_conversation_history.py
"""

import json, time, os
from datetime import datetime
from config import client, MODELS, DAILY_CONVERSATIONS, token_cost, print_config

MODEL = MODELS.default

SYSTEM = "Banking assistant. Answer questions about regulations and compliance."

CONVERSATION_TURNS = [
    "Hello, I need help with GDPR compliance for our AI credit scoring system.",
    "We're using transaction history from the last 5 years. Is that allowed?",
    "Do we need explicit consent for each data point we use?",
    "What's the difference between legitimate interest and consent under GDPR?",
    "Can we use anonymized data without consent?",
    "What does 'pseudonymization' mean in practice for banking?",
    "How long can we retain the credit scoring data?",
    "What are the deletion rights for customers who were scored?",
    "We have EU and UK customers — does Brexit affect the rules differently?",
    "What about US customers whose data is processed in France?",
    "Do we need a Data Protection Officer for this use case?",
    "What DPA notification is required before going live?",
    "What happens if we have a data breach affecting scoring data?",
    "Does the EU AI Act add additional requirements on top of GDPR here?",
    "What's the first thing we should do before deploying this system?",
]

def call(messages: list) -> dict:
    start = time.time()
    r = client.chat.completions.create(model=MODEL, messages=messages)
    return {
        "input":  r.usage.prompt_tokens,
        "output": r.usage.completion_tokens,
        "latency_s": round(time.time() - start, 2),
        "answer": r.choices[0].message.content,
    }

def run_full_history() -> list[dict]:
    history, results = [], []
    for i, user_msg in enumerate(CONVERSATION_TURNS):
        history.append({"role": "user", "content": user_msg})
        r = call([{"role": "system", "content": SYSTEM}] + history)
        history.append({"role": "assistant", "content": r["answer"]})
        results.append({"turn": i+1, "input": r["input"], "output": r["output"],
                        "total": r["input"]+r["output"], "latency_s": r["latency_s"]})
        print(f"  Turn {i+1:>2}: {r['input']+r['output']:>6} tokens (input={r['input']:>5}) | {r['latency_s']}s")
    return results

def run_sliding_window(window: int = 4) -> list[dict]:
    history, results = [], []
    for i, user_msg in enumerate(CONVERSATION_TURNS):
        history.append({"role": "user", "content": user_msg})
        windowed = history[-(window * 2):]
        r = call([{"role": "system", "content": SYSTEM}] + windowed)
        history.append({"role": "assistant", "content": r["answer"]})
        results.append({"turn": i+1, "msgs_sent": len(windowed)+1,
                        "input": r["input"], "output": r["output"],
                        "total": r["input"]+r["output"], "latency_s": r["latency_s"]})
        print(f"  Turn {i+1:>2}: {r['input']+r['output']:>6} tokens ({len(windowed)} msgs sent) | {r['latency_s']}s")
    return results

def total_cost(results: list[dict]) -> float:
    return sum(token_cost(MODEL, r["input"], r["output"]) for r in results)

def main():
    print("=" * 60)
    print("BENCHMARK 4 — Conversation History Growth")
    print(f"Model: {MODEL} | Turns: {len(CONVERSATION_TURNS)}")
    print_config()
    print("=" * 60)

    print("\n🔴 Full history (no management):")
    full = run_full_history()

    print("\n🟢 Sliding window (last 4 pairs):")
    windowed = run_sliding_window(window=4)

    cost_full   = total_cost(full)
    cost_window = total_cost(windowed)
    savings_pct = (cost_full - cost_window) / cost_full * 100

    growth = full[-1]["total"] / full[0]["total"]

    scale          = DAILY_CONVERSATIONS
    monthly_full   = cost_full   * scale * 30
    monthly_window = cost_window * scale * 30

    print(f"\n{'='*60}\nRESULTS\n{'='*60}")
    print(f"  Token growth (unmanaged): {growth:.1f}x  (turn 1→{len(CONVERSATION_TURNS)})")
    print(f"  Cost per conversation:")
    print(f"    Full history:    ${cost_full:.4f}")
    print(f"    Sliding window:  ${cost_window:.4f}  (−{savings_pct:.1f}%)")
    print(f"  Monthly ({scale:,} conversations/day):")
    print(f"    Full history:    ${monthly_full:>10,.2f}/month")
    print(f"    Sliding window:  ${monthly_window:>10,.2f}/month")
    print(f"    Savings:         ${monthly_full - monthly_window:>10,.2f}/month")
    print(f"    Annual:          ${(monthly_full - monthly_window)*12:>10,.2f}/year")
    print(f"  ✅ Implementation effort: ~15 lines in your chat handler")

    report = {
        "benchmark": "conversation_history", "date": datetime.now().isoformat(),
        "model": MODEL, "turns": len(CONVERSATION_TURNS),
        "token_growth_factor": round(growth, 1),
        "savings_pct": round(savings_pct, 1),
        "monthly_savings_usd": round(monthly_full - monthly_window, 2),
        "annual_savings_usd":  round((monthly_full - monthly_window) * 12, 2),
        "results_full": full, "results_window": windowed,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark4_history_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")

if __name__ == "__main__":
    main()
