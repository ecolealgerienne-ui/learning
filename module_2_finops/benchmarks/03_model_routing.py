"""
Module 2 — Benchmark 3: Smart Model Routing
=============================================
Compares the cost of routing tasks to the right model vs always using the premium.

Tasks:
  SIMPLE   → Haiku  ($0.0008/1K tokens)
  MODERATE → Sonnet ($0.003/1K tokens)
  COMPLEX  → Opus   ($0.015/1K tokens)

Run: python 03_model_routing.py
"""

import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Install: pip install openai python-dotenv")
    exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_API_KEY  = os.getenv("LITELLM_API_KEY", "sk-litellm-master-2026")

client = OpenAI(base_url=f"{LITELLM_BASE_URL}/v1", api_key=LITELLM_API_KEY)

# ── Model config ──────────────────────────────────────────────────────────────

class TaskComplexity(Enum):
    SIMPLE   = "simple"
    MODERATE = "moderate"
    COMPLEX  = "complex"

MODEL_CONFIG = {
    TaskComplexity.SIMPLE:   {"model": "claude-haiku",  "input_per_1k": 0.00025, "output_per_1k": 0.00125},
    TaskComplexity.MODERATE: {"model": "claude-sonnet", "input_per_1k": 0.003,   "output_per_1k": 0.015},
    TaskComplexity.COMPLEX:  {"model": "claude-opus",   "input_per_1k": 0.015,   "output_per_1k": 0.075},
}

# ── Classifier (keyword-based, fast, free) ────────────────────────────────────

COMPLEX_PATTERNS = re.compile(
    r"(legal reasoning|multi.?step|adversarial|regulatory opinion|"
    r"compliance judgment|risk assessment|edge case|unprecedented)", re.I
)
MODERATE_PATTERNS = re.compile(
    r"(analyze|audit|contract|compliance|regulation|report|"
    r"risk|explain|detail|compare)", re.I
)

def classify_task(question: str) -> TaskComplexity:
    if COMPLEX_PATTERNS.search(question):
        return TaskComplexity.COMPLEX
    if MODERATE_PATTERNS.search(question):
        return TaskComplexity.MODERATE
    return TaskComplexity.SIMPLE

# ── Banking task dataset ──────────────────────────────────────────────────────

TASKS = [
    # SIMPLE — classification, extraction, FAQ
    {"question": "What does DORA stand for?",                                     "expected": TaskComplexity.SIMPLE},
    {"question": "What is the maximum GDPR fine?",                                "expected": TaskComplexity.SIMPLE},
    {"question": "Extract the contract date from this text: signed on 2026-01-15","expected": TaskComplexity.SIMPLE},
    {"question": "Is this email about credit or insurance?",                      "expected": TaskComplexity.SIMPLE},
    {"question": "Summarize this paragraph in 2 sentences.",                      "expected": TaskComplexity.SIMPLE},
    # MODERATE — analysis, reports
    {"question": "Analyze the compliance risks in this loan contract.",            "expected": TaskComplexity.MODERATE},
    {"question": "Explain the EU AI Act requirements for high-risk AI systems.",   "expected": TaskComplexity.MODERATE},
    {"question": "Compare MiFID II and DORA requirements for AI systems.",        "expected": TaskComplexity.MODERATE},
    {"question": "Generate a compliance report for our LLM deployment.",          "expected": TaskComplexity.MODERATE},
    {"question": "What are the audit requirements under DORA for AI?",            "expected": TaskComplexity.MODERATE},
    # COMPLEX — legal, edge cases
    {"question": "Provide legal reasoning on an unprecedented AI liability case.", "expected": TaskComplexity.COMPLEX},
    {"question": "Multi-step regulatory opinion on cross-border AI compliance.",   "expected": TaskComplexity.COMPLEX},
    {"question": "Adversarial review of our AI governance framework.",             "expected": TaskComplexity.COMPLEX},
]

# ── LLM call ─────────────────────────────────────────────────────────────────

SYSTEM = "Banking regulatory expert. Precise, concise answers."

def call_model(question: str, model: str) -> dict:
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user",   "content": question},
            ],
            max_tokens=300,
        )
        elapsed = time.time() - start
        return {
            "input_tokens":  response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "latency_s":     round(elapsed, 2),
            "success":       True,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "input_tokens": 0, "output_tokens": 0, "latency_s": 0}

def compute_cost(input_tokens: int, output_tokens: int, complexity: TaskComplexity) -> float:
    cfg = MODEL_CONFIG[complexity]
    return (input_tokens / 1000 * cfg["input_per_1k"]) + (output_tokens / 1000 * cfg["output_per_1k"])

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BENCHMARK 3 — Smart Model Routing")
    print(f"Tasks: {len(TASKS)}")
    print("=" * 60)

    results = []
    total_routed_cost  = 0.0
    total_premium_cost = 0.0   # if everything went to Opus
    classification_correct = 0

    for task in TASKS:
        q         = task["question"]
        expected  = task["expected"]
        detected  = classify_task(q)
        correct   = detected == expected

        if correct:
            classification_correct += 1

        cfg   = MODEL_CONFIG[detected]
        model = cfg["model"]

        print(f"\n{'✅' if correct else '⚠️ '} [{detected.value:8}] {q[:55]}...")
        print(f"   Model: {model}")

        call = call_model(q, model)
        if not call["success"]:
            print(f"   ❌ Error: {call.get('error', 'unknown')}")
            continue

        routed_cost  = compute_cost(call["input_tokens"], call["output_tokens"], detected)
        premium_cost = compute_cost(call["input_tokens"], call["output_tokens"], TaskComplexity.COMPLEX)

        total_routed_cost  += routed_cost
        total_premium_cost += premium_cost

        print(f"   Tokens: {call['input_tokens']}in + {call['output_tokens']}out | ${routed_cost:.5f} (vs ${premium_cost:.5f} Opus)")
        results.append({
            "question":       q,
            "expected":       expected.value,
            "detected":       detected.value,
            "correct":        correct,
            "model":          model,
            "input_tokens":   call["input_tokens"],
            "output_tokens":  call["output_tokens"],
            "latency_s":      call["latency_s"],
            "cost_routed":    round(routed_cost, 6),
            "cost_premium":   round(premium_cost, 6),
        })

    # ── Analysis ──────────────────────────────────────────────────────────────

    accuracy = classification_correct / len(TASKS) * 100
    savings_pct = (total_premium_cost - total_routed_cost) / total_premium_cost * 100

    # Monthly at 200K requests/day
    daily_calls = 200_000
    scale = daily_calls / len(TASKS)
    monthly_routed  = total_routed_cost  * scale * 30
    monthly_premium = total_premium_cost * scale * 30

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nClassifier accuracy:  {accuracy:.1f}%  ({classification_correct}/{len(TASKS)} tasks)")
    print(f"\nCost comparison (this test):")
    print(f"  Smart routing:  ${total_routed_cost:.4f}")
    print(f"  All Opus:       ${total_premium_cost:.4f}")
    print(f"  Savings:        {savings_pct:.1f}%")
    print(f"\nMonthly projection ({daily_calls:,} calls/day):")
    print(f"  All Opus:      ${monthly_premium:,.0f}/month")
    print(f"  Smart routing: ${monthly_routed:,.0f}/month")
    print(f"  Savings:       ${monthly_premium - monthly_routed:,.0f}/month")
    print(f"  Annual:        ${(monthly_premium - monthly_routed)*12:,.0f}/year")

    # Model distribution
    from collections import Counter
    dist = Counter(r["detected"] for r in results)
    print(f"\nRouting distribution:")
    for complexity, count in sorted(dist.items()):
        pct = count / len(results) * 100
        print(f"  {complexity:8}: {count:>3} calls ({pct:.0f}%)")

    # ── Save ──────────────────────────────────────────────────────────────────

    report = {
        "benchmark":         "model_routing",
        "date":              datetime.now().isoformat(),
        "classifier_accuracy_pct": round(accuracy, 1),
        "savings_pct":       round(savings_pct, 1),
        "monthly_savings_usd": round(monthly_premium - monthly_routed, 0),
        "annual_savings_usd":  round((monthly_premium - monthly_routed) * 12, 0),
        "distribution":      dict(dist),
        "raw_results":       results,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark3_routing_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Results saved: {fname}")


if __name__ == "__main__":
    main()
