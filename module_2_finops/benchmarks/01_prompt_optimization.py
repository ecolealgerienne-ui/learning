"""
Benchmark 1 — Prompt Optimization
===================================
Measures token and cost savings from optimizing system prompts.
Uses MODEL_DEFAULT from .env (cheap model for stabilisation).

Run: python 01_prompt_optimization.py
"""

import json, time, os
from datetime import datetime
from config import client, MODELS, MONTHLY_CALLS, token_cost, print_config

MODEL = MODELS.default

PROMPT_NAIVE = """You are an expert banking assistant with deep knowledge of French
and European banking regulations. You must always respond in a professional, courteous
and formal manner appropriate for a financial institution. You must verify that the
user clearly understands your response and ask for clarification if needed. Remember
to always be precise, accurate and cite your regulatory sources when relevant. You
must always stay within the regulatory framework applicable to French banks under
ACPR supervision and European directives. As an AI assistant, you should note that
your responses do not constitute financial advice. Please note that you should always
consider the client's best interest and applicable regulations including MiFID II,
GDPR, DORA, and the EU AI Act. Always structure your responses clearly."""

PROMPT_OPTIMIZED = """Banking expert. French/EU regulatory scope (ACPR, MiFID II, DORA, EU AI Act).
Factual, structured responses. Cite regulatory sources. Not financial advice."""

TEST_QUESTIONS = [
    "What are the key requirements of DORA for AI systems in banking?",
    "Explain the EU AI Act requirements for credit scoring systems.",
    "What data retention rules apply to AI audit logs under GDPR?",
    "How does MiFID II affect algorithmic trading systems?",
    "What are the ACPR guidelines for AI governance in French banks?",
]

def call(system: str, question: str) -> dict:
    start = time.time()
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
    )
    return {
        "input_tokens":  r.usage.prompt_tokens,
        "output_tokens": r.usage.completion_tokens,
        "total_tokens":  r.usage.total_tokens,
        "latency_s":     round(time.time() - start, 2),
    }

def main():
    print("=" * 60)
    print("BENCHMARK 1 — Prompt Optimization")
    print(f"Model: {MODEL}")
    print_config()
    print("=" * 60)

    results_naive, results_opt = [], []

    print("\n🔴 Naive prompt...")
    for i, q in enumerate(TEST_QUESTIONS, 1):
        r = call(PROMPT_NAIVE, q)
        results_naive.append(r)
        print(f"  Q{i}: {r['total_tokens']:>5} tokens | {r['latency_s']}s")

    print("\n🟢 Optimized prompt...")
    for i, q in enumerate(TEST_QUESTIONS, 1):
        r = call(PROMPT_OPTIMIZED, q)
        results_opt.append(r)
        print(f"  Q{i}: {r['total_tokens']:>5} tokens | {r['latency_s']}s")

    avg_naive = sum(r["total_tokens"] for r in results_naive) / len(results_naive)
    avg_opt   = sum(r["total_tokens"] for r in results_opt)   / len(results_opt)
    reduction = (avg_naive - avg_opt) / avg_naive * 100

    monthly_cost_naive = token_cost(MODEL, sum(r["input_tokens"] for r in results_naive) / len(results_naive) * MONTHLY_CALLS,
                                           sum(r["output_tokens"] for r in results_naive) / len(results_naive) * MONTHLY_CALLS)
    monthly_cost_opt   = token_cost(MODEL, sum(r["input_tokens"] for r in results_opt)   / len(results_opt)   * MONTHLY_CALLS,
                                           sum(r["output_tokens"] for r in results_opt)   / len(results_opt)   * MONTHLY_CALLS)

    print(f"\n{'='*60}\nRESULTS\n{'='*60}")
    print(f"  Token reduction:        {reduction:.1f}%")
    print(f"  Avg tokens (naive):     {avg_naive:.0f}")
    print(f"  Avg tokens (optimized): {avg_opt:.0f}")
    print(f"  Monthly cost (naive):   ${monthly_cost_naive:.2f}  ({MONTHLY_CALLS:,} calls)")
    print(f"  Monthly cost (opt):     ${monthly_cost_opt:.2f}")
    print(f"  Monthly savings:        ${monthly_cost_naive - monthly_cost_opt:.2f}")
    print(f"  Annual savings:         ${(monthly_cost_naive - monthly_cost_opt)*12:.2f}")

    report = {
        "benchmark": "prompt_optimization", "date": datetime.now().isoformat(),
        "model": MODEL, "reduction_pct": round(reduction, 1),
        "monthly_cost_naive_usd": round(monthly_cost_naive, 2),
        "monthly_cost_opt_usd":   round(monthly_cost_opt, 2),
        "monthly_savings_usd":    round(monthly_cost_naive - monthly_cost_opt, 2),
        "annual_savings_usd":     round((monthly_cost_naive - monthly_cost_opt) * 12, 2),
        "raw_naive": results_naive, "raw_opt": results_opt,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark1_prompt_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")

if __name__ == "__main__":
    main()
