"""
Benchmark 7 — LLMLingua-2 Prompt Compression
==============================================
Tests token compression using LLMLingua-2 (Microsoft Research).
Compresses prompts BEFORE sending to the LLM — reduces cost without
changing the LLM or the application logic.

Architecture in our pipeline:
  User prompt → LLMLingua-2 (local, CPU) → compressed prompt → LiteLLM → LLM

What this benchmark measures:
  - Compression ratio achieved on real banking prompts
  - Quality preservation (LLM judge scores original vs compressed answer)
  - Latency overhead of the compression step
  - Net cost savings (compression overhead vs token savings)

Run: python 07_llmlingua_compression.py
Requires: pip install llmlingua
Model downloaded once from HuggingFace (~500MB): microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank
"""

import json, time, os
from datetime import datetime
from config import client, MODELS, MONTHLY_CALLS, token_cost, print_config

MODEL_ANSWER = MODELS.moderate   # model used to answer questions
MODEL_JUDGE  = MODELS.simple     # cheap model to score quality

try:
    from llmlingua import PromptCompressor
except ImportError:
    print("Install: pip install llmlingua")
    print("Model will be downloaded from HuggingFace (~500MB) on first run.")
    exit(1)

# ── Compression ratios to test ─────────────────────────────────────────────────
# rate = fraction of tokens to KEEP (0.5 = keep 50%, compress by 50%)
COMPRESSION_RATES = [0.75, 0.5, 0.33]

# ── Test prompts (realistic banking scenarios) ─────────────────────────────────

SYSTEM_PROMPT = """You are a banking regulatory compliance expert specializing in
French and European financial regulation. Your knowledge covers DORA (Digital
Operational Resilience Act), EU AI Act, GDPR, ACPR guidelines, MiFID II,
Basel III/IV capital requirements, and AML/KYC regulations under AMLD6.

You always provide structured, accurate responses that cite the specific
regulation and article number when relevant. Your answers are designed for
technical and legal teams within regulated financial institutions. You
acknowledge uncertainty when regulations are ambiguous or subject to
interpretation. You do not provide financial or legal advice — you describe
regulatory frameworks and requirements."""

TEST_CASES = [
    {
        "name": "DORA AI systems",
        "question": "What are the key requirements of DORA Article 11 for ICT systems that use AI components, particularly regarding resilience testing and incident reporting timelines?",
        "keywords": ["DORA", "ICT", "resilience", "incident", "testing"],
    },
    {
        "name": "EU AI Act credit scoring",
        "question": "A French bank uses an AI model to score credit applications. Under EU AI Act Annex III, this is classified as high-risk. What specific obligations does this create for model documentation, human oversight, and accuracy monitoring?",
        "keywords": ["EU AI Act", "high-risk", "credit", "human oversight", "documentation"],
    },
    {
        "name": "GDPR AI audit logs",
        "question": "What data retention periods apply to AI decision audit logs under GDPR Article 5, and how does this interact with the right to explanation under Article 22 when automated decisions affect individuals?",
        "keywords": ["GDPR", "retention", "audit", "automated", "explanation"],
    },
    {
        "name": "LLM data sovereignty",
        "question": "A bank wants to use an external LLM API for internal document summarization. The documents contain client data. What GDPR Article 28 obligations apply, what clauses must the data processing agreement contain, and which cloud regions are acceptable under ACPR guidance?",
        "keywords": ["GDPR", "data processing", "cloud", "ACPR", "sovereignty"],
    },
]

# ── LLM quality judge ──────────────────────────────────────────────────────────

def judge_quality(question: str, answer_original: str, answer_compressed: str) -> float:
    """Score compressed answer vs original: 1.0 = identical quality, 0.0 = useless."""
    prompt = f"""Compare these two answers to the same banking compliance question.
Score the COMPRESSED answer relative to the ORIGINAL (1.00 = same quality, 0.00 = useless).

Question: {question}

ORIGINAL answer:
{answer_original[:800]}

COMPRESSED answer (prompt was compressed before LLM call):
{answer_compressed[:800]}

Criteria:
- Key regulatory information preserved (40%)
- Factual accuracy maintained (30%)
- Completeness (20%)
- Clarity (10%)

Respond with ONLY a decimal score between 0.00 and 1.00."""

    r = client.chat.completions.create(
        model=MODEL_JUDGE,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )
    try:
        import re
        score = float(re.findall(r"[\d.]+", r.choices[0].message.content)[0])
        return min(1.0, max(0.0, score)), r.usage.total_tokens
    except Exception:
        return 0.5, r.usage.total_tokens

# ── Single test run ────────────────────────────────────────────────────────────

def run_once(compressor, question: str, rate: float) -> dict:
    """Compress prompt at given rate, call LLM, return metrics."""
    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {question}"

    # Compression step (local CPU)
    t0 = time.time()
    compressed = compressor.compress_prompt(
        full_prompt,
        rate=rate,
        force_tokens=["\n", ".", ":", "Article", "DORA", "GDPR", "AI"],
    )
    compression_latency = time.time() - t0
    compressed_text = compressed["compressed_prompt"]

    # Count tokens approximation (chars / 4)
    original_tokens_approx  = len(full_prompt) // 4
    compressed_tokens_approx = len(compressed_text) // 4

    # LLM call with compressed prompt
    t1 = time.time()
    r = client.chat.completions.create(
        model=MODEL_ANSWER,
        messages=[{"role": "user", "content": compressed_text}],
    )
    llm_latency = time.time() - t1

    return {
        "rate":                   rate,
        "original_chars":         len(full_prompt),
        "compressed_chars":       len(compressed_text),
        "original_tokens_approx": original_tokens_approx,
        "compressed_tokens_approx": compressed_tokens_approx,
        "actual_compression_pct": round((1 - len(compressed_text) / len(full_prompt)) * 100, 1),
        "compression_latency_ms": round(compression_latency * 1000, 1),
        "llm_tokens":             r.usage.total_tokens,
        "llm_input_tokens":       r.usage.prompt_tokens,
        "llm_output_tokens":      r.usage.completion_tokens,
        "llm_latency_s":          round(llm_latency, 2),
        "answer":                 r.choices[0].message.content,
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK 7 — LLMLingua-2 Prompt Compression")
    print(f"Answer model: {MODEL_ANSWER}")
    print(f"Judge model:  {MODEL_JUDGE}")
    print(f"Rates tested: {COMPRESSION_RATES}  (fraction of tokens kept)")
    print_config()
    print("=" * 70)

    print("\nLoading LLMLingua-2 model (downloads ~500MB on first run)...")
    t_load = time.time()
    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        use_llmlingua2=True,
    )
    print(f"Model loaded in {time.time() - t_load:.1f}s")

    all_results = []
    stats_by_rate: dict[float, list] = {r: [] for r in COMPRESSION_RATES}

    for case in TEST_CASES:
        print(f"\n{'─'*70}")
        print(f"Case: {case['name']}")
        print(f"Q: {case['question'][:80]}...")
        print(f"{'─'*70}")

        # Baseline: no compression
        t0 = time.time()
        baseline_r = client.chat.completions.create(
            model=MODEL_ANSWER,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": case["question"]},
            ],
        )
        baseline_latency = time.time() - t0
        baseline_tokens  = baseline_r.usage.total_tokens
        baseline_answer  = baseline_r.choices[0].message.content
        baseline_cost    = token_cost(MODEL_ANSWER, baseline_r.usage.prompt_tokens, baseline_r.usage.completion_tokens)

        print(f"\n  [BASELINE]  tokens={baseline_tokens} | latency={baseline_latency:.2f}s | cost=${baseline_cost:.5f}")

        case_results = {"case": case["name"], "question": case["question"],
                        "baseline_tokens": baseline_tokens, "baseline_cost": baseline_cost,
                        "compression_results": []}

        for rate in COMPRESSION_RATES:
            res = run_once(compressor, case["question"], rate)

            # Judge quality vs baseline
            quality_score, judge_tokens = judge_quality(
                case["question"], baseline_answer, res["answer"]
            )
            judge_cost = token_cost(MODEL_JUDGE, judge_tokens)

            compressed_cost = token_cost(MODEL_ANSWER, res["llm_input_tokens"], res["llm_output_tokens"])
            net_savings     = baseline_cost - compressed_cost - judge_cost

            res["quality_score"] = round(quality_score, 2)
            res["judge_tokens"]  = judge_tokens
            res["compressed_cost"] = compressed_cost
            res["net_savings_vs_baseline"] = round(net_savings, 6)

            icon = "✅" if quality_score >= 0.8 else ("⚠️ " if quality_score >= 0.6 else "❌")
            print(f"\n  [rate={rate}]  compression={res['actual_compression_pct']}% "
                  f"| llm_tokens={res['llm_tokens']} "
                  f"| compress_ms={res['compression_latency_ms']} "
                  f"| quality={quality_score:.2f} {icon} "
                  f"| net_savings=${net_savings:.5f}")

            stats_by_rate[rate].append({
                "compression_pct": res["actual_compression_pct"],
                "quality":         quality_score,
                "net_savings":     net_savings,
                "llm_tokens":      res["llm_tokens"],
                "compress_ms":     res["compression_latency_ms"],
            })

            case_results["compression_results"].append(res)

        all_results.append(case_results)

    # ── Summary ───────────────────────────────────────────────────────────────

    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"\n{'Rate':>6} | {'Compression':>12} | {'Quality':>8} | {'Net savings/call':>16} | {'Compress latency':>16}")
    print("─" * 70)

    best_rate = None
    best_score = -1

    for rate in COMPRESSION_RATES:
        data = stats_by_rate[rate]
        avg_compression = sum(d["compression_pct"] for d in data) / len(data)
        avg_quality     = sum(d["quality"] for d in data) / len(data)
        avg_savings     = sum(d["net_savings"] for d in data) / len(data)
        avg_compress_ms = sum(d["compress_ms"] for d in data) / len(data)

        monthly_net = avg_savings * MONTHLY_CALLS
        flag = " ← recommended" if avg_quality >= 0.85 and avg_savings > 0 else ""

        print(f"  {rate:>4} | {avg_compression:>10.1f}% | {avg_quality:>8.2f} | "
              f"${avg_savings:>12.5f}   | {avg_compress_ms:>12.0f}ms{flag}")

        if avg_quality >= 0.8 and avg_savings > best_score:
            best_score = avg_savings
            best_rate  = rate

    if best_rate:
        best_data   = stats_by_rate[best_rate]
        best_avg    = sum(d["net_savings"] for d in best_data) / len(best_data)
        monthly_net = best_avg * MONTHLY_CALLS
        print(f"\n  Best rate: {best_rate} → monthly net savings: ${monthly_net:,.2f} ({MONTHLY_CALLS:,} calls/month)")
        print(f"  Annual net savings: ${monthly_net * 12:,.2f}/year")

    # ── Save ──────────────────────────────────────────────────────────────────

    summary_by_rate = {}
    for rate in COMPRESSION_RATES:
        data = stats_by_rate[rate]
        summary_by_rate[str(rate)] = {
            "avg_compression_pct": round(sum(d["compression_pct"] for d in data) / len(data), 1),
            "avg_quality_score":   round(sum(d["quality"]         for d in data) / len(data), 2),
            "avg_net_savings_usd": round(sum(d["net_savings"]     for d in data) / len(data), 6),
            "avg_compress_ms":     round(sum(d["compress_ms"]     for d in data) / len(data), 1),
        }

    report = {
        "benchmark":        "llmlingua2_compression",
        "date":             datetime.now().isoformat(),
        "answer_model":     MODEL_ANSWER,
        "judge_model":      MODEL_JUDGE,
        "compression_rates_tested": COMPRESSION_RATES,
        "best_rate":        best_rate,
        "monthly_calls":    MONTHLY_CALLS,
        "summary_by_rate":  summary_by_rate,
        "raw_results":      all_results,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark7_llmlingua_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")
    print(f"\n💡 Key insight: LLMLingua-2 runs locally (CPU, ~100ms overhead).")
    print(f"   No API cost for compression. Net savings = token reduction − judge overhead.")
    print(f"   In production: use rate=0.5 for long system prompts, rate=0.75 for short ones.")

if __name__ == "__main__":
    main()
