# Requirements Document

## Introduction

FoundrAI is an AI-powered SaaS platform that transforms startup ideas into validated business plans, product roadmaps, technical architectures, financial strategies, marketing plans, and investor-ready documentation. It is a structured project workspace with multi-agent AI orchestration, persistent project memory, and RAG-powered reasoning — not a chatbot.

Users manage **startup projects** inside a workspace where every AI-generated artifact is persisted, versioned, cross-linked, and reused across subsequent workflows. The system orchestrates multiple specialized AI agents, retrieval-augmented generation (RAG), and persistent project memory to produce structured, actionable outputs.

**Tech Stack:**
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, TanStack Query 5, Framer Motion 11
- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16, JWT
- AI: LangGraph, LangChain, Ollama (Qwen 3 8B), Sentence Transformers (BAAI/bge-base-en-v1.5), FAISS
- Deployment: Docker, Docker Compose v2

## Glossary

- **Project**: A startup workspace owned by a single user containing 8 AI modules and associated artifacts
- **Module**: One of 8 domain-specific workflow units (e.g., idea_validation, market_research) that produces a typed artifact
- **Artifact**: A schema-validated JSON + markdown document produced by an AI agent or user edit
- **Artifact Version**: An immutable snapshot of an artifact at a point in time; versions increment monotonically
- **Workflow Run**: An asynchronous execution of a LangGraph pipeline for a given module
- **Workflow Step**: A LangGraph node-level execution record within a workflow run
- **Agent Execution**: A single LLM invocation within a workflow step
- **Memory Chunk**: A text fragment from an artifact or project brief, embedded and stored in FAISS for retrieval
- **RAG**: Retrieval-Augmented Generation — querying project memory before LLM generation
- **FAISS**: Facebook AI Similarity Search — per-project vector index for semantic retrieval
- **Module Status**: One of: locked, available, in_progress, completed, failed
- **Investor Pack**: A consolidated markdown export of all project artifacts for fundraising
- **SSE**: Server-Sent Events — a push mechanism for streaming workflow progress to the frontend
- **JWT**: JSON Web Token — used for access (15 min) and refresh (7 days) authentication
- **idea_brief**: The user's initial startup idea description; the seed for all AI workflows
- **System**: The FoundrAI backend API and AI runtime
- **Agent**: A domain-specific AI component that generates one artifact type
- **Orchestrator**: The component that routes and sequences agent workflows via LangGraph

## Requirements

### 1. User Authentication and Account Management

**User Story:** As a founder, I want to register, login, and manage my account, so that I can securely access and own my startup projects.

**Acceptance Criteria:**

1. WHEN a user submits a registration request with email, password (min 8 chars, ≥1 letter + ≥1 number), and full name, THE System SHALL create a user account and return a JWT access token (15 min) and refresh token (7 days)
2. WHEN a user submits valid login credentials, THE System SHALL return a JWT access token and a rotating refresh token set via httpOnly cookie
3. WHEN a user submits a valid refresh token, THE System SHALL issue a new access token and rotate the refresh token
4. WHEN a user submits a logout request, THE System SHALL revoke the refresh token and invalidate the session
5. WHEN a user requests their profile via GET /auth/me with a valid Bearer token, THE System SHALL return the authenticated user's profile
6. IF a registration request contains an already-registered email, THEN THE System SHALL return a 409 EMAIL_ALREADY_EXISTS error
7. IF a login request contains invalid credentials, THEN THE System SHALL return a 401 INVALID_CREDENTIALS error
8. THE System SHALL store all passwords as bcrypt hashes and never log password values
9. THE System SHALL validate email format and enforce password constraints at the application layer

### 2. Project Management

**User Story:** As a founder, I want to create and manage startup projects, so that I can organize my idea validation and planning work.

**Acceptance Criteria:**

1. WHEN a user creates a project with a name (1–255 chars), idea_brief (50–10000 chars), and optional tagline and industry, THE System SHALL persist the project and return it with 201 status
2. WHEN a project is created, THE System SHALL seed exactly 8 project_module rows with the module_keys: idea_validation, market_research, business_model, product_strategy, technical_architecture, financial_planning, marketing_strategy, investor_documentation
3. WHEN a project is created, THE System SHALL set the idea_validation module status to available and all other modules to locked
4. WHEN a project is created, THE System SHALL index the idea_brief into project memory (chunk, embed, store in FAISS)
5. WHEN a user requests their project list, THE System SHALL return only projects owned by the authenticated user with pagination support (page, page_size)
6. WHEN a user updates a project's idea_brief, THE System SHALL re-index the idea_brief in project memory
7. WHEN a user deletes a project, THE System SHALL perform a soft delete by setting the deleted_at timestamp and return 204
8. IF a user attempts to access a project they do not own or a deleted project, THEN THE System SHALL return 404 PROJECT_NOT_FOUND
9. THE System SHALL write an audit_log entry on project.create

### 3. Module System and Dependencies

**User Story:** As a founder, I want modules to unlock in a defined order based on completed artifacts, so that I am guided through the startup planning sequence.

**Acceptance Criteria:**

1. THE System SHALL enforce the following module dependency rules: market_research requires validation_report; business_model requires validation_report and market_analysis; product_strategy requires business_model_canvas; technical_architecture requires product_roadmap; financial_planning requires business_model_canvas and product_roadmap; marketing_strategy requires business_model_canvas and product_roadmap; investor_documentation requires all prior artifact types
2. WHEN a user requests a module's detail, THE System SHALL return a dependencies_met boolean and a missing_artifacts list
3. WHEN a workflow run completes successfully for a module, THE System SHALL set that module's status to completed and unlock all modules whose dependency conditions are now satisfied
4. IF a user attempts to trigger a workflow for a module with unmet dependencies, THEN THE System SHALL return 409 MODULE_DEPENDENCY_NOT_MET
5. IF a user attempts to trigger a workflow for a module that already has a pending or running workflow, THEN THE System SHALL return 409 WORKFLOW_ALREADY_RUNNING

### 4. Workflow Execution and Orchestration

**User Story:** As a founder, I want to trigger AI workflows per module and receive real-time progress updates, so that I know the status of AI generation.

**Acceptance Criteria:**

1. WHEN a user triggers a workflow for an available module, THE System SHALL create a workflow_run record with status pending and return 202 with the run id and SSE stream_url
2. WHILE a workflow is executing, THE System SHALL emit SSE events for: step_started, step_completed, agent_execution_update, run_completed, run_failed
3. WHEN a workflow run starts executing, THE System SHALL update the module status to in_progress
4. WHEN a workflow run completes successfully, THE System SHALL update the workflow_run status to completed and set the module status to completed
5. IF a workflow run fails, THEN THE System SHALL set the workflow_run status to failed with an error_code and error_message, and set the module status to failed
6. WHEN a user cancels a pending or running workflow, THE System SHALL set the workflow_run status to cancelled
7. THE System SHALL persist every workflow_step and agent_execution record including model_name, latency_ms, prompt_tokens, and completion_tokens
8. THE LangGraph pipeline SHALL execute the following node sequence: load_context → rag_retrieve → generation → validation → repair (if validation fails, max 2 retries) → reflection → persist → memory_index
9. THE System SHALL write an audit_log entry on workflow.trigger

### 5. Artifact Management and Versioning

**User Story:** As a founder, I want to view, edit, and track the history of AI-generated artifacts, so that I can refine outputs with my own domain knowledge.

**Acceptance Criteria:**

1. WHEN a workflow run completes successfully, THE System SHALL upsert a typed artifact for the module (one artifact per artifact_type per project) with source set to ai
2. WHEN an artifact is created or updated, THE System SHALL create an immutable artifact_version row with an incrementing version_number starting at 1
3. WHEN a user edits an artifact via PATCH, THE System SHALL create a new artifact_version with source set to user_edit and re-index memory chunks for that artifact
4. WHEN a user requests artifact versions, THE System SHALL return the full version history ordered by version_number descending
5. IF a user submits an artifact edit that fails schema validation, THEN THE System SHALL return 422 SCHEMA_VALIDATION_FAILED without persisting the edit
6. THE System SHALL ensure no orphan artifacts exist without a corresponding artifact_version row
7. THE System SHALL enforce the unique constraint of one artifact per (project_id, artifact_type)

### 6. AI Agent System and Multi-Agent Orchestration

**User Story:** As a founder, I want 8 specialized AI agents to generate domain-specific artifacts, so that each module produces expert-level structured output.

**Acceptance Criteria:**

1. THE System SHALL implement 8 domain agents: idea_validator, market_researcher, business_modeler, product_strategist, technical_architect, financial_analyst, marketing_strategist, investor_writer
2. WHEN any agent generates output, THE Agent SHALL retrieve top-k memory chunks (default k=8) from project FAISS before invoking the LLM
3. WHEN an agent generates output, THE Agent SHALL produce JSON that validates against the corresponding Pydantic artifact schema before persisting
4. IF an agent's output fails schema validation, THEN THE System SHALL invoke a repair_node with the validation errors and retry up to 2 times before marking the run failed
5. THE System SHALL log model_name, latency_ms, prompt_tokens, completion_tokens, and prompt_version for every agent_execution
6. THE System SHALL configure agents with per-agent inference parameters from ai/config/agents.yaml (temperature, top_p, top_k, max_tokens, context_window)
7. WHEN the idea_validator agent runs, THE Agent SHALL produce a validation_report with risks array (≥3 items), validation_score (0–100), problem, solution, target_customer, recommendations, and summary
8. WHEN the market_researcher agent runs, THE Agent SHALL produce a market_analysis with competitors array (≥3 items), TAM, SAM, SOM fields, segments, trends, and summary
9. WHEN the business_modeler agent runs, THE Agent SHALL produce a business_model_canvas with all 9 canvas blocks non-empty
10. WHEN the product_strategist agent runs, THE Agent SHALL produce a product_roadmap with ≥2 phases, each containing ≥3 features
11. WHEN the financial_analyst agent runs, THE Agent SHALL produce a financial_model with a 12-month projection and ≥5 assumptions
12. WHEN the marketing_strategist agent runs, THE Agent SHALL produce a marketing_plan with ≥3 channels and a launch checklist of ≥5 items
13. WHEN the investor_writer agent runs, THE Agent SHALL produce an investor_deck_outline with ≥10 slides including problem, market, product, and funding ask sections

### 7. Embedding, FAISS, and Project Memory

**User Story:** As a developer, I want project artifacts and the idea brief to be embedded and indexed, so that agents can retrieve relevant context before generating new artifacts.

**Acceptance Criteria:**

1. THE System SHALL use the BAAI/bge-base-en-v1.5 Sentence Transformers model to generate 768-dimensional embeddings
2. THE System SHALL chunk text with chunk_size=800 characters and chunk_overlap=150 characters using content-aware splitting
3. WHEN an artifact is created or updated, THE System SHALL chunk the content, embed the chunks, store vectors in the project FAISS index, and create memory_chunk records
4. WHEN memory chunks are re-indexed after an edit, THE System SHALL invalidate old chunks for that artifact before inserting new ones using content_hash deduplication
5. WHEN a memory search is performed, THE System SHALL return scored MemorySearchResult records with chunk_id, content_text, score, and metadata
6. THE System SHALL persist FAISS indexes to disk at the path configured by FAISS_INDEX_PATH
7. THE System SHALL seed knowledge documents from data/knowledge/ into each project's FAISS index at first workflow run

### 8. Export System

**User Story:** As a founder with completed modules, I want to export an investor-ready documentation pack, so that I can share my startup plan with investors.

**Acceptance Criteria:**

1. WHEN a user requests an investor pack export, THE System SHALL collect all available artifacts, render them as structured markdown, and return a download URL
2. IF a user requests an investor pack export but the project is missing the minimum required artifacts (validation_report, business_model_canvas, financial_model), THEN THE System SHALL return 409 INSUFFICIENT_ARTIFACTS
3. THE System SHALL save export files to the data/exports/ directory with an expiry timestamp
4. THE System SHALL support markdown format in v1 (PDF is future scope)

### 9. Frontend Application

**User Story:** As a founder, I want a polished web application with auth, project management, module workspaces, and real-time AI progress, so that I can use FoundrAI without needing to interact with APIs directly.

**Acceptance Criteria:**

1. THE Frontend SHALL implement authentication pages (login, register) using the existing TanStack Start design ported to Next.js 15 App Router
2. THE Frontend SHALL implement a dashboard page with project stats, recent activity, and quick actions
3. THE Frontend SHALL implement a projects list page with a create project modal
4. THE Frontend SHALL implement a project detail page showing all 8 module status cards
5. THE Frontend SHALL implement a module workspace page with artifact viewer (JSON + markdown tabs), workflow trigger button, SSE progress indicator, artifact editor, and version history panel
6. WHEN a workflow is running, THE Frontend SHALL display live step-by-step progress updates received via SSE
7. THE Frontend SHALL handle token refresh automatically before access token expiry using an API client interceptor
8. THE Frontend SHALL display loading skeletons, empty states, error boundaries, and toast notifications for all async operations
9. THE Frontend SHALL be responsive across desktop and mobile screen sizes
10. THE Frontend SHALL preserve all existing UI designs, components, and design tokens from the existing TanStack Start frontend during migration to Next.js 15

### 10. Health, Observability, and Operations

**User Story:** As a developer, I want health endpoints, structured logs, and audit trails, so that I can monitor the system and troubleshoot issues.

**Acceptance Criteria:**

1. THE System SHALL expose GET /health returning 200 with status: ok as a liveness probe
2. THE System SHALL expose GET /health/ready that checks PostgreSQL connectivity, Ollama model availability (qwen3:8b), and FAISS directory writability
3. IF any critical health check fails, THEN THE System SHALL return 503 with status: degraded and per-check status details
4. THE System SHALL emit structured JSON logs for all HTTP requests and workflow events with correlation IDs tied to workflow_run_id
5. THE System SHALL write audit_log entries for project.create, workflow.trigger, and export actions
6. THE System SHALL return consistent error JSON with the shape: { "error": { "code": "SCREAMING_SNAKE_CASE", "message": "...", "details": {} } }

### 11. Docker Deployment

**User Story:** As a developer, I want the full stack to run via Docker Compose, so that I can set up the development and production environment with a single command.

**Acceptance Criteria:**

1. THE System SHALL provide a docker-compose.yml for development with a postgres service accessible on port 5432
2. THE System SHALL provide a docker-compose.prod.yml with postgres, backend, frontend, and nginx services
3. THE System SHALL provide multi-stage Dockerfiles for backend (Python) and frontend (Next.js) that produce minimal production images
4. THE System SHALL provide an nginx.conf as a reverse proxy routing frontend and backend traffic
5. WHEN the production Docker Compose stack starts, THE System SHALL be fully accessible via the nginx proxy
6. THE System SHALL provide a .env.example file with all required environment variables and descriptions
