# 📌 claude.md — Persistent Training Context

Read this file FIRST at the start of every Claude Code session.  
Update after each session to maintain continuity.

---

## 🎯 CURRENT PROJECT

**Project:** AI Architect Training for Regulated Environments  
**Total duration:** 2–3 months (16 weeks, Option B)  
**Estimated completion:** End of August 2026

**Final goal:** Freelance AI consultant for regulated environments (banking, insurance)

---

## 📍 CURRENT STATUS

**Last updated:** 2026-06-16  
**Current module:** Module 1 complete (theory) → hands-on pending  
**Week:** 3  
**Phase:** HANDS-ON

**Overall progress:**

```
Module 1 (LLM Gateway)         ████░░░░░░  [40%] — Theory done, stack not started yet
Module 2 (FinOps)              ██░░░░░░░░  [20%] — Scripts ready, tests pending
Module 3 (Security)            ░░░░░░░░░░  [0%]
Module 4 (Azure)               ░░░░░░░░░░  [0%]
Module 5-6 (RAG + Governance)  ░░░░░░░░░░  [0%]
```

---

## ✅ ACCOMPLISHED — FULL SESSION HISTORY

### Repository & Infrastructure
- [x] Complete repo structure created at `~/learning/`
- [x] `module_1_gateway/docker/docker-compose.yml` — full stack (Postgres, Redis, LiteLLM, Langfuse)
- [x] `module_1_gateway/docker/litellm-config.yaml` — models, Langfuse callbacks, budget config
- [x] `module_1_gateway/docker/.env.example` — template with all required variables
- [x] `module_1_gateway/code/test_claude_api.py` — API test script ready to run
- [x] `module_1_gateway/deliverables/starter-kit/` — production-ready client deliverable

### Course Code (Udemy — Paulo Dichone)
- [x] `module_1_gateway/course_code/instrumented_llm.py` — @observe() decorator, Langfuse SDK v3
- [x] `module_1_gateway/course_code/model_routing.py` — TaskType enum, regex classifier
- [x] `module_1_gateway/course_code/semantic_cache.py` — ChromaDB + SentenceTransformer, TTL 24h
- [x] 15 Python files from Udemy course integrated into repo
- [x] **Course "LLM Observability & Cost Management" (Paulo Dichone) — COMPLETED ✅**

### Commercial Materials (all in English)
- [x] `ARGUMENTS_CLIENT.md` — 23 arguments from course slides with banking translations
- [x] `OFFRE_SPRINT_IA_30JOURS.md` — standalone 30-day sprint proposal
- [x] `PITCH_VOCABULARY.md` — 30 technical + commercial terms, 30-second pitch
- [x] `MARCHE_ET_OPPORTUNITES.md` — market research: Gartner, EU AI Act, BaFin, rates
- [x] `LINKEDIN_POSTS.md` — 10 posts in English, 10-week calendar, LinkedIn profile

### LinkedIn Visuals (10 original SVGs, 1200×627px, dark theme, English)
- [x] `post1_boite_noire.svg` — Classic Monitoring vs LLM Observability
- [x] `post2_token_spike.svg` — Token spike chart + guardrails config
- [x] `post3_roi.svg` — €35K→€15K before/after + 7–30x ROI badge
- [x] `post4_prompt_optimization.svg` — 847→127 tokens, −85%
- [x] `post5_top5_cost_drivers.svg` — 5 leaks with color-coded impact %
- [x] `post6_rag_pipeline.svg` — RAG pipeline cost by step
- [x] `post7_gartner.svg` — Market $1.97B→$9.26B + Gartner quote + EU AI Act
- [x] `post8_model_routing.svg` — Decision tree Haiku/Sonnet/Opus + cost comparison
- [x] `post9_audit_2jours.svg` — Day 1 diagnostic + Day 2 quick wins checklist
- [x] `post10_langfuse_vs_others.svg` — Langfuse vs LangSmith vs Helicone vs DataDog

### Module 2 (FinOps)
- [x] `module_2_finops/` folder structure created
- [x] `module_2_finops/benchmarks/01_prompt_optimization.py` — ready to run
- [x] `module_2_finops/benchmarks/02_semantic_cache.py` — ready to run
- [x] `module_2_finops/benchmarks/03_model_routing.py` — ready to run
- [x] `module_2_finops/benchmarks/04_conversation_history.py` — ready to run
- [x] `module_2_finops/benchmarks/05_combined_report.py` — ready to run
- [x] `GUIDE_DOCKER_FIRST_RUN.md` — step-by-step first launch guide

---

## 🔴 NEXT IMMEDIATE STEP

**To do at home (requires ANTHROPIC_API_KEY):**

```bash
cd ~/learning/module_1_gateway/docker
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY, LITELLM_MASTER_KEY, DB passwords
docker-compose up -d
curl http://localhost:4000/health
# Open http://localhost:3000 → Langfuse UI
```

Full step-by-step guide: `GUIDE_DOCKER_FIRST_RUN.md`

Then run FinOps benchmarks:
```bash
cd ~/learning/module_2_finops/benchmarks
python 01_prompt_optimization.py
```

---

## 🚨 CURRENT BLOCKERS

**Active:**
- [ ] ANTHROPIC_API_KEY not configured in `.env` → Docker stack never launched
- [ ] Zero containers running → all hands-on tests pending

**Resolved:**
- ✅ Git divergence (26 images uploaded directly to GitHub) → fixed with rebase
- ✅ Copyright concern on course slides → created 10 original SVG visuals
- ✅ Language → everything converted to English (posts + visuals)

---

## 📝 PROFILE REMINDER

**Amar — Banking Technical Architect (France)**
- Stack: Docker, NestJS, PostgreSQL, Redis, Keycloak (production experience)
- Python: comfortable, Odoo multi-tenant background
- Available: 2–3 days/week
- Hardware: RTX 4070 SUPER (for local Ollama)

**Target positioning:**
> **"AI Architect for Regulated Environments"**

❌ NOT a generalist AI consultant  
❌ NOT an agent developer  
✅ Focus: industrialization, governance, security, AI FinOps

**Rules:**
- ✅ Code must be deployable (not theoretical)
- ✅ Everything generic (no real bank data in examples)
- ✅ Git commits after every session
- ❌ Avoid: LangGraph, CrewAI, AutoGen, fine-tuning
- ❌ No real banking data in examples

---

## 📅 REMAINING ROADMAP

### Module 1 — IN PROGRESS
```
✅ Udemy course "LLM Observability & Cost Management" — DONE
✅ Docker Compose + LiteLLM config — files ready
✅ Starter-kit deliverable — files ready
⬜ docker-compose up → first health check     ← NEXT
⬜ First real Claude API call via LiteLLM
⬜ Traces visible in Langfuse UI
⬜ Virtual keys (multi-tenant) configured
⬜ End-to-end test + screenshots
```

### Module 2 — FinOps (scripts ready, tests pending)
```
✅ Benchmark scripts created in module_2_finops/benchmarks/
⬜ Run 01_prompt_optimization.py  → measure real savings
⬜ Run 02_semantic_cache.py       → measure cache hit rate
⬜ Run 03_model_routing.py        → measure routing savings
⬜ Run 04_conversation_history.py → measure context growth
⬜ Run 05_combined_report.py      → full FinOps report
⬜ Produce report with real numbers for client pitches
```

### Module 3 — Security (not started)
```
⬜ Keycloak + LiteLLM SSO
⬜ Secrets management (Vault or Docker secrets)
⬜ Basic DLP (prompt scanning)
⬜ Audit logs (structured + ELK optional)
```

### Module 4 — Azure (not started)
```
⬜ Course: "Microsoft Azure AI Foundry" (Udemy)
⬜ Course: "AB-100 Agentic AI Architect" (Udemy)
⬜ Deploy on Azure
⬜ AB-100 certification
```

---

## 📂 KEY FILES

```
~/learning/
├── claude.md                              ← THIS FILE
├── GUIDE_DOCKER_FIRST_RUN.md              ← Step-by-step first launch ✅
├── ARGUMENTS_CLIENT.md                    ← 23 client arguments ✅
├── OFFRE_SPRINT_IA_30JOURS.md             ← Commercial proposal ✅
├── MARCHE_ET_OPPORTUNITES.md              ← Market research ✅
├── LINKEDIN_POSTS.md                      ← 10 posts (English) ✅
├── assets/linkedin_visuals/               ← 10 SVG visuals (English) ✅
├── module_1_gateway/
│   ├── docker/docker-compose.yml          ✅ Ready to run
│   ├── docker/litellm-config.yaml         ✅ Ready to run
│   ├── docker/.env.example                ✅ → copy to .env and fill
│   ├── code/test_claude_api.py            ✅ Ready to run
│   ├── course_code/                       ✅ 15 files from Udemy
│   └── deliverables/starter-kit/         ✅ Client deliverable ready
└── module_2_finops/
    ├── README.md                          ✅
    ├── benchmarks/01_prompt_optimization.py   ✅ Ready to run
    ├── benchmarks/02_semantic_cache.py        ✅ Ready to run
    ├── benchmarks/03_model_routing.py         ✅ Ready to run
    ├── benchmarks/04_conversation_history.py  ✅ Ready to run
    ├── benchmarks/05_combined_report.py       ✅ Ready to run
    └── reports/                           ⬜ Generated after running tests
```

---

## ⚡ MAIN COMMANDS

```bash
# --- MODULE 1: Docker stack ---
cd ~/learning/module_1_gateway/docker
cp .env.example .env          # first time only
docker-compose up -d
docker-compose ps
docker-compose logs litellm -f
docker-compose logs langfuse-web -f
docker-compose down

# Health checks
curl http://localhost:4000/health
open http://localhost:3000      # Langfuse UI

# First API test
python ~/learning/module_1_gateway/code/test_claude_api.py

# --- MODULE 2: FinOps benchmarks ---
cd ~/learning/module_2_finops/benchmarks
pip install openai anthropic langfuse python-dotenv
python 01_prompt_optimization.py
python 02_semantic_cache.py
python 03_model_routing.py
python 04_conversation_history.py
python 05_combined_report.py

# --- Git ---
cd ~/learning
git add -A
git commit -m "Module X: [description]"
git push origin claude/pensive-mccarthy-4ukxr8
git log --oneline -5
```

---

## 🔗 LOCAL URLs (when containers running)

- LiteLLM API:  http://localhost:4000
- LiteLLM UI:   http://localhost:4000/ui
- Langfuse UI:  http://localhost:3000
- Health check: http://localhost:4000/health

---

## 📊 SESSION UPDATE TEMPLATE

```
## Last Session — [DATE]
### Done
- [x] ...
### Results
✅ ...  ❌ ...
### Next step
- [ ] ...
```

---

_Update this file at the end of every session._  
_Goal: zero context loss, full continuity._
