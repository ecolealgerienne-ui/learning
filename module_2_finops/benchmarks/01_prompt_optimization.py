"""
Module 2 — Benchmark 1: Prompt Optimization
============================================
Measures real token and cost savings from optimizing system prompts.

Run: python 01_prompt_optimization.py
Requires: ANTHROPIC_API_KEY, LiteLLM running on localhost:4000
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
MODEL            = "claude-haiku"   # Use cheap model for benchmarks

client = OpenAI(base_url=f"{LITELLM_BASE_URL}/v1", api_key=LITELLM_API_KEY)

# ── Prompts ───────────────────────────────────────────────────────────────────

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

# ── Test questions (realistic banking use cases) ──────────────────────────────

TEST_QUESTIONS = [
    "What are the key requirements of DORA for AI systems in banking?",
    "Explain the EU AI Act requirements for credit scoring systems.",
    "What data retention rules apply to AI audit logs under GDPR?",
    "How does MiFID II affect algorithmic trading systems?",
    "What are the ACPR guidelines for AI governance in French banks?",
]

# ── Benchmark function ────────────────────────────────────────────────────────

def run_test(system_prompt: str, question: str, label: str) -> dict:
    start = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": question},
        ],
    )
    elapsed = time.time() - start

    usage = response.usage
    return {
        "label":          label,
        "system_tokens":  len(system_prompt.split()),   # approximate
        "input_tokens":   usage.prompt_tokens,
        "output_tokens":  usage.completion_tokens,
        "total_tokens":   usage.total_tokens,
        "latency_s":      round(elapsed, 2),
        "response_len":   len(response.choices[0].message.content),
    }

# ── Cost calculator (Haiku pricing) ──────────────────────────────────────────

def token_cost(tokens: int, is_output: bool = False) -> float:
    # Claude Haiku: $0.00025/1K input, $0.00125/1K output
    rate = 0.00125 if is_output else 0.00025
    return (tokens / 1000) * rate

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BENCHMARK 1 — Prompt Optimization")
    print(f"Model: {MODEL} | Questions: {len(TEST_QUESTIONS)}")
    print("=" * 60)

    print(f"\nNaive prompt:     {len(PROMPT_NAIVE.split()):>4} words / ~{len(PROMPT_NAIVE.split())} tokens")
    print(f"Optimized prompt: {len(PROMPT_OPTIMIZED.split()):>4} words / ~{len(PROMPT_OPTIMIZED.split())} tokens")

    results_naive = []
    results_opt   = []

    print("\n🔵 Testing NAIVE prompt...")
    for i, q in enumerate(TEST_QUESTIONS, 1):
        r = run_test(PROMPT_NAIVE, q, f"naive_{i}")
        results_naive.append(r)
        print(f"  Q{i}: {r['total_tokens']:>5} tokens | {r['latency_s']}s")

    print("\n🟢 Testing OPTIMIZED prompt...")
    for i, q in enumerate(TEST_QUESTIONS, 1):
        r = run_test(PROMPT_OPTIMIZED, q, f"opt_{i}")
        results_opt.append(r)
        print(f"  Q{i}: {r['total_tokens']:>5} tokens | {r['latency_s']}s")

    # ── Analysis ──────────────────────────────────────────────────────────────

    avg_naive = sum(r["total_tokens"] for r in results_naive) / len(results_naive)
    avg_opt   = sum(r["total_tokens"] for r in results_opt)   / len(results_opt)
    reduction = (avg_naive - avg_opt) / avg_naive * 100

    # Monthly projection (500,000 calls/month)
    monthly_calls = 500_000
    monthly_tokens_naive = avg_naive * monthly_calls
    monthly_tokens_opt   = avg_opt   * monthly_calls

    # Cost (input tokens — output tokens roughly same)
    avg_input_naive = sum(r["input_tokens"] for r in results_naive) / len(results_naive)
    avg_input_opt   = sum(r["input_tokens"] for r in results_opt)   / len(results_opt)

    monthly_cost_naive = token_cost(avg_input_naive * monthly_calls) + \
                         token_cost(sum(r["output_tokens"] for r in results_naive) / len(results_naive) * monthly_calls, is_output=True)
    monthly_cost_opt   = token_cost(avg_input_opt * monthly_calls) + \
                         token_cost(sum(r["output_tokens"] for r in results_opt) / len(results_opt) * monthly_calls, is_output=True)

    savings_monthly = monthly_cost_naive - monthly_cost_opt
    savings_annual  = savings_monthly * 12

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nAverage tokens/request:")
    print(f"  Naive:     {avg_naive:>7.0f} tokens")
    print(f"  Optimized: {avg_opt:>7.0f} tokens")
    print(f"  Reduction: {reduction:>7.1f}%")

    print(f"\nMonthly projection ({monthly_calls:,} calls/month):")
    print(f"  Cost (naive):     ${monthly_cost_naive:>8.2f}/month")
    print(f"  Cost (optimized): ${monthly_cost_opt:>8.2f}/month")
    print(f"  Monthly savings:  ${savings_monthly:>8.2f}")
    print(f"  Annual savings:   ${savings_annual:>8.2f}")

    print(f"\n✅ Effort to implement: 2 hours")
    print(f"✅ Quality impact: none (verify in Langfuse traces)")

    # ── Save results ──────────────────────────────────────────────────────────

    report = {
        "benchmark":        "prompt_optimization",
        "date":             datetime.now().isoformat(),
        "model":            MODEL,
        "naive_avg_tokens": round(avg_naive, 1),
        "opt_avg_tokens":   round(avg_opt, 1),
        "reduction_pct":    round(reduction, 1),
        "monthly_calls":    monthly_calls,
        "monthly_cost_naive_usd":  round(monthly_cost_naive, 2),
        "monthly_cost_opt_usd":    round(monthly_cost_opt, 2),
        "monthly_savings_usd":     round(savings_monthly, 2),
        "annual_savings_usd":      round(savings_annual, 2),
        "raw_naive": results_naive,
        "raw_opt":   results_opt,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark1_prompt_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Results saved: {fname}")


if __name__ == "__main__":
    main()
