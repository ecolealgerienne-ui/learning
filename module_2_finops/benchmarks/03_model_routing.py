"""
Benchmark 3 — Cross-Provider Smart Model Routing
==================================================
Routes tasks to the right model based on complexity.
Models are configured in .env — can mix ANY providers.

Examples:
  Simple   → mistral/mistral-small-latest  ($0.0001/1K)
  Moderate → deepseek/deepseek-chat        ($0.00027/1K)
  Complex  → claude-sonnet                 ($0.003/1K)

Run: python 03_model_routing.py
"""

import json, time, re, os
from datetime import datetime
from collections import Counter
from config import client, MODELS, DAILY_CALLS, token_cost, print_config

# ── Task classifier (keyword-based, zero cost) ────────────────────────────────

COMPLEX_RE  = re.compile(r"(legal reasoning|multi.?step|adversarial|regulatory opinion|"
                          r"compliance judgment|risk assessment|edge case|unprecedented)", re.I)
MODERATE_RE = re.compile(r"(analyz|audit|contract|compliance|regulation|report|"
                          r"risk|explain|detail|compare|assess)", re.I)

def classify(question: str) -> str:
    if COMPLEX_RE.search(question):  return "complex"
    if MODERATE_RE.search(question): return "moderate"
    return "simple"

def model_for(complexity: str) -> str:
    return {"simple": MODELS.simple, "moderate": MODELS.moderate,
            "complex": MODELS.complex}.get(complexity, MODELS.default)

# ── Banking tasks dataset ─────────────────────────────────────────────────────

TASKS = [
    # SIMPLE
    {"q": "What does DORA stand for?",                                      "expected": "simple"},
    {"q": "What is the maximum GDPR fine?",                                 "expected": "simple"},
    {"q": "Extract the contract date from: signed on 2026-01-15",           "expected": "simple"},
    {"q": "Is this email about credit or insurance?",                       "expected": "simple"},
    {"q": "Summarize this paragraph in 2 sentences.",                       "expected": "simple"},
    # MODERATE
    {"q": "Analyze the compliance risks in this loan contract.",             "expected": "moderate"},
    {"q": "Explain the EU AI Act requirements for high-risk AI systems.",    "expected": "moderate"},
    {"q": "Compare MiFID II and DORA requirements for AI systems.",         "expected": "moderate"},
    {"q": "Assess the regulatory exposure of our credit scoring AI.",       "expected": "moderate"},
    {"q": "What audit trail is required under DORA for AI decisions?",      "expected": "moderate"},
    # COMPLEX
    {"q": "Provide legal reasoning on an unprecedented AI liability case.",  "expected": "complex"},
    {"q": "Multi-step regulatory opinion on cross-border AI compliance.",    "expected": "complex"},
    {"q": "Adversarial review of our AI governance framework.",              "expected": "complex"},
]

SYSTEM = "Banking regulatory expert. Precise, concise answers."

def call(question: str, model: str) -> dict:
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=model, max_tokens=300,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user",   "content": question}],
        )
        return {"input": r.usage.prompt_tokens, "output": r.usage.completion_tokens,
                "latency_s": round(time.time() - start, 2), "ok": True,
                "answer": r.choices[0].message.content}
    except Exception as e:
        return {"ok": False, "error": str(e), "input": 0, "output": 0, "latency_s": 0, "answer": ""}

def main():
    print("=" * 65)
    print("BENCHMARK 3 — Cross-Provider Smart Model Routing")
    print("Model routing config:")
    print_config()
    print("=" * 65)

    results = []
    correct = 0
    total_routed_cost  = 0.0
    total_allsimple_cost  = 0.0
    total_allcomplex_cost = 0.0

    for task in TASKS:
        q        = task["q"]
        expected = task["expected"]
        detected = classify(q)
        model    = model_for(detected)
        is_correct = detected == expected
        if is_correct:
            correct += 1

        print(f"\n{'✅' if is_correct else '⚠️ '} [{detected:8}] [{model.split('/')[-1][:20]:20}] {q[:45]}...")

        r = call(q, model)
        if not r["ok"]:
            print(f"   ❌ {r.get('error')}")
            continue

        routed_cost     = token_cost(model,            r["input"], r["output"])
        simple_cost     = token_cost(MODELS.simple,    r["input"], r["output"])
        complex_cost    = token_cost(MODELS.complex,   r["input"], r["output"])

        total_routed_cost     += routed_cost
        total_allsimple_cost  += simple_cost
        total_allcomplex_cost += complex_cost

        print(f"   {r['input']}in + {r['output']}out tokens | ${routed_cost:.5f} routed "
              f"| ${complex_cost:.5f} if all-complex | {r['latency_s']}s")

        results.append({
            "question": q, "expected": expected, "detected": detected,
            "correct": is_correct, "model": model,
            "input": r["input"], "output": r["output"],
            "latency_s": r["latency_s"],
            "cost_routed": round(routed_cost, 6),
            "cost_allsimple": round(simple_cost, 6),
            "cost_allcomplex": round(complex_cost, 6),
            "answer_preview": r["answer"][:120],
        })

    # ── Analysis ──────────────────────────────────────────────────────────────

    n = len(results)
    accuracy       = correct / len(TASKS) * 100
    vs_allcomplex  = (total_allcomplex_cost - total_routed_cost) / total_allcomplex_cost * 100
    vs_allsimple   = (total_routed_cost - total_allsimple_cost)  / total_allsimple_cost  * 100

    scale          = DAILY_CALLS / n
    monthly_routed  = total_routed_cost    * scale * 30
    monthly_complex = total_allcomplex_cost * scale * 30
    monthly_simple  = total_allsimple_cost  * scale * 30

    dist = Counter(r["detected"] for r in results)

    print(f"\n{'='*65}\nRESULTS\n{'='*65}")
    print(f"\n  Classifier accuracy: {accuracy:.1f}%  ({correct}/{len(TASKS)})")
    print(f"\n  Cost comparison ({n} tasks):")
    print(f"    All-complex model ({MODELS.complex.split('/')[-1]:20}): ${total_allcomplex_cost:.4f}")
    print(f"    Smart routing:                              ${total_routed_cost:.4f}  (−{vs_allcomplex:.1f}%)")
    print(f"    All-simple model  ({MODELS.simple.split('/')[-1]:20}): ${total_allsimple_cost:.4f}")
    print(f"\n  Monthly at {DAILY_CALLS:,} calls/day:")
    print(f"    All-complex: ${monthly_complex:>10,.2f}/month")
    print(f"    Routing:     ${monthly_routed:>10,.2f}/month  ← smart routing")
    print(f"    All-simple:  ${monthly_simple:>10,.2f}/month  (quality risk)")
    print(f"    Savings vs all-complex: ${monthly_complex - monthly_routed:,.2f}/month")
    print(f"    Annual:                 ${(monthly_complex - monthly_routed)*12:,.0f}/year")
    print(f"\n  Routing distribution:")
    for k, v in sorted(dist.items()):
        model_name = model_for(k).split("/")[-1]
        print(f"    {k:8}: {v:>3} tasks ({v/n*100:.0f}%)  → {model_name}")

    report = {
        "benchmark": "model_routing", "date": datetime.now().isoformat(),
        "models": {"simple": MODELS.simple, "moderate": MODELS.moderate, "complex": MODELS.complex},
        "classifier_accuracy_pct": round(accuracy, 1),
        "savings_vs_allcomplex_pct": round(vs_allcomplex, 1),
        "monthly_savings_usd": round(monthly_complex - monthly_routed, 2),
        "annual_savings_usd":  round((monthly_complex - monthly_routed) * 12, 0),
        "distribution": dict(dist),
        "raw_results": results,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark3_routing_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")

if __name__ == "__main__":
    main()
