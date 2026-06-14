# Plan d'Action — Semaine 1

**Objectif** : Comprendre LiteLLM + Langfuse et lancer la stack Docker Compose  
**Dates** : 9–13 juin 2026  
**Volume cible** : 6–8 heures

---

## Lundi – Mardi : Fondations théoriques + structure

### Théorie
- [ ] Udemy module 1 : Introduction à LiteLLM — pourquoi un LLM proxy ?
- [ ] Udemy module 2 : Architecture générale (proxy, router, SDK)
- [ ] Udemy module 3 : Premiers concepts — modèles, providers, routing

### Pratique
- [ ] Lire la documentation LiteLLM : https://docs.litellm.ai/docs/proxy/quick_start
- [ ] Créer la structure de dossiers du repo :
  ```
  module_1_gateway/
  ├── docker/
  ├── notes/
  ├── code/
  └── deliverables/starter-kit/
  ```
- [ ] Rédiger un `docker-compose.yml` de base avec PostgreSQL + Redis
- [ ] Vérifier que les services de base démarrent : `docker compose up -d postgres redis`

### Notes à prendre
- [ ] Qu'est-ce qu'un LLM Gateway ? (dans `notes/concepts.md`)
- [ ] Différence LiteLLM proxy vs SDK

---

## Mercredi : LiteLLM configuration

### Théorie
- [ ] Udemy module 4 : Configuration du proxy LiteLLM
- [ ] Udemy module 5 : Gestion des modèles et providers
- [ ] Udemy module 6 : Variables d'environnement et sécurité de base

### Pratique
- [ ] Créer `docker/litellm-config.yaml` avec claude-sonnet et claude-haiku
- [ ] Ajouter le service LiteLLM au `docker-compose.yml`
- [ ] Créer le fichier `.env` (à partir de `.env.example`)
- [ ] Renseigner `ANTHROPIC_API_KEY` dans `.env`
- [ ] Lancer LiteLLM : `docker compose up -d litellm`
- [ ] Tester le health check : `curl http://localhost:8000/health`

### Notes à prendre
- [ ] Structure du fichier `litellm-config.yaml` (dans `notes/concepts.md`)
- [ ] Variables d'environnement requises

---

## Jeudi : Premier appel API + virtual keys

### Théorie
- [ ] Udemy module 7 : Virtual keys — concept et configuration
- [ ] Udemy module 8 : Multi-tenant avec LiteLLM

### Pratique
- [ ] Tester un appel curl direct à Claude via le proxy :
  ```bash
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model": "claude-sonnet-4-5", "messages": [{"role": "user", "content": "Bonjour !"}]}'
  ```
- [ ] Créer 2 virtual keys via l'API LiteLLM :
  - `vk-equipe-dev` pour l'équipe développement
  - `vk-equipe-data` pour l'équipe data science
- [ ] Tester un appel avec chaque virtual key
- [ ] Exécuter le script `code/test_claude_api.py`

### Notes à prendre
- [ ] Comment fonctionnent les virtual keys (dans `notes/concepts.md`)
- [ ] Différence master key vs virtual key

---

## Vendredi : Langfuse + finalisation + git

### Théorie
- [ ] Udemy module 9 : Langfuse — introduction et architecture
- [ ] Udemy module 10 : Intégration LiteLLM ↔ Langfuse
- [ ] Udemy module 11 : Dashboard et métriques Langfuse

### Pratique
- [ ] Ajouter les services Langfuse au `docker-compose.yml` :
  - `langfuse-web` (port 3000)
  - `langfuse-worker`
- [ ] Configurer les callbacks Langfuse dans `litellm-config.yaml`
- [ ] Relancer la stack complète : `docker compose up -d`
- [ ] Ouvrir Langfuse UI : http://localhost:3000
- [ ] Créer un compte admin dans Langfuse
- [ ] Générer une trace en faisant un appel API
- [ ] Vérifier que la trace apparaît dans Langfuse
- [ ] Rédiger le README du module 1
- [ ] Git commit et push :
  ```bash
  git add .
  git commit -m "Module 1 semaine 1 : stack LiteLLM + Langfuse fonctionnelle"
  git push
  ```

### Notes à prendre
- [ ] Architecture Langfuse (dans `notes/concepts.md`)
- [ ] Variables d'environnement Langfuse

---

## Récapitulatif des livrables semaine 1

| Livrable | Statut |
|----------|--------|
| Structure du repo | ⏳ |
| `docker-compose.yml` fonctionnel | ⏳ |
| `litellm-config.yaml` | ⏳ |
| Appel API Claude réussi via proxy | ⏳ |
| 2 virtual keys créées et testées | ⏳ |
| Langfuse UI avec traces visibles | ⏳ |
| `notes/concepts.md` rempli | ⏳ |
| README module 1 | ⏳ |
| Commit/push git | ⏳ |

---

## Ressources rapides

- LiteLLM proxy quickstart : https://docs.litellm.ai/docs/proxy/quick_start
- LiteLLM virtual keys : https://docs.litellm.ai/docs/proxy/virtual_keys
- Langfuse self-host : https://langfuse.com/docs/deployment/self-host
- Anthropic API Claude models : https://docs.anthropic.com/en/docs/models-overview
- Image Docker LiteLLM : `ghcr.io/berriai/litellm:main-latest`
- Image Docker Langfuse : `langfuse/langfuse:latest`
