# FoundrAI — AI Agent Reference

This document describes the 8 AI agents in FoundrAI — what each one does, what it consumes, what it produces, and how they connect.

---

## The LangGraph Pipeline

Every module runs the same 8-node LangGraph pipeline. The graph is deterministic: nodes execute in order, with the repair loop being the only conditional branch.

```
┌─────────────────┐
│  load_context   │  Load project brief + upstream artifacts from DB
└────────┬────────┘
         │
┌────────▼────────┐
│   rag_retrieve  │  Query project FAISS + knowledge base, return top-8 chunks
└────────┬────────┘
         │
┌────────▼────────┐
│   generation    │  Build prompt → call Ollama (qwen3:4b) → parse JSON
└────────┬────────┘
         │
┌────────▼────────┐
│   validation    │  Validate against Pydantic schema + domain rules
└────────┬────────┘
    pass │ fail
         │    ┌─────────────────┐
         │    │     repair      │  Re-prompt with error details (max 2 retries)
         │    └────────┬────────┘
         │             │ still failing after 2 retries → mark run FAILED
         │◄────────────┘
         │
┌────────▼────────┐
│   reflection    │  Self-critique against a quality rubric, log score
└────────┬────────┘
         │
┌────────▼────────┐
│     persist     │  Upsert artifact in DB, create new version record
└────────┬────────┘
         │
┌────────▼────────┐
│  memory_index   │  Chunk artifact text → embed → add to project FAISS index
└─────────────────┘
```

**SSE events** are emitted at `step_started` and `step_completed` for each node, and `run_completed` / `run_failed` at the end. The frontend subscribes to the stream endpoint and renders a live progress timeline.

**State object** (`WorkflowState` TypedDict — `ai/graphs/state.py`):
```python
{
    "project_id": str,
    "module_key": str,
    "run_id": str,
    "inputs": dict,                # project brief + upstream artifacts
    "retrieved_chunks": list[str], # RAG results
    "required_artifacts": dict,    # upstream artifact data
    "current_draft": dict,         # LLM output (in progress)
    "errors": list[str],           # validation errors for repair loop
    "steps_metadata": list[dict],  # timing + token counts per step
    "retry_count": int,            # repair attempts so far
}
```

---

## Module Dependency Order

Modules unlock in a strict dependency chain. A module is `locked` until all its required artifacts exist.

```
idea_validation               (always available)
└── market_research           (requires: validation_report)
    └── business_model        (requires: validation_report + market_analysis)
        ├── product_strategy  (requires: business_model_canvas)
        │   ├── technical_architecture  (requires: product_roadmap)
        │   ├── financial_planning      (requires: business_model_canvas + product_roadmap)
        │   └── marketing_strategy      (requires: business_model_canvas + product_roadmap)
        └── investor_documentation      (requires: ALL prior artifacts)
```

Module status lifecycle: `locked → available → in_progress → completed | failed`

---

## Agent 1 — Idea Validator

**Module key**: `idea_validation`  
**Graph**: `ai/graphs/validation_graph.py`  
**Agent**: `ai/agents/idea_validator/agent.py`  
**Schema**: `ai/schemas/validation_report.py`

### What it does
Evaluates the feasibility and market fit of a raw startup idea. It assesses the problem clarity, solution uniqueness, target customer definition, and potential risks. It produces a structured validation report with a numeric confidence score.

### Inputs
- Project idea brief (free-text, provided by the founder)

### Output: `validation_report`
```json
{
  "problem_statement": "string",
  "proposed_solution": "string",
  "target_customer": "string",
  "validation_score": 0–100,
  "risks": ["≥3 risk items"],
  "recommendations": ["list of actionable suggestions"],
  "go_no_go": "go | no_go | pivot"
}
```

### Schema requirements
- `risks` must have ≥ 3 items
- `validation_score` must be in range 0–100
- `problem_statement`, `proposed_solution`, `target_customer` must all be non-empty

### Prompt files
- `ai/prompts/agents/idea_validator/system.v1.md` — persona and task framing
- `ai/prompts/agents/idea_validator/developer.v1.md` — JSON schema instructions
- `ai/prompts/agents/idea_validator/user.v1.md` — input template with placeholders
- `ai/prompts/agents/idea_validator/repair.v1.md` — re-prompt with validation errors

---

## Agent 2 — Market Researcher

**Module key**: `market_research`  
**Graph**: `ai/graphs/market_research_graph.py`  
**Agent**: `ai/agents/market_researcher/agent.py`  
**Schema**: `ai/schemas/market_analysis.py`

### What it does
Analyzes the target market for the startup. It sizes the opportunity (TAM/SAM/SOM), identifies competitors, segments the customer base, and surfaces key market trends. Uses the validation report as context.

### Inputs
- Idea brief
- `validation_report` artifact

### Output: `market_analysis`
```json
{
  "tam": "string (e.g. '$4.5B global market')",
  "sam": "string",
  "som": "string",
  "competitors": [
    {
      "name": "string",
      "description": "string",
      "strengths": ["list"],
      "weaknesses": ["list"]
    }
  ],
  "market_segments": ["≥2 segments"],
  "trends": ["list of trends"],
  "entry_strategy": "string"
}
```

### Schema requirements
- `competitors` must have ≥ 3 entries
- `market_segments` must have ≥ 2 entries
- TAM, SAM, SOM must all be non-empty

---

## Agent 3 — Business Modeler

**Module key**: `business_model`  
**Graph**: `ai/graphs/business_model_graph.py`  
**Agent**: `ai/agents/business_modeler/agent.py`  
**Schema**: `ai/schemas/business_model_canvas.py`

### What it does
Generates a complete Business Model Canvas using the Osterwalder framework. All 9 canvas blocks are populated with startup-specific content derived from the prior validation and market research artifacts.

### Inputs
- Idea brief
- `validation_report` artifact
- `market_analysis` artifact

### Output: `business_model_canvas`
```json
{
  "value_propositions": ["list"],
  "customer_segments": ["list"],
  "channels": ["list"],
  "customer_relationships": ["list"],
  "revenue_streams": ["list"],
  "key_resources": ["list"],
  "key_activities": ["list"],
  "key_partnerships": ["list"],
  "cost_structure": ["list"]
}
```

### Schema requirements
- All 9 blocks must be non-empty arrays

---

## Agent 4 — Product Strategist

**Module key**: `product_strategy`  
**Graph**: `ai/graphs/product_strategy_graph.py`  
**Agent**: `ai/agents/product_strategist/agent.py`  
**Schema**: `ai/schemas/product_roadmap.py`

### What it does
Creates a phased product roadmap with feature priorities, success metrics, and key assumptions. Grounds decisions in the business model canvas.

### Inputs
- Idea brief
- `business_model_canvas` artifact

### Output: `product_roadmap`
```json
{
  "vision": "string",
  "phases": [
    {
      "name": "string (e.g. MVP)",
      "duration": "string",
      "features": ["≥3 feature descriptions"],
      "success_metrics": ["list"],
      "assumptions": ["list"]
    }
  ]
}
```

### Schema requirements
- `phases` must have ≥ 2 entries
- Each phase must have ≥ 3 features

---

## Agent 5 — Technical Architect

**Module key**: `technical_architecture`  
**Graph**: `ai/graphs/architecture_graph.py`  
**Agent**: `ai/agents/technical_architect/agent.py`  
**Schema**: `ai/schemas/architecture_doc.py`

### What it does
Designs the technical architecture for the product. Recommends a technology stack, defines system components and their interactions, describes data flows, and addresses security considerations.

### Inputs
- Idea brief
- `product_roadmap` artifact

### Output: `architecture_doc`
```json
{
  "overview": "string",
  "tech_stack": {
    "frontend": "string",
    "backend": "string",
    "database": "string",
    "infrastructure": "string"
  },
  "components": [
    {
      "name": "string",
      "responsibility": "string",
      "technology": "string"
    }
  ],
  "data_flows": ["list describing key flows"],
  "security": {
    "authentication": "string",
    "authorization": "string",
    "data_protection": "string"
  },
  "scalability_notes": "string"
}
```

### Schema requirements
- `components`, `data_flows` must be non-empty
- `security` object must have all three sub-fields

---

## Agent 6 — Financial Analyst

**Module key**: `financial_planning`  
**Graph**: `ai/graphs/financial_graph.py`  
**Agent**: `ai/agents/financial_analyst/agent.py`  
**Schema**: `ai/schemas/financial_model.py`

### What it does
Builds a 12-month financial model with revenue projections, cost structure, and unit economics. Uses the business model and product roadmap to derive realistic assumptions.

### Inputs
- Idea brief
- `business_model_canvas` artifact
- `product_roadmap` artifact

### Output: `financial_model`
```json
{
  "assumptions": ["≥5 key assumptions"],
  "revenue_model": "string",
  "monthly_projections": [
    {
      "month": 1–12,
      "revenue": number,
      "costs": number,
      "profit": number
    }
  ],
  "unit_economics": {
    "cac": "string",
    "ltv": "string",
    "payback_period": "string",
    "gross_margin": "string"
  },
  "funding_required": "string",
  "break_even_month": number
}
```

### Schema requirements
- `assumptions` must have ≥ 5 entries
- `monthly_projections` must cover 12 months
- `unit_economics` must have all four sub-fields

---

## Agent 7 — Marketing Strategist

**Module key**: `marketing_strategy`  
**Graph**: `ai/graphs/marketing_graph.py`  
**Agent**: `ai/agents/marketing_strategist/agent.py`  
**Schema**: `ai/schemas/marketing_plan.py`

### What it does
Creates a go-to-market strategy with channel recommendations, ideal customer profile (ICP), core messaging, and a launch checklist. Grounded in the business model and product roadmap.

### Inputs
- Idea brief
- `business_model_canvas` artifact
- `product_roadmap` artifact

### Output: `marketing_plan`
```json
{
  "icp": "string (ideal customer profile)",
  "positioning": "string",
  "channels": [
    {
      "name": "string",
      "rationale": "string",
      "tactics": ["list"]
    }
  ],
  "messaging": {
    "tagline": "string",
    "value_prop": "string",
    "objection_handling": ["list"]
  },
  "launch_checklist": ["≥5 launch tasks"],
  "kpis": ["list of success metrics"]
}
```

### Schema requirements
- `channels` must have ≥ 3 entries
- `launch_checklist` must have ≥ 5 items

---

## Agent 8 — Investor Writer

**Module key**: `investor_documentation`  
**Graph**: `ai/graphs/investor_graph.py`  
**Agent**: `ai/agents/investor_writer/agent.py`  
**Schema**: `ai/schemas/investor_deck_outline.py`

### What it does
Synthesizes all prior artifacts into a structured investor deck outline. Each slide is mapped to content derived from the upstream agents. This is the final stage and requires all 7 prior artifacts to be complete.

### Inputs
- Idea brief
- ALL prior artifacts: `validation_report`, `market_analysis`, `business_model_canvas`, `product_roadmap`, `architecture_doc`, `financial_model`, `marketing_plan`

### Output: `investor_deck_outline`
```json
{
  "deck_title": "string",
  "slides": [
    {
      "number": 1,
      "title": "string",
      "content_points": ["list of bullet points"],
      "speaker_notes": "string",
      "source_artifact": "string (which agent produced this content)"
    }
  ],
  "ask": {
    "amount": "string",
    "use_of_funds": ["list"],
    "milestones": ["list"]
  }
}
```

### Schema requirements
- `slides` must have ≥ 10 entries
- Must include slides covering: problem, market size, product/solution, business model, traction, team, financials, funding ask
- `ask` object must be fully populated

---

## Agent Implementation Structure

Each agent follows the same file layout:

```
ai/agents/{agent_name}/
└── agent.py          # Agent constants: SYSTEM_PROMPT_PATH, USER_PROMPT_PATH,
                      # SCHEMA_CLASS, MODULE_KEY, REQUIRED_ARTIFACTS

ai/prompts/agents/{agent_name}/
├── system.v1.md      # System persona and task framing
├── developer.v1.md   # JSON output schema instructions
├── user.v1.md        # Input template with {{placeholders}}
└── repair.v1.md      # Re-prompt for repair loop with {{errors}}

ai/graphs/{agent_name}_graph.py   # LangGraph StateGraph wiring all 8 nodes
ai/schemas/{artifact_type}.py     # Pydantic model for output validation
```

---

## Graph Factory

`ai/graphs/graph_factory.py` maps module keys to their compiled LangGraph instances:

```python
GRAPHS = {
    "idea_validation":         get_validation_graph(),
    "market_research":         get_market_research_graph(),
    "business_model":          get_business_model_graph(),
    "product_strategy":        get_product_strategy_graph(),
    "technical_architecture":  get_architecture_graph(),
    "financial_planning":      get_financial_graph(),
    "marketing_strategy":      get_marketing_graph(),
    "investor_documentation":  get_investor_graph(),
}
```

`WorkflowService.execute(run_id, module_key, inputs)` calls `GraphFactory.run(module_key, state)` in a background task. The graph emits SSE events via a callback registered in the `WorkflowState`.

---

## RAG Pipeline

Before the `generation` node runs, the `rag_retrieve` node queries two FAISS indexes:

1. **Project index** (`data/faiss/{project_id}/`) — all prior artifacts and the idea brief, indexed as the project evolves
2. **Knowledge index** (`data/faiss/knowledge/`) — 5 seed documents covering startup methodology, unit economics, GTM strategies, product planning, and validation frameworks

Top-8 chunks by cosine similarity (L2-normalized inner product) are injected into the generation prompt as a `## Context` block.

**Embedding model**: `BAAI/bge-base-en-v1.5` — 768-dimensional embeddings, loaded as a singleton to avoid repeated model loads.

**Chunking**: 800-character chunks with 150-character overlap, split on sentence boundaries where possible.

**Deduplication**: Each chunk is SHA-256 hashed before indexing. Identical content is never indexed twice per project.

---

## Guardrails

Three layers of protection run around each agent execution:

| Layer | File | What it does |
|---|---|---|
| Prompt injection detection | `ai/guardrails/prompt_injection.py` | Scans user-provided inputs for injection patterns before they reach the prompt builder |
| Schema validation | `ai/guardrails/schema_validation.py` | Validates LLM output against Pydantic schema; triggers repair loop on failure |
| Output quality check | `ai/guardrails/output_validation.py` | Domain-level checks (e.g., risk count, slide count) beyond structural schema validation |

If prompt injection is detected, the workflow is immediately cancelled with `PROMPT_INJECTION_DETECTED` error code. Schema failures trigger the repair loop (max 2 retries) before the run is marked failed.
