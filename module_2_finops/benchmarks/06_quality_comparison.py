"""
Benchmark 6 — Cross-Model Quality Comparison
=============================================
Sends the same questions to MODEL_SIMPLE, MODEL_MODERATE, MODEL_COMPLEX.
Scores responses on: length, keyword coverage, consistency.
Helps decide if the cheap model is "good enough" for each task type.

Run: python 06_quality_comparison.py
"""

import json, time, os, re
from datetime import datetime
from config import client, MODELS, token_cost, print_config

# ── Evaluation questions ──────────────────────────────────────────────────────

EVAL_TASKS = [
    {
        "complexity": "simple",
        "question": "What does DORA stand for and when did it enter into force?",
        "keywords": ["Digital Operational Resilience Act", "2025", "financial", "ICT"],
    },
    {
        "complexity": "simple",
        "question": "What is the maximum penalty under the EU AI Act?",
        "keywords": ["35 million", "7%", "revenue", "high-risk"],
    },
    {
        "complexity": "moderate",
        "question": "What are the key obligations for high-risk AI systems under the EU AI Act in banking?",
        "keywords": ["transparency", "human oversight", "documentation", "audit", "conformity"],
    },
    {
        "complexity": "moderate",
        "question": "Explain how DORA affects AI systems used for credit decisions in EU banks.",
        "keywords": ["ICT risk", "resilience", "testing", "incident", "third-party"],
    },
    {
        "complexity": "complex",
        "question": "Provide a detailed regulatory opinion on the compliance obligations for a French bank deploying an LLM-based credit scoring system, covering GDPR, EU AI Act, DORA and ACPR guidelines.",
        "keywords": ["GDPR", "EU AI Act", "DORA", "ACPR", "explainability",
                     "data protection", "audit trail", "high-risk"],
    },
]

SYSTEM = "You are a banking regulatory compliance expert. Provide accurate, detailed answers."

# ── Scoring ───────────────────────────────────────────────────────────────────

def score_response(answer: str, keywords: list[str]) -> dict:
    answer_lower = answer.lower()
    found = [kw for kw in keywords if kw.lower() in answer_lower]
    keyword_score = len(found) / len(keywords) if keywords else 0
    word_count    = len(answer.split())
    # Simple fluency proxy: no repeated sentences
    sentences = [s.strip() for s in re.split(r'[.!?]', answer) if len(s.strip()) > 10]
    unique_sentences = len(set(sentences))
    fluency = unique_sentences / max(len(sentences), 1)
    combined = round((keyword_score * 0.6) + (fluency * 0.2) + min(word_count / 300, 1.0) * 0.2, 3)
    return {
        "keyword_score": round(keyword_score, 2),
        "keywords_found": found,
        "word_count": word_count,
        "combined_score": combined,
    }

# ── Call ──────────────────────────────────────────────────────────────────────

def call(question: str, model: str) -> dict:
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user",   "content": question}],
            max_tokens=600,
        )
        return {
            "ok": True,
            "answer":  r.choices[0].message.content,
            "input":   r.usage.prompt_tokens,
            "output":  r.usage.completion_tokens,
            "latency": round(time.time() - start, 2),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "answer": "", "input": 0, "output": 0, "latency": 0}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK 6 — Cross-Model Quality Comparison")
    print("Models under test:")
    print_config()
    print("=" * 70)

    models_to_test = [
        ("simple",   MODELS.simple),
        ("moderate", MODELS.moderate),
        ("complex",  MODELS.complex),
    ]
    # Deduplicate — no point calling same model twice
    seen, unique_models = set(), []
    for label, m in models_to_test:
        if m not in seen:
            seen.add(m)
            unique_models.append((label, m))

    all_results = []

    for task in EVAL_TASKS:
        print(f"\n{'─'*70}")
        print(f"[{task['complexity'].upper():8}] {task['question'][:70]}...")
        print(f"{'─'*70}")

        task_results = {"question": task["question"], "complexity": task["complexity"], "models": {}}

        for label, model in unique_models:
            r = call(task["question"], model)
            if not r["ok"]:
                print(f"  ❌ {model}: {r.get('error')}")
                continue

            scores = score_response(r["answer"], task["keywords"])
            cost   = token_cost(model, r["input"], r["output"])

            print(f"\n  🤖 {model.split('/')[-1]:<30} [{label}]")
            print(f"     Score:    {scores['combined_score']:.2f}  "
                  f"| Keywords: {scores['keyword_score']:.0%} ({len(scores['keywords_found'])}/{len(task['keywords'])})")
            print(f"     Words:    {scores['word_count']:<5}"
                  f"| Cost: ${cost:.5f}"
                  f"| Latency: {r['latency']}s")
            print(f"     Keywords found: {', '.join(scores['keywords_found']) or 'none'}")
            print(f"     Preview:  {r['answer'][:200]}...")

            task_results["models"][model] = {
                "label": label, "score": scores["combined_score"],
                "keyword_score": scores["keyword_score"],
                "keywords_found": scores["keywords_found"],
                "word_count": scores["word_count"],
                "cost_usd": round(cost, 6),
                "latency_s": r["latency"],
                "input_tokens": r["input"],
                "output_tokens": r["output"],
                "answer": r["answer"],
            }

        all_results.append(task_results)

    # ── Summary ───────────────────────────────────────────────────────────────

    print(f"\n{'='*70}")
    print("QUALITY SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'Task complexity':<12} {'Model':<35} {'Score':>6} {'Cost':>10} {'Verdict'}")
    print("-" * 70)

    for task_r in all_results:
        complexity = task_r["complexity"]
        model_scores = sorted(task_r["models"].items(), key=lambda x: x[1]["score"], reverse=True)
        for i, (model, data) in enumerate(model_scores):
            verdict = "✅ BEST" if i == 0 else ("🟡 OK" if data["score"] >= 0.5 else "❌ WEAK")
            # Check if cheap model is good enough
            if i == 0 and model == MODELS.simple:
                verdict += " — cheap model wins!"
            print(f"  {complexity:<12} {model.split('/')[-1]:<35} {data['score']:>6.2f} "
                  f"${data['cost_usd']:>8.5f}  {verdict}")
        print()

    print("\n💡 ROUTING RECOMMENDATION:")
    for task_r in all_results:
        models_data = task_r["models"]
        # Find cheapest model with score >= 0.7
        viable = [(m, d) for m, d in models_data.items() if d["score"] >= 0.6]
        viable_sorted = sorted(viable, key=lambda x: x[1]["cost_usd"])
        if viable_sorted:
            best_cheap = viable_sorted[0]
            print(f"  [{task_r['complexity']:8}] → {best_cheap[0].split('/')[-1]:<30} "
                  f"(score={best_cheap[1]['score']:.2f}, ${best_cheap[1]['cost_usd']:.5f})")
        else:
            print(f"  [{task_r['complexity']:8}] → No model scored >= 0.6 on this task")

    # ── Save ──────────────────────────────────────────────────────────────────

    report = {
        "benchmark": "quality_comparison",
        "date": datetime.now().isoformat(),
        "models_tested": {lbl: m for lbl, m in unique_models},
        "results": all_results,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark6_quality_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")
    print("→ Use these scores to validate your routing decisions.")

if __name__ == "__main__":
    main()
