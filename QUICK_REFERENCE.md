# Quick Reference — LLM Gateway Module 1

> Cheatsheet 5 minutes pour retrouver rapidement les commandes essentielles

---

## URLs clés

| Service | URL | Description |
|---------|-----|-------------|
| LiteLLM Proxy | http://localhost:8000 | Point d'entrée des requêtes LLM |
| LiteLLM UI | http://localhost:8000/ui | Interface admin LiteLLM |
| LiteLLM Health | http://localhost:8000/health | Statut du proxy |
| Langfuse UI | http://localhost:3000 | Dashboard observabilité |
| PostgreSQL | localhost:5432 | Base de données |
| Redis | localhost:6379 | Cache et rate limiting |

---

## Docker Compose — commandes essentielles

```bash
# Démarrer toute la stack
docker compose up -d

# Démarrer un service spécifique
docker compose up -d litellm

# Arrêter la stack
docker compose down

# Arrêter et supprimer les volumes (ATTENTION : supprime les données)
docker compose down -v

# Voir le statut des services
docker compose ps

# Voir les logs d'un service
docker compose logs -f litellm
docker compose logs -f langfuse-web

# Redémarrer un service
docker compose restart litellm

# Reconstruire et relancer
docker compose up -d --force-recreate litellm
```

---

## Curl — tests API essentiels

```bash
# Health check LiteLLM
curl http://localhost:8000/health

# Lister les modèles disponibles
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Appel simple à Claude Sonnet
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5",
    "messages": [{"role": "user", "content": "Bonjour, peux-tu te présenter ?"}],
    "max_tokens": 200
  }'

# Appel avec une virtual key
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer $VIRTUAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "claude-haiku-4-5", "messages": [{"role": "user", "content": "Test"}]}'

# Créer une virtual key
curl -X POST http://localhost:8000/key/generate \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "models": ["claude-sonnet-4-5", "claude-haiku-4-5"],
    "metadata": {"team": "dev"},
    "key_alias": "vk-equipe-dev",
    "max_budget": 10.0
  }'

# Lister les virtual keys
curl http://localhost:8000/key/list \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

---

## Git workflow

```bash
# Voir l'état du repo
git status

# Ajouter tous les fichiers modifiés
git add .

# Commit avec message descriptif
git commit -m "Module 1 : description des changements"

# Push vers le remote
git push

# Pull les dernières modifications
git pull

# Voir l'historique
git log --oneline -10
```

---

## Troubleshooting — Top 5 problèmes

### 1. LiteLLM ne démarre pas
```bash
# Vérifier les logs
docker compose logs litellm

# Causes fréquentes :
# - ANTHROPIC_API_KEY manquante dans .env
# - DATABASE_URL incorrecte
# - Port 8000 déjà utilisé
lsof -i :8000
```

### 2. Erreur "Invalid API Key"
```bash
# Vérifier que la master key est bien définie
echo $LITELLM_MASTER_KEY

# Vérifier dans .env
grep LITELLM_MASTER_KEY .env

# La master key doit commencer par "sk-"
```

### 3. Langfuse ne reçoit pas les traces
```bash
# Vérifier la connexion LiteLLM -> Langfuse
docker compose logs litellm | grep langfuse

# Vérifier les variables dans litellm-config.yaml
# success_callback: ["langfuse"]
# LANGFUSE_PUBLIC_KEY et LANGFUSE_SECRET_KEY doivent être définis
```

### 4. PostgreSQL inaccessible
```bash
# Vérifier que postgres tourne
docker compose ps postgres

# Se connecter directement
docker compose exec postgres psql -U litellm -d litellm_db

# Vérifier les logs postgres
docker compose logs postgres
```

### 5. Modèle non trouvé (404)
```bash
# Vérifier la liste des modèles configurés
curl http://localhost:8000/v1/models -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Le nom du modèle dans la requête doit correspondre exactement
# à "model_name" dans litellm-config.yaml
```

---

## Concepts clés

### LiteLLM
Proxy open-source qui unifie les APIs de tous les providers LLM (Anthropic, OpenAI, Azure, Ollama...) derrière une interface compatible OpenAI. Permet le routing, le rate limiting, les budgets et l'observabilité centralisée.

### Langfuse
Plateforme d'observabilité LLM open-source. Enregistre chaque trace (requête + réponse + métadonnées), calcule les coûts, permet le débogage et l'évaluation de la qualité.

### Virtual Keys
Clés API générées par LiteLLM qui permettent d'isoler les usages par équipe, projet ou tenant. Chaque virtual key peut avoir des budgets, des limites de modèles et des métadonnées distinctes.

### Multi-tenant
Architecture où plusieurs équipes ou clients utilisent la même infrastructure LiteLLM avec une isolation complète : budgets séparés, logs séparés, modèles autorisés différents, traçabilité par tenant dans Langfuse.
