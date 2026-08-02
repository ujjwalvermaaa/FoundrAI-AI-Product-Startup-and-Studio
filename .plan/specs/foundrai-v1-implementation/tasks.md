# Implementation Plan: FoundrAI v1

## Overview

Complete implementation from scratch across 6 phases with 48 tasks. Each task builds incrementally on prior work to ensure stable, testable progress.

**Key Principles**:
- Start every task by reading requirements.md and design.md
- Never skip phases or tasks
- Complete acceptance criteria before moving forward
- Test at each checkpoint
- No shortcuts — production-quality code only

## Tasks

- [x] 1. Create project root structure
  - Create `foundrai/` root at `/Users/ujjwal/Desktop/foundrai/`
  - Create all folders from design.md Section 1
  - Create `.gitignore` with: node_modules, .env, data/faiss/*, __pycache__, .next, .venv, *.pyc
  - Create `.env.example` with all variables from design.md Section 7
  - _Requirements: 10, 11_

- [x] 2. Docker Compose setup for development
  - Create `docker-compose.yml` with postgres service
  - Create `docker-compose.prod.yml` with all services
  - Create `docker/Dockerfile.backend`
  - Create `docker/Dockerfile.frontend`
  - Create `docker/nginx.conf`
  - Test: `docker compose up postgres` starts successfully
  - _Requirements: 11_

- [x] 3. Create Makefile with dev targets
  - Targets: dev, db-up, migrate, test, lint, build, clean
  - Verify all targets run without errors
  - _Requirements: 10, 11_

- [x] 4. Initialize backend project with FastAPI
  - `cd backend && poetry init` with Python 3.12
  - Add dependencies: FastAPI, Uvicorn, SQLAlchemy, asyncpg, Alembic, Pydantic, python-jose, passlib, bcrypt, httpx
  - Create `app/main.py` with FastAPI app + health endpoint
  - Configure Uvicorn with reload
  - Test: `GET /health` returns 200
  - _Requirements: 10_

- [x] 5. Initialize Next.js 15 frontend
  - Create Next.js 15 app using `pnpm create next-app`
  - Configure: TypeScript, Tailwind CSS 4, App Router, src/ directory
  - Install: TanStack Query 5, Framer Motion 11, Zod 3
  - Initialize shadcn/ui with required components
  - Port design tokens from existing `Frontend/src/styles.css` → `globals.css`
  - Port existing UI components from existing Frontend directory
  - Test: `pnpm dev` starts, design tokens work
  - _Requirements: 9_

- [x] 6. CI pipeline setup
  - Create `.github/workflows/ci.yml`
  - Lint job: ruff (backend), eslint (frontend)
  - Type check: mypy (backend), tsc (frontend)
  - Test job: pytest (backend), vitest (frontend)
  - Runs on PR and main push
  - _Requirements: 10_

- [x] 7. Database configuration and connection
  - Create `backend/app/core/config.py` with pydantic-settings
  - Create `backend/app/database/base.py` (SQLAlchemy async engine)
  - Create `backend/app/database/session.py` (async session factory)
  - Integration test: verify DB connection
  - _Requirements: 1, 2_

- [x] 8. Alembic setup and initial migrations
  - Initialize Alembic: `alembic init alembic`
  - Configure `alembic/env.py` for async SQLAlchemy
  - Migration 001: UUID extensions (`pgcrypto` or `uuid-ossp`)
  - Migration 002: `users` + `refresh_tokens` tables
  - Migration 003: `projects` + `project_modules` tables
  - Run: `alembic upgrade head` and `alembic downgrade base`
  - Verify: all migrations apply and roll back cleanly
  - _Requirements: 1, 2, 3_

- [x] 9. User model, repository, and authentication service
  - Create `app/models/user.py` (SQLAlchemy model)
  - Create `app/models/refresh_token.py`
  - Create `app/repositories/user_repository.py`
  - Create `app/repositories/token_repository.py`
  - Create `app/auth/password.py` (bcrypt hash + verify)
  - Create `app/auth/jwt.py` (encode + decode + refresh)
  - Create `app/services/auth_service.py` (register, login, refresh, logout)
  - Create `app/api/deps.py` (get_current_user dependency)
  - Unit tests: password hash, JWT round-trip, repository CRUD
  - _Requirements: 1_

- [x] 10. Authentication API endpoints
  - Create `app/api/v1/auth.py`:
    - `POST /auth/register` → 201 with user + tokens
    - `POST /auth/login` → 200 with tokens
    - `POST /auth/refresh` → new access token
    - `POST /auth/logout` → 204
    - `GET /auth/me` → user profile
  - Implement all validation and error codes per API reference
  - Integration tests: full auth flow
  - _Requirements: 1_

- [x] 11. Project model, repository, and service
  - Create `app/models/project.py`
  - Create `app/models/project_module.py`
  - Create `app/repositories/project_repository.py`
  - Create `app/services/project_service.py`
  - Implement module seeding logic (8 modules on project create)
  - Unit tests for CRUD and module seeding
  - _Requirements: 2, 3_

- [x] 12. Projects and modules API endpoints
  - `POST /projects` → 201 with 8 seeded modules
  - `GET /projects` → paginated list
  - `GET /projects/{id}` → project with modules
  - `PATCH /projects/{id}` → update, re-index if brief changes
  - `DELETE /projects/{id}` → soft delete
  - `GET /projects/{id}/modules` → module list
  - `GET /projects/{id}/modules/{key}` → module detail with dependencies
  - Integration tests for all endpoints
  - _Requirements: 2, 3_

- [x] 13. Frontend authentication pages
  - Create `app/(auth)/layout.tsx` — auth layout
  - Create `app/(auth)/login/page.tsx` — login form (port from existing)
  - Create `app/(auth)/register/page.tsx` — register form
  - Create `lib/api-client.ts` — typed HTTP client with auth
  - Create `services/auth.service.ts` — auth API calls
  - Create `store/auth.store.ts` — auth state (Zustand)
  - Create `middleware.ts` — Next.js auth middleware
  - Test: login/register UI works, tokens stored, redirects work
  - _Requirements: 9_

- [x] 14. Frontend dashboard and projects UI
  - Create `app/(dashboard)/layout.tsx` — sidebar + topbar
  - Port `AppSidebar` from existing frontend (update routing)
  - Port `AppTopbar` from existing frontend
  - Create `app/(dashboard)/dashboard/page.tsx` — port existing dashboard
  - Create `app/(dashboard)/projects/page.tsx` — projects list
  - Create `app/(dashboard)/projects/new/page.tsx` — create project
  - Create `app/(dashboard)/projects/[id]/page.tsx` — project detail
  - Test: Dashboard and projects pages load with real API data
  - _Requirements: 9_

- [x] 15. Artifact database migrations and models
  - Migration 004: `artifacts`, `artifact_versions` tables
  - Migration 005: `workflow_runs`, `workflow_steps`, `agent_executions` tables
  - Migration 006: `memory_chunks`, `knowledge_documents` tables
  - Migration 007: `audit_logs` table
  - Migration 008: all indexes from API reference Section 6
  - Test: all migrations reversible
  - _Requirements: 4, 5, 7, 10_

- [x] 16. Artifact models, repository, and service
  - Create `app/models/artifact.py`
  - Create `app/models/artifact_version.py`
  - Create `app/repositories/artifact_repository.py`
  - Create `app/services/artifact_service.py` (upsert with versioning)
  - Unit tests: versioning increments correctly
  - _Requirements: 5_

- [x] 17. Artifact API endpoints
  - `GET /projects/{id}/artifacts` → paginated list
  - `GET /projects/{id}/artifacts/{aid}` → full artifact
  - `PATCH /projects/{id}/artifacts/{aid}` → user edit, new version
  - `GET /projects/{id}/artifacts/{aid}/versions` → version list
  - `GET /projects/{id}/artifacts/{aid}/versions/{vid}` → snapshot
  - Schema validation on PATCH
  - Integration tests
  - _Requirements: 5_

- [x] 18. Workflow models, repository, and service
  - Create `app/models/workflow_run.py`
  - Create `app/models/workflow_step.py`
  - Create `app/models/agent_execution.py`
  - Create `app/repositories/workflow_repository.py`
  - Create `app/services/workflow_service.py`: trigger, cancel, update_status, persist_artifact
  - Test: workflow state transitions work correctly
  - _Requirements: 4_

- [x] 19. Workflow API and SSE
  - `POST /projects/{id}/workflows/{module_key}/run` → 202
  - `GET /projects/{id}/workflows/runs` → paginated
  - `GET /projects/{id}/workflows/runs/{run_id}` → full detail with steps
  - `POST /projects/{id}/workflows/runs/{run_id}/cancel` → cancel
  - SSE endpoint: `GET /projects/{id}/workflows/runs/{run_id}/stream`
    - Events: step_started, step_completed, run_completed, run_failed
  - Integration tests
  - _Requirements: 4_

- [x] 20. Frontend module workspace
  - Create `app/(dashboard)/projects/[id]/modules/[module]/page.tsx`
  - Port module workspace from existing `_app.modules.$moduleId.tsx`
  - Module status card component
  - Workflow trigger button with dependency check display
  - Artifact viewer (JSON + markdown tabs)
  - Artifact editor modal
  - Version history panel
  - SSE progress indicator
  - Test: Module page loads, shows artifact, allows editing
  - _Requirements: 9_

- [x] 21. Ollama client and model factory
  - Create `ai/models/ollama.py` — HTTP client for Ollama
    - `chat()`, `generate()`, `list_models()`, `is_available()`
  - Create `ai/models/model_factory.py` — agent model resolution
  - Create `ai/config/models.yaml` — model configuration
  - Create `ai/config/agents.yaml` — per-agent model settings
  - Test: Ollama connection works, models.yaml drives config
  - _Requirements: 6_

- [x] 22. Embedding pipeline
  - Create `ai/rag/embeddings.py`
    - Load `BAAI/bge-base-en-v1.5`
    - `embed(texts)` → numpy array
    - Singleton pattern for model reuse
  - Create `ai/rag/chunking.py`
    - `chunk_text(text, size=800, overlap=150)`
    - Content-aware splitting (prefer sentence breaks)
  - Unit tests: chunks correct size, embeddings correct shape
  - _Requirements: 7_

- [x] 23. FAISS index management
  - Create `ai/rag/indexing.py`
    - `create_index(project_id)` → IndexFlatIP
    - `add_vectors(project_id, vectors, chunk_ids)`
    - `save_index(project_id)` → file
    - `load_index(project_id)` → from file
  - Create `ai/rag/retrieval.py`
    - `search(project_id, query, top_k=8)` → chunks
  - Integration test: index, save, load, search
  - _Requirements: 7_

- [x] 24. Memory manager
  - Create `ai/memory/memory_manager.py`
    - `index_artifact(project_id, artifact)` → chunk + embed + store
    - `index_brief(project_id, brief)` → same pipeline
    - `invalidate_artifact(project_id, artifact_id)` → remove old chunks
    - `search(project_id, query, top_k)` → ranked results
  - Create `ai/memory/artifact_memory.py` — artifact-specific logic
  - Integration test: index brief, search returns it
  - _Requirements: 7_

- [x] 25. Backend memory integration
  - Wire `MemoryManager` into `ArtifactService`: after create/update → `index_artifact()`
  - Wire into `ProjectService`: after create/update brief → `index_brief()`
  - Memory search endpoint: `POST /projects/{id}/memory/search`
  - Integration test: create project → search brief returns results
  - _Requirements: 7_

- [x] 26. Knowledge base setup
  - Create knowledge documents in `data/knowledge/`:
    - `startup/startup_playbook.md`
    - `finance/unit_economics.md`
    - `marketing/gtm_strategies.md`
    - `product/product_roadmap_guide.md`
    - `templates/validation_template.md`
  - Create `scripts/build_index.py` — seed knowledge → FAISS
  - Run: `python scripts/build_index.py`
  - _Requirements: 7_

- [x] 27. LangGraph state and base nodes
  - Create `ai/graphs/state.py` — `WorkflowState` TypedDict
    - Fields: project_id, module_key, run_id, inputs, retrieved_chunks, required_artifacts, current_draft, errors, steps_metadata, retry_count
  - Create `ai/graphs/nodes/context_loader.py` — load project + upstream artifacts
  - Create `ai/graphs/nodes/rag_node.py` — query memory, format context
  - Create `ai/runtime/prompt_builder.py` — load templates, fill placeholders
  - Test: state schema defined, nodes callable with mock state
  - _Requirements: 6_

- [x] 28. Generation, validation, and repair nodes
  - Create `ai/graphs/nodes/generation_node.py` — prompt → Ollama → parse JSON
  - Create `ai/graphs/nodes/validation_node.py` — Pydantic schema check
  - Create `ai/graphs/nodes/repair_node.py` — re-prompt with errors (max 2 retries)
  - Create `ai/graphs/nodes/reflection_node.py` — self-critique rubric
  - Create `ai/graphs/nodes/persist_node.py` — save artifact via callback
  - Unit tests with mock LLM responses
  - _Requirements: 6_

- [x] 29. Artifact Pydantic schemas
  - Create `ai/schemas/validation_report.py`
  - Create `ai/schemas/market_analysis.py`
  - Create `ai/schemas/business_model_canvas.py`
  - Create `ai/schemas/product_roadmap.py`
  - Create `ai/schemas/architecture_doc.py`
  - Create `ai/schemas/financial_model.py`
  - Create `ai/schemas/marketing_plan.py`
  - Create `ai/schemas/investor_deck_outline.py`
  - Unit tests: valid/invalid fixtures
  - _Requirements: 6_

- [x] 30. Agent 1 — Idea Validator
  - Create prompts in `ai/prompts/agents/idea_validator/`: system.v1.md, developer.v1.md, user.v1.md, repair.v1.md
  - Create `ai/agents/idea_validator/agent.py`
  - Create `ai/graphs/validation_graph.py`
  - Integration test: full pipeline with test idea_brief
  - Verify: `validation_report` produced with all required fields
  - _Requirements: 6_

- [x] 31. Agent 2 — Market Researcher
  - Create prompts: system, developer, user, repair
  - Create `ai/agents/market_researcher/agent.py`
  - Create `ai/graphs/market_research_graph.py`
  - Integration test with `validation_report` as input
  - Verify: `market_analysis` with 3+ competitors, TAM/SAM/SOM
  - _Requirements: 6_

- [x] 32. Agent 3 — Business Modeler
  - Create prompts + agent + graph
  - Create `ai/graphs/business_model_graph.py`
  - Integration test with validation + market inputs
  - Verify: all 9 canvas blocks populated
  - _Requirements: 6_

- [x] 33. Agent 4 — Product Strategist
  - Create prompts + agent + graph
  - Create `ai/graphs/product_strategy_graph.py`
  - Integration test with business model input
  - Verify: roadmap with ≥2 phases, ≥3 features each
  - _Requirements: 6_

- [x] 34. Agent 5 — Technical Architect
  - Create prompts + agent + graph
  - Create `ai/graphs/architecture_graph.py`
  - Integration test with product roadmap input
  - Verify: architecture doc with component diagram, stack, security section
  - _Requirements: 6_

- [x] 35. Agent 6 — Financial Analyst
  - Create prompts + agent + graph
  - Create `ai/graphs/financial_graph.py`
  - Integration test with business model + product roadmap inputs
  - Verify: 12-month projection, ≥5 assumptions
  - _Requirements: 6_

- [x] 36. Agent 7 — Marketing Strategist
  - Create prompts + agent + graph
  - Create `ai/graphs/marketing_graph.py`
  - Integration test
  - Verify: ≥3 channels, launch checklist ≥5 items
  - _Requirements: 6_

- [x] 37. Agent 8 — Investor Writer
  - Create prompts + agent + graph
  - Create `ai/graphs/investor_graph.py` (uses all prior artifacts)
  - Integration test with all upstream artifacts
  - Verify: ≥10 slides outlined, includes problem/market/product/ask
  - _Requirements: 6_

- [x] 38. Graph factory and workflow wire-up
  - Create `ai/graphs/graph_factory.py`: `get_graph(module_key)` → correct LangGraph
  - Wire `WorkflowService.execute()` → `GraphFactory.run()`
  - Background task execution with DB persistence callbacks
  - SSE event emission at each step
  - Integration test: full workflow end-to-end
  - Verify: all 8 modules run end-to-end via API trigger
  - _Requirements: 4, 6_

- [x] 39. Guardrails
  - Create `ai/guardrails/prompt_injection.py` — detect/neutralize injection attempts
  - Create `ai/guardrails/schema_validation.py` — domain-level checks
  - Create `ai/guardrails/output_validation.py` — post-generation quality checks
  - Test: injection attempts rejected, invalid outputs caught
  - _Requirements: 6_

- [x] 40. Frontend workflow UI
  - Workflow trigger button with loading state
  - SSE-based progress bar component
  - Step timeline display (step_started, step_completed)
  - Error display on failure
  - Re-run button after failure
  - Module dependency visualization (locked state with reason)
  - Test: user can trigger workflow, see live progress, view result
  - _Requirements: 9_

- [x] 41. Export service
  - Create `backend/app/exporters/investor_pack.py`
    - Collect all artifacts for project
    - Render as structured markdown
    - Save to `data/exports/`
  - `POST /projects/{id}/export/investor-pack` endpoint
  - Frontend export button + download link
  - Integration test
  - Verify: export generates complete markdown investor pack
  - _Requirements: 8_

- [x] 42. Audit logs and error handling
  - Create `app/models/audit_log.py`
  - Middleware for logging: project.create, workflow.trigger, export
  - Global exception handlers per API reference Section 15
  - Consistent error JSON format
  - Test: audit events logged, errors return correct codes/shapes
  - _Requirements: 10_

- [x] 43. Health and readiness endpoints
  - `GET /health` — liveness (always 200 if running)
  - `GET /health/ready` — checks:
    - PostgreSQL connection
    - Ollama responds + qwen3:8b listed
    - FAISS directory writable
  - Return correct 503 on failure
  - Test: readiness detects missing Ollama, returns 503
  - _Requirements: 10_

- [x] 44. Backend unit and integration tests
  - Unit tests: auth, password, JWT, repos, services
  - Integration tests: all API endpoints
  - AI unit tests: chunking, embedding shape, schema validation
  - Test fixtures and factories
  - Verify: ≥70% coverage target
  - _Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 10_

- [x] 45. Frontend polish
  - Error boundaries on all pages
  - Toast notifications (sonner) for success/error
  - Loading skeletons for all async data
  - Empty states (no projects, no artifacts)
  - Responsive layout for mobile
  - Dark mode toggle
  - Test: no unhandled errors visible, responsive design works
  - _Requirements: 9_

- [x] 46. Docker production setup
  - `Dockerfile.backend` — multi-stage, minimal image
  - `Dockerfile.frontend` — multi-stage Next.js
  - `docker-compose.prod.yml` — all services with env files
  - `docker/nginx.conf` — reverse proxy
  - `scripts/setup.sh` — one-command setup script
  - Test: `docker compose -f docker-compose.prod.yml up`
  - Verify: full stack starts from docker compose, accessible via nginx
  - _Requirements: 11_

- [x] 47. Documentation
  - `README.md` — project overview, quick start, architecture
  - `docs/SETUP.md` — Ollama install guide, step-by-step local setup
  - `.env.example` — all vars with descriptions
  - `AGENTS.md` — agent descriptions and capabilities
  - API documentation via FastAPI OpenAPI (auto-generated)
  - Verify: new developer can set up project following README in <30 min
  - _Requirements: 11_

- [x] 48. Evaluation suite
  - Create `ai/evaluation/` with test fixtures per agent
  - Eval runner: compare outputs against golden fixtures
  - Schema validation rate metric
  - `scripts/run_evals.py`
  - Test: eval suite runs, reports schema-valid percentage
  - _Requirements: 6_

## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "tasks": [1, 2, 3, 5, 6],
      "description": "Foundation: Project structure, Docker, Makefile, Frontend init, CI"
    },
    {
      "wave": 2,
      "tasks": [4, 7],
      "description": "Backend init and DB configuration"
    },
    {
      "wave": 3,
      "tasks": [8],
      "description": "Alembic setup and initial migrations (users, projects)"
    },
    {
      "wave": 4,
      "tasks": [9, 21],
      "description": "User model + auth service; Ollama client (parallelizable)"
    },
    {
      "wave": 5,
      "tasks": [10, 22],
      "description": "Auth API endpoints; Embedding pipeline"
    },
    {
      "wave": 6,
      "tasks": [11, 13, 23],
      "description": "Project model + service; Frontend auth pages; FAISS index"
    },
    {
      "wave": 7,
      "tasks": [12, 14, 24],
      "description": "Projects + modules API; Frontend dashboard; Memory manager"
    },
    {
      "wave": 8,
      "tasks": [15, 25, 26],
      "description": "Artifact migrations; Backend memory integration; Knowledge base"
    },
    {
      "wave": 9,
      "tasks": [16, 27],
      "description": "Artifact models + service; LangGraph state + base nodes"
    },
    {
      "wave": 10,
      "tasks": [17, 28],
      "description": "Artifact API; Generation + validation nodes"
    },
    {
      "wave": 11,
      "tasks": [18, 29],
      "description": "Workflow models + service; Artifact Pydantic schemas"
    },
    {
      "wave": 12,
      "tasks": [19, 30],
      "description": "Workflow API + SSE; Agent 1 (Idea Validator)"
    },
    {
      "wave": 13,
      "tasks": [20, 31],
      "description": "Frontend module workspace; Agent 2 (Market Researcher)"
    },
    {
      "wave": 14,
      "tasks": [32],
      "description": "Agent 3 (Business Modeler)"
    },
    {
      "wave": 15,
      "tasks": [33],
      "description": "Agent 4 (Product Strategist)"
    },
    {
      "wave": 16,
      "tasks": [34, 35],
      "description": "Agent 5 (Technical Architect); Agent 6 (Financial Analyst)"
    },
    {
      "wave": 17,
      "tasks": [36, 37],
      "description": "Agent 7 (Marketing Strategist); Agent 8 (Investor Writer)"
    },
    {
      "wave": 18,
      "tasks": [38],
      "description": "Graph factory and full workflow wire-up"
    },
    {
      "wave": 19,
      "tasks": [39, 40, 41, 42, 43, 48],
      "description": "Guardrails, Frontend workflow UI, Export, Audit logs, Health endpoints, Eval suite"
    },
    {
      "wave": 20,
      "tasks": [44, 45],
      "description": "Backend tests + Frontend polish"
    },
    {
      "wave": 21,
      "tasks": [46, 47],
      "description": "Docker production setup + Documentation"
    }
  ],
  "dependencies": {
    "2": [1], "3": [1], "4": [2], "5": [1], "6": [1],
    "7": [4], "8": [7],
    "9": [8], "10": [9],
    "11": [10], "12": [11],
    "13": [10], "14": [13],
    "15": [8], "16": [15], "17": [16],
    "18": [15], "19": [18],
    "20": [17, 19],
    "21": [4], "22": [21], "23": [22], "24": [23],
    "25": [24], "26": [24],
    "27": [21], "28": [27], "29": [28],
    "30": [29], "31": [30], "32": [31], "33": [32],
    "34": [33], "35": [33], "36": [35], "37": [36],
    "38": [37], "39": [38],
    "40": [38], "41": [38], "42": [10], "43": [21],
    "44": [38], "45": [40],
    "46": [2], "47": [46], "48": [38]
  }
}
```

## Notes

**Implementation Rules**:
1. Always test before proceeding — each task has acceptance criteria
2. No shortcuts or mock implementations in production code
3. Preserve UI designs when porting frontend from existing TanStack Start app
4. Ask if documentation is ambiguous rather than guessing
5. Update `progress.json` after each task completion (optional tracking)

**Testing Checkpoints**:
- After Task 10: Full auth flow works
- After Task 12: Project CRUD works
- After Task 19: Workflow trigger returns 202
- After Task 38: All 8 modules runnable end-to-end
- After Task 46: Docker stack boots successfully

**Key Milestones**:
- **M1 (Tasks 1-6)**: Foundation complete, CI green
- **M2 (Tasks 7-14)**: Auth + Projects functional
- **M3 (Tasks 15-20)**: Artifacts + Module UI complete
- **M4 (Tasks 21-26)**: AI infrastructure ready
- **M5 (Tasks 27-40)**: All agents + workflows implemented
- **M6 (Tasks 41-48)**: Hardening + ship

---

**Document Status**: Complete — All 48 tasks done  
**Last Updated**: 2025-07-31
