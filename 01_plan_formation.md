# Plan de Formation — Architecte IA pour Environnements Réglementés

## Vue d'ensemble

**Option B** : 16 semaines · 100–120h · 2–3 jours/semaine

---

## Module 1 — Gateway LLM : LiteLLM + Langfuse + Multi-tenant

**Semaines** : 1–3  
**Volume** : ~24h

### Objectifs

- Comprendre le rôle et l'architecture d'un LLM Gateway en production
- Déployer LiteLLM Proxy en mode conteneurisé
- Configurer Langfuse pour l'observabilité et le suivi des coûts
- Implémenter le multi-tenant via les virtual keys LiteLLM
- Documenter et packager un starter kit livrable client

### Livrables

- [ ] Stack Docker Compose fonctionnelle (LiteLLM + Langfuse + PostgreSQL + Redis)
- [ ] Configuration multi-tenant avec au moins 3 virtual keys distinctes
- [ ] Dashboard Langfuse avec traces et métriques de coût
- [ ] Script Python de test de l'API
- [ ] Starter kit documenté prêt à partager avec un client

### Ressources

- Cours Udemy : "LiteLLM Proxy — Complete Guide" (modules 1–11)
- Documentation officielle LiteLLM : https://docs.litellm.ai
- Documentation Langfuse : https://langfuse.com/docs
- Anthropic API : https://docs.anthropic.com

---

## Module 2 — FinOps & Optimisation des Coûts LLM

**Semaines** : 4–5  
**Volume** : ~16h

### Objectifs

- Maîtriser les leviers d'optimisation des coûts LLM (caching, prompt compression, model routing)
- Mettre en place des budgets par équipe/projet via LiteLLM
- Analyser et alerter sur les dérives de consommation
- Construire un tableau de bord FinOps LLM

### Livrables

- [ ] Configuration de budgets et alertes dans LiteLLM
- [ ] Mise en place du semantic caching (Redis)
- [ ] Rapport de comparaison coût/performance entre modèles
- [ ] Dashboard FinOps avec métriques clés (coût/token, coût/requête, top consommateurs)
- [ ] Guide FinOps LLM pour architectes

### Ressources

- LiteLLM Budget Manager : https://docs.litellm.ai/docs/proxy/budgets
- LiteLLM Caching : https://docs.litellm.ai/docs/proxy/caching
- Articles FinOps LLM (medium, substack)

---

## Module 3 — Sécurité Opérationnelle

**Semaines** : 6–8  
**Volume** : ~24h

### Objectifs

- Sécuriser les secrets (vault, rotation automatique)
- Mettre en place un audit trail complet (qui a appelé quoi, quand, avec quel résultat)
- Configurer le RBAC granulaire avec intégration Keycloak
- Appliquer les principes DORA à une infrastructure LLM
- Gérer les données sensibles (PII, secrets bancaires) : détection et masquage

### Livrables

- [ ] Intégration HashiCorp Vault (ou Azure Key Vault) pour les secrets
- [ ] Audit trail structuré avec export vers SIEM
- [ ] Intégration Keycloak pour l'authentification des utilisateurs LiteLLM
- [ ] Politique de données sensibles (PII guardrails)
- [ ] Checklist sécurité "LLM en environnement bancaire"

### Ressources

- OWASP LLM Top 10 : https://owasp.org/www-project-top-10-for-large-language-model-applications/
- LiteLLM Guardrails : https://docs.litellm.ai/docs/proxy/guardrails
- DORA (Digital Operational Resilience Act) — texte officiel EUR-Lex
- Documentation HashiCorp Vault

---

## Module 4 — Microsoft Azure AI Foundry + Certification AI-102

**Semaines** : 9–16  
**Volume** : ~48h

### Objectifs

- Maîtriser Azure AI Foundry (déploiement, gestion des modèles, monitoring)
- Comprendre Azure OpenAI Service et ses spécificités (private endpoints, data residency)
- Préparer et passer la certification Microsoft AI-102 (Azure AI Engineer Associate)
- Comparer les approches self-hosted (LiteLLM) vs cloud managé (Azure)
- Architecturer une solution hybride pour le secteur bancaire

### Livrables

- [ ] Déploiement d'un modèle sur Azure AI Foundry
- [ ] Intégration LiteLLM ↔ Azure OpenAI (via proxy)
- [ ] Architecture de référence hybride (on-premise + Azure)
- [ ] Score de préparation certification AI-102 > 80% sur tests blancs
- [ ] Passage de la certification AI-102

### Ressources

- Microsoft Learn — AI-102 Learning Path : https://learn.microsoft.com/fr-fr/certifications/exams/ai-102
- Azure AI Foundry documentation : https://learn.microsoft.com/fr-fr/azure/ai-studio/
- Azure OpenAI Service : https://learn.microsoft.com/fr-fr/azure/ai-services/openai/
- Examtopics AI-102 (tests blancs)

---

## Module 5 — RAG Avancé & Gouvernance Documentaire (Optionnel)

**Semaines** : 17+  
**Volume** : ~20h

### Objectifs

- Implémenter un pipeline RAG production-grade pour la banque
- Gérer la gouvernance des documents (droits d'accès, versioning, audit)
- Optimiser la qualité de la recherche (re-ranking, hybrid search)
- Évaluer la qualité des réponses RAG (RAGAs, LLM-as-judge)

### Livrables

- [ ] Pipeline RAG avec LlamaIndex ou LangChain
- [ ] Intégration avec une base vectorielle (pgvector ou Qdrant)
- [ ] Système de gouvernance documentaire avec RBAC
- [ ] Framework d'évaluation RAG automatisé

---

## Module 6 — Agents & Orchestration (Optionnel)

**Semaines** : 17+  
**Volume** : ~20h

### Objectifs

- Comprendre les patterns d'agents LLM (ReAct, Plan-and-Execute, Multi-agent)
- Implémenter des agents avec LangGraph ou CrewAI
- Gérer la sécurité et les guardrails des agents (actions dangereuses, boucles infinies)
- Cas d'usage bancaire : agent de conformité, agent d'analyse de risque

### Livrables

- [ ] Agent de démonstration avec LangGraph
- [ ] Guardrails et observabilité pour les agents
- [ ] Cas d'usage documenté pour le secteur bancaire

---

## Jalons clés

| Jalon | Semaine | Description |
|-------|---------|-------------|
| M1 | 3 | Starter kit LLM Gateway livrable |
| M2 | 5 | Dashboard FinOps opérationnel |
| M3 | 8 | Checklist sécurité bancaire validée |
| M4 | 16 | Certification AI-102 passée |
