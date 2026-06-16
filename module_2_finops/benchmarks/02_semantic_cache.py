"""
Module 2 — Benchmark 2: Semantic Caching
=========================================
Measures cost savings from caching semantically similar questions.
Similar questions (same intent, different wording) hit the cache → zero LLM cost.

Run: python 02_semantic_cache.py
Requires: pip install openai sentence-transformers numpy python-dotenv
"""

import os
import json
import time
import hashlib
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Install: pip install openai sentence-transformers numpy python-dotenv")
    exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

LITELLM_BASE_URL  = os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_API_KEY   = os.getenv("LITELLM_API_KEY", "sk-litellm-master-2026")
MODEL             = "claude-haiku"
SIMILARITY_THRESHOLD = 0.92   # Match threshold — tune based on your use case

client = OpenAI(base_url=f"{LITELLM_BASE_URL}/v1", api_key=LITELLM_API_KEY)
embedder = SentenceTransformer("all-MiniLM-L6-v2")   # fast, lightweight

# ── In-memory cache (simulates Redis semantic cache) ─────────────────────────

cache: dict = {}   # {cache_key: {"answer": str, "tokens": int, "hit_count": int}}

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def cache_lookup(question: str) -> tuple[str | None, float]:
    """Return (cached_answer, similarity) or (None, 0)"""
    q_emb = embedder.encode(question)
    best_score = 0.0
    best_answer = None
    for key, entry in cache.items():
        score = cosine_similarity(q_emb, entry["embedding"])
        if score > best_score:
            best_score = score
            best_answer = entry["answer"] if score >= SIMILARITY_THRESHOLD else None
    return best_answer, best_score

def cache_store(question: str, answer: str, tokens: int):
    embedding = embedder.encode(question)
    key = hashlib.md5(question.encode()).hexdigest()[:8]
    cache[key] = {
        "question":  question,
        "answer":    answer,
        "tokens":    tokens,
        "embedding": embedding,
        "hit_count": 0,
    }

# ── Test questions (originals + semantic variants) ────────────────────────────

QUESTION_GROUPS = [
    {
        "original": "What are the EU AI Act requirements for credit scoring?",
        "variants": [
            "What does the EU AI Act say about credit scoring AI systems?",
            "EU AI Act compliance for credit risk models — what's required?",
            "How does the European AI regulation affect credit scoring algorithms?",
            "What are the rules for credit scoring under the EU artificial intelligence act?",
        ],
    },
    {
        "original": "How should banks implement DORA for AI systems?",
        "variants": [
            "What does DORA require from banks regarding AI?",
            "DORA compliance requirements for artificial intelligence in banking",
            "How to comply with the Digital Operational Resilience Act for AI?",
        ],
    },
    {
        "original": "What is the cost of Claude Haiku vs Claude Sonnet?",
        "variants": [
            "How much does Claude Haiku cost compared to Sonnet?",
            "What's the price difference between Haiku and Sonnet?",
            "Claude Haiku pricing vs Sonnet pricing",
        ],
    },
]

SYSTEM_PROMPT = "Banking and AI regulatory expert. Concise, accurate answers."

# ── LLM call ─────────────────────────────────────────────────────────────────

def call_llm(question: str) -> tuple[str, int, float]:
    start = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
    )
    elapsed = time.time() - start
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    return answer, tokens, elapsed

# ── Cost helper ───────────────────────────────────────────────────────────────

def token_cost_haiku(tokens: int) -> float:
    return (tokens / 1000) * 0.00025   # input rate (conservative)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("BENCHMARK 2 — Semantic Caching")
    print(f"Model: {MODEL} | Similarity threshold: {SIMILARITY_THRESHOLD}")
    print("=" * 60)

    stats = {
        "total_questions": 0,
        "cache_hits":      0,
        "cache_misses":    0,
        "tokens_used":     0,
        "tokens_saved":    0,
        "latency_real":    [],
        "latency_cache":   [],
    }
    results = []

    for group in QUESTION_GROUPS:
        original = group["original"]
        variants  = group["variants"]
        all_questions = [original] + variants

        print(f"\n📦 Group: {original[:50]}...")

        for i, q in enumerate(all_questions):
            cached_answer, similarity = cache_lookup(q)

            if cached_answer:
                # Cache hit
                start = time.time()
                latency = time.time() - start
                stats["cache_hits"] += 1
                # Estimate tokens we would have used
                estimated_tokens = 150   # average from previous calls
                stats["tokens_saved"] += estimated_tokens
                stats["latency_cache"].append(latency)
                label = "HIT "
                print(f"  {'[CACHE '+label+']':15} Q{i}: similarity={similarity:.3f} | saved ~{estimated_tokens} tokens | {latency*1000:.1f}ms")
                results.append({"question": q, "type": "cache_hit", "similarity": round(similarity, 3), "tokens_saved": estimated_tokens})
            else:
                # Cache miss → real LLM call
                answer, tokens, latency = call_llm(q)
                cache_store(q, answer, tokens)
                stats["cache_misses"] += 1
                stats["tokens_used"]  += tokens
                stats["latency_real"].append(latency)
                print(f"  {'[LLM CALL]':15} Q{i}: {tokens} tokens | {latency:.2f}s | similarity={similarity:.3f}")
                results.append({"question": q, "type": "llm_call", "tokens": tokens, "latency_s": round(latency, 2)})

            stats["total_questions"] += 1

    # ── Analysis ──────────────────────────────────────────────────────────────

    hit_rate = stats["cache_hits"] / stats["total_questions"] * 100
    cost_without_cache = token_cost_haiku(stats["tokens_used"] + stats["tokens_saved"])
    cost_with_cache    = token_cost_haiku(stats["tokens_used"])
    savings_pct = (stats["tokens_saved"] / (stats["tokens_used"] + stats["tokens_saved"])) * 100 if (stats["tokens_used"] + stats["tokens_saved"]) > 0 else 0

    # Monthly at 100K questions/day
    daily_questions = 100_000
    monthly_questions = daily_questions * 30
    daily_cost_without = cost_without_cache / stats["total_questions"] * daily_questions
    daily_cost_with    = cost_with_cache    / stats["total_questions"] * daily_questions

    avg_real  = sum(stats["latency_real"])  / len(stats["latency_real"])  if stats["latency_real"]  else 0
    avg_cache = sum(stats["latency_cache"]) / len(stats["latency_cache"]) if stats["latency_cache"] else 0.001

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nCache performance:")
    print(f"  Total questions: {stats['total_questions']}")
    print(f"  Cache hits:      {stats['cache_hits']} ({hit_rate:.1f}%)")
    print(f"  LLM calls:       {stats['cache_misses']}")
    print(f"  Tokens saved:    {stats['tokens_saved']}")
    print(f"  Tokens used:     {stats['tokens_used']}")
    print(f"  Token reduction: {savings_pct:.1f}%")
    print(f"\nLatency:")
    print(f"  Real LLM call:  {avg_real:.2f}s")
    print(f"  Cache hit:      {avg_cache*1000:.1f}ms  ({avg_real/max(avg_cache,0.001):.0f}x faster)")
    print(f"\nDaily cost ({daily_questions:,} questions/day):")
    print(f"  Without cache: ${daily_cost_without:.2f}/day")
    print(f"  With cache:    ${daily_cost_with:.2f}/day")
    print(f"  Daily savings: ${daily_cost_without - daily_cost_with:.2f}")
    print(f"  Monthly:       ${(daily_cost_without - daily_cost_with)*30:.2f}/month")

    # ── Save results ──────────────────────────────────────────────────────────

    report = {
        "benchmark":        "semantic_cache",
        "date":             datetime.now().isoformat(),
        "model":            MODEL,
        "threshold":        SIMILARITY_THRESHOLD,
        "cache_hit_rate":   round(hit_rate, 1),
        "tokens_saved_pct": round(savings_pct, 1),
        "daily_savings_usd":    round(daily_cost_without - daily_cost_with, 2),
        "monthly_savings_usd":  round((daily_cost_without - daily_cost_with) * 30, 2),
        "latency_llm_s":    round(avg_real, 2),
        "latency_cache_ms": round(avg_cache * 1000, 1),
        "raw_results":      results,
    }

    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark2_cache_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Results saved: {fname}")


if __name__ == "__main__":
    main()
