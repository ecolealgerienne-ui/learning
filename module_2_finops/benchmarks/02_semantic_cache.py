"""
Benchmark 2 — Hybrid Semantic Cache
=====================================
Architecture:
  1. New question arrives
  2. ANN search in Redis (simulated with ChromaDB locally) → top-N candidates
  3. Mistral Small ranks candidates by true semantic similarity
  4. If best candidate score >= threshold → return cached answer (no LLM call)
  5. Otherwise → full LLM call + store in cache

This approach is more reliable than pure cosine similarity because the LLM
understands intent, not just vector proximity.

Run: python 02_semantic_cache.py
Requires: pip install chromadb sentence-transformers
"""

import json, time, os, uuid
from datetime import datetime
from config import client, MODELS, DAILY_CALLS, token_cost, print_config

MODEL_JUDGE  = MODELS.simple     # cheap model for similarity judgment
MODEL_ANSWER = MODELS.moderate   # model used for actual answers on cache miss

SIMILARITY_THRESHOLD = 0.85      # LLM judge score threshold (0-1)
TOP_N_CANDIDATES     = 5         # how many ANN candidates to send to the judge

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Install: pip install chromadb sentence-transformers")
    exit(1)

# ── Vector store (ChromaDB — simulates Redis ANN locally) ─────────────────────

chroma  = chromadb.Client()
store   = chroma.create_collection("cache", get_or_create=True)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory answer store {doc_id → answer}
answer_store: dict[str, str] = {}
token_store:  dict[str, int] = {}

def cache_store(question: str, answer: str, tokens: int) -> str:
    doc_id    = str(uuid.uuid4())
    embedding = embedder.encode(question).tolist()
    store.add(documents=[question], embeddings=[embedding], ids=[doc_id])
    answer_store[doc_id] = answer
    token_store[doc_id]  = tokens
    return doc_id

def cache_ann_search(question: str, top_n: int = TOP_N_CANDIDATES) -> list[dict]:
    """Return top-N closest cached questions with their cosine distances."""
    if store.count() == 0:
        return []
    embedding = embedder.encode(question).tolist()
    results   = store.query(query_embeddings=[embedding], n_results=min(top_n, store.count()))
    candidates = []
    for doc_id, doc, distance in zip(
        results["ids"][0], results["documents"][0], results["distances"][0]
    ):
        cosine_sim = 1 - distance   # ChromaDB returns L2 distance by default
        candidates.append({
            "id":         doc_id,
            "question":   doc,
            "cosine_sim": round(cosine_sim, 3),
            "answer":     answer_store.get(doc_id, ""),
        })
    return candidates

# ── LLM Judge: ranks candidates by semantic similarity ────────────────────────

def llm_judge(new_question: str, candidates: list[dict]) -> dict | None:
    """
    Ask a cheap model to find the most semantically equivalent question.
    Returns the best candidate dict with an added 'llm_score' key, or None.
    """
    if not candidates:
        return None

    candidates_text = "\n".join(
        f"[{i+1}] {c['question']}" for i, c in enumerate(candidates)
    )

    prompt = f"""You are evaluating whether cached questions can answer a new question.

New question: "{new_question}"

Cached questions:
{candidates_text}

For each cached question, rate its semantic equivalence to the new question on a scale 0.00 to 1.00:
- 1.00 = identical meaning, same answer would work perfectly
- 0.80 = very similar, answer would work with minor differences
- 0.50 = related topic but different specific question
- 0.00 = completely different

Respond ONLY with a JSON array, one score per candidate, in order.
Example for 3 candidates: [0.95, 0.40, 0.10]"""

    start = time.time()
    response = client.chat.completions.create(
        model=MODEL_JUDGE,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
    )
    latency = time.time() - start
    judge_tokens = response.usage.total_tokens

    raw = response.choices[0].message.content.strip()

    # Parse scores
    try:
        import re
        numbers = re.findall(r"[\d.]+", raw)
        scores  = [float(n) for n in numbers[:len(candidates)]]
    except Exception:
        return None

    # Find best candidate
    if not scores:
        return None
    best_idx   = scores.index(max(scores))
    best_score = scores[best_idx]
    best       = candidates[best_idx].copy()
    best["llm_score"]     = best_score
    best["all_scores"]    = scores
    best["judge_tokens"]  = judge_tokens
    best["judge_latency"] = round(latency, 2)
    best["judge_model"]   = MODEL_JUDGE
    return best

# ── Full LLM call (cache miss) ────────────────────────────────────────────────

SYSTEM = "Banking regulatory compliance expert. Accurate, concise answers."

def llm_answer(question: str) -> tuple[str, int, float]:
    start    = time.time()
    response = client.chat.completions.create(
        model=MODEL_ANSWER,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user",   "content": question}],
    )
    return (response.choices[0].message.content,
            response.usage.total_tokens,
            round(time.time() - start, 2))

# ── Test questions ─────────────────────────────────────────────────────────────

QUESTION_GROUPS = [
    {
        "original": "What are the EU AI Act requirements for credit scoring systems?",
        "variants": [
            "What does the EU AI Act say about AI used in credit scoring?",
            "EU AI Act compliance obligations for credit risk models",
            "How does European AI regulation apply to credit scoring algorithms?",
        ],
        "different": "What are the GDPR requirements for storing credit scoring data?",
    },
    {
        "original": "How should banks implement DORA for AI systems?",
        "variants": [
            "What does DORA require from banks regarding their AI tools?",
            "DORA compliance for artificial intelligence in banking",
        ],
        "different": "What is the EU AI Act penalty for non-compliance?",
    },
    {
        "original": "What is the difference between Mistral Small and Mistral Large?",
        "variants": [
            "How does Mistral Small compare to Mistral Large in terms of capability?",
            "Mistral Small vs Large — which one should I use?",
        ],
        "different": "How do I set up a semantic cache with Redis?",
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("BENCHMARK 2 — Hybrid Semantic Cache")
    print(f"Judge model:  {MODEL_JUDGE}  (ranks candidates)")
    print(f"Answer model: {MODEL_ANSWER}  (used on cache miss)")
    print(f"Top-N ANN:    {TOP_N_CANDIDATES}  |  LLM threshold: {SIMILARITY_THRESHOLD}")
    print_config()
    print("=" * 70)

    stats = {
        "total": 0, "hits": 0, "misses": 0,
        "false_positive_prevented": 0,
        "tokens_answer_used": 0,   # tokens from real LLM calls
        "tokens_answer_saved": 0,  # tokens saved by cache hits
        "tokens_judge_used": 0,    # tokens used by judge calls
        "latency_miss": [], "latency_hit": [], "latency_judge": [],
    }
    results = []

    for group_idx, group in enumerate(QUESTION_GROUPS):
        original   = group["original"]
        variants   = group["variants"]
        different  = group["different"]
        all_questions = [
            (original,  "ORIGINAL",   True),
            *[(v,       "VARIANT",    True)  for v in variants],
            (different, "DIFFERENT",  False),   # should NOT hit cache
        ]

        print(f"\n{'─'*70}")
        print(f"Group {group_idx+1}: {original[:60]}...")
        print(f"{'─'*70}")

        for question, q_type, should_hit in all_questions:
            print(f"\n  [{q_type:9}] {question[:60]}...")

            ann_start   = time.time()
            candidates  = cache_ann_search(question)
            ann_latency = time.time() - ann_start

            if not candidates:
                # Nothing in cache yet → full LLM call
                print(f"  → Cache empty. LLM call...")
                answer, tokens, lat = llm_answer(question)
                cache_store(question, answer, tokens)
                stats["misses"]             += 1
                stats["tokens_answer_used"] += tokens
                stats["latency_miss"].append(lat)
                print(f"  → Stored. {tokens} tokens | {lat}s")
                results.append({"q": question, "type": q_type, "outcome": "miss_empty",
                                "tokens_used": tokens, "latency_s": lat})
                stats["total"] += 1
                continue

            # ANN found candidates → send to judge
            judge = llm_judge(question, candidates)
            stats["tokens_judge_used"] += judge["judge_tokens"] if judge else 0
            stats["latency_judge"].append(judge["judge_latency"] if judge else 0)

            best_score = judge["llm_score"] if judge else 0

            print(f"  → ANN found {len(candidates)} candidates | judge score: {best_score:.2f} "
                  f"| judge: {judge['judge_latency'] if judge else 0}s")
            if judge:
                print(f"     Best match: \"{judge['question'][:55]}...\"")
                print(f"     All scores: {judge['all_scores']}")

            if judge and best_score >= SIMILARITY_THRESHOLD:
                # Cache HIT
                cached_tokens = token_store.get(judge["id"], 200)
                stats["hits"]                 += 1
                stats["tokens_answer_saved"]  += cached_tokens
                stats["latency_hit"].append(ann_latency + judge["judge_latency"])

                if not should_hit:
                    stats["false_positive_prevented"] += 1
                    print(f"  ⚠️  UNEXPECTED HIT (different question) — score {best_score:.2f} > {SIMILARITY_THRESHOLD}")
                else:
                    print(f"  ✅ CACHE HIT — score {best_score:.2f} | saved ~{cached_tokens} tokens")

                results.append({"q": question, "type": q_type, "outcome": "hit",
                                "llm_score": best_score, "tokens_saved": cached_tokens,
                                "judge_tokens": judge["judge_tokens"],
                                "should_hit": should_hit})
            else:
                # Cache MISS → full LLM call
                answer, tokens, lat = llm_answer(question)
                cache_store(question, answer, tokens)
                stats["misses"]             += 1
                stats["tokens_answer_used"] += tokens
                stats["latency_miss"].append(lat)

                outcome = "miss_correct" if not should_hit else "miss_wrong"
                icon    = "✅" if not should_hit else "❌"
                print(f"  {icon} CACHE MISS (score {best_score:.2f} < {SIMILARITY_THRESHOLD}) "
                      f"— {'correct, different question' if not should_hit else 'missed a variant'}")
                print(f"  → LLM call. {tokens} tokens | {lat}s")
                results.append({"q": question, "type": q_type, "outcome": outcome,
                                "llm_score": best_score, "tokens_used": tokens,
                                "judge_tokens": judge["judge_tokens"] if judge else 0})

            stats["total"] += 1

    # ── Analysis ──────────────────────────────────────────────────────────────

    hit_rate  = stats["hits"]  / stats["total"] * 100
    total_answer_tokens = stats["tokens_answer_used"] + stats["tokens_answer_saved"]
    saved_pct = stats["tokens_answer_saved"] / total_answer_tokens * 100 if total_answer_tokens else 0

    avg_miss  = sum(stats["latency_miss"])  / len(stats["latency_miss"])  if stats["latency_miss"]  else 0
    avg_hit   = sum(stats["latency_hit"])   / len(stats["latency_hit"])   if stats["latency_hit"]   else 0
    avg_judge = sum(stats["latency_judge"]) / len(stats["latency_judge"]) if stats["latency_judge"] else 0

    # Cost
    cost_answer_used  = token_cost(MODEL_ANSWER, stats["tokens_answer_used"])
    cost_answer_saved = token_cost(MODEL_ANSWER, stats["tokens_answer_saved"])
    cost_judge        = token_cost(MODEL_JUDGE,  stats["tokens_judge_used"])
    net_savings       = cost_answer_saved - cost_judge

    # Monthly projection
    scale          = DAILY_CALLS / stats["total"] * 30
    monthly_saved  = cost_answer_saved * scale
    monthly_judge  = cost_judge        * scale
    monthly_net    = net_savings       * scale

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"\n  Cache performance:")
    print(f"    Total questions:          {stats['total']}")
    print(f"    Cache hits:               {stats['hits']}  ({hit_rate:.1f}%)")
    print(f"    Cache misses:             {stats['misses']}")
    print(f"    False positives blocked:  {stats['false_positive_prevented']}")
    print(f"    Answer tokens saved:      {stats['tokens_answer_saved']}")
    print(f"    Judge tokens used:        {stats['tokens_judge_used']}  (overhead)")

    print(f"\n  Latency breakdown:")
    print(f"    Full LLM call (miss):     {avg_miss:.2f}s")
    print(f"    ANN + judge (hit):        {avg_hit:.2f}s  ({avg_miss/max(avg_hit,0.01):.1f}x faster)")
    print(f"    Judge alone:              {avg_judge:.2f}s  ({MODEL_JUDGE.split('/')[-1]})")

    print(f"\n  Cost analysis (this run):")
    print(f"    Answer cost (used):       ${cost_answer_used:.4f}")
    print(f"    Answer cost (saved):      ${cost_answer_saved:.4f}")
    print(f"    Judge cost (overhead):    ${cost_judge:.4f}")
    print(f"    Net savings:              ${net_savings:.4f}  (saved − judge overhead)")

    print(f"\n  Monthly projection ({DAILY_CALLS:,} calls/day):")
    print(f"    Gross savings:            ${monthly_saved:>10,.2f}/month")
    print(f"    Judge overhead:           ${monthly_judge:>10,.2f}/month")
    print(f"    Net savings:              ${monthly_net:>10,.2f}/month")
    print(f"    Annual net savings:       ${monthly_net*12:>10,.2f}/year")

    # ── Save ──────────────────────────────────────────────────────────────────

    report = {
        "benchmark":        "hybrid_semantic_cache",
        "date":             datetime.now().isoformat(),
        "judge_model":      MODEL_JUDGE,
        "answer_model":     MODEL_ANSWER,
        "threshold":        SIMILARITY_THRESHOLD,
        "top_n_candidates": TOP_N_CANDIDATES,
        "cache_hit_rate":   round(hit_rate, 1),
        "tokens_saved_pct": round(saved_pct, 1),
        "false_positives_blocked": stats["false_positive_prevented"],
        "monthly_net_savings_usd": round(monthly_net, 2),
        "annual_net_savings_usd":  round(monthly_net * 12, 2),
        "latency_miss_s":   round(avg_miss, 2),
        "latency_hit_s":    round(avg_hit, 2),
        "latency_judge_s":  round(avg_judge, 2),
        "raw_results":      results,
    }
    os.makedirs("../reports", exist_ok=True)
    fname = f"../reports/benchmark2_cache_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(fname, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Saved: {fname}")
    print(f"\n💡 Key insight: judge overhead ({MODEL_JUDGE.split('/')[-1]}) costs "
          f"${cost_judge:.4f} but prevents wrong cache hits AND saves "
          f"${cost_answer_saved:.4f} in answer calls — net positive.")

if __name__ == "__main__":
    main()
