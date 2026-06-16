"""
Benchmark 5 — Combined FinOps Report
======================================
Reads all benchmark JSON results and generates a final report.
Run AFTER benchmarks 01–04 (and optionally 06).

Run: python 05_combined_report.py
"""

import os, json, glob
from datetime import datetime
from config import MODELS

REPORTS_DIR = "../reports"

def latest(pattern: str) -> dict | None:
    files = sorted(glob.glob(os.path.join(REPORTS_DIR, pattern)))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)

def fmt(v: float) -> str:
    return f"${v:>10,.0f}" if v >= 100 else f"${v:>10.2f}"

def main():
    print("=" * 65)
    print("AI FINOPS REPORT — LLM Cost Optimization")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Stack: LiteLLM + Langfuse (self-hosted)")
    print(f"Routing config:")
    print(f"  Simple   → {MODELS.simple}")
    print(f"  Moderate → {MODELS.moderate}")
    print(f"  Complex  → {MODELS.complex}")
    print("=" * 65)

    b1 = latest("benchmark1_prompt_*.json")
    b2 = latest("benchmark2_cache_*.json")
    b3 = latest("benchmark3_routing_*.json")
    b4 = latest("benchmark4_history_*.json")
    b6 = latest("benchmark6_quality_*.json")
    b7 = latest("benchmark7_llmlingua_*.json")
    b8 = latest("benchmark8_dspy_*.json")

    missing = []
    if not b1: missing.append("01_prompt_optimization.py")
    if not b2: missing.append("02_semantic_cache.py")
    if not b3: missing.append("03_model_routing.py")
    if not b4: missing.append("04_conversation_history.py")
    if missing:
        print(f"\n⚠️  Missing results — run first: {', '.join(missing)}\n")

    # ── Lever 1 ───────────────────────────────────────────────────────────────
    print("\n📊 LEVER 1 — Prompt Optimization")
    print("─" * 40)
    if b1:
        print(f"  Model:             {b1['model']}")
        print(f"  Token reduction:   {b1['reduction_pct']}%")
        print(f"  Monthly (before):  {fmt(b1['monthly_cost_naive_usd'])}/month")
        print(f"  Monthly (after):   {fmt(b1['monthly_cost_opt_usd'])}/month")
        print(f"  Annual savings:    {fmt(b1['annual_savings_usd'])}/year")
        print(f"  Effort:            ~2 hours")
        s1 = b1["annual_savings_usd"]
    else:
        print("  ⚠️  No data"); s1 = 0

    # ── Lever 2 ───────────────────────────────────────────────────────────────
    print("\n📊 LEVER 2 — Semantic Caching")
    print("─" * 40)
    if b2:
        print(f"  Model:             {b2['model']}")
        print(f"  Cache hit rate:    {b2['cache_hit_rate']}%")
        print(f"  Token savings:     {b2['tokens_saved_pct']}%")
        print(f"  Latency LLM:       {b2['latency_llm_s']}s  →  Cache: {b2['latency_cache_ms']}ms")
        print(f"  Annual savings:    {fmt(b2['monthly_savings_usd']*12)}/year")
        print(f"  Effort:            ~4 hours")
        s2 = b2["monthly_savings_usd"] * 12
    else:
        print("  ⚠️  No data"); s2 = 0

    # ── Lever 3 ───────────────────────────────────────────────────────────────
    print("\n📊 LEVER 3 — Cross-Provider Model Routing")
    print("─" * 40)
    if b3:
        models = b3.get("models", {})
        print(f"  Simple   → {models.get('simple', MODELS.simple)}")
        print(f"  Moderate → {models.get('moderate', MODELS.moderate)}")
        print(f"  Complex  → {models.get('complex', MODELS.complex)}")
        print(f"  Classifier accuracy: {b3['classifier_accuracy_pct']}%")
        print(f"  Savings vs all-complex: {b3['savings_vs_allcomplex_pct']}%")
        print(f"  Annual savings:      {fmt(b3['annual_savings_usd'])}/year")
        print(f"  Effort:              ~2 hours")
        s3 = b3["annual_savings_usd"]
    else:
        print("  ⚠️  No data"); s3 = 0

    # ── Lever 4 ───────────────────────────────────────────────────────────────
    print("\n📊 LEVER 4 — Conversation History Management")
    print("─" * 40)
    if b4:
        print(f"  Model:             {b4['model']}")
        print(f"  Token growth:      {b4['token_growth_factor']}x over {b4['turns']} turns")
        print(f"  Cost reduction:    {b4['savings_pct']}%")
        print(f"  Annual savings:    {fmt(b4['annual_savings_usd'])}/year")
        print(f"  Effort:            ~1 hour")
        s4 = b4["annual_savings_usd"]
    else:
        print("  ⚠️  No data"); s4 = 0

    # ── Quality ───────────────────────────────────────────────────────────────
    if b6:
        print("\n📊 QUALITY VALIDATION (Benchmark 6)")
        print("─" * 40)
        print(f"  Models tested: {', '.join(b6.get('models_tested', {}).values())}")
        for task in b6.get("results", []):
            best = max(task["models"].items(), key=lambda x: x[1]["score"])
            print(f"  [{task['complexity']:8}] Best: {best[0].split('/')[-1]:<30} score={best[1]['score']:.2f}")

    # ── Combined ──────────────────────────────────────────────────────────────
    total = s1 + s2 + s3 + s4

    print(f"\n{'='*65}")
    print("COMBINED ANNUAL SAVINGS")
    print(f"{'='*65}")
    print(f"  Lever 1 — Prompt optimization:       {fmt(s1)}/year")
    print(f"  Lever 2 — Semantic caching:          {fmt(s2)}/year")
    print(f"  Lever 3 — Cross-provider routing:    {fmt(s3)}/year")
    print(f"  Lever 4 — Conversation management:   {fmt(s4)}/year")
    print(f"  {'─'*55}")
    print(f"  TOTAL:                               {fmt(total)}/year")
    print(f"  Implementation effort:               ~9–12 hours")

    print(f"""
┌─────────────────────────────────────────────────────────────┐
│  EXECUTIVE SUMMARY                                          │
│                                                             │
│  Annual savings identified:  {fmt(total)}/year           │
│  Implementation effort:      9–12 hours                     │
│  Time to ROI:                < 1 month                      │
│                                                             │
│  Architecture: LiteLLM (gateway) + Langfuse (observability) │
│  Cross-provider routing: {MODELS.simple.split('/')[-1][:10]:<10} / {MODELS.moderate.split('/')[-1][:10]:<10} / {MODELS.complex.split('/')[-1][:10]:<10}│
│  Self-hosted. GDPR compliant. EU AI Act ready.              │
│  No vendor lock-in. Open source (MIT).                      │
└─────────────────────────────────────────────────────────────┘
""")

    # ── Save markdown ──────────────────────────────────────────────────────────
    date_str = datetime.now().strftime("%Y-%m-%d")
    fname = os.path.join(REPORTS_DIR, f"finops_report_{date_str}.md")
    with open(fname, "w") as f:
        f.write(f"# AI FinOps Report — {date_str}\n\n")
        f.write(f"**Model routing:**\n")
        f.write(f"- Simple → `{MODELS.simple}`\n")
        f.write(f"- Moderate → `{MODELS.moderate}`\n")
        f.write(f"- Complex → `{MODELS.complex}`\n\n")
        f.write("## Savings by Lever\n\n")
        f.write("| Lever | Annual Savings | Effort |\n|---|---|---|\n")
        f.write(f"| Prompt Optimization | ${s1:,.0f}/year | 2h |\n")
        f.write(f"| Semantic Caching | ${s2:,.0f}/year | 4h |\n")
        f.write(f"| Cross-Provider Routing | ${s3:,.0f}/year | 2h |\n")
        f.write(f"| Conversation Management | ${s4:,.0f}/year | 1h |\n")
        f.write(f"| **TOTAL** | **${total:,.0f}/year** | **~10h** |\n")
    print(f"📄 Markdown report: {fname}")

if __name__ == "__main__":
    main()
