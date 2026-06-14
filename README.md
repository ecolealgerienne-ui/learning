# Formation Architecte IA — Environnements Réglementés

## Objectif

Acquérir les compétences d'un **Architecte IA pour environnements réglementés** (banque, assurance, secteur public) en maîtrisant le déploiement, la sécurisation et la gouvernance de solutions LLM en production.

## Profil

Architecte technique bancaire avec 5+ ans d'expérience sur Docker, NestJS, PostgreSQL, Redis, Keycloak et Python. Objectif : monter en compétence sur l'IA appliquée aux contraintes réglementaires (DORA, RGPD, Bâle III).

## Plan de formation (Option B — 16 semaines)

| Module | Semaines | Thème | Statut |
|--------|----------|-------|--------|
| 1 | 1–3 | Gateway LLM : LiteLLM + Langfuse + multi-tenant | 🔄 En cours |
| 2 | 4–5 | FinOps & Optimisation des coûts LLM | ⏳ À venir |
| 3 | 6–8 | Sécurité opérationnelle (secrets, audit, RBAC) | ⏳ À venir |
| 4 | 9–16 | Microsoft Azure AI Foundry + Certification AI-102 | ⏳ À venir |
| 5 | 17+ | RAG avancé & Gouvernance (optionnel) | ⏳ Optionnel |
| 6 | 17+ | Agents & Orchestration (optionnel) | ⏳ Optionnel |

**Rythme** : 2–3 jours/semaine · 6–8h/session · 100–120h au total

## Stack technique

- **Proxy/Gateway** : LiteLLM
- **Observabilité** : Langfuse
- **LLMs** : Claude (Anthropic), modèles locaux via Ollama (RTX 4070 SUPER)
- **Infrastructure** : Docker Compose → Docker Swarm / Kubernetes
- **Auth** : Keycloak (OIDC/OAuth2)
- **Cloud** : Microsoft Azure (Azure AI Foundry, Azure OpenAI)
- **Base de données** : PostgreSQL 15, Redis 7

## Structure du repo

```
learning/
├── .gitignore
├── README.md
├── CONTEXTE.md              # Profil et contexte détaillé
├── 01_plan_formation.md     # Plan complet avec objectifs et livrables
├── 03_progression.md        # Journal de progression hebdomadaire
├── SEMAINE_1_plan_action.md # Plan d'action jour par jour — semaine 1
├── QUICK_REFERENCE.md       # Cheatsheet 5 minutes
└── module_1_gateway/
    ├── README.md
    ├── docker/              # Docker Compose de dev
    │   ├── docker-compose.yml
    │   ├── litellm-config.yaml
    │   └── README_DOCKER.md
    ├── notes/               # concepts.md, setup.md, questions.md
    ├── code/                # Scripts Python de test
    └── deliverables/        # Starter kit livrable client
        └── starter-kit/
```

## Comment démarrer

```bash
# 1. Cloner le repo
git clone <url> && cd learning

# 2. Aller dans le module 1
cd module_1_gateway/docker

# 3. Copier le fichier d'environnement et renseigner les clés
cp .env.example .env
# Éditer .env avec votre ANTHROPIC_API_KEY et les mots de passe

# 4. Lancer la stack
docker compose up -d

# 5. Vérifier que tout tourne
docker compose ps

# 6. Tester l'API
curl http://localhost:8000/health
```

Consulter `SEMAINE_1_plan_action.md` pour le détail des activités de la semaine en cours.
