# 📌 claude.md — Contexte Persistant Formation IA

Ce fichier doit être lu **EN PREMIER** à chaque nouvelle session Claude Code.  
Mise à jour après chaque session pour garder un fil continu.

---

## 🎯 PROJET EN COURS

**Projet :** Formation Architecte IA pour Environnements Réglementés  
**Durée totale :** 2-3 mois (16 semaines, Option B)  
**Fin estimée :** Fin août 2026

**Objectif final :** Consultant freelance IA en environnements réglementés (banque, assurance)

---

## 📍 STATUT ACTUEL

**Date dernière mise à jour :** [À remplir après chaque session]  
**Module en cours :** Module 1 — Gateway LLM  
**Semaine :** [À mettre à jour : 1, 2, 3, etc.]  
**Phase :** [FORMATION / HANDS-ON / LIVRABLE]

**Progression globale :**

```
Module 1 (Gateway LLM)         ██░░░░░░░░  [10%]
Module 2 (FinOps)              ░░░░░░░░░░  [0%]
Module 3 (Sécurité)            ░░░░░░░░░░  [0%]
Module 4 (Azure)               ░░░░░░░░░░  [0%]
Module 5-6 (RAG + Gouvernance) ░░░░░░░░░░  [0%]
```

---

## 📋 ÉTAT ACTUEL DU MODULE 1

### Udemy

- [ ] Module 1 (Introduction) — LANCÉ
- [ ] Module 2 (LLM Basics) — EN COURS
- [ ] Module 3 (Langfuse Overview) — À faire
- [ ] Module 4 (Langfuse Setup) — À faire
- [ ] Module 5 (Integrations) — À faire
- [ ] Module 6 (Basic Monitoring) — À faire
- [ ] Modules 7-11 (Cost tracking, Optimization, etc.) — À faire

**Concepts notés :** [À remplir dans `module_1_gateway/notes/concepts.md`]

### Docker & Infrastructure

- [x] Dossier structure créée : `module_1_gateway/`
- [x] Docker Compose créé : `module_1_gateway/docker/docker-compose.yml`
- [x] LiteLLM config créée : `module_1_gateway/docker/litellm-config.yaml`
- [ ] Premier test "health check" — À faire
- [ ] Claude API connectée — À faire
- [ ] Virtual keys setup (multi-tenant) — À faire

**Containers running :** [Nombre : 0/4]

- [ ] PostgreSQL 15 — ❌
- [ ] Redis 7 — ❌
- [ ] LiteLLM — ❌
- [ ] Langfuse web — ❌

### Livrable (Starter Kit)

- [x] `docker-compose.yml` créé (dans `deliverables/starter-kit/`)
- [x] `litellm-config.yaml` créé (dans `deliverables/starter-kit/`)
- [x] `README.md` écrit
- [x] `ARCHITECTURE.md` écrit
- [ ] Screenshots UI prises
- [ ] Testé end-to-end
- [ ] Prêt pour GitHub public

**Status :** EN COURS

---

## 🔄 DERNIÈRE SESSION

**Date :** 2026-06-14  
**Durée :** [À remplir]  
**Ce qu'on a fait :**

- [x] Création de la structure complète du repo
- [x] Génération de tous les fichiers de base (docker-compose, configs, notes, code)
- [x] Git commit initial + push sur `claude/pensive-mccarthy-4ukxr8`
- [x] Création de `claude.md`

**Résultats :**

- ✅ Repo initialisé avec 8 fichiers, structure complète
- ✅ `docker-compose.yml` et `litellm-config.yaml` prêts à tester
- ✅ `test_claude_api.py` prêt

**Prochaine étape :** Lancer `docker-compose up -d` et tester le health check LiteLLM

---

## 🚨 BLOCAGES ACTUELS

### Actifs (à résoudre)

_Aucun pour le moment_

### Résolus (archivés)

_Aucun pour le moment_

---

## 📝 NOTES IMPORTANTES

### Profil Amar (RAPPEL)

- Architecte technique en banque (France)
- Stack : Docker, NestJS, PostgreSQL, Redis, Keycloak (production)
- Python confortable, expérience Odoo multi-tenant
- 2-3 jours/semaine disponible
- RTX 4070 SUPER (pour Ollama)

### Positionnement Cible

> **"Architecte IA pour environnements réglementés"**

❌ PAS consultant généraliste IA  
❌ PAS développeur d'agents  
✅ Focus : industrialisation, gouvernance, sécurité, FinOps IA

### Règles À Respecter

- ✅ Code = français (commentaires, README)
- ✅ Tout = générique (PAS de données réelles banque)
- ✅ Code deployable (pas théorique)
- ✅ Git commits réguliers
- ❌ Éviter : LangGraph, CrewAI, AutoGen, fine-tuning
- ❌ Pas de données bancaires réelles dans les exemples

---

## 📅 ROADMAP RESTANTE

### Semaines 1-3 (MODULE 1)

```
Semaine 1 :
  - Udemy Modules 1-3
  - Docker Compose up + tests premiers endpoints
  - Claude API connectée

Semaine 2 :
  - Udemy Modules 4-8
  - Ollama + fallback automatique
  - Observabilité partielle Langfuse

Semaine 3 :
  - Udemy Modules 9-11
  - Langfuse complet
  - Livrable starter kit finalisé
```

### Semaines 4-5 (MODULE 2 — FinOps)

```
Benchmarks :
  - Prompt caching (tokens/coûts)
  - Model routing (Haiku vs Sonnet)
  - Historique conversation (effet exponentiel)
```

### Semaines 6-8 (MODULE 3 — Sécurité)

```
Keycloak + LiteLLM SSO
Vault + secrets management
DLP basique
Audit logs (ELK)
```

### Semaines 9-16 (MODULE 4 — Azure)

```
Udemy : "Microsoft Foundry & Python" (25-30h)
Udemy : "AB-100 Agentic AI Architect" (25-30h)
Deploy agents sur Azure
Certification AB-100
```

---

## 📂 FICHIERS CLÉS

```
~/learning/
├── claude.md                    ← CE FICHIER (Contexte persistant)
├── CONTEXTE.md                  ← Prompt pour Claude Code
├── 01_plan_formation.md         ← Plan complet 16 semaines
├── 03_progression.md            ← Journal détaillé (mise à jour chaque semaine)
├── SEMAINE_1_plan_action.md     ← Jour par jour Module 1
└── module_1_gateway/
    ├── docker/
    │   ├── docker-compose.yml   ✅ Créé
    │   ├── litellm-config.yaml  ✅ Créé
    │   └── README_DOCKER.md     ✅ Créé
    ├── notes/
    │   ├── concepts.md          ← À remplir (concepts Udemy)
    │   ├── setup.md             ← À remplir (log du setup)
    │   └── questions.md         ← À remplir (blocages)
    ├── code/
    │   └── test_claude_api.py   ✅ Créé
    ├── deliverables/
    │   └── starter-kit/         ✅ Créé (livrable final)
    └── README.md                ✅ Créé
```

---

## 🔗 RESSOURCES ESSENTIELLES

### Udemy (Formation principale)

- "LLM Observability & Cost Management" (Paulo Dichone)
- https://www.udemy.com/course/llm-observability-cost/

### Docs Officielles

- LiteLLM : https://docs.litellm.ai/docs/proxy/quick_start
- Langfuse : https://langfuse.com/docs
- Anthropic : https://docs.anthropic.com/

### Local URLs (quand containers running)

- LiteLLM : http://localhost:8000
- Langfuse : http://localhost:3000
- Health check : http://localhost:8000/health

---

## ⚡ COMMANDES PRINCIPALES

```bash
# Navigation
cd ~/learning/module_1_gateway/docker

# Docker
docker-compose up -d
docker-compose logs litellm -f
docker-compose ps
docker-compose down

# Tests
curl http://localhost:8000/health

curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-sonnet", "messages": [{"role": "user", "content": "test"}]}'

# Git
cd ~/learning
git add .
git commit -m "Module 1: [description]"
git push origin claude/pensive-mccarthy-4ukxr8
git log --oneline -10
```

---

## 📊 TEMPLATE MISE À JOUR (À COPIER APRÈS CHAQUE SESSION)

```markdown
## 🔄 Dernière Session

**Date** : [AAAA-MM-DD]
**Durée** : [Xh Ym]

### Ce qu'on a fait
- [ ] [Action 1] ✅
- [ ] [Action 2] ✅
- [ ] [Action 3] ❌

### Résultats
✅ [Succès 1 - description]
✅ [Succès 2 - description]
❌ [Blocage 1 - description]

### Bloqué sur
1. [Blocage 1] - Status : EN COURS
2. [Blocage 2] - Status : EN COURS

### Prochaine étape
- [ ] [Action A - description précise]
- [ ] [Action B - description précise]

### Git commits
git log --oneline -3

### Notes importantes
- [Note 1]
- [Note 2]
```

---

## 🎯 RAPPELS IMPORTANTS

### À CHAQUE NOUVELLE SESSION :

1. ✅ Lis ce fichier `claude.md` EN PREMIER
2. ✅ Vérifie les blocages actuels
3. ✅ Repère où on s'était arrêté
4. ✅ Lance les commandes nécessaires
5. ✅ Dis-moi "Contexte compris, on continue [description]"

### À LA FIN DE CHAQUE SESSION :

1. ✅ Git commit
2. ✅ Mets à jour ce fichier `claude.md`
3. ✅ Mets à jour `03_progression.md`
4. ✅ Note les blocages dans `notes/questions.md`

---

## 📞 COMMENT JE REPRENDS LE CONTEXTE

**Tu dis :**
```
"Salut, je reprends Module 1, j'ai relu claude.md,
on s'était arrêtés sur [blocage], maintenant on fait [action]"
```

**Je fais :**
```
✅ Lis claude.md
✅ Lis les derniers commits git
✅ Vois ton état Docker
✅ On continue de là
```

---

_MISE À JOUR : Après chaque session, remplis les sections ci-dessus._  
_FORMAT : Clair, concis, actionnable._  
_OBJECTIF : Zero context loss, continuité totale._
