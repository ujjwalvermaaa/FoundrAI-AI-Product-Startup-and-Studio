# FoundrAI — Local Setup Guide

This guide walks you through setting up FoundrAI for local development from scratch. Follow these steps in order and you'll have the full stack running in under 30 minutes.

---

## Table of Contents

1. [Prerequisites Overview](#1-prerequisites-overview)
2. [Install Ollama](#2-install-ollama)
3. [Pull the LLM Model](#3-pull-the-llm-model)
4. [Set Up PostgreSQL](#4-set-up-postgresql)
5. [Clone the Repository](#5-clone-the-repository)
6. [Set Up the Backend](#6-set-up-the-backend)
7. [Set Up the Frontend](#7-set-up-the-frontend)
8. [Seed the Knowledge Base](#8-seed-the-knowledge-base)
9. [Start All Services](#9-start-all-services)
10. [Verify Everything Works](#10-verify-everything-works)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites Overview

You need the following installed before starting:

| Tool | Version | Install |
|---|---|---|
| Python | 3.11 or 3.12 | [python.org](https://www.python.org/downloads/) or pyenv |
| Poetry | 2.x | See below |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| bun | 1.x | [bun.sh](https://bun.sh) |
| PostgreSQL | 14+ | See Section 4 |
| Ollama | latest | See Section 2 |
| Git | any | [git-scm.com](https://git-scm.com) |

### Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
After install, verify:
```bash
poetry --version
# Poetry (version 2.x.x)
```
If `poetry` is not on your PATH, add `~/.local/bin` to your shell profile (`~/.zshrc` or `~/.bashrc`).

### Install bun
```bash
curl -fsSL https://bun.sh/install | bash
```
Verify:
```bash
bun --version
# 1.x.x
```

---

## 2. Install Ollama

Ollama runs the LLM locally. It must be running as a service while you use FoundrAI.

### macOS
```bash
brew install ollama
```
Or download the macOS app from [ollama.com/download](https://ollama.com/download).

Start Ollama as a background service:
```bash
brew services start ollama
```

To start it manually instead:
```bash
ollama serve
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Start the service:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Windows
Download the installer from [ollama.com/download](https://ollama.com/download). The installer registers Ollama as a Windows service automatically.

### Verify Ollama is running
```bash
curl http://localhost:11434/api/tags
# Should return {"models":[...]}
```

---

## 3. Pull the LLM Model

FoundrAI uses **qwen3:4b** (~2.5 GB download). This only needs to be done once.

```bash
ollama pull qwen3:4b
```

Verify it downloaded:
```bash
ollama list
# NAME         ID              SIZE    MODIFIED
# qwen3:4b     ...             2.5 GB  ...
```

---

## 4. Set Up PostgreSQL

FoundrAI requires PostgreSQL 14+. You have two options.

### Option A — EDB Installer (Recommended for macOS)

Download the installer from [enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).

Select:
- PostgreSQL 17
- Port: **5432**
- Locale: Default

After installation, PostgreSQL starts automatically on boot.

Create the application user and database:
```bash
# Open a superuser psql shell
psql -U postgres

# Inside psql:
CREATE USER foundrai WITH PASSWORD 'foundrai_dev';
CREATE DATABASE foundrai OWNER foundrai;
GRANT ALL PRIVILEGES ON DATABASE foundrai TO foundrai;
\q
```

### Option B — Homebrew (macOS)

```bash
brew install postgresql@17
brew services start postgresql@17
```

Then create the user and database as shown above.

### Option C — Docker (any OS)

If you prefer not to install PostgreSQL locally, use the included Docker Compose config.

> Note: The `docker-compose.yml` maps the container to port **5433** on your host to avoid conflicts with a locally installed PostgreSQL. Adjust `DATABASE_URL` accordingly.

```bash
docker compose up -d postgres
```

Then create the user and database:
```bash
docker compose exec postgres psql -U postgres -c "CREATE USER foundrai WITH PASSWORD 'foundrai_dev';"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE foundrai OWNER foundrai;"
```

---

## 5. Clone the Repository

```bash
git clone https://github.com/your-org/foundrai.git
cd FoundrAI
```

---

## 6. Set Up the Backend

### 6.1 Install Python dependencies

```bash
cd backend
poetry install
```

This creates a virtual environment and installs all dependencies (FastAPI, SQLAlchemy, LangChain, FAISS, sentence-transformers, etc.).

First install may take 2–3 minutes because `sentence-transformers` and `faiss-cpu` are large packages.

### 6.2 Create the backend environment file

Create `backend/.env`:
```bash
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
JWT_SECRET_KEY=dev-secret-change-in-production
FRONTEND_URL=http://localhost:3000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
EOF
```

Or copy and edit manually:
```bash
cp .env.example backend/.env
# Edit backend/.env — change DATABASE_URL to point to localhost, not postgres:5432
```

> **JWT_SECRET_KEY**: In development, any string works. For production, generate a proper secret:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

### 6.3 Run database migrations

```bash
cd backend
poetry run alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001...
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002...
...
INFO  [alembic.runtime.migration] Running upgrade 007 -> 008...
```

This creates all 13 tables across 8 migration revisions.

Verify migrations ran:
```bash
poetry run alembic current
# 008 (head)
```

### 6.4 Verify the backend starts

```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Test the health endpoint in another terminal:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## 7. Set Up the Frontend

### 7.1 Install dependencies

```bash
cd Frontend
bun install
```

### 7.2 Create the frontend environment file

```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > Frontend/.env.local
```

### 7.3 Verify the frontend builds

```bash
cd Frontend
bun run build
# ✓ Compiled successfully
# Route (app) ...
```

---

## 8. Seed the Knowledge Base

FoundrAI's RAG pipeline uses a knowledge base of 5 documents (startup playbook, unit economics, GTM strategies, product roadmap guide, validation templates). These are pre-written in `data/knowledge/` and need to be chunked and indexed into FAISS.

This step requires Ollama to be running (embeddings are computed locally).

```bash
cd backend
poetry run python ../scripts/build_index.py
```

Expected output:
```
Loading embedding model BAAI/bge-base-en-v1.5...
Processing 5 knowledge documents...
Indexed 54 chunks into data/faiss/knowledge/
Knowledge base ready.
```

The script is **idempotent** — it rebuilds from scratch on every run. Re-run any time you add documents to `data/knowledge/`.

> First run downloads the `BAAI/bge-base-en-v1.5` model (~440 MB) to `~/.cache/huggingface/`. Subsequent runs are fast.

---

## 9. Start All Services

Open three terminal windows:

**Terminal 1 — Backend**
```bash
cd /path/to/FoundrAI/backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```bash
cd /path/to/FoundrAI/Frontend
bun dev
```

**Terminal 3 — Ollama** (if not running as a service)
```bash
ollama serve
```

---

## 10. Verify Everything Works

### Backend health
```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/health/ready
# {"status":"ready","checks":{"database":"up","ollama":"up","faiss":"up"}}
```

If `ollama` shows `"down"` in `/health/ready`, make sure `ollama serve` is running and `qwen3:4b` is pulled.

### API documentation

Open your browser:
- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

### Frontend

Open [http://localhost:3000](http://localhost:3000)

You should see the FoundrAI login page. Register a new account and create your first project.

### Run the test suite
```bash
cd backend
poetry run pytest tests/ -v
# 310 passed in X.Xs
```

---

## 11. Troubleshooting

### "Could not connect to database"
- Check PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Verify the `foundrai` user exists: `psql -U postgres -c "\du"`
- Check `DATABASE_URL` in `backend/.env` — it should point to `localhost:5432`, not `postgres:5432` (that hostname is for Docker)

### "Ollama not running" in /health/ready
- macOS: `brew services start ollama` or `ollama serve` in a terminal
- Linux: `sudo systemctl start ollama`
- Check: `curl http://localhost:11434/api/tags`

### "Model not found: qwen3:4b"
```bash
ollama pull qwen3:4b
```

### Poetry not found
Add `~/.local/bin` to your PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```
Add this line to your `~/.zshrc` or `~/.bashrc` to make it permanent.

### Frontend "Cannot find module"
```bash
cd Frontend
bun install   # re-install dependencies
```

### Migrations fail with "role does not exist"
The `foundrai` PostgreSQL user needs to be created before running migrations:
```bash
psql -U postgres -c "CREATE USER foundrai WITH PASSWORD 'foundrai_dev';"
psql -U postgres -c "CREATE DATABASE foundrai OWNER foundrai;"
```

### FAISS "directory not writable"
```bash
mkdir -p data/faiss data/exports data/uploads data/knowledge logs
```

### Port 5432 already in use
If you have both an EDB/Homebrew PostgreSQL and Docker PostgreSQL running, the Docker one uses port 5433 by default (configured in `docker-compose.yml`). For local dev, use the native PostgreSQL on 5432 and set `DATABASE_URL` with `@localhost:5432`.

---

## Production Setup

For production deployment using Docker:

```bash
cp .env.example .env
# Edit .env:
#   - Set JWT_SECRET_KEY to a 64-char random hex string
#   - Set POSTGRES_PASSWORD to a strong password
#   - Update DATABASE_URL to use the new password

chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script:
1. Checks Docker, Docker Compose, and Ollama are installed
2. Creates `.env` from `.env.example` if missing
3. Creates data directories (`data/faiss`, `data/exports`, etc.)
4. Pulls `qwen3:4b` via Ollama
5. Builds Docker images (first build: 5–10 min)
6. Starts all services
7. Waits for PostgreSQL health
8. Seeds the knowledge base FAISS index

After setup, the app is available at `http://localhost` (nginx on port 80).

Stop the stack:
```bash
docker compose -f docker-compose.prod.yml down
```

View logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
```
