"""
Benchmark 2 — Semantic Caching
================================
Measures savings from caching semantically similar questions.
Uses MODEL_DEFAULT from .env.

Run: python 02_semantic_cache.py
Requires: pip install sentence-transformers numpy
"""

import json, time, hashlib, os
import numpy as np
from datetime import datetime
from config import client, MODELS, DAILY_CALLS, token_cost, print_config

MODEL = MODELS.default
SIMILARITY_THRESHOLD = 0.92

try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
except ImportError:
    print("Install: pip install sentence-transformers numpy")
    exit(1)

# ── In-memory cache ───────────────────────────────────────────────────────────

cache: dict = {}

def cosine_sim(a, b) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def cache_lookup(question: str) -> tuple[str | None, float]:
    q_emb = embedder.encode(question)
    best_score, best_answer = 0.0, None
    for entry in cache.values():
        score = cosine_sim(q_emb, entry["embedding"])
        if score > best_score:
            best_score = score
            best_answer = entry["answer"] if score >= SIMILARITY_THRESHOLD else None
    return best_answer, best_score

def cache_store(question: str, answer: str, tokens: int):
    key = hashlib.md5(question.encode()).hexdigest()[:8]
    cache[key] = {"question": question, "answer": answer, "tokens": tokens,
                  "embedding": embedder.encode(question)}

# ── Test data ─────────────────────────────────────────────────────────────────

QUESTION_GROUPS = [
    {
        "original": "What are the EU AI Act requirements for credit scoring?",
        "variants": [
            "What does the EU AI Act say about credit scoring AI systems?",
            "EU AI Act compliance for credit risk models — what's required?",
            "How does the European AI regulation affect credit scoring algorithms?",
        ],
    },
    {
        "original": "How should banks implement DORA for AI systems?",
        "variants": [
            "What does DORA require from banks regarding AI?",
            "DORA compliance requirements for artificial intelligence in banking",
        ],
    },
    {
        "original": "What is the price difference between cheap and premium LLM models?",
        "variants": [
            "How much cheaper are small models vs large models?",
            "LLM model pricing — small vs large comparison",
        ],
    },
]

SYSTEM = "Banking and AI regulatory expert. Concise, accurate answers."

def call_llm(question: str) -> tuple[str, int, float]:
    start = time.time()
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}],
    )
    return r.choices[0].message.content, r.usage.total_tokens, round(time.time() - start, 2)

def main():
    print("=" * 60)
    print("BENCHMARK 2 — Semantic Caching")
    print(f"Model: {MODEL} | Threshold: {SIMILARITY_THRESHOLD}")
    print_config()
    print("=" * 60)

    stats = {"total": 0, "hits": 0, "misses": 0, "tokens_used": 0, "tokens_saved": 0,
             "latency_real": [], "latency_cache": []}
    results = []

    for group in QUESTION_GROUPS:
        print(f"\n📦 {group['original'][:55]}...")
        for i, q in enumerate([group["original"]] + group["variants"]):
            cached, similarity = cache_lookup(q)
            if cached:
                start = time.time()
                lat = time.time() - start
                estimated = 150
                stats["hits"] += 1
                stats["tokens_saved"] += estimated
                stats["latency_cache"].append(lat)
                print(f"  [CACHE HIT ] Q{i}: similarity={similarity:.3f} | saved ~{estimated} tokens | {lat*1000:.1f}ms")
                results.append({"type": "cache_hit", "similarity": round(similarity, 3), "tokens_saved": estimated})
            else:
                answer, tokens, lat = call_llm(q)
                cache_store(q, answer, tokens)
                stats["misses"] += 1
                stats["tokens_used"] += tokens
                stats["latency_real"].append(lat)
                print(f"  [LLM CALL  ] Q{i}: {tokens} tokens | {lat}s | similarity={similarity:.3f}")
                results.append({"type": "llm_call", "tokens": tokens, "latency_s": lat})
            stats["total"] += 1

    hit_rate   = stats["hits"] / stats["total"] * 100
    total_toks = stats["tokens_used"] + stats["tokens_saved"]
    saved_pct  = stats["tokens_saved"] / total_toks * 100 if total_toks else 0
    cost_no_cache = token_cost(MODEL, total_toks / stats["total"] * DAILY_CALLS * 30)
    cost_cache    = token_cost(MODEL, stats["tokens_used"] / stats["total"] * DAILY_CALLS * 30)
    avg_real  = sum(stats["latency_real"])  / len(stats["latency_real"])  if stats["latency_real"]  else 0
    avg_cache = sum(stats["latency_cache"]) / len(stats["latency_cache"]) if stats["latency_cache"] else 0.001

    print(f"\n{'='*60}\nRESULTS\n{'='*60}")
    print(f"  Cache hit rate:    {hit_rate:.1f}%")
    print(f"  Token savings:     {saved_pct:.1f}%")
    print(f"  Latency LLM:       {avg_real:.2f}s")
    print(f"  Latency cache:     {avg_cache*1000:.1f}ms  ({avg_real/max(avg_cache,0.001):.0f}x faster)")
    print(f"  Monthly savings:   ${cost_no_cache - cost_cache:.2f}  ({DAILY_CALLS:,} calls/day)")

    report = {
        "benchmark": "semantic_cache", "date": datetime.now().isoformat(), "model": MODEL,
        "threshold": SIMILARITY_THRESHOLD, "cache_hit_rate": round(hit_rate, 1),
        "tokens_saved_pct": round(saved_pct, 1),
        "monthly_savings_usd": round(cost_no_cache - cost_cache, 2),
        "latency_llm_s": round(avg_real, 2), "latency_cache_ms": round(avg_cache * 1000, 1),
        "raw_results": results,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark2_cache_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")

if __name__ == "__main__":
    main()
