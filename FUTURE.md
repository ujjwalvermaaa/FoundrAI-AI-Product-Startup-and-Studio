# FoundrAI — Future Roadmap & Hosting Plan

This document captures the current state of the project, why it isn't hosted yet, and the concrete path forward to get it production-ready and publicly accessible.

---

## Current State

FoundrAI is fully built and runs perfectly on a local machine. All 8 AI agents work end-to-end, the full pipeline from idea brief to investor deck outline is functional, and the frontend, backend, and database are all wired together.

**The reason it isn't hosted yet is purely infrastructure cost.**

The current AI stack runs on **Ollama** — a tool that serves large language models locally on your own hardware. The primary model is `qwen3:4b` (~2.5 GB), and the embedding model is `BAAI/bge-base-en-v1.5` (~440 MB). Running these requires a server with at minimum **16 GB of RAM**, and ideally a GPU for reasonable inference speed. A server with those specs costs anywhere from $80–150/month, which is not justifiable for a project that isn't generating revenue yet.

This is not a code problem. The application is production-ready. It is simply waiting for the right infrastructure setup.

---

## Why Ollama Was Chosen

Ollama was the right call during development:

- **Zero API costs** — every test run, every agent execution, every debug session was free
- **No rate limits** — 310 tests can run against the real AI stack without hitting quotas
- **Privacy** — idea briefs and business data never leave the local machine
- **No dependencies on third-party uptime** — the whole stack works offline
- **Fast iteration** — swap models, change prompts, re-run instantly

For local development it remains the best option and will stay as the default for anyone running the project on their own machine.

---

## The Hosting Problem

To host FoundrAI as-is (with Ollama), the server needs to:

- Run `qwen3:4b` in memory → **~8 GB RAM just for the model**
- Run PostgreSQL, the FastAPI backend, the embedding model, and nginx alongside it
- Stay running 24/7, not spin down between requests (Ollama needs the model warm)

The cheapest server that can handle this is around **€14–20/month** (Hetzner CPX31, 16 GB RAM). That's acceptable for a funded project or one with users, but it's a committed cost before there's any traction.

On top of that, `qwen3:4b` on CPU inference runs at roughly 1–3 tokens per second. A full 8-agent pipeline from idea to investor deck could take 10–20 minutes. For real users that's too slow without a GPU, and GPU servers start at $80–150/month.
---

## The Plan Forward

### Phase 1 — Replace Ollama with a Cloud LLM API

This is the highest-impact change and the one that unblocks hosting on cheap infrastructure.

Instead of running the model locally, the generation node in each LangGraph pipeline would call an external LLM API. LangChain (already in the stack) abstracts this — the change is a configuration swap, not a rewrite.

**Target APIs:**

| Provider | Model | Why |
|---|---|---|
| **Groq** | `llama-3.1-8b-instant` or `qwen` variants | Extremely fast inference, generous free tier, near-zero latency |
| **OpenRouter** | Any open model | Single API key, access to 100+ models, pay-per-token, easy to swap |
| **Gemini (Google)** | `gemini-1.5-flash` | Very cheap per token, large context window, good JSON output |
| **OpenAI** | `gpt-4o-mini` | Reliable, predictable, great at structured JSON output |

The current `OLLAMA_BASE_URL` and `OLLAMA_MODEL` env vars would be replaced with `LLM_PROVIDER`, `LLM_API_KEY`, and `LLM_MODEL` settings. The LangChain swap is roughly a 10-line change per agent.

**Cost estimate with Groq free tier:** $0/month for moderate usage. Even on paid tiers, 8-agent pipeline runs would cost pennies per execution.

### Phase 2 — Replace Local Embeddings with an API

The embedding model (`BAAI/bge-base-en-v1.5`) currently loads into RAM on startup (~1 GB). This needs to move to an API too.

**Options:**
- **OpenAI `text-embedding-3-small`** — $0.02 per million tokens, extremely cheap
- **Cohere Embed** — good multilingual support if needed later
- **Voyage AI** — strong retrieval-focused embeddings

With API embeddings, the backend can run on a **$5–10/month server** (2 GB RAM) since it no longer needs to hold a model in memory.

### Phase 3 — Hosting Stack After API Migration

Once the AI layer moves to APIs, the entire app fits on minimal infrastructure:

| Component | Service | Estimated Cost |
|---|---|---|
| Frontend (Vite/React) | Vercel / Cloudflare Pages | Free |
| Backend (FastAPI) | Railway / Render / Fly.io | $5–20/month |
| PostgreSQL | Supabase / Neon / Railway | $0–10/month |
| FAISS indexes | Persisted on backend server disk | Included above |
| LLM inference | Groq / OpenRouter | ~$0–10/month (usage-based) |
| Embeddings | OpenAI / Cohere | ~$0–5/month (usage-based) |

**Total: ~$10–35/month** instead of $80–150/month. Scales with usage rather than being a fixed cost.

### Phase 4 — Performance & Scale

Once hosted and getting real users:

- **Streaming improvements** — SSE already works; ensure Fly.io / Railway don't buffer streams
- **Job queue** — move LangGraph workflow execution to a proper task queue (Celery + Redis or ARQ) so the backend doesn't block on long-running agent pipelines
- **FAISS → managed vector DB** — replace per-project FAISS files with Pinecone, Qdrant Cloud, or Supabase pgvector for easier scaling and backups
- **Rate limiting per user** — workflow runs are expensive; add per-account quotas
- **Caching** — cache RAG retrieval results for identical queries within a project

---

## What Stays the Same

The migration to APIs is an infrastructure change, not a product change. Everything else stays identical:

- All 8 LangGraph pipelines and their logic
- All Pydantic schemas and validation rules
- The repair loop, reflection node, and guardrails
- The RAG chunking, retrieval, and memory indexing
- The entire frontend, all routes and UI
- The PostgreSQL schema and all 13 tables
- The FastAPI routers and SSE streaming
- The artifact versioning system

The core product — the 8-agent sequential pipeline that turns an idea into a full business plan — does not change at all.

---

## For Anyone Running This Locally

The Ollama setup stays as the default for local development. It costs nothing, works offline, and gives you full control over the model. The API migration is a future production concern only.

See [Docs/LOCAL_RUN.md](./Docs/LOCAL_RUN.md) for the local setup guide.

---

## Summary

| | Now | Future |
|---|---|---|
| LLM inference | Ollama (local, free, slow) | Groq / OpenRouter (API, cheap, fast) |
| Embeddings | BAAI/bge-base-en-v1.5 (local, ~1 GB RAM) | OpenAI / Cohere (API, near-zero RAM) |
| Hosting | Not hosted (cost barrier) | $10–35/month total |
| Inference speed | 1–3 tokens/sec (CPU) | ~200–500 tokens/sec (Groq) |
| Setup complexity | Docker + Ollama pull | Docker + API keys in `.env` |
| Privacy | Fully local, data never leaves machine | Data sent to LLM provider |

The project is built. The code is done. Hosting is purely a "flip the switch when ready" decision.
