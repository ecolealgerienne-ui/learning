# First Docker Run — Step-by-Step Guide

Complete guide to launch the LLM Gateway stack for the first time.  
Estimated time: **20–30 minutes**

---

## Prerequisites

- [ ] Docker Desktop running (or Docker Engine on Linux)
- [ ] `ANTHROPIC_API_KEY` available (from console.anthropic.com)
- [ ] At least 4 GB RAM free for Docker
- [ ] Ports 3000, 4000, 5432, 6379 not in use

Check free ports:
```bash
lsof -i :3000 -i :4000 -i :5432 -i :6379
# Should return nothing (ports free)
```

---

## Step 1 — Configure environment variables

```bash
cd ~/learning/module_1_gateway/docker

# Create .env from template
cp .env.example .env
```

Open `.env` and fill in these values:

```bash
# Required — your Anthropic key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx

# LiteLLM master key (choose any string)
LITELLM_MASTER_KEY=sk-litellm-master-2026

# PostgreSQL — choose your passwords
POSTGRES_USER=litellm
POSTGRES_PASSWORD=litellm_secure_2026
POSTGRES_DB=litellm

# Langfuse database (can use same Postgres or separate)
DATABASE_URL=postgresql://litellm:litellm_secure_2026@postgres:5432/litellm

# Langfuse secret keys (generate random strings)
LANGFUSE_SECRET_KEY=ls-secret-xxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
NEXTAUTH_SECRET=nextauth-secret-xxxxxxxx
NEXTAUTH_URL=http://localhost:3000
```

> **Security:** `.env` is in `.gitignore`. Never commit it.

---

## Step 2 — Start the stack

```bash
cd ~/learning/module_1_gateway/docker

# Start all containers in background
docker-compose up -d
```

Expected output:
```
✅ Container postgres    Started
✅ Container redis       Started
✅ Container litellm     Started
✅ Container langfuse-web    Started
✅ Container langfuse-worker Started
```

---

## Step 3 — Verify all containers are running

```bash
docker-compose ps
```

Expected output (all "Up" or "healthy"):
```
NAME              STATUS          PORTS
postgres          Up (healthy)    5432/tcp
redis             Up              6379/tcp
litellm           Up (healthy)    0.0.0.0:4000->4000/tcp
langfuse-web      Up              0.0.0.0:3000->3000/tcp
langfuse-worker   Up
```

If a container shows "Exit" or "Restarting":
```bash
docker-compose logs [container-name] --tail 50
# Example: docker-compose logs litellm --tail 50
```

---

## Step 4 — Health check LiteLLM

```bash
curl http://localhost:4000/health
```

Expected response:
```json
{"status": "healthy", "litellm_version": "x.x.x"}
```

If port 4000 doesn't respond, try 8000:
```bash
curl http://localhost:8000/health
```

---

## Step 5 — Open Langfuse UI

Open browser: **http://localhost:3000**

First time:
1. Click "Sign Up"
2. Create an admin account (email + password, local only)
3. Create an Organization → Create a Project
4. Go to Settings → API Keys
5. **Copy Public Key and Secret Key** → add to `.env`:
   ```
   LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
   LANGFUSE_SECRET_KEY=ls-sk-xxxxxxxx
   ```
6. Restart LiteLLM to pick up the keys:
   ```bash
   docker-compose restart litellm
   ```

---

## Step 6 — First real API call

```bash
# Via curl
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-litellm-master-2026" \
  -d '{
    "model": "claude-sonnet",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}]
  }'
```

Expected response:
```json
{
  "choices": [{
    "message": {"role": "assistant", "content": "Hello! I'm happy to help you today."}
  }],
  "usage": {"prompt_tokens": 12, "completion_tokens": 14, "total_tokens": 26}
}
```

---

## Step 7 — Run the Python test script

```bash
cd ~/learning

# Install dependencies
pip install openai anthropic python-dotenv

# Run full test suite
python module_1_gateway/code/test_claude_api.py
```

Expected output:
```
✅ Health check: OK
✅ Claude Sonnet call: 26 tokens, $0.000234
✅ Claude Haiku call: 22 tokens, $0.000018
✅ Virtual key test: budget enforced
```

---

## Step 8 — Verify traces in Langfuse

1. Go to http://localhost:3000
2. Click "Traces" in left menu
3. You should see the calls from Step 6 and 7
4. Click on a trace to see: prompt, response, tokens, cost, latency

**This is the "wow" moment** — your AI calls are now fully observable.

---

## Troubleshooting

### LiteLLM won't start
```bash
docker-compose logs litellm --tail 100
# Common causes:
# - ANTHROPIC_API_KEY missing or invalid
# - DATABASE_URL format wrong
# - Port conflict (another app on 4000)
```

### Langfuse login not working
```bash
docker-compose logs langfuse-web --tail 50
# Check: NEXTAUTH_SECRET and NEXTAUTH_URL are set
```

### Postgres connection error
```bash
docker-compose logs postgres --tail 30
# Check: POSTGRES_PASSWORD matches DATABASE_URL
```

### Complete restart (clean slate)
```bash
docker-compose down -v    # WARNING: deletes all data
docker-compose up -d
```

---

## After a successful first run

Update `claude.md` checklist:
```
- [x] docker-compose up → first health check ✅
- [x] First real Claude API call via LiteLLM ✅
- [x] Traces visible in Langfuse UI ✅
```

Then move to **Module 2 FinOps benchmarks:**
```bash
cd ~/learning/module_2_finops/benchmarks
python 01_prompt_optimization.py
```
