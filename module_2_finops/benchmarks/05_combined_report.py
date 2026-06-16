"""
Module 2 — Combined FinOps Report
===================================
Reads all benchmark JSON results and generates a final FinOps report.
Use this AFTER running benchmarks 01 through 04.

Run: python 05_combined_report.py
"""

import os
import json
import glob
from datetime import datetime

REPORTS_DIR = "../reports"

def load_latest(pattern: str) -> dict | None:
    files = sorted(glob.glob(os.path.join(REPORTS_DIR, pattern)))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)

def fmt(value: float, prefix: str = "$") -> str:
    return f"{prefix}{value:,.0f}" if value >= 100 else f"{prefix}{value:.2f}"

def main():
    print("=" * 65)
    print("AI FINOPS REPORT — LLM Cost Optimization")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Stack: LiteLLM + Langfuse (self-hosted)")
    print("=" * 65)

    b1 = load_latest("benchmark1_prompt_*.json")
    b2 = load_latest("benchmark2_cache_*.json")
    b3 = load_latest("benchmark3_routing_*.json")
    b4 = load_latest("benchmark4_history_*.json")

    missing = []
    if not b1: missing.append("01_prompt_optimization.py")
    if not b2: missing.append("02_semantic_cache.py")
    if not b3: missing.append("03_model_routing.py")
    if not b4: missing.append("04_conversation_history.py")

    if missing:
        print(f"\n⚠️  Missing benchmark results. Run first:")
        for m in missing:
            print(f"   python {m}")
        print()

    # ── Lever 1: Prompt Optimization ─────────────────────────────────────────

    print("\n📊 LEVER 1 — Prompt Optimization")
    print("-" * 40)
    if b1:
        print(f"  Token reduction:    {b1['reduction_pct']}%")
        print(f"  Monthly cost (was): {fmt(b1['monthly_cost_naive_usd'])}/month")
        print(f"  Monthly cost (now): {fmt(b1['monthly_cost_opt_usd'])}/month")
        print(f"  Monthly savings:    {fmt(b1['monthly_savings_usd'])}/month")
        print(f"  Annual savings:     {fmt(b1['annual_savings_usd'])}/year")
        print(f"  Effort:             ~2 hours")
        savings_1 = b1["annual_savings_usd"]
    else:
        print("  ⚠️  No data — run 01_prompt_optimization.py")
        savings_1 = 0

    # ── Lever 2: Semantic Caching ─────────────────────────────────────────────

    print("\n📊 LEVER 2 — Semantic Caching")
    print("-" * 40)
    if b2:
        print(f"  Cache hit rate:     {b2['cache_hit_rate']}%")
        print(f"  Token savings:      {b2['tokens_saved_pct']}%")
        print(f"  Latency (LLM):      {b2['latency_llm_s']}s")
        print(f"  Latency (cache):    {b2['latency_cache_ms']}ms  ({b2['latency_llm_s']/max(b2['latency_cache_ms']/1000, 0.001):.0f}x faster)")
        print(f"  Monthly savings:    {fmt(b2['monthly_savings_usd'])}/month")
        print(f"  Annual savings:     {fmt(b2['monthly_savings_usd']*12)}/year")
        print(f"  Effort:             ~4 hours (Redis + sentence-transformers)")
        savings_2 = b2["monthly_savings_usd"] * 12
    else:
        print("  ⚠️  No data — run 02_semantic_cache.py")
        savings_2 = 0

    # ── Lever 3: Model Routing ────────────────────────────────────────────────

    print("\n📊 LEVER 3 — Smart Model Routing")
    print("-" * 40)
    if b3:
        print(f"  Classifier accuracy:{b3['classifier_accuracy_pct']}%")
        print(f"  Cost reduction:     {b3['savings_pct']}%")
        print(f"  Monthly savings:    {fmt(b3['monthly_savings_usd'])}/month")
        print(f"  Annual savings:     {fmt(b3['annual_savings_usd'])}/year")
        dist = b3.get("distribution", {})
        if dist:
            total = sum(dist.values())
            print(f"  Distribution:      ", end="")
            print(" | ".join(f"{k}: {v/total*100:.0f}%" for k, v in sorted(dist.items())))
        print(f"  Effort:             ~2 hours (LiteLLM router config)")
        savings_3 = b3["annual_savings_usd"]
    else:
        print("  ⚠️  No data — run 03_model_routing.py")
        savings_3 = 0

    # ── Lever 4: Conversation History ─────────────────────────────────────────

    print("\n📊 LEVER 4 — Conversation History Management")
    print("-" * 40)
    if b4:
        print(f"  Token growth (unmanaged): {b4['token_growth_factor']}x over conversation")
        print(f"  Cost reduction:     {b4['savings_pct']}%")
        print(f"  Monthly savings:    {fmt(b4['monthly_savings_usd'])}/month")
        print(f"  Annual savings:     {fmt(b4['annual_savings_usd'])}/year")
        print(f"  Effort:             ~1 hour (sliding window in chat handler)")
        savings_4 = b4["annual_savings_usd"]
    else:
        print("  ⚠️  No data — run 04_conversation_history.py")
        savings_4 = 0

    # ── Combined impact ───────────────────────────────────────────────────────

    total_annual = savings_1 + savings_2 + savings_3 + savings_4

    print("\n" + "=" * 65)
    print("COMBINED ANNUAL SAVINGS")
    print("=" * 65)
    print(f"  Lever 1 — Prompt optimization:          {fmt(savings_1):>15}/year")
    print(f"  Lever 2 — Semantic caching:             {fmt(savings_2):>15}/year")
    print(f"  Lever 3 — Model routing:                {fmt(savings_3):>15}/year")
    print(f"  Lever 4 — Conversation management:      {fmt(savings_4):>15}/year")
    print(f"  {'─'*50}")
    print(f"  TOTAL SAVINGS:                          {fmt(total_annual):>15}/year")
    print(f"  Total effort:                           ~9–12 hours")

    print(f"""
┌──────────────────────────────────────────────────────────────┐
│  EXECUTIVE SUMMARY                                           │
│                                                              │
│  4 optimization levers identified and measured.              │
│  Combined annual savings: {fmt(total_annual):>10}                   │
│  Implementation effort:   9–12 hours                         │
│  Time to ROI:             < 1 month                          │
│                                                              │
│  Stack: LiteLLM (gateway) + Langfuse (observability)        │
│  Self-hosted. GDPR compliant. EU AI Act ready.               │
│  No vendor lock-in. Open source (MIT license).               │
└──────────────────────────────────────────────────────────────┘
""")

    # ── Save markdown report ──────────────────────────────────────────────────

    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    fname = os.path.join(REPORTS_DIR, f"finops_report_{date_str}.md")

    with open(fname, "w") as f:
        f.write(f"# AI FinOps Report — {date_str}\n\n")
        f.write("**Stack:** LiteLLM + Langfuse (self-hosted, open source)\n\n")
        f.write("## Savings by Lever\n\n")
        f.write("| Lever | Annual Savings | Effort |\n")
        f.write("|---|---|---|\n")
        f.write(f"| Prompt Optimization | {fmt(savings_1)}/year | 2h |\n")
        f.write(f"| Semantic Caching | {fmt(savings_2)}/year | 4h |\n")
        f.write(f"| Model Routing | {fmt(savings_3)}/year | 2h |\n")
        f.write(f"| Conversation Management | {fmt(savings_4)}/year | 1h |\n")
        f.write(f"| **TOTAL** | **{fmt(total_annual)}/year** | **~10h** |\n\n")
        if b1:
            f.write(f"## Details\n\n")
            f.write(f"- Prompt token reduction: {b1['reduction_pct']}%\n")
        if b2:
            f.write(f"- Cache hit rate: {b2['cache_hit_rate']}%\n")
        if b3:
            f.write(f"- Routing savings: {b3['savings_pct']}%\n")
        if b4:
            f.write(f"- Context growth factor (unmanaged): {b4['token_growth_factor']}x\n")

    print(f"📄 Markdown report saved: {fname}")
    print(f"📄 Use this for client pitches and LinkedIn posts.\n")


if __name__ == "__main__":
    main()
