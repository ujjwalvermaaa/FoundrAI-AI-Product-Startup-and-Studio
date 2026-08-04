# FoundrAI Documentation

Official internal documentation for **FoundrAI – AI Product & Startup Studio** (*From Idea to Startup, Powered by AI*).

## Documents

| # | Document | File | Audience |
|---|----------|------|----------|
| 1 | [Product & Software Specification](./01-foundrai-product-software-specification.md) | Master blueprint: product definition, modules, agents, screens, system/AI/RAG/memory architecture, risks, roadmap | Product, Engineering, Design, Leadership |
| 2 | [Developer Implementation Guide](./02-developer-implementation-guide.md) | Environment setup, sprints, sequenced backend/frontend/AI/RAG build order, Docker, milestones | Engineers |
| 3 | [API & Database Reference](./03-api-database-reference.md) | PostgreSQL tables, ER diagram, REST endpoints, models, errors, indexing | Backend, Frontend, QA |
| 4 | [AI System Design Specification](./04-ai-system-design-specification.md) | Models, prompts, agents, LangGraph, memory, RAG, eval, guardrails — AI layer only | AI/ML, Backend Engineers |

## Reading Order

1. **Product Spec** §1–9 — what we are building and why  
2. **Product Spec** §10–15 — journeys, modules, agents, screens, AI workflows  
3. **Product Spec** §16–34 — software and AI architecture  
4. **AI System Design Spec** — implementable AI subsystem depth  
5. **Implementation Guide** — execution from empty repo to v1  
6. **API Reference** — contracts while implementing routers and UI  

## Conventions

- Numbered headings (`## 1.`, `### 1.1`) throughout  
- Cross-references between docs instead of duplicated sections  
- v1 stack: Next.js, FastAPI, PostgreSQL, JWT, LangGraph, Ollama (Qwen 3 8B), FAISS, Docker  

**Document version:** 1.0 · **Status:** Draft

