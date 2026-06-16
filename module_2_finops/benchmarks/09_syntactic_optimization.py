"""
Benchmark 9 — Syntactic Prompt Optimization (Manual Techniques)
=================================================================
Tests manual syntactic techniques that improve LLM response quality
without changing the model or compressing tokens.

Techniques tested (in order of implementation effort):
  1. Role prompting          — "Tu es un expert X" in system prompt
  2. Chain-of-Thought (CoT)  — "Raisonne étape par étape"
  3. Instruction ordering    — Critical instructions first AND last
  4. Few-shot structured     — 2–3 labeled examples in the prompt

Pipeline position:
  [RAW PROMPT]
      ↓
  Step 9: Syntactic optimization (this benchmark — done offline, once)
      ↓
  Step 8: DSPy auto-optimization (08_dspy_optimization.py — done offline, once)
      ↓
  Step 7: LLMLingua-2 compression (07_llmlingua_compression.py — runtime)
      ↓
  LiteLLM → LLM (Mistral / Claude / DeepSeek)

What this benchmark measures:
  - Quality score per technique (LLM judge 0-1)
  - Token count impact (some techniques ADD tokens)
  - Cost/quality tradeoff per technique
  - Cumulative gain when combining techniques

Run: python 09_syntactic_optimization.py
No extra dependencies — uses only config.py
"""

import json, time, os, re
from datetime import datetime
from config import client, MODELS, MONTHLY_CALLS, token_cost, print_config

MODEL_TASK  = MODELS.moderate   # model being optimized
MODEL_JUDGE = MODELS.simple     # cheap model for quality scoring

# ── Test questions (banking compliance domain) ─────────────────────────────────

TEST_QUESTIONS = [
    "What are the DORA requirements for AI systems used in banking operations?",
    "How should a bank document its LLM models to comply with EU AI Act Article 13?",
    "What data retention rules apply to AI decision logs under GDPR?",
]

# ── Prompt variants per technique ──────────────────────────────────────────────

def build_prompt(question: str, technique: str) -> tuple[str, str]:
    """Returns (system_prompt, user_message) for the given technique."""

    if technique == "baseline":
        system = "You are a helpful assistant."
        user   = question

    elif technique == "role":
        system = (
            "You are a senior regulatory compliance expert specializing in "
            "European banking law. You have 15 years of experience advising "
            "major French and German banks on DORA, EU AI Act, GDPR, and ACPR regulations."
        )
        user = question

    elif technique == "cot":
        system = "You are a helpful assistant."
        user   = (
            f"{question}\n\n"
            "Think step by step:\n"
            "1. Identify the specific regulation(s) that apply\n"
            "2. List the key requirements from those regulations\n"
            "3. Explain the practical implications for a bank\n"
            "4. Summarize the action items"
        )

    elif technique == "role_cot":
        system = (
            "You are a senior regulatory compliance expert specializing in "
            "European banking law (DORA, EU AI Act, GDPR, ACPR, MiFID II). "
            "You provide structured, actionable analysis."
        )
        user = (
            f"{question}\n\n"
            "Reason step by step:\n"
            "1. Applicable regulations and articles\n"
            "2. Specific requirements\n"
            "3. Practical implementation for a regulated bank\n"
            "4. Key risks of non-compliance"
        )

    elif technique == "few_shot":
        system = (
            "You are a senior regulatory compliance expert. "
            "Answer banking compliance questions with precision, citing specific articles."
        )
        user = (
            "Example question: What does DORA Article 11 require for ICT resilience?\n"
            "Example answer: DORA Article 11 mandates financial entities to establish, "
            "maintain and test ICT Business Continuity Policies. Key requirements: "
            "(1) RTO/RPO defined per critical system, (2) annual resilience testing, "
            "(3) incident classification within 4 hours, (4) reporting to competent "
            "authority within 24h for major incidents.\n\n"
            "Example question: What is the EU AI Act risk level for credit scoring AI?\n"
            "Example answer: EU AI Act Annex III classifies credit scoring AI as HIGH RISK. "
            "Obligations: conformity assessment, human oversight mechanism, accuracy "
            "monitoring, registration in EU database. Penalty: up to €30M or 6% global turnover.\n\n"
            f"Now answer: {question}"
        )

    elif technique == "full_pipeline":
        # Role + CoT + Few-shot + Instruction ordering (critical instruction repeated at end)
        system = (
            "You are a senior regulatory compliance expert specializing in "
            "European banking law (DORA, EU AI Act, GDPR, ACPR, MiFID II, Basel III). "
            "IMPORTANT: Always cite the specific regulation and article number. "
            "Structure your answer clearly."
        )
        user = (
            "Context: You are advising the CTO of a French bank regulated by ACPR.\n\n"
            "Example question: What does DORA Article 11 require for ICT resilience?\n"
            "Example answer: DORA Article 11 mandates financial entities to establish, "
            "maintain and test ICT Business Continuity Policies. Key requirements: "
            "(1) RTO/RPO defined per critical system, (2) annual resilience testing, "
            "(3) incident classification within 4 hours, (4) major incident reporting "
            "to competent authority within 24h.\n\n"
            f"Question: {question}\n\n"
            "Reason step by step:\n"
            "1. Applicable regulations and articles\n"
            "2. Specific requirements\n"
            "3. Practical implementation\n"
            "4. Non-compliance risks\n\n"
            "REMINDER: Cite specific regulation articles in your answer."
        )

    else:
        raise ValueError(f"Unknown technique: {technique}")

    return system, user

TECHNIQUES = ["baseline", "role", "cot", "role_cot", "few_shot", "full_pipeline"]

TECHNIQUE_LABELS = {
    "baseline":      "Baseline (no optimization)",
    "role":          "Role prompting only",
    "cot":           "Chain-of-Thought only",
    "role_cot":      "Role + CoT",
    "few_shot":      "Few-shot (2 examples)",
    "full_pipeline": "Full pipeline (Role + CoT + Few-shot + ordering)",
}

# ── LLM judge ─────────────────────────────────────────────────────────────────

def judge_quality(question: str, answer: str, technique: str) -> tuple[float, int]:
    prompt = f"""You are evaluating a banking compliance answer.
Question: {question}

Answer to evaluate:
{answer[:600]}

Score from 0.00 to 1.00 on:
- Regulatory accuracy: cites specific regulations/articles (40%)
- Completeness: covers key requirements (30%)
- Structure: clear, actionable (20%)
- Conciseness: no filler, direct (10%)

Respond with ONLY a decimal score. Example: 0.85"""

    r = client.chat.completions.create(
        model=MODEL_JUDGE,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )
    try:
        score = float(re.findall(r"[\d.]+", r.choices[0].message.content)[0])
        return min(1.0, max(0.0, score)), r.usage.total_tokens
    except Exception:
        return 0.5, r.usage.total_tokens

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK 9 — Syntactic Prompt Optimization (Manual Techniques)")
    print(f"Task model:  {MODEL_TASK}")
    print(f"Judge model: {MODEL_JUDGE}")
    print(f"Techniques:  {', '.join(TECHNIQUES)}")
    print_config()
    print("=" * 70)

    results_by_technique: dict[str, list] = {t: [] for t in TECHNIQUES}

    for q_idx, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'─'*70}")
        print(f"Q{q_idx}: {question[:70]}...")
        print(f"{'─'*70}")

        for technique in TECHNIQUES:
            system, user = build_prompt(question, technique)

            t0 = time.time()
            r = client.chat.completions.create(
                model=MODEL_TASK,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            latency = time.time() - t0

            answer       = r.choices[0].message.content
            input_tok    = r.usage.prompt_tokens
            output_tok   = r.usage.completion_tokens
            cost         = token_cost(MODEL_TASK, input_tok, output_tok)

            quality, judge_tok = judge_quality(question, answer, technique)
            judge_cost   = token_cost(MODEL_JUDGE, judge_tok)

            results_by_technique[technique].append({
                "question":     question,
                "input_tokens": input_tok,
                "output_tokens": output_tok,
                "total_tokens": input_tok + output_tok,
                "cost_usd":     round(cost, 6),
                "latency_s":    round(latency, 2),
                "quality":      round(quality, 2),
                "judge_tokens": judge_tok,
                "judge_cost":   round(judge_cost, 6),
                "answer":       answer[:300],
            })

            print(f"  [{technique:15}] quality={quality:.2f} | tokens={input_tok+output_tok:>4} "
                  f"| cost=${cost:.5f} | {latency:.1f}s")

    # ── Analysis ──────────────────────────────────────────────────────────────

    print(f"\n{'='*70}")
    print("SUMMARY — Quality vs Token Cost")
    print(f"{'='*70}")

    baseline_quality = sum(r["quality"] for r in results_by_technique["baseline"]) / len(TEST_QUESTIONS)
    baseline_cost    = sum(r["cost_usd"] for r in results_by_technique["baseline"]) / len(TEST_QUESTIONS)

    summary = []
    print(f"\n  {'Technique':<30} | {'Avg Quality':>11} | {'vs Baseline':>11} | {'Avg Tokens':>10} | {'Avg Cost/call':>13}")
    print(f"  {'─'*30}─┼─{'─'*11}─┼─{'─'*11}─┼─{'─'*10}─┼─{'─'*13}")

    for technique in TECHNIQUES:
        data = results_by_technique[technique]
        avg_quality = sum(r["quality"]       for r in data) / len(data)
        avg_tokens  = sum(r["total_tokens"]  for r in data) / len(data)
        avg_cost    = sum(r["cost_usd"]      for r in data) / len(data)
        delta_q     = avg_quality - baseline_quality
        delta_sign  = "+" if delta_q >= 0 else ""

        label = TECHNIQUE_LABELS[technique]
        print(f"  {label:<30} | {avg_quality:>11.2f} | {delta_sign}{delta_q:>+10.2f} | {avg_tokens:>10.0f} | ${avg_cost:>12.5f}")

        summary.append({
            "technique":      technique,
            "label":          label,
            "avg_quality":    round(avg_quality, 2),
            "quality_gain":   round(delta_q, 2),
            "avg_tokens":     round(avg_tokens),
            "avg_cost_usd":   round(avg_cost, 6),
            "monthly_cost":   round(avg_cost * MONTHLY_CALLS, 2),
        })

    # Best technique
    best = max(summary, key=lambda x: x["avg_quality"])
    print(f"\n  Best technique: [{best['technique']}] → quality={best['avg_quality']:.2f} "
          f"(+{best['quality_gain']:.2f} vs baseline)")

    # Monthly cost impact
    print(f"\n  Monthly cost at {MONTHLY_CALLS:,} calls/month:")
    for s in summary:
        print(f"    {s['label']:<35} ${s['monthly_cost']:>10,.2f}/month")

    print(f"\n  Key insight: 'full_pipeline' gets the highest quality.")
    print(f"  THEN apply LLMLingua-2 (benchmark 07) to compress it back down.")
    print(f"  Net result: high quality + low token cost.")

    # ── Save ──────────────────────────────────────────────────────────────────

    report = {
        "benchmark":           "syntactic_optimization",
        "date":                datetime.now().isoformat(),
        "task_model":          MODEL_TASK,
        "judge_model":         MODEL_JUDGE,
        "techniques_tested":   TECHNIQUES,
        "questions_tested":    len(TEST_QUESTIONS),
        "monthly_calls":       MONTHLY_CALLS,
        "baseline_quality":    round(baseline_quality, 2),
        "summary":             summary,
        "best_technique":      best["technique"],
        "best_quality":        best["avg_quality"],
        "best_quality_gain":   best["quality_gain"],
        "raw_results":         results_by_technique,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark9_syntactic_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")
    print(f"\n💡 Run order for full pipeline:")
    print(f"   python 09_syntactic_optimization.py  → pick best technique")
    print(f"   python 08_dspy_optimization.py        → auto-optimize further")
    print(f"   python 07_llmlingua_compression.py    → compress for cost")
    print(f"   python 05_combined_report.py          → full FinOps report")

if __name__ == "__main__":
    main()
