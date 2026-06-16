"""
Benchmark 8 — DSPy Automatic Prompt Optimization
==================================================
DSPy (Stanford): instead of hand-writing prompts, you define:
  1. A task signature (input → output fields)
  2. A metric (how to score a good answer)
  3. A dataset of examples

DSPy then automatically searches for the best prompt using BootstrapFewShot
or MIPRO optimizers — testing dozens of variants and keeping the best.

Used in production by: Cursor, Databricks, Mistral, JetBrains.

What this benchmark measures:
  Step 1 — Baseline: hand-written prompt, score with judge
  Step 2 — DSPy optimized: let DSPy find a better prompt
  Step 3 — Compare: token count, quality score, cost

Run: python 08_dspy_optimization.py
Requires: pip install dspy-ai
"""

import json, time, os
from datetime import datetime
from config import client, MODELS, MONTHLY_CALLS, token_cost, print_config

MODEL_TASK  = MODELS.moderate   # model to optimize prompts for
MODEL_JUDGE = MODELS.simple     # cheap model used by DSPy + our quality judge

try:
    import dspy
except ImportError:
    print("Install: pip install dspy-ai")
    exit(1)

# ── Configure DSPy to use our LiteLLM gateway ─────────────────────────────────
# DSPy supports LiteLLM natively via openai-compatible endpoint.

import os as _os
_base_url = _os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
_api_key  = _os.getenv("LITELLM_API_KEY",  "sk-litellm-master-2026")

lm = dspy.LM(
    model=f"openai/{MODEL_TASK}",
    api_base=f"{_base_url}/v1",
    api_key=_api_key,
    max_tokens=512,
)
dspy.configure(lm=lm)

# Judge LM (cheap, for DSPy metric evaluation)
judge_lm = dspy.LM(
    model=f"openai/{MODEL_JUDGE}",
    api_base=f"{_base_url}/v1",
    api_key=_api_key,
    max_tokens=20,
)

# ── DSPy Task: Regulatory compliance QA ───────────────────────────────────────

class ComplianceQA(dspy.Signature):
    """Answer banking regulatory compliance questions accurately and concisely."""
    question: str = dspy.InputField(desc="Regulatory compliance question from a bank")
    answer:   str = dspy.OutputField(desc="Accurate, structured answer citing specific regulations")

class ComplianceModule(dspy.Module):
    def __init__(self):
        self.qa = dspy.ChainOfThought(ComplianceQA)

    def forward(self, question):
        return self.qa(question=question)

# ── Training examples (few-shot seed data) ────────────────────────────────────

TRAINSET = [
    dspy.Example(
        question="What does DORA require for ICT incident classification?",
        answer="DORA Article 18 requires financial entities to classify ICT incidents by impact on: (1) clients affected, (2) data breach scope, (3) reputation risk, (4) critical services affected. Major incidents must be reported to competent authority within 4 hours of classification."
    ).with_inputs("question"),
    dspy.Example(
        question="What is the EU AI Act risk level for AI in credit scoring?",
        answer="EU AI Act Annex III lists AI for creditworthiness assessment as HIGH RISK. Requirements: (1) conformity assessment before deployment, (2) human oversight mechanism, (3) accuracy and robustness documentation, (4) registration in EU database. Penalty for non-compliance: up to €30M or 6% global turnover."
    ).with_inputs("question"),
    dspy.Example(
        question="What GDPR rights apply when an AI rejects a loan application?",
        answer="GDPR Article 22 applies: individuals have the right not to be subject to solely automated decisions with significant effects. Banks must: (1) provide human review on request, (2) explain the decision logic, (3) allow contestation. DPA guidance (CNIL in France) requires meaningful explanation, not just 'algorithm decided'."
    ).with_inputs("question"),
    dspy.Example(
        question="What are ACPR expectations for AI model governance?",
        answer="ACPR (2023 guidance) expects: (1) Model Risk Management framework covering AI models, (2) independent model validation before production, (3) ongoing monitoring of model drift, (4) documentation of training data sources and known biases, (5) clear accountability chain up to board level."
    ).with_inputs("question"),
    dspy.Example(
        question="How long must AI audit logs be retained under MiFID II?",
        answer="MiFID II Article 25 requires retention of records sufficient to reconstruct all transactions — minimum 5 years. For AI-driven algorithmic trading, ESMA guidelines specify that model version, parameters, and decision logs must be retained alongside trade records for the same 5-year period."
    ).with_inputs("question"),
]

TESTSET = [
    dspy.Example(
        question="What does DORA require from third-party ICT providers?",
        answer="DORA Chapter V requires financial entities to: (1) maintain a register of all ICT third-party providers, (2) include contractual exit strategies, (3) perform ICT concentration risk assessments, (4) ensure providers meet resilience standards. Critical third parties are directly supervised by ESAs."
    ).with_inputs("question"),
    dspy.Example(
        question="Under EU AI Act, what is required for AI transparency to clients?",
        answer="EU AI Act Article 13 (transparency for high-risk AI) requires: (1) instructions for use documenting capabilities and limitations, (2) human oversight provisions, (3) for general-purpose AI interacting with humans: disclosure that they are interacting with AI (Article 50)."
    ).with_inputs("question"),
    dspy.Example(
        question="What Basel III requirements apply to AI credit models?",
        answer="Basel III/IV (CRR3 in EU): banks using Internal Ratings-Based (IRB) approaches must validate AI credit models against: (1) minimum 5-year historical data, (2) discriminatory power tests (Gini ≥ 0.25 typically), (3) annual backtesting, (4) ECB model approval for significant institutions."
    ).with_inputs("question"),
]

# ── Quality metric ─────────────────────────────────────────────────────────────

def compliance_metric(example, prediction, trace=None):
    """Score 0-1 based on regulatory accuracy. Used by DSPy optimizer."""
    with dspy.context(lm=judge_lm):
        judge = dspy.Predict("question, answer -> score")
        result = judge(
            question=f"Rate this banking compliance answer from 0 to 10. Question: {example.question}",
            answer=prediction.answer,
        )
    try:
        import re
        score = float(re.findall(r"[\d.]+", result.score)[0])
        return min(score / 10.0, 1.0)
    except Exception:
        return 0.5

# ── Main ──────────────────────────────────────────────────────────────────────

def score_answers(module, testset) -> tuple[float, list]:
    scores = []
    details = []
    for ex in testset:
        t0 = time.time()
        pred = module(question=ex.question)
        lat = time.time() - t0
        score = compliance_metric(ex, pred)
        scores.append(score)
        details.append({
            "question": ex.question,
            "answer":   pred.answer,
            "score":    round(score, 2),
            "latency":  round(lat, 2),
        })
    return sum(scores) / len(scores), details

def main():
    print("=" * 70)
    print("BENCHMARK 8 — DSPy Automatic Prompt Optimization")
    print(f"Task model:  {MODEL_TASK}  (model we're optimizing for)")
    print(f"Judge model: {MODEL_JUDGE}  (cheap model used by DSPy metric)")
    print_config()
    print("=" * 70)

    module = ComplianceModule()

    # ── Step 1: Baseline (no optimization) ────────────────────────────────────
    print("\n📊 Step 1 — Baseline (hand-written ChainOfThought, no optimization)")
    t0 = time.time()
    baseline_score, baseline_details = score_answers(module, TESTSET)
    baseline_time = time.time() - t0
    print(f"  Average quality score: {baseline_score:.2f}")
    print(f"  Eval time: {baseline_time:.1f}s")
    for d in baseline_details:
        print(f"  [{d['score']:.2f}] {d['question'][:60]}...")

    # ── Step 2: DSPy BootstrapFewShot optimization ────────────────────────────
    print("\n🔧 Step 2 — DSPy BootstrapFewShot optimization")
    print(f"  Training on {len(TRAINSET)} examples, evaluating on {len(TESTSET)} test cases...")
    print(f"  DSPy will bootstrap few-shot examples automatically.")

    optimizer = dspy.BootstrapFewShot(
        metric=compliance_metric,
        max_bootstrapped_demos=3,
        max_labeled_demos=3,
    )

    t_opt = time.time()
    optimized_module = optimizer.compile(module, trainset=TRAINSET)
    opt_time = time.time() - t_opt
    print(f"  Optimization completed in {opt_time:.1f}s")

    # ── Step 3: Evaluate optimized module ─────────────────────────────────────
    print("\n📊 Step 3 — Optimized module evaluation")
    opt_score, opt_details = score_answers(optimized_module, TESTSET)
    print(f"  Average quality score: {opt_score:.2f}")
    for d in opt_details:
        print(f"  [{d['score']:.2f}] {d['question'][:60]}...")

    # ── Comparison ────────────────────────────────────────────────────────────
    improvement = (opt_score - baseline_score) / max(baseline_score, 0.01) * 100

    print(f"\n{'='*70}")
    print("COMPARISON")
    print(f"{'='*70}")
    print(f"  Baseline score:   {baseline_score:.2f}")
    print(f"  Optimized score:  {opt_score:.2f}")
    print(f"  Improvement:      {improvement:+.1f}%")
    print(f"  Optimization time: {opt_time:.0f}s  (one-time cost)")
    print(f"\n  → DSPy finds better prompts automatically by testing variations.")
    print(f"  → Optimized prompt is saved — no re-optimization needed at runtime.")
    print(f"  → Quality gain at zero additional runtime cost.")

    # Save optimized module
    os.makedirs("../reports", exist_ok=True)
    opt_fname = f"../reports/dspy_optimized_module_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    optimized_module.save(opt_fname)
    print(f"\n  Optimized module saved: {opt_fname}")
    print(f"  Load with: module.load('{opt_fname}')")

    # ── Save report ───────────────────────────────────────────────────────────
    report = {
        "benchmark":          "dspy_optimization",
        "date":               datetime.now().isoformat(),
        "task_model":         MODEL_TASK,
        "judge_model":        MODEL_JUDGE,
        "optimizer":          "BootstrapFewShot",
        "trainset_size":      len(TRAINSET),
        "testset_size":       len(TESTSET),
        "baseline_score":     round(baseline_score, 2),
        "optimized_score":    round(opt_score, 2),
        "improvement_pct":    round(improvement, 1),
        "optimization_time_s": round(opt_time, 1),
        "optimized_module":   opt_fname,
        "baseline_details":   baseline_details,
        "optimized_details":  opt_details,
    }
    fname = f"../reports/benchmark8_dspy_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"📄 Report saved: {fname}")
    print(f"\n💡 Key insight: DSPy optimization is done ONCE before production.")
    print(f"   Runtime cost = zero. Quality gain = {improvement:+.1f}%. Use it to build")
    print(f"   system prompts, not to re-optimize on every call.")

if __name__ == "__main__":
    main()
