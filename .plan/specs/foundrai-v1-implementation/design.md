# Design Document

## Overview

FoundrAI is an AI-powered SaaS platform that transforms startup ideas into validated business plans through a structured, multi-agent AI workflow system. The platform operates as a project workspace where domain-specific AI agents generate schema-validated, versioned artifacts using retrieval-augmented generation (RAG) over persistent project memory.

**Core Architectural Principles:**
- **Artifact-centric, not session-centric**: All AI outputs are persisted as typed JSON artifacts with versioning
- **Multi-agent orchestration**: 8 specialized domain agents (idea validation, market research, business model, product strategy, architecture, finance, marketing, investor documentation) coordinate via LangGraph workflows
- **RAG-grounded reasoning**: All agent generations retrieve relevant context from FAISS-indexed project memory before invoking the LLM
- **Persistent project memory**: Every artifact and the idea brief is chunked, embedded, and indexed for future retrieval
- **Explicit dependency gates**: Modules unlock sequentially based on artifact availability

**Technology Foundation:**
- Backend: FastAPI (async, SQLAlchemy ORM) + PostgreSQL + JWT auth
- Frontend: Next.js 15 App Router + React 19 + TanStack Query + shadcn/ui
- AI: LangGraph + LangChain + Ollama (Qwen 3 8B) + Sentence Transformers (BAAI/bge-base-en-v1.5) + FAISS (per-project indexes)
- Deployment: Docker + Docker Compose v2

## Architecture

### High-Level System Architecture

```mermaid
flowchart TB
    subgraph Frontend["Next.js 15 Frontend"]
        UI[Next.js App Router]
        RQ[TanStack Query]
        SSE[SSE Client]
    end
    
    subgraph Backend["FastAPI Backend"]
        API[API Routers]
        SVC[Services Layer]
        REPO[Repositories]
        DB[(PostgreSQL)]
    end
    
    subgraph AI["AI Runtime (In-Process)"]
        LG[LangGraph Orchestrator]
        AGENTS[8 Domain Agents]
        RAG[RAG Pipeline]
        FAISS[(Project FAISS Indexes)]
    end
    
    OLLAMA[Ollama + Qwen3:8B]
    
    UI --> API
    API --> SVC
    SVC --> REPO
    REPO --> DB
    SVC --> LG
    LG --> AGENTS
    AGENTS --> RAG
    RAG --> FAISS
    AGENTS --> OLLAMA
    SSE -.-> SVC
```

### Layer Architecture

**Presentation → Business → Data → AI**

1. **API Layer** (FastAPI routers): HTTP request validation, authentication, response serialization
2. **Service Layer**: Business logic, workflow orchestration, transaction boundaries
3. **Repository Layer**: Database access via SQLAlchemy ORM
4. **AI Runtime Layer**: LangGraph execution, agent invocation, RAG retrieval, memory indexing

**Key Principle**: AI agents never write to the database directly. All persistence flows through service layer callbacks.

### Database Entity Relationship

```mermaid
erDiagram
    users ||--o{ projects : owns
    users ||--o{ refresh_tokens : has
    users ||--o{ workflow_runs : triggers
    
    projects ||--|{ project_modules : contains
    projects ||--o{ artifacts : has
    projects ||--o{ workflow_runs : executes
    projects ||--o{ memory_chunks : indexes
    
    artifacts ||--o{ artifact_versions : versions
    
    workflow_runs ||--o{ workflow_steps : steps
    workflow_runs ||--o{ agent_executions : invokes
    workflow_runs }o--|| project_modules : last_run
    
    knowledge_documents ||--o{ memory_chunks : sources
```

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant DB as PostgreSQL
    
    U->>F: Login (email, password)
    F->>API: POST /auth/login
    API->>DB: Verify credentials
    DB-->>API: User record
    API->>API: Generate JWT tokens
    API-->>F: Access token (15min) + Refresh token (7d)
    F->>F: Store tokens
    F->>API: Protected request + Bearer token
    API->>API: Validate JWT
    API->>API: Check project ownership
    API-->>F: Protected resource
    
    Note over F,API: Before access token expires
    F->>API: POST /auth/refresh
    API->>DB: Verify refresh token
    API->>API: Rotate refresh token
    API-->>F: New access token + rotated refresh token
```

### Workflow Execution Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as Backend
    participant LG as LangGraph
    participant AG as Agent
    participant OL as Ollama
    participant FAISS as FAISS Index
    participant DB as PostgreSQL
    
    U->>UI: Trigger workflow
    UI->>API: POST /workflows/{module}/run
    API->>DB: Check dependencies
    API->>DB: Create workflow_run (status: pending)
    API-->>UI: 202 + run_id + SSE stream_url
    
    API->>LG: Execute graph async
    LG->>DB: Load project + artifacts
    LG->>FAISS: RAG retrieve (top-k=8)
    FAISS-->>LG: Retrieved chunks
    LG->>AG: Generation node (context + prompt)
    AG->>OL: LLM invoke
    OL-->>AG: JSON response
    AG->>AG: Schema validation
    alt Validation passes
        LG->>DB: Persist artifact + version
        LG->>FAISS: Index new artifact chunks
        LG->>DB: Update module status: completed
        LG->>DB: Update workflow_run: completed
    else Validation fails
        LG->>AG: Repair node (max 2 retries)
        AG->>OL: Retry with errors
    end
    
    loop For each step
        LG->>API: SSE event (step_started/completed)
        API-->>UI: Stream event
        UI->>UI: Update progress UI
    end
```

## Components and Interfaces

### Backend Components

#### API Layer (`backend/app/api/v1/`)
- **auth.py**: Authentication endpoints (register, login, refresh, logout, me)
- **projects.py**: Project CRUD endpoints
- **modules.py**: Module status and dependency checks
- **workflows.py**: Workflow trigger, status, cancel, SSE stream
- **artifacts.py**: Artifact list, get, update, version history
- **memory.py**: Memory search (semantic retrieval)
- **export.py**: Investor pack generation
- **health.py**: Liveness and readiness probes

#### Service Layer (`backend/app/services/`)
- **AuthService**: User registration, login, token refresh, logout
- **ProjectService**: Project CRUD, module seeding, idea brief indexing
- **WorkflowService**: Workflow trigger, orchestration, status management, SSE emission
- **ArtifactService**: Artifact upsert, versioning, memory re-indexing
- **MemoryService**: Memory search, chunk management

#### Repository Layer (`backend/app/repositories/`)
- **UserRepository**: User CRUD
- **TokenRepository**: Refresh token management
- **ProjectRepository**: Project CRUD
- **ModuleRepository**: Module status updates
- **ArtifactRepository**: Artifact and version CRUD
- **WorkflowRepository**: Workflow run, step, execution records
- **MemoryRepository**: Memory chunk queries

### AI Components

#### LangGraph Orchestrator (`ai/graphs/`)
- **State Management**: `WorkflowState` TypedDict with project_id, module_key, run_id, inputs, retrieved_chunks, current_draft, errors
- **Standard Pipeline Nodes**:
  - `load_context_node`: Fetch project, upstream artifacts from DB
  - `rag_retrieve_node`: Query FAISS, return top-k chunks
  - `generation_node`: Assemble prompt, invoke Ollama, parse JSON
  - `validation_node`: Pydantic schema check
  - `repair_node`: Re-prompt with validation errors (max 2 retries)
  - `reflection_node`: Self-critique for quality
  - `persist_node`: Save artifact via service callback
  - `memory_index_node`: Chunk, embed, store in FAISS

- **Module-Specific Graphs** (one per module):
  - `validation_graph.py`
  - `market_research_graph.py`
  - `business_model_graph.py`
  - `product_strategy_graph.py`
  - `architecture_graph.py`
  - `financial_graph.py`
  - `marketing_graph.py`
  - `investor_graph.py`

#### Domain Agents (`ai/agents/`)
Each agent directory contains:
- `agent.py`: LangChain runnable or node function
- `schema.py`: Pydantic output model
- `tools.py`: Optional tools (memory_search, calculator)

**8 Domain Agents**:
1. **idea_validator**: Produces `validation_report` (problem, solution, risks, score)
2. **market_researcher**: Produces `market_analysis` (TAM/SAM/SOM, competitors, trends)
3. **business_modeler**: Produces `business_model_canvas` (9 canvas blocks)
4. **product_strategist**: Produces `product_roadmap` (phases, features)
5. **technical_architect**: Produces `architecture_doc` (components, stack)
6. **financial_analyst**: Produces `financial_model` (12-month projection)
7. **marketing_strategist**: Produces `marketing_plan` (channels, launch plan)
8. **investor_writer**: Produces `investor_deck_outline` (slide deck)

#### RAG Pipeline (`ai/rag/`)
- **chunking.py**: Text chunking (size=800, overlap=150)
- **embeddings.py**: Sentence Transformers model loading, embedding generation
- **indexing.py**: FAISS index creation, vector addition, persistence
- **retrieval.py**: Semantic search, top-k retrieval

#### Memory Management (`ai/memory/`)
- **memory_manager.py**: Orchestrates chunking, embedding, indexing lifecycle
- **artifact_memory.py**: Artifact-specific indexing logic
- **project_memory.py**: Project brief and cross-artifact memory

### Frontend Components

#### App Router Structure (`apps/web/src/app/`)
- `(auth)/`: Public auth pages (login, register)
- `(dashboard)/`: Protected pages with sidebar layout
  - `dashboard/`: Overview page with stats
  - `projects/`: Project list and create modal
  - `projects/[id]/`: Project detail with module cards
  - `projects/[id]/modules/[module]/`: Module workspace

#### UI Components (`apps/web/src/components/`)
- **ui/**: shadcn/ui primitives (button, card, dialog, etc.)
- **layout/**: AppSidebar, AppTopbar
- **forms/**: Auth forms, project forms
- **projects/**: Project cards, modals
- **modules/**: Module status cards, workflow triggers, artifact viewers
- **ai/**: Workflow progress indicators, SSE listeners

#### State Management
- **Server State**: TanStack Query for all API data
- **Client State**: Zustand for auth, UI preferences
- **SSE State**: EventSource for real-time workflow updates

## Data Models

### Database Tables

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

#### projects
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| name | VARCHAR(255) | NOT NULL |
| tagline | VARCHAR(500) | NULL |
| idea_brief | TEXT | NOT NULL |
| industry | VARCHAR(100) | NULL |
| stage | VARCHAR(50) | DEFAULT 'draft' |
| deleted_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

#### project_modules
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| project_id | UUID | FK → projects.id |
| module_key | VARCHAR(64) | NOT NULL |
| display_name | VARCHAR(128) | NOT NULL |
| status | VARCHAR(32) | DEFAULT 'locked' |
| sort_order | SMALLINT | NOT NULL |
| last_run_id | UUID | FK → workflow_runs.id |
| completed_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**UNIQUE**: (project_id, module_key)

**Module Keys**: idea_validation, market_research, business_model, product_strategy, technical_architecture, financial_planning, marketing_strategy, investor_documentation

**Module Status**: locked → available → in_progress → completed | failed

#### artifacts
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| project_id | UUID | FK → projects.id |
| module_key | VARCHAR(64) | NOT NULL |
| artifact_type | VARCHAR(64) | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| content_json | JSONB | NOT NULL |
| content_markdown | TEXT | NULL |
| source | VARCHAR(32) | DEFAULT 'ai' |
| current_version_id | UUID | FK → artifact_versions.id |
| workflow_run_id | UUID | FK → workflow_runs.id |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**UNIQUE**: (project_id, artifact_type)

**Artifact Types**: validation_report, market_analysis, business_model_canvas, product_roadmap, architecture_doc, financial_model, marketing_plan, investor_deck_outline

#### artifact_versions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| artifact_id | UUID | FK → artifacts.id |
| version_number | INTEGER | NOT NULL |
| content_json | JSONB | NOT NULL |
| content_markdown | TEXT | NULL |
| change_summary | VARCHAR(500) | NULL |
| created_by | VARCHAR(32) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

**UNIQUE**: (artifact_id, version_number)

#### workflow_runs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| project_id | UUID | FK → projects.id |
| module_key | VARCHAR(64) | NOT NULL |
| status | VARCHAR(32) | DEFAULT 'pending' |
| triggered_by | UUID | FK → users.id |
| input_snapshot | JSONB | NOT NULL |
| error_code | VARCHAR(64) | NULL |
| error_message | TEXT | NULL |
| started_at | TIMESTAMPTZ | NULL |
| completed_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

**Status**: pending → running → completed | failed | cancelled

#### workflow_steps
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workflow_run_id | UUID | FK → workflow_runs.id |
| step_key | VARCHAR(64) | NOT NULL |
| status | VARCHAR(32) | NOT NULL |
| sequence | SMALLINT | NOT NULL |
| started_at | TIMESTAMPTZ | NULL |
| completed_at | TIMESTAMPTZ | NULL |
| metadata_json | JSONB | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

#### agent_executions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workflow_run_id | UUID | FK → workflow_runs.id |
| workflow_step_id | UUID | FK → workflow_steps.id |
| agent_id | VARCHAR(64) | NOT NULL |
| model_name | VARCHAR(128) | NOT NULL |
| status | VARCHAR(32) | NOT NULL |
| prompt_tokens | INTEGER | NULL |
| completion_tokens | INTEGER | NULL |
| latency_ms | INTEGER | NULL |
| raw_output | TEXT | NULL |
| parsed_output_json | JSONB | NULL |
| error_message | TEXT | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

#### memory_chunks
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| project_id | UUID | FK → projects.id |
| source_type | VARCHAR(32) | NOT NULL |
| source_id | UUID | NULL |
| module_key | VARCHAR(64) | NULL |
| chunk_index | INTEGER | NOT NULL |
| content_text | TEXT | NOT NULL |
| content_hash | VARCHAR(64) | NOT NULL |
| embedding_model | VARCHAR(128) | NOT NULL |
| faiss_vector_id | BIGINT | NOT NULL |
| metadata_json | JSONB | NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Source Types**: artifact, project_field, knowledge

### Artifact JSON Schemas

Each artifact type has a Pydantic schema in `ai/schemas/`. Key fields:

**validation_report**: problem, solution, target_customer, risks[], validation_score (0-100), recommendations[], summary

**market_analysis**: tam, sam, som, segments[], competitors[] (≥3), trends[], summary

**business_model_canvas**: value_proposition, customer_segments, channels, customer_relationships, revenue_streams, key_resources, key_activities, key_partnerships, cost_structure

**product_roadmap**: phases[] (≥2), features[] (≥3 per phase), metrics, assumptions

**architecture_doc**: components, stack_recommendations, data_flows, security_considerations, scalability_notes

**financial_model**: revenue_drivers, cost_buckets, projection_12_months[], assumptions[] (≥5), unit_economics

**marketing_plan**: icp, messaging, channels[] (≥3), launch_checklist[] (≥5), calendar

**investor_deck_outline**: slides[] (≥10), narrative_flow, key_metrics

## Error Handling

### Error Response Format

All API errors return consistent JSON:

```json
{
  "error": {
    "code": "SCREAMING_SNAKE_CASE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Resource created |
| 202 | Async operation accepted |
| 204 | Success with no content |
| 400 | Bad request (client validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 409 | Conflict (dependency not met, duplicate, workflow already running) |
| 422 | Unprocessable entity (schema validation failed) |
| 500 | Internal server error |
| 503 | Service unavailable (dependency down) |

### Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| EMAIL_ALREADY_EXISTS | 409 | Registration with existing email |
| INVALID_CREDENTIALS | 401 | Login failed |
| INVALID_REFRESH_TOKEN | 401 | Refresh token invalid/expired |
| PROJECT_NOT_FOUND | 404 | Project doesn't exist or not owned |
| MODULE_NOT_FOUND | 404 | Invalid module_key |
| MODULE_DEPENDENCY_NOT_MET | 409 | Upstream artifacts missing |
| WORKFLOW_ALREADY_RUNNING | 409 | Module has active workflow |
| SCHEMA_VALIDATION_FAILED | 422 | Artifact edit invalid |
| INSUFFICIENT_ARTIFACTS | 409 | Export requires minimum artifacts |
| OLLAMA_UNAVAILABLE | 503 | LLM service down |
| VALIDATION_ERROR | 400/422 | Generic validation failure |

### AI Workflow Failure Handling

**Retry Ladder**:
1. **LLM Timeout**: Retry once with same context
2. **Invalid JSON**: Repair node with validation errors (max 2 attempts)
3. **Schema Validation Failed**: Repair node → reflection node → fail if still invalid
4. **Context Length Exceeded**: Trim retrieved chunks by 50%, retry once
5. **Ollama Unavailable**: Fail immediately, return 503 on workflow trigger

All failures:
- Set workflow_run status to `failed`
- Set module status to `failed`
- Record error_code and error_message
- Log agent_execution with status `failed`

## Testing Strategy

### Backend Testing

**Unit Tests** (pytest):
- Password hashing round-trip
- JWT encode/decode
- Repository CRUD operations
- Service business logic (module dependency checks, artifact versioning)
- Prompt rendering (PromptBuilder)

**Integration Tests** (pytest + httpx):
- Full auth flow (register → login → refresh → logout)
- Project CRUD via API
- Workflow trigger and status transitions
- Artifact versioning
- Memory search

**AI Tests**:
- Embedding generation (shape, determinism)
- FAISS index persistence and retrieval
- Schema validation fixtures per artifact type
- Agent output format (mock LLM)

**Coverage Target**: ≥70%

### Frontend Testing

**Unit Tests** (vitest):
- Component rendering
- Form validation (Zod schemas)
- API client utility functions
- State management (Zustand stores)

**E2E Tests** (Playwright):
- Auth flow (register → login → token refresh)
- Project creation → module navigation
- Workflow trigger → progress display
- Artifact viewing and editing

### AI Evaluation

**Per-Agent Eval Fixtures** (`ai/evaluation/`):
- 3+ test cases per agent (happy path, edge case, adversarial)
- Schema validation rate metric (target: ≥85% before repair)
- Faithfulness to retrieved context (LLM judge, target: ≥4/5)
- Eval runner: `scripts/run_evals.py`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

FoundrAI's core logic involves data transformations (chunking, embedding, JSON schema validation) and state transitions (module status, workflow runs, artifact versioning) that are well-suited for property-based testing.

### Property 1: Artifact versioning monotonicity

*For any* artifact that receives N updates, the version_number of each successive version SHALL be exactly one greater than the previous, and the total number of versions SHALL equal N+1 (original AI generation plus N edits).

**Validates: Requirements 5.1, 5.2**

### Property 2: Module dependency gate enforcement

*For any* project and module combination where required upstream artifacts are missing, triggering a workflow SHALL consistently return a MODULE_DEPENDENCY_NOT_MET error — regardless of the order or timing of trigger attempts.

**Validates: Requirements 3.1, 3.4**

### Property 3: Artifact schema validation consistency

*For any* JSON object that passes the Pydantic schema for an artifact_type, attempting to persist it SHALL succeed; *for any* JSON object that fails the schema, attempting to persist it SHALL return SCHEMA_VALIDATION_FAILED — and this SHALL hold for all valid inputs to those schemas.

**Validates: Requirements 5.5, 6.3**

### Property 4: Memory indexing round-trip

*For any* non-empty text string indexed via the memory manager, a semantic search with that exact text as query SHALL return a result with score > 0 in the top-k results for that project.

**Validates: Requirements 7.3, 7.4**

### Property 5: Text chunking coverage

*For any* input text of length L, the set of all chunks produced by `chunk_text()` SHALL cover every character in the original text (no content is dropped), and each chunk SHALL be at most `chunk_size` characters long.

**Validates: Requirements 7.2**

### Property 6: Project ownership isolation

*For any* two distinct user accounts U1 and U2 and a project owned by U1, all API requests by U2 to that project's resources SHALL return 404 — regardless of the request type or resource path.

**Validates: Requirements 2.8**

### Property 7: Soft delete visibility

*For any* project that has been soft-deleted, all subsequent GET requests for that project by the same owner SHALL return 404 — indistinguishable from a project that never existed.

**Validates: Requirements 2.7, 2.8**



```
foundrai/                               ← New clean root (Desktop/foundrai)
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── mission.json
├── progress.json
│
├── docs/
│   ├── 01-foundrai-product-software-specification.md
│   ├── 02-developer-implementation-guide.md
│   ├── 03-api-database-reference.md
│   └── 04-ai-system-design-specification.md
│
├── frontend/                           ← Next.js 15 App Router
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   ├── register/page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── projects/page.tsx
│   │   │   │   ├── projects/new/page.tsx
│   │   │   │   ├── projects/[id]/page.tsx
│   │   │   │   ├── projects/[id]/modules/[module]/page.tsx
│   │   │   │   ├── settings/page.tsx
│   │   │   │   ├── profile/page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── api/
│   │   │   │   └── health/route.ts
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/         ← shadcn/ui components
│   │   │   ├── layout/     ← AppSidebar, AppTopbar
│   │   │   ├── forms/      ← Auth forms, Project forms
│   │   │   ├── dashboard/  ← Dashboard-specific components
│   │   │   ├── projects/   ← Project cards, modals
│   │   │   ├── modules/    ← Module workspace, status cards
│   │   │   ├── ai/         ← Workflow progress, artifacts
│   │   │   ├── charts/     ← Recharts wrappers
│   │   │   └── common/     ← Shared utility components
│   │   ├── hooks/          ← Custom React hooks
│   │   ├── lib/            ← Utils, constants, API client
│   │   ├── services/       ← API service layer
│   │   ├── store/          ← Zustand stores (auth, etc.)
│   │   ├── types/          ← TypeScript type definitions
│   │   └── middleware.ts   ← Next.js auth middleware
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── components.json     ← shadcn config
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   ├── router.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── projects.py
│   │   │       ├── modules.py
│   │   │       ├── workflows.py
│   │   │       ├── artifacts.py
│   │   │       ├── memory.py
│   │   │       ├── export.py
│   │   │       ├── health.py
│   │   │       └── admin.py
│   │   ├── core/
│   │   │   ├── config.py       ← Settings via pydantic-settings
│   │   │   ├── logging.py      ← Structured JSON logging
│   │   │   ├── security.py     ← JWT utilities
│   │   │   ├── constants.py    ← App constants
│   │   │   └── exceptions.py   ← Custom exceptions
│   │   ├── auth/
│   │   │   ├── jwt.py
│   │   │   ├── password.py
│   │   │   └── permissions.py
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   ├── migrations/
│   │   │   └── seed.py
│   │   ├── models/             ← SQLAlchemy ORM models
│   │   ├── schemas/            ← Pydantic request/response models
│   │   ├── repositories/       ← Data access layer
│   │   ├── services/           ← Business logic layer
│   │   ├── middleware/
│   │   ├── dependencies/
│   │   ├── events/
│   │   ├── websocket/
│   │   ├── background/
│   │   ├── exporters/
│   │   ├── validators/
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   └── pyproject.toml
│
├── ai/
│   ├── agents/
│   │   ├── base/           ← BaseAgent class
│   │   ├── idea_validator/
│   │   │   ├── agent.py
│   │   │   ├── schema.py
│   │   │   └── tools.py
│   │   ├── market_researcher/
│   │   ├── business_modeler/
│   │   ├── product_strategist/
│   │   ├── technical_architect/
│   │   ├── financial_analyst/
│   │   ├── marketing_strategist/
│   │   ├── investor_writer/
│   │   ├── manager/
│   │   └── registry.py     ← AgentRegistry
│   ├── graphs/
│   │   ├── state.py        ← WorkflowState TypedDict
│   │   ├── nodes/          ← All LangGraph nodes
│   │   │   ├── context_loader.py
│   │   │   ├── rag_node.py
│   │   │   ├── generation_node.py
│   │   │   ├── validation_node.py
│   │   │   ├── repair_node.py
│   │   │   ├── reflection_node.py
│   │   │   ├── persist_node.py
│   │   │   └── memory_node.py
│   │   ├── validation_graph.py
│   │   ├── market_research_graph.py
│   │   ├── business_model_graph.py
│   │   ├── product_strategy_graph.py
│   │   ├── architecture_graph.py
│   │   ├── financial_graph.py
│   │   ├── marketing_graph.py
│   │   ├── investor_graph.py
│   │   └── graph_factory.py
│   ├── prompts/
│   │   ├── agents/
│   │   │   ├── idea_validator/
│   │   │   │   ├── system.v1.md
│   │   │   │   ├── developer.v1.md
│   │   │   │   ├── user.v1.md
│   │   │   │   ├── repair.v1.md
│   │   │   │   └── reflection.v1.md
│   │   │   └── ...  (same for each agent)
│   │   └── CHANGELOG.md
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── indexing.py
│   │   ├── retrieval.py
│   │   ├── reranker.py
│   │   └── pipeline.py
│   ├── memory/
│   │   ├── project_memory.py
│   │   ├── artifact_memory.py
│   │   ├── memory_manager.py
│   │   └── summarizer.py
│   ├── models/
│   │   ├── ollama.py       ← Ollama HTTP client
│   │   ├── model_factory.py
│   │   └── settings.py
│   ├── schemas/            ← Artifact output schemas
│   │   ├── validation_report.py
│   │   ├── market_analysis.py
│   │   ├── business_model_canvas.py
│   │   ├── product_roadmap.py
│   │   ├── architecture_doc.py
│   │   ├── financial_model.py
│   │   ├── marketing_plan.py
│   │   └── investor_deck_outline.py
│   ├── guardrails/
│   │   ├── prompt_injection.py
│   │   ├── schema_validation.py
│   │   └── output_validation.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── evaluator.py
│   │   └── benchmarks/
│   ├── config/
│   │   ├── agents.yaml
│   │   ├── models.yaml
│   │   └── graphs.yaml
│   ├── runtime/
│   │   ├── prompt_builder.py
│   │   └── error_handler.py
│   └── utils/
│
├── data/
│   ├── knowledge/
│   │   ├── startup/
│   │   ├── finance/
│   │   ├── marketing/
│   │   ├── product/
│   │   └── templates/
│   ├── faiss/              ← FAISS indexes (gitignored)
│   ├── exports/
│   └── uploads/
│
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── nginx.conf
│
├── scripts/
│   ├── setup.sh
│   ├── seed_database.py
│   ├── build_index.py
│   └── reset_dev.py
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── ai/
│
└── .github/
    └── workflows/
        └── ci.yml
```

## 2. Database Design

### 2.1 Entity Relationship

```
users (1) ──────── (N) projects
  └── (1) ──── (N) refresh_tokens
  └── (1) ──── (N) audit_logs

projects (1) ──── (8) project_modules
  └── (1) ──── (N) artifacts
  └── (1) ──── (N) workflow_runs
  └── (1) ──── (N) memory_chunks

artifacts (1) ──── (N) artifact_versions
workflow_runs (1) ── (N) workflow_steps
workflow_runs (1) ── (N) agent_executions
knowledge_documents (1) ── (N) memory_chunks
```

### 2.2 Migration Order

1. `001_initial` — UUID extension
2. `002_users_auth` — users, refresh_tokens
3. `003_projects` — projects, project_modules
4. `004_artifacts` — artifacts, artifact_versions
5. `005_workflows` — workflow_runs, workflow_steps, agent_executions
6. `006_memory` — memory_chunks, knowledge_documents
7. `007_audit` — audit_logs
8. `008_indexes` — Performance indexes

## 3. API Architecture

### 3.1 Layer Architecture

```
HTTP Request
    ↓
FastAPI Router (src/api/v1/)
    ↓ Pydantic validation
Service Layer (src/services/)
    ↓ Business logic
Repository Layer (src/repositories/)
    ↓ SQLAlchemy queries
PostgreSQL
    
Service Layer also calls:
    ↓
AI Runtime (ai/)
    ↓
Ollama → Qwen 3 8B
```

### 3.2 Authentication Flow

```
1. Register: POST /auth/register
   → Hash password → Create user → Issue tokens
   → Set refresh_token cookie (httpOnly, Secure, SameSite=Lax)

2. Login: POST /auth/login
   → Verify credentials → Issue tokens

3. Refresh: POST /auth/refresh
   → Verify refresh token → Rotate token → Issue new access

4. Protected requests:
   → Bearer token in Authorization header
   → FastAPI Depends(get_current_user)
   → Check project ownership for project routes
```

## 4. AI System Architecture

### 4.1 LangGraph Workflow Pipeline

```
WorkflowService.trigger()
    ↓
GraphFactory.get_graph(module_key)
    ↓ (async background task)
    
LangGraph Pipeline:
START
  ↓
load_context_node     ← Fetch project, prior artifacts from DB
  ↓
rag_retrieve_node     ← Query FAISS, return top-k chunks
  ↓
generation_node       ← PromptBuilder → Ollama → parse JSON
  ↓
validation_node       ← Pydantic schema check
  ↓ (fail → repair)
repair_node           ← Re-prompt with errors
  ↓ (2x max)
reflection_node       ← Quality self-check
  ↓
persist_node          ← Save artifact, version, update module
  ↓
memory_node           ← Chunk artifact, embed, FAISS index
  ↓
END

Each step updates workflow_steps table
Each agent call logs to agent_executions table
SSE events emitted at each step transition
```

### 4.2 Memory Pipeline

```
Project Creation:
  idea_brief → chunk (800 chars/150 overlap) → embed → FAISS

Artifact Completed:
  content_json + markdown → chunk → embed → FAISS → memory_chunks

User Edits:
  Invalidate old chunks → Re-chunk → Re-embed → FAISS update

Agent Retrieval:
  query → embed → FAISS search → top-k → format for prompt
```

### 4.3 Per-Agent Configuration

| Agent | Model | Temp | Context | Max Tokens | Knowledge |
|-------|-------|------|---------|------------|-----------|
| idea_validator | qwen3:8b | 0.30 | 8192 | 2048 | startup/, templates/ |
| market_researcher | qwen3:8b | 0.35 | 8192 | 3072 | marketing/, startup/ |
| business_modeler | qwen3:8b | 0.30 | 8192 | 2560 | startup/business_model/ |
| product_strategist | qwen3:8b | 0.35 | 8192 | 2560 | product/ |
| technical_architect | qwen3:8b | 0.25 | 8192 | 3072 | software/, architecture/ |
| financial_analyst | qwen3:8b | 0.20 | 8192 | 4096 | finance/ |
| marketing_strategist | qwen3:8b | 0.35 | 8192 | 2560 | marketing/ |
| investor_writer | qwen3:8b | 0.30 | 12288 | 4096 | templates/pitch/ |

## 5. Frontend Architecture

### 5.1 Next.js App Router Structure

```
/(auth) route group:    Public routes (no auth required)
  /login               Login form
  /register            Registration form
  
/(dashboard) route group: Protected routes (auth required)
  /dashboard           Overview with stats
  /projects            Project list
  /projects/new        Create project modal/page
  /projects/[id]       Project detail with modules
  /projects/[id]/modules/[module]   Module workspace
  /settings            User settings
  /profile             User profile
  
Middleware:
  - Auth check on all /(dashboard) routes
  - Redirect to /login if no valid token
```

### 5.2 State Management

```
Server State (TanStack Query):
  - queries: ['projects'], ['project', id], ['modules', projectId]
  - queries: ['artifacts', projectId, moduleKey]
  - queries: ['workflow-run', runId], ['memory-search']
  - mutations: createProject, triggerWorkflow, updateArtifact

Client State (Zustand or React State):
  - auth: { user, accessToken, isLoading }
  - ui: { sidebarOpen, theme }

SSE (EventSource):
  - Workflow run progress
  - Step status updates
```

### 5.3 API Client

```typescript
// lib/api-client.ts
class ApiClient {
  baseUrl: string                      // NEXT_PUBLIC_API_URL
  // Auto-injects Bearer token
  // Handles 401 → auto-refresh
  // Typed responses via Zod
}

// services/
  auth.service.ts     → /auth/*
  projects.service.ts → /projects/*
  modules.service.ts  → /projects/{id}/modules/*
  workflows.service.ts → /projects/{id}/workflows/*
  artifacts.service.ts → /projects/{id}/artifacts/*
  memory.service.ts   → /projects/{id}/memory/*
  export.service.ts   → /projects/{id}/export/*
```

## 6. Security Design

### 6.1 Authentication

- JWT access tokens: 15 min expiry, claim `{sub, exp, iat, type: "access"}`
- Refresh tokens: 7 days, opaque random 32 bytes base64url
- Stored as SHA-256 hash in `refresh_tokens` table
- Rotation: each refresh invalidates previous token
- Cookies: httpOnly, Secure, SameSite=Lax

### 6.2 Authorization

- All project routes verify `project.user_id == current_user.id`
- 404 returned for deleted projects (not 403, to prevent enumeration)
- Rate limiting on auth endpoints (future, via nginx in prod)

### 6.3 Input Validation

- All API inputs validated via Pydantic v2
- Idea brief and user content treated as data, NOT instructions
- Prompt injection defense in `ai/guardrails/prompt_injection.py`

## 7. Environment Variables

```bash
# Application
APP_ENV=development
APP_NAME=FoundrAI
LOG_LEVEL=INFO
DEBUG=true

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=foundrai
POSTGRES_USER=foundrai
POSTGRES_PASSWORD=foundrai_dev
DATABASE_URL=postgresql+asyncpg://foundrai:foundrai_dev@localhost:5432/foundrai

# JWT
JWT_SECRET_KEY=<min-256-bit-random-string>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Embeddings
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Vector Database
FAISS_INDEX_PATH=./data/faiss

# RAG Settings
RAG_TOP_K=8
RAG_CHUNK_SIZE=800
RAG_CHUNK_OVERLAP=150

# LLM Defaults
LLM_TEMPERATURE=0.3
LLM_TOP_P=0.9
LLM_TOP_K=40
LLM_MAX_TOKENS=4096

# AI Features
ENABLE_RAG=true
ENABLE_MEMORY=true
ENABLE_REFLECTION=true
ENABLE_REPAIR=true

# Streaming
ENABLE_STREAMING=false  # v1: workflow SSE, not token streaming

# File Storage
UPLOAD_DIR=./uploads
EXPORT_DIR=./exports

# Knowledge Base
KNOWLEDGE_DIR=./data/knowledge

# Logging
LOG_DIR=./logs

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=false

# Feature Flags
ENABLE_MARKETING_MODULE=true
ENABLE_FINANCIAL_MODULE=true
ENABLE_INVESTOR_MODULE=true
ENABLE_EXPORT=true
```

## 8. Docker Architecture

```yaml
# docker-compose.yml (development)
services:
  postgres:
    image: postgres:16-alpine
    ports: 5432:5432
    
  frontend:
    build: docker/Dockerfile.frontend
    ports: 3000:3000
    depends_on: [backend]
    
  backend:
    build: docker/Dockerfile.backend
    ports: 8000:8000
    depends_on: [postgres]
    
  # Ollama runs on host (not in Docker for GPU access)
  # ollama: manual setup required
```

## 9. Data Flow Diagrams

### 9.1 Create Project

```
User → POST /projects
  → Backend validates input
  → Create project row
  → Create 8 module rows (locked except idea_validation)
  → Queue: chunk + embed idea_brief → FAISS
  → Create audit_log
  → Return project with modules
```

### 9.2 Trigger Workflow

```
User → POST /projects/{id}/workflows/{module_key}/run
  → Check dependencies met (all required artifacts exist)
  → Check no active run for this module
  → Create workflow_run (status: pending)
  → Return 202 with run_id and stream_url
  → Background: execute LangGraph pipeline
    → Emit SSE events at each step
    → On completion: update artifact, module status
    → On failure: update run with error
```

### 9.3 Memory Retrieval in Agent

```
Generation Node (inside LangGraph):
  1. Get project_id from WorkflowState
  2. Formulate query from prior state
  3. Embed query → FAISS search top-k=8
  4. Fetch chunk metadata from DB
  5. Format: "[1] (artifact/validation_report) chunk text..."
  6. Inject into PromptBuilder context
  7. Call Ollama with assembled prompt
```

## 10. Testing Strategy

### 10.1 Backend Tests

```
Unit Tests (pytest):
  - Password hashing round-trip
  - JWT encode/decode
  - Repository CRUD operations
  - Service business logic

Integration Tests (pytest + httpx):
  - Full auth flow
  - Project CRUD via API
  - Workflow trigger and status
  - Artifact versioning

AI Tests:
  - Embedding generation
  - FAISS index/retrieve
  - Schema validation fixtures
  - Prompt rendering
```

### 10.2 Frontend Tests

```
Unit Tests (vitest):
  - Component rendering
  - Form validation
  - API client utility

E2E Tests (Playwright):
  - Auth flow
  - Project creation
  - Module workflow trigger
  - Artifact viewing/editing
```

---

**Document Status**: Draft  
**Last Updated**: 2025-01-30
