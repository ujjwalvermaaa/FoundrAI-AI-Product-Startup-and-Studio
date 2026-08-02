# FoundrAI — Local Run Guide

This is the exact step-by-step guide to start FoundrAI on your machine (macOS, Apple Silicon).
Everything is already set up. Just follow these steps in order.

---

## What you need running

| Service | Status |
|---|---|
| PostgreSQL 17 (EDB) | Auto-starts on boot at port 5432 ✓ |
| Ollama | Must be started manually |
| Backend (FastAPI) | Run in Terminal |
| Frontend (Next.js) | Run in Terminal |

---

## Step 1 — Check your .env files (already done, just verify)

**Backend** — `backend/.env` should contain:
```
DATABASE_URL=postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
JWT_SECRET_KEY=dev-secret-change-in-production
FRONTEND_URL=http://localhost:3000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

**Frontend** — `Frontend/.env.local` should contain:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Both files already exist. No changes needed for local dev.

> **Note**: If you ever get `ModuleNotFoundError: No module named 'ai'`, run:
> ```bash
> cd /Users/ujjwal/Desktop/FoundrAI/backend
> /Users/ujjwal/.local/bin/poetry install
> ```
> This registers the `ai` package from the parent directory into the virtualenv.

---

## Step 2 — Start Ollama

Open Terminal and run:

```bash
brew services start ollama
```

Or if you prefer to see the output:
```bash
ollama serve
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```
You should see a JSON response with your models list.

Check that `qwen3:4b` is available:
```bash
ollama list
```

If `qwen3:4b` is missing, pull it (one-time, ~2.5 GB):
```bash
ollama pull qwen3:4b
```

---

## Step 3 — Start the Backend

Open a **new Terminal tab** and run:

```bash
cd /Users/ujjwal/Desktop/FoundrAI/backend
/Users/ujjwal/.local/bin/poetry run uvicorn app.main:app --reload --port 8000
```

Wait for this line:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify the backend is healthy** (in another tab or use curl):
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

```bash
curl http://localhost:8000/health/ready
```
Expected: `{"status":"ready","checks":{"database":"up","ollama":"up","faiss":"up"}}`

If `ollama` shows `"down"`, go back to Step 2.

---

## Step 4 — Start the Frontend

Open another **new Terminal tab** and run:

```bash
cd /Users/ujjwal/Desktop/FoundrAI/Frontend
bun dev
```

Wait for:
```
▲ Next.js 15.x.x
- Local: http://localhost:3000
```

---

## Step 5 — Open the app

Open your browser and go to:

```
http://localhost:3000
```

You'll see the FoundrAI login page. Register a new account and start building.

---

## One-time setup (only needed on fresh clone)

If you're starting on a fresh machine or the DB is empty, run these once:

```bash
# Install backend dependencies
cd /Users/ujjwal/Desktop/FoundrAI/backend
/Users/ujjwal/.local/bin/poetry install

# Run database migrations (creates all 13 tables)
/Users/ujjwal/.local/bin/poetry run alembic upgrade head

# Seed the knowledge base (FAISS index for RAG)
/Users/ujjwal/.local/bin/poetry run python ../scripts/build_index.py

# Install frontend dependencies
cd /Users/ujjwal/Desktop/FoundrAI/Frontend
bun install
```

---

## Summary — 3 terminals, everything running

```
Terminal 1:  ollama serve
Terminal 2:  cd backend  →  poetry run uvicorn app.main:app --reload --port 8000
Terminal 3:  cd Frontend →  bun dev
Browser:     http://localhost:3000
```

---

## Useful URLs while running

| URL | What it is |
|---|---|
| http://localhost:3000 | Frontend app |
| http://localhost:8000/health | Backend liveness |
| http://localhost:8000/health/ready | Backend readiness (DB + Ollama + FAISS) |
| http://localhost:8000/api/docs | Swagger UI (interactive API docs) |
| http://localhost:8000/api/redoc | ReDoc API docs |

---

## Stop everything

```bash
# Stop backend and frontend: Ctrl+C in their terminals

# Stop Ollama service:
brew services stop ollama

# PostgreSQL stops on shutdown automatically (EDB service)
```

---

## Common issues

**"Could not connect to database"**
PostgreSQL auto-starts on boot via launchd. Check it's running:
```bash
pg_isready -h localhost -p 5432
```

**"ollama: down" in /health/ready**
```bash
brew services start ollama
# wait 5 seconds, then retry
```

**"Model not found: qwen3:4b"**
```bash
ollama pull qwen3:4b
```

**Frontend "bun: command not found"**
```bash
curl -fsSL https://bun.sh/install | bash
# then restart your terminal
```

**Poetry not found**
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add this to your ~/.zshrc to make it permanent
```

**Port 8000 already in use**
```bash
lsof -i :8000
kill -9 <PID>
```

**Port 3000 already in use**
```bash
lsof -i :3000
kill -9 <PID>
```
