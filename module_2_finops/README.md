# Module 2 — AI FinOps Benchmarks

**Goal:** Measure real savings from each LLM cost optimization lever.  
**Stack required:** Module 1 running (LiteLLM + Langfuse on localhost)

---

## The 4 Levers

| Lever | Script | Typical saving |
|---|---|---|
| Prompt optimization | `01_prompt_optimization.py` | −30 to −85% |
| Semantic caching | `02_semantic_cache.py` | −40 to −60% |
| Model routing | `03_model_routing.py` | −50 to −70% |
| Conversation history | `04_conversation_history.py` | variable |
| **Combined report** | `05_combined_report.py` | **−70 to −85%** |

---

## Setup

```bash
pip install anthropic langfuse openai python-dotenv sentence-transformers
```

Create `benchmarks/.env` (or reuse module_1 .env):
```
ANTHROPIC_API_KEY=sk-ant-...
LANGFUSE_SECRET_KEY=ls-sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=http://localhost:3000
LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=sk-litellm-master-2026
```

---

## Run all benchmarks

```bash
cd ~/learning/module_2_finops/benchmarks
python 01_prompt_optimization.py    # ~2 min
python 02_semantic_cache.py         # ~3 min
python 03_model_routing.py          # ~3 min
python 04_conversation_history.py   # ~2 min
python 05_combined_report.py        # generates report
```

Results saved in `../reports/`

---

## Output

Each script produces:
- Console output with real numbers
- A JSON file in `reports/` with raw data
- Langfuse traces visible at http://localhost:3000

Final report: `reports/finops_report_[date].md`  
→ Use this as the basis for client pitches and LinkedIn posts.
