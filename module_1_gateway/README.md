# Module 1 — Gateway LLM : LiteLLM + Langfuse + Multi-tenant

**Semaines** : 1–3 | **Volume** : ~24h | **Statut** : 🔄 En cours

---

## Objectifs

1. Comprendre le rôle d'un LLM Gateway dans une architecture enterprise
2. Déployer LiteLLM Proxy en mode conteneurisé avec PostgreSQL et Redis
3. Configurer Langfuse pour l'observabilité et le suivi des coûts
4. Implémenter une isolation multi-tenant via les virtual keys
5. Livrer un starter kit documenté et partageable avec des clients

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (curl / Python / app)          │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS + Bearer Token (virtual key)
                      ▼
┌─────────────────────────────────────────────────────────┐
│              LiteLLM Proxy  :8000                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Auth / RBAC  │  │   Router     │  │  Budget Mgr  │  │
│  └──────────────┘  └──────┬───────┘  └──────────────┘  │
│                            │                             │
│  ┌─────────────────────────┴──────────────────────────┐ │
│  │              Callbacks (Langfuse)                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────┬───────────────────────────┬──────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────┐       ┌──────────────────────────────┐
│  Anthropic API   │       │       Langfuse  :3000         │
│  (Claude Sonnet, │       │  ┌──────────┐  ┌──────────┐  │
│   Claude Haiku)  │       │  │  Traces  │  │ Metrics  │  │
└──────────────────┘       │  └──────────┘  └──────────┘  │
                           └──────────────────────────────┘
           ┌───────────────────────────┐
           │     PostgreSQL  :5432     │ ← LiteLLM DB + Langfuse DB
           └───────────────────────────┘
           ┌───────────────────────────┐
           │       Redis  :6379        │ ← Cache + Rate limiting
           └───────────────────────────┘
```

---

## Composants

### LiteLLM Proxy
- **Rôle** : Point d'entrée unique pour toutes les requêtes LLM
- **Image** : `ghcr.io/berriai/litellm:main-latest`
- **Port** : 8000
- **Fonctionnalités** : routing, virtual keys, budgets, callbacks

### Langfuse
- **Rôle** : Observabilité et traçabilité des appels LLM
- **Image** : `langfuse/langfuse:latest`
- **Port** : 3000
- **Fonctionnalités** : traces, métriques coût, évaluation

### PostgreSQL 15
- **Rôle** : Persistance des données LiteLLM (virtual keys, logs) et Langfuse
- **Image** : `postgres:15-alpine`
- **Port** : 5432

### Redis 7
- **Rôle** : Cache des réponses LLM et rate limiting
- **Image** : `redis:7-alpine`
- **Port** : 6379

---

## Livrable

Le livrable de ce module est un **Starter Kit LLM Gateway Self-Hosted** :

- Stack Docker Compose production-ready
- Configuration LiteLLM multi-modèles et multi-tenant
- Guide d'installation et de configuration
- Documentation architecture
- Scripts de test et validation

Voir : `deliverables/starter-kit/`

---

## Structure du module

```
module_1_gateway/
├── README.md                    # Ce fichier
├── docker/
│   ├── docker-compose.yml       # Stack Docker Compose de dev
│   ├── litellm-config.yaml      # Configuration LiteLLM
│   ├── .env.example             # Variables d'environnement
│   └── README_DOCKER.md         # Guide de démarrage Docker
├── notes/
│   ├── concepts.md              # Notes théoriques
│   ├── setup.md                 # Journal de setup
│   └── questions.md             # Blockers et questions
├── code/
│   └── test_claude_api.py       # Script de test Python
└── deliverables/
    └── starter-kit/
        ├── README.md
        ├── ARCHITECTURE.md
        ├── docker-compose.yml
        ├── litellm-config.yaml
        └── screenshots/
```

---

## Démarrage rapide

```bash
# Se placer dans le dossier docker
cd module_1_gateway/docker

# Copier et compléter le .env
cp .env.example .env
# Renseigner ANTHROPIC_API_KEY et les mots de passe

# Lancer la stack
docker compose up -d

# Vérifier
docker compose ps
curl http://localhost:8000/health
```

Voir `docker/README_DOCKER.md` pour les instructions complètes.
