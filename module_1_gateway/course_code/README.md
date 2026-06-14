# Code Source — Cours Udemy

**Cours :** LLM Observability & Cost Management  
**Instructeur :** Paulo Dichone  
**Source :** https://github.com/pdichone/llm-observability-course

---

## Fichiers par thème

### Observabilité Langfuse (cœur du cours)

| Fichier | Niveau | Sujet |
|---------|--------|-------|
| `first_trace_llm.py` | Débutant | Première trace Langfuse |
| `decorator_trace_llm.py` | Intermédiaire | API Niveau 2 — Décorateurs `@observe` |
| `context_manager_trace_llm.py` | Avancé | API Niveau 3 — Context managers |
| `low_level_trace_llm.py` | Expert | API Niveau 4 — SDK bas niveau |
| `langf_obs.py` | Intermédiaire | Observabilité générale |
| `instrumented_llm.py` | Avancé | Wrapper LLM production-ready |

### Optimisation Coûts (FinOps)

| Fichier | Sujet |
|---------|-------|
| `token_calculator-2.py` | Calcul coûts tokens |
| `tokens-demo-1.py` | Démo tokenisation (tiktoken) |
| `prompt_optimazation.py` | Optimisation prompts |
| `semantic_cache.py` | Cache sémantique Redis |
| `model_routing.py` | Routing intelligent Haiku vs Sonnet |
| `alert_webhook.py` | Alertes budget via webhook |

### Sécurité & Conformité

| Fichier | Sujet |
|---------|-------|
| `pii_redaction.py` | Anonymisation PII (RGPD) |

### RAG & Avancé

| Fichier | Sujet |
|---------|-------|
| `rag_pipeline_obs.py` | Pipeline RAG avec observabilité |
| `instrumentation_langchain.py` | Intégration LangChain (à titre informatif) |

### Documentation

| Fichier | Sujet |
|---------|-------|
| `docs/python_cloud_cookbooks.md` | Recettes cloud |
| `docs/python_cloud_general_*.md` | Billing, pricing, rate limits, regions |
| `token_cal.md` | Référence calcul tokens |

---

## Ordre de lecture recommandé (Module 1)

1. `first_trace_llm.py` — comprendre une trace
2. `decorator_trace_llm.py` — pattern production
3. `instrumented_llm.py` — wrapper réutilisable
4. `token_calculator-2.py` — FinOps basique
5. `model_routing.py` — routing intelligent
6. `pii_redaction.py` — conformité RGPD

---

## ⚠️ Adaptations nécessaires

Le cours utilise parfois **LangChain** et **LangSmith** — on les ignore.  
Notre stack : **LiteLLM + Langfuse + Anthropic direct**.  
Les concepts restent identiques, seule l'implémentation change.
