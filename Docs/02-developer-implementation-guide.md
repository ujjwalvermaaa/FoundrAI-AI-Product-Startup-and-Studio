# FoundrAI Developer Implementation Guide

**Product:** FoundrAI – AI Product & Startup Studio  
**Tagline:** From Idea to Startup, Powered by AI  

---

## Document Index

| Doc | Purpose |
|-----|---------|
| [01 — Product & Software Specification](./01-foundrai-product-software-specification.md) | Master blueprint: product scope, modules, agents, architecture (Sections 16–34) |
| **02 — Developer Implementation Guide** (this document) | Chronological build order from empty repo to v1 |
| [03 — API & Database Reference](./03-api-database-reference.md) | REST endpoints, schemas, tables, indexes, error codes |
| [04 — AI System Design Specification](./04-ai-system-design-specification.md) | AI layer: models, prompts, agents, LangGraph, memory, RAG, eval |

**How to use this guide:** Read Sections 1–5 for context, then execute tasks in the order listed in Sections 7–15. Cross-reference the Product Spec for *what* to build and the API Reference for *exact contracts*. Do not re-derive architecture here.

---

## 1. Purpose and Prerequisites

### 1.1 Purpose

This guide is the **execution playbook** for building FoundrAI v1 from scratch. It sequences work across backend, frontend, database, AI, and infrastructure so that:

1. Dependencies are satisfied before dependent work begins.
2. Each sprint produces a demoable increment.
3. Engineers can pick up the next task without architectural ambiguity.

Architecture decisions live in Product Spec Sections 16–30. API and schema details live in Document 3. This document answers: **what to build next, in what order, and how to verify it.**

### 1.2 Prerequisites

| Category | Requirement |
|----------|-------------|
| **Skills** | TypeScript/React, Python/FastAPI, PostgreSQL, Docker, basic LLM/RAG concepts |
| **Hardware** | 16 GB RAM minimum (32 GB recommended for local Ollama + embeddings) |
| **OS** | macOS, Linux, or WSL2 on Windows |
| **Accounts** | GitHub org/repo access; no cloud accounts required for v1 local dev |
| **Documents** | Product Spec Sections 7–15 (modules, agents, screens); Sections 16–34 (architecture) |

### 1.3 Before You Write Code

1. Read Product Spec Section 1 (Executive Summary) and Section 7 (Product Scope).
2. Skim Section 12 (Module Specifications) and Section 13 (AI Agent Specifications).
3. Bookmark Document 3 for endpoint and table definitions.
4. Confirm Ollama can run Qwen 3 8B on your machine (Section 2.5).

### 1.4 Definition of Done (Global)

Every task in this guide is complete when:

- Code is merged via PR with passing CI (lint, type-check, unit tests).
- Relevant API endpoints match Document 3 contracts.
- Migrations are reversible (Alembic downgrade tested locally).
- No secrets committed; `.env.example` updated if new vars added.
- Acceptance criteria from the referenced Product Spec section are met.

---

## 2. Environment Setup

Pin versions in `.tool-versions` or document in `README.md`. All engineers must match these for v1.

### 2.1 Core Toolchain

| Tool | Version | Notes |
|------|---------|-------|
| **Node.js** | 22.x LTS | Use `nvm` or `fnm` |
| **pnpm** | 9.x | Package manager for frontend monorepo root |
| **Python** | 3.12.x | Backend and AI runtime |
| **Poetry** or **uv** | Latest stable | Python dependency management (pick one; standardize in repo) |
| **PostgreSQL** | 16.x | Local via Docker or native install |
| **Docker** | 27.x+ | Docker Compose v2 |
| **Git** | 2.45+ | Conventional commits enforced in CI |

### 2.2 Frontend Dependencies (installed during scaffold)

| Package | Version Target | Role |
|---------|----------------|------|
| Next.js | 15.x | App Router |
| React | 19.x | UI |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| shadcn/ui | Latest | Component primitives |
| TanStack Query | 5.x | Server state |
| Framer Motion | 11.x | Transitions |
| Zod | 3.x | Client-side validation |

### 2.3 Backend Dependencies (installed during scaffold)

| Package | Version Target | Role |
|---------|----------------|------|
| FastAPI | 0.115+ | HTTP API |
| Uvicorn | 0.32+ | ASGI server |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.14+ | Migrations |
| Pydantic | 2.x | Request/response models |
| python-jose / PyJWT | Latest | JWT |
| passlib + bcrypt | Latest | Password hashing |
| httpx | Latest | Ollama HTTP client |

### 2.4 AI Stack Dependencies

| Component | Version Target | Role |
|-----------|----------------|------|
| LangGraph | 0.2+ | Workflow graphs |
| LangChain | 0.3+ | LLM abstractions, tools |
| sentence-transformers | Latest | `BAAI/bge-base-en-v1.5` embeddings |
| faiss-cpu | Latest | Vector index (use `faiss-gpu` only if CUDA available) |
| Ollama | Latest | Local model server |

### 2.5 Ollama Setup

```bash
# Install Ollama (macOS)
brew install ollama

# Start daemon
ollama serve

# Pull primary model
ollama pull qwen3:8b

# Verify
curl http://localhost:11434/api/generate -d '{"model":"qwen3:8b","prompt":"Hello","stream":false}'
```

**Acceptance:** Response JSON within 30s on dev hardware. If latency exceeds Product Spec NFR targets, document hardware limits and proceed—do not switch to cloud LLM for v1.

### 2.6 PostgreSQL (Local)

```bash
# Via Docker (recommended)
docker run -d \
  --name foundrai-postgres \
  -e POSTGRES_USER=foundrai \
  -e POSTGRES_PASSWORD=foundrai_dev \
  -e POSTGRES_DB=foundrai \
  -p 5432:5432 \
  postgres:16-alpine
```

Connection string (dev): `postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai`

### 2.7 Environment Variables

Create root `.env.example` (never commit `.env`):

```bash
# App
APP_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai

# JWT
JWT_SECRET_KEY=change-me-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Embeddings
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
FAISS_INDEX_PATH=./data/faiss

# Frontend (apps/web/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 2.8 IDE and Quality Tools

| Tool | Scope | Config Location |
|------|-------|-----------------|
| ESLint + Prettier | Frontend | `apps/web/.eslintrc`, `.prettierrc` |
| Ruff | Backend Python | `backend/pyproject.toml` |
| mypy | Backend types | `backend/pyproject.toml` |
| pre-commit | Repo root | `.pre-commit-config.yaml` |

---

## 3. Repository Structure

Monorepo layout per Product Spec Section 29. Single Git repository; independent deployable services.

```
foundrai/
├── apps/
│   └── web/                    # Next.js frontend
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routers (v1)
│   │   ├── core/               # Config, security, deps
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic DTOs
│   │   ├── services/           # Business logic
│   │   ├── repositories/       # Data access
│   │   └── main.py
│   ├── alembic/                # Migrations
│   ├── tests/
│   └── pyproject.toml
├── ai/
│   ├── agents/                 # One module per agent
│   ├── graphs/                 # LangGraph definitions per module
│   ├── prompts/                # Versioned prompt templates
│   ├── rag/                    # Chunking, indexing, retrieval
│   ├── memory/                 # Project memory lifecycle
│   ├── schemas/                # Artifact JSON schemas (Pydantic)
│   └── runtime/                # Ollama client, inference helpers
├── data/
│   ├── faiss/                  # Vector indexes (gitignored)
│   └── knowledge/              # Seed knowledge documents
├── docker/
│   ├── Dockerfile.web
│   ├── Dockerfile.api
│   └── docker-compose.yml
├── docs/                       # Specification documents
├── scripts/                    # Dev utilities, seed scripts
├── .github/workflows/          # CI pipelines
├── pnpm-workspace.yaml
├── package.json                # Root scripts
├── Makefile                    # Common dev commands
└── README.md
```

### 3.1 Service Boundaries

| Service | Directory | Port (dev) | Responsibility |
|---------|-----------|------------|----------------|
| Web | `apps/web` | 3000 | UI, client-side routing, API proxy optional |
| API | `backend` | 8000 | REST, auth, orchestration entrypoints |
| AI Runtime | `ai/` (imported by backend) | — | LangGraph, agents, RAG (same process as API in v1) |
| PostgreSQL | Docker | 5432 | Persistent data |
| Ollama | External daemon | 11434 | LLM inference |

v1 runs AI logic **in-process** with FastAPI (Product Spec Section 19). Separate AI microservice is future scope.

---

## 4. Folder Creation

Execute in order on Day 1. Assumes empty repo cloned locally.

### 4.1 Initialize Repository

```bash
git init foundrai && cd foundrai
mkdir -p apps/web backend/app ai/{agents,graphs,prompts,rag,memory,schemas,runtime} \
  data/{faiss,knowledge} docker scripts docs .github/workflows
```

### 4.2 Frontend Scaffold

```bash
cd apps/web
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
pnpm add @tanstack/react-query zod framer-motion
pnpm dlx shadcn@latest init
```

Create placeholder routes (empty pages OK):

| Path | Purpose |
|------|---------|
| `src/app/(auth)/login/page.tsx` | Login |
| `src/app/(auth)/register/page.tsx` | Register |
| `src/app/(dashboard)/projects/page.tsx` | Project list |
| `src/app/(dashboard)/projects/[id]/page.tsx` | Project overview |
| `src/app/(dashboard)/projects/[id]/modules/[module]/page.tsx` | Module workspace |

### 4.3 Backend Scaffold

```bash
cd backend
poetry init  # or uv init
poetry add fastapi uvicorn sqlalchemy asyncpg alembic pydantic pydantic-settings \
  python-jose passlib bcrypt httpx
poetry add --group dev pytest pytest-asyncio ruff mypy
alembic init alembic
```

Create minimal `app/main.py` with health check:

```python
from fastapi import FastAPI

app = FastAPI(title="FoundrAI API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}
```

### 4.4 AI Package Scaffold

```bash
touch ai/__init__.py ai/runtime/ollama_client.py ai/rag/embedder.py ai/rag/retriever.py
```

Add `ai` to Python path via `backend/pyproject.toml` package config or install as editable local package.

### 4.5 Docker and CI Skeleton

```bash
touch docker/docker-compose.yml docker/Dockerfile.api docker/Dockerfile.web
touch .github/workflows/ci.yml Makefile .env.example .gitignore
```

Add to `.gitignore`: `.env`, `data/faiss/*`, `__pycache__`, `.next`, `node_modules`, `.venv`

### 4.6 Makefile Targets (initial)

```makefile
.PHONY: dev db-up migrate test lint

dev:
	docker compose -f docker/docker-compose.yml up -d postgres
	cd backend && poetry run uvicorn app.main:app --reload --port 8000

db-up:
	docker compose -f docker/docker-compose.yml up -d postgres

migrate:
	cd backend && poetry run alembic upgrade head

test:
	cd backend && poetry run pytest
	cd apps/web && pnpm test

lint:
	cd backend && poetry run ruff check .
	cd apps/web && pnpm lint
```

**Checkpoint:** `make dev` serves API on `:8000`; `pnpm dev` in `apps/web` serves UI on `:3000`; `/health` returns 200.

---

## 5. Development Phases

High-level phases map to Milestones M1–M6 (Section 20). Do not skip phases.

```mermaid
flowchart LR
    P0["Phase 0\nFoundation"] --> P1["Phase 1\nCore Platform"]
    P1 --> P2["Phase 2\nWorkspace"]
    P2 --> P3["Phase 3\nAI Infrastructure"]
    P3 --> P4["Phase 4\nWorkflows & Agents"]
    P4 --> P5["Phase 5\nHardening & Ship"]
```

| Phase | Name | Goal | Spec Reference |
|-------|------|------|----------------|
| **0** | Foundation | Repo, env, CI, health checks | §29, §30 |
| **1** | Core Platform | Auth, users, projects, DB | §23, §25, Doc 3 |
| **2** | Workspace | Modules UI, artifacts CRUD, versioning | §12, §14, §17 |
| **3** | AI Infrastructure | Ollama, embeddings, FAISS, memory chunks | §19, §21, §22 |
| **4** | Workflows & Agents | LangGraph per module, all 8 modules | §13, §15, §20 |
| **5** | Hardening & Ship | Testing, Docker prod compose, export, docs | §26–28, §33 |

### 5.1 Phase Exit Criteria

| Phase | Exit Criteria |
|-------|---------------|
| 0 | CI green on lint; both services boot via Makefile |
| 1 | Register/login/me works; project CRUD persisted |
| 2 | User can view module tabs; create/edit artifact versions |
| 3 | Memory search returns relevant chunks from indexed artifacts |
| 4 | At least Idea Validation workflow runs end-to-end with stored artifact |
| 5 | All 8 modules runnable; investor export generates document; Docker stack runs |

---

## 6. Sprint Planning

Eight two-week sprints (~16 weeks to v1). Adjust team size: 2–4 engineers can parallelize frontend/backend after Sprint 2.

| Sprint | Dates (example) | Phase | Goals | Key Deliverables |
|--------|-----------------|-------|-------|------------------|
| **S1** | W1–W2 | 0 | Scaffold, CI, DB connection | Monorepo, health endpoints, Postgres, Alembic init |
| **S2** | W3–W4 | 1 | Authentication | JWT auth, users table, login/register UI |
| **S3** | W5–W6 | 1–2 | Projects & modules | Project CRUD API + list/detail UI, `project_modules` seed |
| **S4** | W7–W8 | 2 | Artifacts | Artifact storage, versioning, module workspace shell |
| **S5** | W9–W10 | 3 | AI base | Ollama client, embedder, FAISS index, `memory_chunks` |
| **S6** | W11–W12 | 3–4 | First workflow | LangGraph runtime, Idea Validation module E2E |
| **S7** | W13–W14 | 4 | Module expansion | Market Research, Business Model, Product Strategy workflows |
| **S8** | W15–W16 | 4–5 | Complete v1 | Remaining modules, export, e2e tests, Docker deploy |

### 6.1 Sprint Ceremonies

| Ceremony | When | Output |
|----------|------|--------|
| Planning | Day 1 | Tasks mapped to Sections 7–15 order |
| Demo | Day 10 | Working increment against exit criteria |
| Retro | Day 10 | Blockers logged (especially Ollama latency) |

### 6.2 Parallel Work Streams (after S2)

| Stream | Owner | Focus |
|--------|-------|-------|
| A — Backend/API | Backend engineer | Sections 7, 9–11 |
| B — Frontend | Frontend engineer | Section 8 |
| C — AI/ML | AI engineer | Sections 12–15 |

Sync daily on shared contracts in Document 3.

---

## 7. Backend Development Order

Tasks are strictly ordered. **Blocked By** must be green before starting.

| # | Task | Blocked By | Spec / Doc Ref | Verification |
|---|------|----------|----------------|--------------|
| B1 | Project config: settings, logging, CORS | Phase 0 | §18, §27 | Structured JSON logs on request |
| B2 | DB engine + session dependency | B1 | §18, Doc 3 | Integration test connects to Postgres |
| B3 | Alembic env + base migration | B2 | §23 | `upgrade` / `downgrade` clean |
| B4 | `users`, `refresh_tokens` models + repos | B3 | Doc 3 §3 | Unit test CRUD |
| B5 | Password hash + JWT utilities | B4 | §25 | Token encode/decode roundtrip |
| B6 | Auth router: register, login, refresh, logout, me | B5 | Doc 3 §10 | Postman/pytest auth flow |
| B7 | Auth dependency + project ownership guard | B6 | Doc 3 §9 | 403 on foreign project |
| B8 | `projects`, `project_modules` models + repos | B7 | Doc 3 §3 | Create project seeds 8 modules |
| B9 | Projects router: CRUD, list | B8 | Doc 3 §10 | Pagination works |
| B10 | `artifacts`, `artifact_versions` models | B9 | Doc 3 §3 | Version increment on update |
| B11 | Artifacts router: list, get, update, versions | B10 | Doc 3 §10 | User edit creates new version |
| B12 | `workflow_runs`, `workflow_steps`, `agent_executions` | B11 | Doc 3 §3 | Status transitions persisted |
| B13 | Workflow service: trigger, status, cancel | B12 | §20, Doc 3 §10 | Async job updates run record |
| B14 | SSE or polling endpoint for run progress | B13 | Doc 3 §17 | UI receives step updates |
| B15 | `memory_chunks`, `knowledge_documents` models | B3 | Doc 3 §3 | Chunk FK to project |
| B16 | Memory search service + router | B15, RAG tasks | Doc 3 §10 | Semantic search returns hits |
| B17 | Export service: investor pack generation | B11, agents | Doc 3 §10 | PDF/Markdown bundle |
| B18 | `audit_logs` middleware | B1 | §27 | Auth + workflow events logged |
| B19 | Global exception handlers + error codes | B1 | Doc 3 §15 | Consistent error JSON |
| B20 | Wire AI runtime into workflow service | B13, §12 | §19 | Graph invoke from API |

### 7.1 Backend Layer Rules

Per Product Spec Section 18:

```
Router → Service → Repository → Model
         ↓
      AI Runtime (graphs/agents) — called from Service only
```

- Routers: validation, auth, HTTP status only.
- Services: business rules, orchestration, transaction boundaries.
- Repositories: SQL only; no business logic.
- Never call Ollama or FAISS from routers directly.

---

## 8. Frontend Development Order

| # | Task | Blocked By | Spec Ref | Verification |
|---|------|----------|----------|--------------|
| F1 | Design tokens, layout shell, sidebar nav | Phase 0 | §14, §17 | Responsive dashboard layout |
| F2 | API client + TanStack Query setup | F1, B6 | §17 | Typed fetch wrapper with auth header |
| F3 | Auth pages: register, login | F2 | §14 | Token stored; redirect to projects |
| F4 | Auth guard + token refresh interceptor | F3 | §25 | Silent refresh before expiry |
| F5 | Project list + create project modal | F4, B9 | §14 | Empty state + populated list |
| F6 | Project overview dashboard | F5 | §14 | Module status cards from API |
| F7 | Module workspace layout (tabs/stepper) | F6 | §12, §14 | Route `/projects/[id]/modules/[module]` |
| F8 | Artifact viewer component (JSON/markdown render) | F7, B11 | §14 | Renders typed artifact schemas |
| F9 | Artifact editor + save (user edits) | F8 | §14 | Creates new version via API |
| F10 | Version history panel | F9 | §14 | Diff or list prior versions |
| F11 | Workflow trigger UI + input form | F7, B13 | §15 | Module-specific inputs collected |
| F12 | Workflow progress UI (SSE/polling) | F11, B14 | §14, Doc 3 §17 | Live step status |
| F13 | Memory search panel (debug/power user) | B16 | §14 | Query returns cited chunks |
| F14 | Export flow UI | B17 | §14 | Download investor pack |
| F15 | Error boundaries, toast notifications, loading skeletons | F2 | §17 | Graceful API error display |
| F16 | Framer Motion transitions on module navigation | F7 | §17 | Polished UX per NFR |

### 8.1 Frontend Data Conventions

- All server state via TanStack Query; query keys: `['projects']`, `['project', id]`, `['artifacts', projectId, module]`, `['workflow-run', runId]`.
- Optimistic updates **disabled** for workflow triggers (wait for server confirmation).
- Form validation mirrors Pydantic rules in Document 3 §14.

---

## 9. Database Development

Full column specs: Document 3 §3. This section defines **migration order** and seed data.

### 9.1 Migration Order

| Migration | Tables | Depends On |
|-----------|--------|------------|
| `001_initial` | Alembic setup, extensions (`uuid-ossp` or `pgcrypto`) | — |
| `002_users_auth` | `users`, `refresh_tokens` | 001 |
| `003_projects` | `projects`, `project_modules` | 002 |
| `004_artifacts` | `artifacts`, `artifact_versions` | 003 |
| `005_workflows` | `workflow_runs`, `workflow_steps`, `agent_executions` | 003, 004 |
| `006_memory` | `memory_chunks`, `knowledge_documents` | 003 |
| `007_audit` | `audit_logs` | 002 |
| `008_indexes` | Performance indexes per Doc 3 §6 | All above |

**Rule:** One migration per logical domain; never edit applied migrations—add new ones.

### 9.2 Seed Data

| Seed Script | When | Contents |
|-------------|------|----------|
| `scripts/seed_modules.py` | After 003 | 8 `project_modules` rows per new project (via service layer, not raw SQL) |
| `scripts/seed_dev_user.py` | Dev only | Test user `founder@foundrai.dev` |
| `scripts/seed_knowledge.py` | After 006 | Baseline `knowledge_documents` for RAG (general startup playbooks) |

Module keys (must match Product Spec Section 12):

| `module_key` | Display Name |
|--------------|--------------|
| `idea_validation` | Idea Validation |
| `market_research` | Market Research |
| `business_model` | Business Model |
| `product_strategy` | Product Strategy |
| `technical_architecture` | Technical Architecture |
| `financial_planning` | Financial Planning |
| `marketing_strategy` | Marketing Strategy |
| `investor_documentation` | Investor Documentation |

### 9.3 Migration Workflow

```bash
cd backend
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
poetry run alembic downgrade -1   # verify rollback
poetry run alembic upgrade head
```

---

## 10. Authentication Implementation Order

Detail: Product Spec Section 25; endpoints: Document 3 §8–9.

| Step | Task | Notes |
|------|------|-------|
| 1 | `users` table + unique email constraint | UUID primary keys |
| 2 | Password hashing (bcrypt, cost factor 12) | Never log passwords |
| 3 | Access JWT (short-lived, 15 min) | Claims: `sub`, `exp`, `type=access` |
| 4 | Refresh token (opaque or JWT, 7 days) | Stored in `refresh_tokens` with revocation |
| 5 | `POST /auth/register` | Returns tokens or requires login—pick one; document in API ref |
| 6 | `POST /auth/login` | Returns access + refresh |
| 7 | `POST /auth/refresh` | Rotates refresh token |
| 8 | `POST /auth/logout` | Revokes refresh token |
| 9 | `GET /auth/me` | Returns user profile |
| 10 | FastAPI `Depends(get_current_user)` | Bearer token extraction |
| 11 | Project ownership dependency | `project.user_id == current_user.id` |
| 12 | Frontend token storage | httpOnly cookie (preferred) or secure memory + refresh flow |

### 10.1 Security Checklist

- [ ] JWT secret from env, min 256 bits
- [ ] Refresh token rotation on use
- [ ] Rate limit login endpoint (middleware or reverse proxy)
- [ ] CORS restricted to `NEXT_PUBLIC_API_URL` origin in staging/prod

---

## 11. API Development Order

Implement routers in this order. Full contracts: Document 3 §10–16.

| Order | Router Prefix | Endpoints | Auth |
|-------|---------------|-----------|------|
| 1 | `/api/v1/health` | Health, readiness (DB + Ollama probe) | Public |
| 2 | `/api/v1/auth` | register, login, refresh, logout, me | Mixed |
| 3 | `/api/v1/projects` | CRUD, list | Bearer |
| 4 | `/api/v1/projects/{id}/modules` | list, get status | Bearer + owner |
| 5 | `/api/v1/projects/{id}/artifacts` | list, get, update, versions | Bearer + owner |
| 6 | `/api/v1/projects/{id}/workflows` | trigger, list runs, get run, cancel | Bearer + owner |
| 7 | `/api/v1/projects/{id}/memory` | search | Bearer + owner |
| 8 | `/api/v1/projects/{id}/export` | generate investor pack | Bearer + owner |

### 11.1 API Conventions

- Base path: `/api/v1` (Document 3 §7).
- JSON field names: `snake_case`.
- IDs: UUID strings in path and body.
- Pagination: `?page=1&page_size=20` on list endpoints.
- Errors: `{ "error": { "code": "...", "message": "...", "details": {} } }`.

### 11.2 Readiness Probe

Readiness (not liveness) checks:

1. PostgreSQL connection.
2. Ollama `GET /api/tags` includes `qwen3:8b`.
3. FAISS index directory writable (optional warning if empty index).

---

## 12. LangGraph Development Order

Architecture: Product Spec Section 20. Graphs live in `ai/graphs/`.

### 12.1 Shared Infrastructure First

| # | Task | Output |
|---|------|--------|
| G1 | Define `WorkflowState` TypedDict / Pydantic model | Shared state schema |
| G2 | Ollama LLM wrapper (`ai/runtime/ollama_client.py`) | Sync + async invoke |
| G3 | Graph runner service with DB persistence hooks | Updates `workflow_runs`, `workflow_steps` |
| G4 | Checkpoint strategy (in-memory v1; Postgres optional) | Retry from failed node |
| G5 | Error handling + step retry policy (max 2 retries) | Failed run marks `status=failed` |

### 12.2 Graph State Schema (minimum fields)

```python
# Conceptual — implement in ai/graphs/state.py
# project_id, module_key, run_id, inputs, retrieved_context,
# agent_outputs, current_artifact_draft, errors
```

### 12.3 Standard Node Pipeline (per module)

Each module graph follows this pattern (Product Spec Section 15):

```mermaid
flowchart TD
    START([Start]) --> LOAD[Load Project Context]
    LOAD --> RETRIEVE[RAG Retrieve]
    RETRIEVE --> AGENT[Domain Agent Node]
    AGENT --> VALIDATE[Schema Validate Output]
    VALIDATE -->|pass| PERSIST[Persist Artifact + Memory]
    VALIDATE -->|fail| RETRY[Retry / Fail]
    PERSIST --> END([End])
```

### 12.4 Graph Implementation Order

| Order | Graph File | Module | Agents Used |
|-------|------------|--------|-------------|
| 1 | `validation_graph.py` | Idea Validation | Idea Validator |
| 2 | `market_research_graph.py` | Market Research | Market Research |
| 3 | `business_model_graph.py` | Business Model | Business Model |
| 4 | `product_strategy_graph.py` | Product Strategy | Product Strategist |
| 5 | `architecture_graph.py` | Technical Architecture | Technical Architect |
| 6 | `financial_graph.py` | Financial Planning | Financial Analyst |
| 7 | `marketing_graph.py` | Marketing Strategy | Marketing Strategist |
| 8 | `investor_graph.py` | Investor Documentation | Investor Writer (+ synthesis of prior artifacts) |

**Rule:** Graph N may read artifacts from modules 1..N-1 via retrieval; enforce dependency in workflow service before trigger.

### 12.5 Module Dependency Gate

| Module | Requires Prior Artifacts |
|--------|--------------------------|
| Idea Validation | Project brief only |
| Market Research | Idea Validation |
| Business Model | Idea Validation, Market Research |
| Product Strategy | Business Model |
| Technical Architecture | Product Strategy |
| Financial Planning | Business Model, Product Strategy |
| Marketing Strategy | Business Model, Product Strategy |
| Investor Documentation | All prior modules (recommended) |

Implement gate in `WorkflowService.trigger()`—return `409` with `MODULE_DEPENDENCY_NOT_MET` if missing.

---

## 13. AI Agent Development Order

Agent specs: Product Spec Section 13. One directory per agent under `ai/agents/`.

### 13.1 Agent Build Sequence

Build agents in module dependency order. Each agent ships with: system prompt, output schema, unit eval fixtures.

| Order | Agent ID | Directory | Primary Output Artifact |
|-------|----------|-----------|-------------------------|
| A1 | `idea_validator` | `ai/agents/idea_validator/` | `validation_report` |
| A2 | `market_researcher` | `ai/agents/market_researcher/` | `market_analysis` |
| A3 | `business_modeler` | `ai/agents/business_modeler/` | `business_model_canvas` |
| A4 | `product_strategist` | `ai/agents/product_strategist/` | `product_roadmap` |
| A5 | `technical_architect` | `ai/agents/technical_architect/` | `architecture_doc` |
| A6 | `financial_analyst` | `ai/agents/financial_analyst/` | `financial_model` |
| A7 | `marketing_strategist` | `ai/agents/marketing_strategist/` | `marketing_plan` |
| A8 | `investor_writer` | `ai/agents/investor_writer/` | `investor_deck_outline` |
| A9 | `orchestrator` | `ai/agents/orchestrator/` | Routing only (no artifact) |

### 13.2 Per-Agent Deliverables

| File | Purpose |
|------|---------|
| `agent.py` | LangChain runnable / node function |
| `schema.py` | Pydantic output model (matches `ai/schemas/`) |
| `tools.py` | Optional tools (memory search, calculator) |
| `README.md` | Inputs, outputs, eval notes |

### 13.3 Agent Implementation Checklist

For each agent:

1. Define output schema in `ai/schemas/{artifact_type}.py`.
2. Write prompt templates in `ai/prompts/{agent_id}/` (Section 14).
3. Implement agent node: retrieve context → build messages → invoke Ollama → parse JSON.
4. Add JSON repair fallback (strip markdown fences, retry once).
5. Validate output against schema; on failure, record error in `agent_executions`.
6. Persist artifact via backend service callback.
7. Index artifact chunks into memory (Section 15).
8. Add eval cases in `ai/tests/evals/{agent_id}.yaml`.

---

## 14. Prompt Development

### 14.1 Prompt Engineering Workflow

```mermaid
flowchart LR
    SPEC["Agent Spec §13"] --> DRAFT["Draft prompt .md"]
    DRAFT --> TEST["Run eval fixtures"]
    TEST -->|fail| ITERATE["Iterate prompt"]
    ITERATE --> DRAFT
    TEST -->|pass| VERSION["Tag version"]
    VERSION --> SHIP["Merge + changelog"]
```

| Step | Action | Owner |
|------|--------|-------|
| 1 | Extract inputs/outputs from Product Spec Section 13 | AI engineer |
| 2 | Draft system + user template with `{variable}` placeholders | AI engineer |
| 3 | Run against 3+ fixture inputs (happy, edge, adversarial) | AI engineer |
| 4 | Validate JSON schema compliance rate ≥ 90% on fixtures | AI engineer |
| 5 | Tag prompt version; update `prompts/CHANGELOG.md` | AI engineer |
| 6 | PR review by second engineer | Team |

### 14.2 Prompt File Structure

```
ai/prompts/
├── idea_validator/
│   ├── v1.0.0.system.md
│   ├── v1.0.0.user.md
│   └── manifest.yaml          # active version, variables, schema ref
├── market_researcher/
│   └── ...
└── CHANGELOG.md
```

### 14.3 Prompt Versioning Rules

| Rule | Detail |
|------|--------|
| **Semver** | MAJOR = output schema change; MINOR = instruction change; PATCH = typo |
| **Active version** | `manifest.yaml` points to active pair; code loads via manifest |
| **No inline prompts** | Production prompts live in `ai/prompts/`, not hardcoded in Python |
| **Context budget** | System + retrieval + user input must fit model context; truncate retrieval first |
| **Grounding instruction** | Every agent prompt includes: "Use only provided context; cite retrieval IDs" |

### 14.4 Prompt Variables (standard)

| Variable | Source |
|----------|--------|
| `{project_name}` | `projects` table |
| `{project_brief}` | Project description / initial input |
| `{retrieved_context}` | RAG formatter output |
| `{prior_artifacts}` | Serialized summaries of dependency modules |
| `{output_schema}` | JSON schema string for structured output |

---

## 15. RAG Development Order

Architecture: Product Spec Sections 21–22.

| # | Task | Blocked By | Verification |
|---|------|----------|--------------|
| R1 | Embedder wrapper (`BAAI/bge-base-en-v1.5`) | Phase 0 | Deterministic vector dim (768) |
| R2 | Chunking strategy (512 tokens, 64 overlap) | R1 | Unit test chunk boundaries |
| R3 | `memory_chunks` write path on artifact persist | B15, R2 | Chunks appear in DB |
| R4 | FAISS index per project (or global with filter) | R3 | Product Spec §22 tier-1 |
| R5 | Index rebuild job on artifact version create | R4 | Search finds new content |
| R6 | `knowledge_documents` ingest script | R4 | Seed docs searchable |
| R7 | Retriever: top-k similarity + metadata filter | R4, R6 | Returns ranked chunks |
| R8 | Context formatter for agent prompts | R7 | Token-limited string output |
| R9 | Memory search API wired | R7, B16 | `GET memory/search?q=` works |
| R10 | Source citation metadata in agent outputs | R8 | Artifact includes `sources[]` |

### 15.1 Index Storage

- Path: `data/faiss/{project_id}/index.faiss` + `metadata.json`
- Gitignore all index files; rebuild from DB in dev if deleted.
- v1: co-located with API container; mount volume in Docker (Product Spec A-4).

### 15.2 Chunk Metadata (required fields)

| Field | Example |
|-------|---------|
| `project_id` | UUID |
| `artifact_id` | UUID |
| `artifact_version` | 3 |
| `module_key` | `market_research` |
| `chunk_index` | 0 |

---

## 16. Testing Strategy

### 16.1 Test Pyramid

| Layer | Scope | Tools | When |
|-------|-------|-------|------|
| **Unit** | Utils, schemas, repos (mocked DB) | pytest, Vitest | Every PR |
| **Integration** | API + real Postgres (test DB) | pytest + TestClient | Every PR |
| **E2E** | Full user flows in browser | Playwright | Nightly + pre-release |
| **AI Eval** | Agent output quality | Custom eval runner + fixtures | Agent PRs + nightly |

### 16.2 Backend Test Order

1. Auth service unit tests.
2. Project ownership authorization tests.
3. Artifact versioning integration tests.
4. Workflow trigger → status transition tests (mock Ollama).
5. Memory search integration tests (seed chunks).

### 16.3 Frontend Test Order

1. Component tests: artifact viewer, forms (Vitest + Testing Library).
2. Hook tests: auth refresh, query invalidation.
3. E2E: register → create project → trigger validation workflow → view artifact.

### 16.4 AI Eval Framework

```
ai/tests/evals/
├── fixtures/           # Input project states
├── expected/           # Schema + keyword assertions
└── run_evals.py        # CLI: score pass rate
```

| Eval Type | Pass Criteria |
|-----------|---------------|
| Schema compliance | 100% parseable JSON matching Pydantic model |
| Required fields | All non-optional fields populated |
| Grounding | No fabricated market stats when retrieval empty (use eval fixtures) |
| Regression | Score ≥ prior prompt version on same fixtures |

### 16.5 CI Pipeline Stages

```yaml
# .github/workflows/ci.yml (conceptual stages)
1. lint (ruff, eslint)
2. typecheck (mypy, tsc)
3. unit tests
4. integration tests (postgres service container)
5. build docker images
# AI evals: nightly workflow (Ollama required — use self-hosted or skip with label)
```

### 16.6 Test Data

- Use factory fixtures (`backend/tests/factories/`), not production data.
- Never call production Ollama in unit tests—mock LLM responses.
- Dedicated `foundrai_test` database; reset between integration modules.

---

## 17. Docker Setup

Detail: Product Spec Section 30.

### 17.1 Compose Services

| Service | Image / Build | Port | Depends On |
|---------|---------------|------|------------|
| `postgres` | `postgres:16-alpine` | 5432 | — |
| `api` | `docker/Dockerfile.api` | 8000 | postgres |
| `web` | `docker/Dockerfile.web` | 3000 | api |
| `ollama` | `ollama/ollama:latest` | 11434 | — (GPU optional) |

**Note:** Ollama may run on host instead of compose for macOS GPU/Metal performance. Set `OLLAMA_BASE_URL=http://host.docker.internal:11434` from API container.

### 17.2 Build Order

1. `postgres` — start first, wait for healthcheck.
2. Run migrations (`api` entrypoint script or init container).
3. `api` — build after backend + ai copy.
4. `web` — build with `NEXT_PUBLIC_API_URL` build arg.
5. Pull Ollama model (init script or manual).

### 17.3 docker-compose.yml (skeleton)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: foundrai
      POSTGRES_PASSWORD: foundrai_dev
      POSTGRES_DB: foundrai
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U foundrai"]
      interval: 5s
      retries: 5

  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.api
    env_file: ../.env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ../data/faiss:/app/data/faiss

  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile.web
      args:
        NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  pgdata:
```

### 17.4 Local Dev vs Compose

| Mode | Use When |
|------|----------|
| `make dev` (native hot reload) | Daily development |
| `docker compose up` | Onboarding, staging parity, demo |

---

## 18. Deployment

### 18.1 Local Deployment

```bash
cp .env.example .env          # Edit secrets
make db-up
make migrate
docker compose -f docker/docker-compose.yml up --build
# Ensure Ollama model pulled
```

Verify: Login → create project → run Idea Validation → artifact persisted.

### 18.2 Staging (single VM)

| Component | Setup |
|-----------|-------|
| VM | 8 vCPU, 32 GB RAM, 100 GB SSD |
| Reverse proxy | Caddy or nginx TLS termination |
| Postgres | Managed or co-located container with backups |
| Ollama | Co-located; model baked in startup script |
| Secrets | Env vars via vault or encrypted `.env` |
| Domain | `staging.foundrai.app` |

Deploy flow: push image tag → SSH pull → `docker compose pull && up -d` → smoke test `/health`.

### 18.3 Production (future AWS — Product Spec Section 32)

Not in v1 scope. Planned direction:

| Service | AWS Target |
|---------|------------|
| Web | Amplify or ECS + CloudFront |
| API | ECS Fargate |
| DB | RDS PostgreSQL |
| Vectors | EFS mount for FAISS → OpenSearch later |
| LLM | EC2 GPU or Bedrock (post-v1) |
| Secrets | Secrets Manager |

Document decisions in ADR before migration.

### 18.4 Environment Matrix

| Env | `APP_ENV` | Ollama | DB |
|-----|-----------|--------|-----|
| local | development | Host or compose | Docker Postgres |
| staging | staging | Dedicated VM | Staging RDS/Postgres |
| prod | production | TBD (v2) | RDS |

---

## 19. Git Workflow

### 19.1 Branching Model

Trunk-based with short-lived feature branches.

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready; protected |
| `develop` | Integration branch (optional; may use `main` only for small team) |
| `feat/{ticket}-{slug}` | Features |
| `fix/{ticket}-{slug}` | Bug fixes |
| `chore/{slug}` | Tooling, deps |

### 19.2 Pull Request Rules

- PR title: conventional commit format (`feat:`, `fix:`, `chore:`, `docs:`).
- Require 1 approval; 2 for auth/security/AI prompt changes.
- CI must pass before merge.
- PR description: what, why, test plan, linked issue.

### 19.3 Commit Conventions

```
feat(api): add workflow cancel endpoint
fix(web): refresh token race on tab focus
chore(ai): bump langgraph to 0.2.1
docs: update implementation guide sprint 6
```

### 19.4 Release Tagging

- Tag releases: `v1.0.0`, `v1.1.0`.
- Changelog in `CHANGELOG.md` at repo root (Keep a Changelog format).

---

## 20. Milestones

| Milestone | Target | Phase | Deliverables | Success Criteria |
|-----------|--------|-------|--------------|------------------|
| **M1** | End S2 | 0–1 | Repo, CI, auth E2E | User can register and log in |
| **M2** | End S4 | 2 | Project workspace + artifacts | User manages project and views/edits artifacts |
| **M3** | End S5 | 3 | RAG + memory search | Semantic search returns project content |
| **M4** | End S6 | 4 | First AI workflow | Idea Validation produces schema-valid artifact |
| **M5** | End S7 | 4 | Core modules live | 4 modules run end-to-end |
| **M6** | End S8 | 5 | **v1 release** | All 8 modules, export, Docker deploy, eval suite green |

### 20.1 Milestone Demo Script (M6)

1. Register new user.
2. Create project with startup brief.
3. Run workflows: Idea Validation → Market Research → Business Model.
4. Edit artifact; confirm version 2 created.
5. Run memory search; confirm citation from edited artifact.
6. Complete remaining modules or demo pre-seeded project.
7. Export investor pack; download file.
8. Show audit log entries for workflow runs.

---

## 21. Best Practices

### 21.1 General Coding

| Practice | Rule |
|----------|------|
| Typing | Strict TypeScript; mypy strict on backend |
| IDs | UUID v4 everywhere; never sequential public IDs |
| Time | UTC in DB; ISO 8601 in API |
| Immutability | Artifact content immutable per version; edits = new version |
| Transactions | One workflow step = one DB transaction boundary where possible |

### 21.2 AI-Specific

| Practice | Rule |
|----------|------|
| Structured output | Always request JSON; validate with Pydantic before persist |
| Timeouts | Ollama call timeout 120s default; configurable |
| Idempotency | Workflow run ID prevents duplicate artifact writes on retry |
| Observability | Log prompt hash + retrieval IDs, never raw prompts in prod logs |
| Eval before merge | Agent/prompt PRs include eval pass rate in description |

### 21.3 Security

| Practice | Rule |
|----------|------|
| Secrets | Env only; scan with gitleaks in CI |
| AuthZ | Every project-scoped route checks ownership |
| Input | Max body size 1 MB on API; sanitize user markdown |
| Dependencies | Weekly `pnpm audit` / `poetry audit` |
| LLM injection | Treat user brief as untrusted; system prompt hardening |

Reference: Product Spec Section 26.

### 21.4 Performance

| Target | Metric (Product Spec §28) |
|--------|---------------------------|
| API p95 (non-AI) | < 200 ms |
| Workflow trigger ACK | < 500 ms (async execution) |
| RAG retrieval | < 300 ms |
| Full agent step | < 90 s (hardware dependent) |

Use async FastAPI endpoints for workflow triggers; run graphs in background tasks or task queue (v1: `asyncio.create_task` or FastAPI BackgroundTasks; v1.1: Celery/ARQ if needed).

---

## 22. Expected Deliverables (v1 Checklist)

Use this checklist for release sign-off.

### 22.1 Platform

- [ ] Monorepo with `apps/web`, `backend`, `ai` per Section 3
- [ ] Docker Compose runs full stack locally
- [ ] CI: lint, test, build on every PR
- [ ] `.env.example` documents all variables
- [ ] README: quickstart in < 15 minutes for new engineer

### 22.2 Authentication & Users

- [ ] Register, login, logout, refresh, me endpoints
- [ ] JWT access + refresh token rotation
- [ ] Frontend auth guard on all dashboard routes

### 22.3 Projects & Modules

- [ ] Project CRUD with ownership enforcement
- [ ] 8 modules auto-created per project
- [ ] Module status reflects workflow/artifact state

### 22.4 Artifacts

- [ ] Typed artifacts per module (schemas in `ai/schemas/`)
- [ ] Version history with user edit support
- [ ] Artifact viewer and editor in UI

### 22.5 Workflows & AI

- [ ] LangGraph graph for each of 8 modules
- [ ] 8 domain agents implemented per Section 13
- [ ] Workflow trigger, progress, cancel API + UI
- [ ] Module dependency gates enforced
- [ ] Ollama Qwen 3 8B integration

### 22.6 RAG & Memory

- [ ] Embeddings via `BAAI/bge-base-en-v1.5`
- [ ] FAISS index per project
- [ ] Memory search API + UI panel
- [ ] Seed knowledge documents ingested

### 22.7 Export

- [ ] Investor pack export endpoint
- [ ] Export UI with download

### 22.8 Observability & Security

- [ ] Structured logging (request ID, user ID)
- [ ] Audit log for auth and workflow events
- [ ] Health + readiness endpoints

### 22.9 Testing

- [ ] Unit + integration test suite in CI
- [ ] Playwright E2E for critical path
- [ ] AI eval suite for all 8 agents

### 22.10 Documentation

- [ ] Product Spec complete (Sections 1–34)
- [ ] API & Database Reference complete (Document 3)
- [ ] This Implementation Guide kept current with as-built changes

---

## Appendix A — Quick Reference: Build Sequence Summary

For engineers asking "what do I do this week?":

| Week | Focus | Primary Sections |
|------|-------|------------------|
| 1–2 | Scaffold, CI, DB | 2, 4, 7 B1–B3, 9 |
| 3–4 | Auth | 7 B4–B7, 8 F1–F4, 10 |
| 5–6 | Projects + UI shell | 7 B8–B9, 8 F5–F7, 11 |
| 7–8 | Artifacts | 7 B10–B11, 8 F8–F10 |
| 9–10 | AI + RAG base | 15, 7 B15–B16 |
| 11–12 | LangGraph + Agent 1 | 12, 13 A1, 14 |
| 13–14 | Agents 2–4 | 13 A2–A4 |
| 15–16 | Agents 5–8, export, ship | 13 A5–A8, 16–18, 22 |

---

## Appendix B — Document Cross-Reference

| Topic | Product Spec | API Reference | This Guide |
|-------|--------------|---------------|------------|
| System architecture | §16 | — | §3, §5 |
| Frontend structure | §17 | — | §8 |
| Backend layers | §18 | — | §7 |
| AI / Ollama | §19 | — | §2.5, §13 |
| LangGraph | §20 | — | §12 |
| RAG | §21 | — | §15 |
| Memory | §22 | — | §15 |
| Database | §23 | §3–6 | §9 |
| API design | §24 | §7–16 | §11 |
| Auth | §25 | §8–9 | §10 |
| Security | §26 | — | §21.3 |
| Deployment | §30 | — | §17–18 |
| Modules | §12 | — | §9.2, §12.4 |
| Agents | §13 | — | §13 |

---

*End of Document 2 — Developer Implementation Guide*
