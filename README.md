# FoundrAI — From Idea to Startup, Powered by AI

> Transform your startup idea into a complete, investor-ready business plan using a multi-agent AI system with persistent project memory, real-time workflow orchestration, and a polished web interface.

---

## What is FoundrAI?

FoundrAI is an AI-powered SaaS platform that takes a founder's raw startup idea and systematically converts it into a full suite of business documents — validated idea report, market analysis, business model canvas, product roadmap, technical architecture, financial model, marketing plan, and an investor deck outline.

It is **not a chatbot**. It is a structured project workspace where 8 specialized AI agents work sequentially, each consuming the previous agent's output as context. Every artifact is schema-validated, versioned, persisted to a database, and indexed into a per-project FAISS vector store so future agents can retrieve relevant context via RAG before generating their outputs.

---

## Core Concept

A founder creates a **Project** and writes their **idea brief**. The system then exposes 8 **Modules** that unlock in a defined dependency order:

```
Idea Validation
    └── Market Research
            └── Business Model
                    ├── Product Strategy
                    │       ├── Technical Architecture
                    │       ├── Financial Planning
                    │       └── Marketing Strategy
                    └── (all above feed into Investor Documentation)
```

Each module runs a **LangGraph workflow pipeline**:

```
load_context → rag_retrieve → generation → validation → repair (max 2 retries) → reflection → persist → memory_index
```

Every workflow step is streamed live to the frontend via **Server-Sent Events (SSE)**.

---

## What's Built (All 46 Core Tasks Complete)

**Foundation**
- Project structure, Docker Compose (dev + prod), Makefile, GitHub Actions CI

**Backend**
- FastAPI with async SQLAlchemy, Alembic migrations (8 revisions, 13 tables)
- User auth — JWT access tokens (15 min) + rotating httpOnly refresh tokens (7 days), bcrypt
- Project + module CRUD, artifact versioning, workflow execution + SSE streaming
- Memory search endpoint, investor pack export, audit logging
- Full health/readiness probes at `/health` and `/health/ready`

**Frontend**
- Next.js 15 App Router with 12 routes — login, register, dashboard, projects, module workspace
- Live SSE progress bar, artifact viewer (JSON + markdown tabs), artifact editor, version history
- Dark mode, toast notifications, loading skeletons, error boundaries, responsive layout

**AI Infrastructure**
- Ollama client for local LLM inference (qwen3:4b)
- BAAI/bge-base-en-v1.5 embeddings (768-dim), FAISS per-project vector indexes
- RAG pipeline — chunking (800 chars, 150 overlap), embedding, semantic retrieval
- Knowledge base — 5 documents, 54 chunks, seeded via `scripts/build_index.py`
- Memory manager with SHA-256 deduplication, per-project artifact indexing

**AI Agents (8 complete)**
- All 8 agents with LangGraph StateGraphs, versioned prompts, Pydantic output schemas
- Graph factory routing all 8 module keys to their respective pipelines
- Guardrails — prompt injection detection, schema validation, output quality checks

**Hardening**
- Export service generating structured markdown investor packs
- Audit log middleware (project.create, workflow.trigger, export)
- Full test suite — 310 tests, ≥70% coverage
- Production Docker stack with nginx reverse proxy

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 15.1 | React framework, App Router, SSR |
| React | 19 | UI library |
| TypeScript | 5.7 | Type safety |
| Tailwind CSS | 3.4 | Utility-first styling |
| shadcn/ui | latest | Component library (New York style) |
| TanStack Query | 5 | Server state management, caching |
| Zustand | 5 | Client auth state with persistence |
| Framer Motion | 11 | Animations |
| Zod | 3 | Schema validation |
| React Hook Form | 7 | Form handling |
| Recharts | 2 | Data visualisation |
| Sonner | 1 | Toast notifications |
| Lucide React | 0.468 | Icons |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| FastAPI | 0.115 | Async REST API framework |
| SQLAlchemy | 2.0 | Async ORM |
| Alembic | 1.14 | Database migrations |
| PostgreSQL | 17 | Primary relational database |
| asyncpg | 0.30 | Async PostgreSQL driver |
| Pydantic v2 | 2.13 | Request/response validation |
| pydantic-settings | 2.5 | Environment config |
| python-jose | 3.3 | JWT encode/decode |
| passlib + bcrypt | latest | Password hashing |
| httpx | 0.28 | Async HTTP client |
| structlog | 24.4 | Structured JSON logging |

### AI / ML
| Technology | Version | Purpose |
|---|---|---|
| LangGraph | 0.2 | Agent workflow orchestration (DAG pipelines) |
| LangChain | 0.3 | LLM abstraction, prompt management |
| Ollama | latest | Local LLM inference server |
| Qwen 3 4B | latest | Primary generation model (`qwen3:4b`) |
| Sentence Transformers | 3.3 | Text embeddings |
| BAAI/bge-base-en-v1.5 | — | 768-dim embedding model |
| FAISS (CPU) | 1.9 | Per-project vector similarity search |
| NumPy | 1.26 | Numerical operations |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Docker Compose v2 | Containerisation, dev and prod stacks |
| nginx | Reverse proxy routing frontend + backend |
| Poetry | Python dependency management |
| bun | Frontend package manager and dev server |
| GitHub Actions | CI/CD pipeline (lint, type-check, test) |

---

## Project Structure

```
FoundrAI/
├── Frontend/                  # Next.js 15 App Router (capital F)
│   └── src/
│       ├── app/
│       │   ├── (auth)/        # login, register
│       │   └── (dashboard)/   # dashboard, projects, modules
│       ├── components/        # UI components (shadcn/ui + custom)
│       ├── hooks/             # Custom React hooks
│       ├── services/          # API service layer
│       ├── store/             # Zustand stores (auth.store.ts)
│       ├── lib/               # API client, utils
│       ├── types/             # TypeScript type definitions
│       └── middleware.ts      # Auth guard
│
├── backend/
│   ├── app/
│   │   ├── api/v1/            # FastAPI routers
│   │   ├── auth/              # JWT, password, deps
│   │   ├── core/              # Config, logging, exceptions
│   │   ├── database/          # SQLAlchemy engine, session
│   │   ├── models/            # ORM models (13 tables)
│   │   ├── repositories/      # Data access layer
│   │   ├── services/          # Business logic
│   │   ├── exporters/         # Investor pack export
│   │   └── main.py            # FastAPI entry point
│   ├── alembic/               # 8 migration revisions
│   └── tests/                 # pytest test suite
│
├── ai/
│   ├── agents/                # 8 domain agent modules
│   ├── graphs/                # LangGraph graphs + 8 pipeline nodes
│   ├── rag/                   # Chunking, embeddings, FAISS, retrieval
│   ├── memory/                # Project memory manager
│   ├── schemas/               # Pydantic artifact output schemas (8)
│   ├── prompts/               # Versioned prompt templates (4 per agent)
│   ├── guardrails/            # Prompt injection, output validation
│   ├── runtime/               # Prompt builder
│   └── config/                # agents.yaml, models.yaml
│
├── data/
│   ├── knowledge/             # 5 seed knowledge documents
│   ├── faiss/                 # FAISS vector indexes (gitignored)
│   └── exports/               # Generated investor packs
│
├── scripts/
│   ├── build_index.py         # Seed knowledge base FAISS index
│   ├── setup.sh               # One-command production setup
│   └── run_evals.py           # AI evaluation suite
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/
│   └── SETUP.md               # Detailed local setup guide
│
├── Docs/                      # Original spec documents
├── docker-compose.yml         # Dev (PostgreSQL only, port 5433)
├── docker-compose.prod.yml    # Prod (all services)
├── Makefile                   # Dev commands
├── AGENTS.md                  # AI agent reference
└── .env.example               # All environment variables (Docker/prod)
```

---

## The 8 AI Agents

| # | Agent | Module Key | Artifact Produced | Key Requirements |
|---|---|---|---|---|
| 1 | Idea Validator | `idea_validation` | `validation_report` | risks ≥ 3, score 0–100, problem/solution/target_customer |
| 2 | Market Researcher | `market_research` | `market_analysis` | competitors ≥ 3, TAM/SAM/SOM, segments, trends |
| 3 | Business Modeler | `business_model` | `business_model_canvas` | All 9 canvas blocks non-empty |
| 4 | Product Strategist | `product_strategy` | `product_roadmap` | phases ≥ 2, features ≥ 3 per phase |
| 5 | Technical Architect | `technical_architecture` | `architecture_doc` | components, stack, data_flows, security |
| 6 | Financial Analyst | `financial_planning` | `financial_model` | 12-month projection, assumptions ≥ 5 |
| 7 | Marketing Strategist | `marketing_strategy` | `marketing_plan` | channels ≥ 3, launch_checklist ≥ 5 items |
| 8 | Investor Writer | `investor_documentation` | `investor_deck_outline` | slides ≥ 10, includes problem/market/product/ask |

Each agent follows the same LangGraph pipeline and retrieves the top-8 RAG chunks from the project's FAISS index before invoking the LLM. Failed schema validation triggers an automatic repair loop (max 2 retries) before the run is marked failed.

See [AGENTS.md](./AGENTS.md) for detailed agent descriptions, capabilities, inputs, outputs, and prompt strategies.

---

## Database Schema (13 Tables)

```
users ──────────────── projects ──────────────── project_modules
  └── refresh_tokens       └── artifacts ────────── artifact_versions
                           └── workflow_runs ─────── workflow_steps
                                                └── agent_executions
                           └── memory_chunks
                           └── audit_logs
knowledge_documents (shared)
alembic_version
```

Key design decisions:
- **One artifact per `(project_id, artifact_type)`** — upsert with versioning
- **Module status**: `locked → available → in_progress → completed | failed`
- **Soft deletes** on projects (`deleted_at` timestamp)
- **Per-project FAISS indexes** stored at `data/faiss/{project_id}/`

---

## API Overview

The full interactive API documentation is available at runtime:
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

```
POST   /auth/register                                     Create account
POST   /auth/login                                        Login, get tokens
POST   /auth/refresh                                      Rotate refresh token
POST   /auth/logout                                       Revoke session
GET    /auth/me                                           Current user profile

GET    /projects                                          Paginated project list
POST   /projects                                          Create project (seeds 8 modules)
GET    /projects/{id}                                     Project detail with modules
PATCH  /projects/{id}                                     Update (re-indexes brief)
DELETE /projects/{id}                                     Soft delete

GET    /projects/{id}/modules                             Module list
GET    /projects/{id}/modules/{key}                       Module detail + dependencies

POST   /projects/{id}/workflows/{key}/run                 Trigger AI workflow → 202
GET    /projects/{id}/workflows/runs                      Paginated run list
GET    /projects/{id}/workflows/runs/{run_id}             Run detail with steps
POST   /projects/{id}/workflows/runs/{run_id}/cancel      Cancel run
GET    /projects/{id}/workflows/runs/{run_id}/stream      SSE live progress

GET    /projects/{id}/artifacts                           List artifacts
GET    /projects/{id}/artifacts/{aid}                     Full artifact
PATCH  /projects/{id}/artifacts/{aid}                     Edit artifact (new version)
GET    /projects/{id}/artifacts/{aid}/versions            Version history
GET    /projects/{id}/artifacts/{aid}/versions/{vid}      Snapshot

POST   /projects/{id}/memory/search                       Semantic search
POST   /projects/{id}/export/investor-pack                Generate export

GET    /health                                            Liveness probe
GET    /health/ready                                      Readiness (DB + Ollama + FAISS)
```

All errors return consistent JSON:
```json
{
  "error": {
    "code": "SCREAMING_SNAKE_CASE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

---

## Quick Start (Local Development)

> For a detailed step-by-step guide including Ollama installation, PostgreSQL setup, and troubleshooting — see **[docs/SETUP.md](./docs/SETUP.md)**.

### Prerequisites
- Python 3.11+ and [Poetry](https://python-poetry.org/docs/#installation)
- [Node.js 20+](https://nodejs.org/) and [bun](https://bun.sh)
- PostgreSQL 14+ running on port 5432 (user: `foundrai`, db: `foundrai`)
- [Ollama](https://ollama.ai) with `qwen3:4b` pulled

### 1. Clone and configure
```bash
git clone https://github.com/your-org/foundrai.git
cd FoundrAI
```

Create the backend environment file:
```bash
cp backend/.env.example backend/.env   # or create manually (see docs/SETUP.md)
```

### 2. Install dependencies

Backend:
```bash
cd backend && poetry install
```

Frontend:
```bash
cd Frontend && bun install
```

### 3. Run database migrations
```bash
cd backend && poetry run alembic upgrade head
```

### 4. Seed the knowledge base
```bash
cd backend && poetry run python ../scripts/build_index.py
```

### 5. Pull the LLM model
```bash
ollama pull qwen3:4b
```

### 6. Start services

In separate terminals:
```bash
# Terminal 1 — backend
cd backend && poetry run uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd Frontend && bun dev
```

Open **http://localhost:3000**

### One-command production stack
```bash
cp .env.example .env      # fill in production values
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script builds Docker images, starts all services, runs migrations, and seeds the knowledge base automatically.

---

## Development Commands

> **Note**: The Makefile uses `pnpm` for frontend targets but the project uses `bun`. Use `bun` directly for frontend commands, or use the backend/AI Makefile targets.

```bash
# Backend
make dev-backend          # Start FastAPI on :8000
make migrate              # Run Alembic migrations
make migrate-down         # Roll back last migration
make test-backend         # pytest with ≥70% coverage
make lint-backend         # ruff + mypy
make format-backend       # ruff format

# AI
make test-ai              # AI unit tests
make seed-knowledge       # Build FAISS knowledge base index
make eval                 # Run AI evaluation suite

# Frontend (use bun directly)
cd Frontend && bun dev    # Start Next.js on :3000
cd Frontend && bun test   # vitest
cd Frontend && bun run build

# Database
make db-up                # Start dev PostgreSQL via Docker (port 5433)
make migrate              # Run migrations
make shell-db             # Open psql shell

# Docker production
make docker-build         # Build images
make docker-up            # Start stack
make docker-down          # Stop stack
make docker-logs          # Tail logs
```

---

## Environment Variables

Backend local dev — create `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://foundrai:<password>@localhost:5432/foundrai
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
JWT_SECRET_KEY=<random 64-char hex string>
FRONTEND_URL=http://localhost:3000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

Frontend local dev — create `Frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

For Docker/production variables see `.env.example` at the project root. All variables are documented with descriptions.

---

## Running Tests

```bash
# Backend tests (310 tests, ≥70% coverage target)
cd backend && poetry run pytest tests/ -v

# Frontend tests
cd Frontend && bun test --run

# AI unit tests only
cd backend && poetry run pytest tests/ai/ -v
```

---

## Correctness Properties

The system is designed with 7 formal correctness properties verified via property-based testing:

1. **Artifact versioning monotonicity** — version numbers always increment by exactly 1
2. **Module dependency gate enforcement** — workflows always reject unmet dependencies
3. **Artifact schema validation consistency** — valid JSON always persists; invalid always rejects
4. **Memory indexing round-trip** — indexed text is always retrievable by semantic search
5. **Text chunking coverage** — chunking never drops content; all chunks ≤ chunk_size
6. **Project ownership isolation** — users can never access other users' projects
7. **Soft delete visibility** — deleted projects always return 404

---

## Roadmap

- [x] Project root structure, Docker, Makefile, CI pipeline
- [x] Backend FastAPI scaffold with health + readiness endpoints
- [x] PostgreSQL schema — 8 Alembic revisions, 13 tables
- [x] User authentication API — register, login, refresh, logout, /me
- [x] Project + module CRUD API with 8 auto-seeded modules
- [x] Artifact versioning API
- [x] Workflow execution API + SSE streaming
- [x] Next.js 15 frontend — all pages, auth, components, design system
- [x] Module workspace — SSE progress, artifact viewer/editor, version history
- [x] Ollama client + BAAI/bge-base-en-v1.5 embedding pipeline
- [x] FAISS index management (per-project)
- [x] Memory manager + RAG pipeline
- [x] Knowledge base — 5 docs, 54 chunks seeded
- [x] All 8 AI agents + LangGraph graphs
- [x] Graph factory + workflow wire-up
- [x] Guardrails — prompt injection, schema validation, output quality
- [x] Investor pack export (structured markdown)
- [x] Audit logging middleware
- [x] Full test suite (310 tests, ≥70% coverage)
- [x] Frontend polish — error boundaries, toasts, skeletons, dark mode
- [x] Production Docker setup + nginx reverse proxy
- [x] Documentation
- [ ] AI evaluation suite (Task 48)

---

## License

MIT
