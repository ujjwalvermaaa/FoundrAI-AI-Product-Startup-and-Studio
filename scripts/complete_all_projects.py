#!/usr/bin/env python3
"""
Mark ALL modules as completed and ensure ALL 8 artifacts exist for every project.
Run from backend dir:  poetry run python ../scripts/complete_all_projects.py
"""
import asyncio, sys, os, uuid, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://foundrai:foundrai_dev@127.0.0.1:5432/foundrai"
USER_EMAIL   = "ujjwalvermauv2004@gmail.com"

engine       = create_async_engine(DATABASE_URL, echo=False)
Session      = async_sessionmaker(engine, expire_on_commit=False)

MODULE_KEYS  = [
    "idea_validation","market_research","business_model","product_strategy",
    "technical_architecture","financial_planning","marketing_strategy","investor_documentation",
]

# ---------------------------------------------------------------------------
# Per-project, per-module artifact definitions
# ---------------------------------------------------------------------------

def artifacts_for(project_name: str, tagline: str, industry: str) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    p, t, ind = project_name, tagline, industry
    return [
        # 1 ── idea_validation
        dict(
            module_key="idea_validation",
            artifact_type="validation_report",
            title=f"Validation Report — {p}",
            content_markdown=f"""# Validation Report: {p}

## Problem Statement
{t}

Founders and operators in the **{ind}** space are underserved by today's tools.
Pain is real, recurring, and customers are already paying workarounds.

## Proposed Solution
{p} removes the friction entirely with an AI-native approach — no manual steps,
no fragmented tools, no expensive consultants required.

## Target Customer
Growth-stage {ind.lower()} companies (10–200 employees) with an urgent, recurring pain
that the current market addresses poorly or not at all.

## Validation Score: **88 / 100**

## Risks
1. **Customer acquisition cost** may exceed initial PLG projections in competitive channels.
2. **Regulatory changes** in {ind} could affect go-to-market timelines.
3. **Enterprise sales cycles** are typically 3–6× longer than SMB; initial cohort may skew.

## Recommendations
- Conduct 20 ICP discovery calls before writing a single line of code.
- Build a concierge MVP to validate willingness-to-pay in 2 weeks.
- Define the single sharpest wedge feature that proves the core hypothesis.

## Go / No-Go: ✅ **GO**
""",
            content_json=dict(
                problem_statement=t,
                proposed_solution=f"AI-native platform that automates {t.lower()}",
                target_customer=f"Growth-stage {ind} companies (10–200 employees)",
                validation_score=88,
                go_no_go="go",
                risks=[
                    "CAC may exceed initial PLG projections",
                    f"Regulatory changes in {ind} could affect GTM timeline",
                    "Enterprise sales cycles 3–6× longer than SMB",
                ],
                recommendations=[
                    "Run 20 ICP discovery calls before building",
                    "Concierge MVP to validate willingness-to-pay",
                    "Identify single sharpest wedge feature",
                ],
            ),
        ),
        # 2 ── market_research
        dict(
            module_key="market_research",
            artifact_type="market_analysis",
            title=f"Market Analysis — {p}",
            content_markdown=f"""# Market Research: {p}

## Market Sizing
| Tier | Value | Notes |
|------|-------|-------|
| **TAM** | $4.8B | Global addressable market, growing 18 % YoY |
| **SAM** | $960M | {ind} segment — early adopters + growth-stage |
| **SOM** | $48M | Realistic 5 % capture over 3 years |

## Competitive Landscape

| Competitor | Pricing | Strength | Weakness |
|------------|---------|----------|----------|
| Northwind Labs | $29/seat | Fast onboarding, Notion export | No AI copilot, weak analytics |
| Ideabench | Free / $19 | Large community | Shallow modules, no investor tooling |
| Foundry OS | $99/mo | Enterprise cohort features | Slow AI, enterprise-only pricing |

## Customer Segments
1. **Growth-stage {ind} startups (10–200 employees)** — highest urgency, shortest sales cycle.
2. **Enterprise innovation labs** — larger ACV, longer cycle, exceptional retention once landed.

## Key Trends
- AI adoption accelerating across {ind.lower()} — 62 % of companies piloting in 2026.
- Remote-first teams growing; async tooling demand up 3× since 2023.
- Vertical SaaS consolidation creating white-space for AI-native entrants.

## Entry Strategy
Product-led growth via a generous free tier, targeting team leads.
Viral mechanic: shared artifacts pull in collaborators organically.
""",
            content_json=dict(
                tam="$4.8B global market growing 18% YoY",
                sam=f"$960M — {ind} segment",
                som="$48M realistic 3-year target",
                market_segments=[
                    f"Growth-stage {ind} startups (10–200 employees)",
                    "Enterprise innovation labs",
                ],
                trends=[
                    f"AI adoption accelerating in {ind}",
                    "Remote-first teams driving async tooling demand",
                    "Vertical SaaS consolidation creating AI-native white-space",
                ],
                entry_strategy="Product-led growth via freemium with viral sharing mechanics",
                competitors=[
                    dict(name="Northwind Labs", description="Legacy SaaS tool",
                         strengths=["Fast onboarding","Notion export"],
                         weaknesses=["No AI copilot","Weak analytics"]),
                    dict(name="Ideabench", description="Freemium community tool",
                         strengths=["Great community"],
                         weaknesses=["Shallow modules","No investor tooling"]),
                    dict(name="Foundry OS", description="Enterprise platform",
                         strengths=["Cohort features","Mentor network"],
                         weaknesses=["Slow AI","Enterprise-only"]),
                ],
            ),
        ),
        # 3 ── business_model
        dict(
            module_key="business_model",
            artifact_type="business_model_canvas",
            title=f"Business Model Canvas — {p}",
            content_markdown=f"""# Business Model Canvas: {p}

| Block | Content |
|-------|---------|
| **Value Propositions** | AI-powered automation · 10× faster workflows · Measurable ROI in 30 days |
| **Customer Segments** | SMB teams 10–200 · Growth-stage {ind} startups · Innovation labs |
| **Channels** | PLG freemium · Content SEO · Developer / founder communities |
| **Customer Relationships** | Self-serve product · Dedicated CS for Team+ · Studio-tier concierge |
| **Revenue Streams** | Solo $29/mo · Team $99/mo · Annual 20 % discount · Usage-based AI credits |
| **Key Resources** | AI models · Engineering team · Founder network · Proprietary datasets |
| **Key Activities** | Product development · Customer success · AI model fine-tuning |
| **Key Partners** | Cloud providers · Integration partners · Accelerator programs |
| **Cost Structure** | AI inference · Engineering payroll · Sales & marketing · Infra |
""",
            content_json=dict(
                value_propositions=["AI-powered automation","10× faster workflows","Measurable ROI in 30 days"],
                customer_segments=[f"SMB {ind} teams 10–200","Growth-stage startups","Enterprise innovation labs"],
                channels=["PLG freemium","Content SEO","Developer communities"],
                customer_relationships=["Self-serve product","Dedicated CS for Team+","Studio-tier concierge"],
                revenue_streams=["$29/mo Solo","$99/mo Team","20% annual discount","Usage-based AI credits"],
                key_resources=["Proprietary AI models","Engineering team","Founder network"],
                key_activities=["Product development","Customer success","AI fine-tuning"],
                key_partnerships=["Cloud providers","Integration partners","Accelerator programs"],
                cost_structure=["AI inference ($0.002/call)","Engineering payroll","Sales & marketing"],
            ),
        ),
        # 4 ── product_strategy
        dict(
            module_key="product_strategy",
            artifact_type="product_roadmap",
            title=f"Product Roadmap — {p}",
            content_markdown=f"""# Product Roadmap: {p}

**Vision:** The default AI-native workspace for every {ind.lower()} team.

## Phase 1 — MVP (Weeks 1–6)
| Feature | Priority |
|---------|----------|
| Core AI workflow automation | P0 |
| {ind} tool integration | P0 |
| Basic analytics dashboard | P1 |

**Success metrics:** 50 active users · 40 % weekly retention · NPS > 40

## Phase 2 — Growth (Weeks 7–16)
| Feature | Priority |
|---------|----------|
| Team collaboration & comments | P0 |
| Advanced AI customisation | P0 |
| Public API + webhooks | P1 |
| Artifact version history | P1 |

**Success metrics:** $10k MRR · NPS > 55 · < 5 % monthly churn

## Phase 3 — Scale (Weeks 17–26)
| Feature | Priority |
|---------|----------|
| Enterprise SSO + audit logs | P0 |
| White-label options | P1 |
| Mobile app (iOS first) | P2 |

**Success metrics:** $50k MRR · 3 enterprise contracts · Series A ready
""",
            content_json=dict(
                vision=f"Default AI-native workspace for every {ind.lower()} team",
                phases=[
                    dict(name="MVP", duration="Weeks 1–6",
                         features=["Core AI workflow automation",f"{ind} tool integration","Basic analytics dashboard"],
                         success_metrics=["50 active users","40% weekly retention","NPS > 40"],
                         assumptions=["Users prefer async","Existing tools are fragmented"]),
                    dict(name="Growth", duration="Weeks 7–16",
                         features=["Team collaboration","Advanced AI customisation","Public API + webhooks","Artifact version history"],
                         success_metrics=["$10k MRR","NPS > 55","< 5% monthly churn"],
                         assumptions=["Teams pay for collaboration","API unlocks partnerships"]),
                    dict(name="Scale", duration="Weeks 17–26",
                         features=["Enterprise SSO + audit logs","White-label options","Mobile app (iOS first)"],
                         success_metrics=["$50k MRR","3 enterprise contracts","Series A ready"],
                         assumptions=["Enterprise buyers exist in segment"]),
                ],
            ),
        ),
        # 5 ── technical_architecture
        dict(
            module_key="technical_architecture",
            artifact_type="architecture_doc",
            title=f"Technical Architecture — {p}",
            content_markdown=f"""# Technical Architecture: {p}

## Overview
A cloud-native, AI-first architecture built for reliability, speed, and developer velocity.

## Technology Stack
| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15 · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui |
| **Backend** | FastAPI · Python 3.12 · SQLAlchemy (async) · Pydantic v2 |
| **Database** | PostgreSQL 16 · Redis (cache + queue) |
| **AI** | LangGraph · Ollama (Qwen 3 4B) · FAISS · BGE-base-en-v1.5 |
| **Infrastructure** | Docker · Railway (prod) · Cloudflare CDN |

## System Components
1. **API Gateway** — FastAPI with JWT auth, rate limiting, CORS, structured error responses.
2. **AI Pipeline** — Deterministic 8-node LangGraph workflow with SSE streaming.
3. **Vector Store** — Per-project FAISS indexes with SHA-256 deduplication.
4. **Background Jobs** — FastAPI BackgroundTasks with isolated async DB sessions.

## Data Flow
```
User → API Gateway → JWT Auth → Service Layer → PostgreSQL
Workflow trigger → LangGraph (8 nodes) → SSE events → Frontend
```

## Security
| Concern | Approach |
|---------|----------|
| **Authentication** | JWT access (15 min) + rotating refresh tokens (7 days) |
| **Authorisation** | Row-level ownership — users only access their own data |
| **Data at rest** | AES-256 encryption |
| **Data in transit** | TLS 1.3, HTTPS-only |
| **Secrets** | Environment variables, never committed |

## Scalability
Stateless API, horizontal pod scaling, async I/O throughout, connection pooling via asyncpg.
""",
            content_json=dict(
                overview=f"Cloud-native AI-first architecture for {p}",
                tech_stack=dict(
                    frontend="Next.js 15 · React 19 · TypeScript · Tailwind CSS v4",
                    backend="FastAPI · Python 3.12 · SQLAlchemy async · Pydantic v2",
                    database="PostgreSQL 16 · Redis cache + queue",
                    infrastructure="Docker · Railway · Cloudflare CDN",
                ),
                components=[
                    dict(name="API Gateway", responsibility="Auth, rate limiting, CORS", technology="FastAPI"),
                    dict(name="AI Pipeline", responsibility="8-node LangGraph workflow + SSE", technology="LangGraph + Ollama"),
                    dict(name="Vector Store", responsibility="Semantic search over artifacts", technology="FAISS + BGE-base-en-v1.5"),
                    dict(name="Background Jobs", responsibility="Isolated async workflow execution", technology="FastAPI BackgroundTasks"),
                ],
                data_flows=[
                    "User → API Gateway → JWT Auth → Service → PostgreSQL",
                    "Workflow trigger → LangGraph nodes → SSE stream → Frontend",
                ],
                security=dict(
                    authentication="JWT access (15 min) + rotating refresh (7 days)",
                    authorization="Row-level ownership per user_id",
                    data_protection="AES-256 at rest · TLS 1.3 in transit · HTTPS-only",
                ),
                scalability_notes="Stateless API, horizontal scaling, async I/O, connection pooling",
            ),
        ),
        # 6 ── financial_planning
        dict(
            module_key="financial_planning",
            artifact_type="financial_model",
            title=f"Financial Model — {p}",
            content_markdown=f"""# Financial Model: {p}

## Revenue Model
SaaS subscription — monthly and annual billing tiers.

## Unit Economics
| Metric | Value |
|--------|-------|
| **CAC** (PLG-assisted) | $180 |
| **ARPU** | $72/month |
| **LTV** (20-month avg retention) | $1,440 |
| **LTV : CAC ratio** | 8× |
| **Payback period** | 3 months |
| **Gross margin** | 82 % |

## 12-Month Revenue Projection
| Month | Revenue | Costs | Net |
|-------|---------|-------|-----|
| 1 | $2,400 | $8,000 | −$5,600 |
| 3 | $7,200 | $12,000 | −$4,800 |
| 6 | $22,000 | $18,000 | +$4,000 |
| 9 | $48,000 | $28,000 | +$20,000 |
| 12 | $85,000 | $40,000 | +$45,000 |

**Break-even: Month 7**

## Funding Required
**$500,000 seed round**
- 60 % product engineering
- 25 % GTM and sales
- 15 % operations
""",
            content_json=dict(
                revenue_model="SaaS subscription $29/$99/month, 20% annual discount",
                assumptions=[
                    "5% monthly churn rate",
                    "CAC $180 via PLG-assisted acquisition",
                    "82% gross margin on SaaS revenue",
                    "20-month average customer lifetime",
                    "3-month payback period on CAC",
                ],
                unit_economics=dict(cac="$180", ltv="$1,440", payback_period="3 months", gross_margin="82%"),
                monthly_projections=[
                    dict(month=i, revenue=int(2400*(1.28**(i-1))),
                         costs=int(8000+i*2800),
                         profit=int(2400*(1.28**(i-1)))-int(8000+i*2800))
                    for i in range(1, 13)
                ],
                funding_required="$500,000 seed round",
                break_even_month=7,
            ),
        ),
        # 7 ── marketing_strategy
        dict(
            module_key="marketing_strategy",
            artifact_type="marketing_plan",
            title=f"Marketing Strategy — {p}",
            content_markdown=f"""# Marketing Strategy: {p}

## Ideal Customer Profile
**{ind} founder or team lead** at a 10–200 person company.
- Urgency: Current tools are fragmented, slow, or require expensive consultants.
- Behaviour: Researches solutions via communities, Twitter/X, and content.
- Budget authority: Direct or one-step approval for tools < $200/month.

## Positioning
> "{p} — {t}"
> The only AI-native workspace that combines generation, versioning, and a structured workflow in one place.

## Channels
| Channel | Rationale | Key Tactics |
|---------|-----------|-------------|
| **Product Hunt** | High-intent early adopters | Launch-day campaign · 2,000 upvote target · Maker Q&A |
| **Founder communities** | Direct ICP access | YC forums · Indie Hackers · Twitter/X threads |
| **Content SEO** | Organic long-term | How-to guides · Competitor comparisons · Case studies |

## Launch Checklist
- [ ] Waitlist landing page — target 500 signups pre-launch
- [ ] 2-minute product demo video
- [ ] 3 beta user case studies with hard metrics
- [ ] Product Hunt launch assets (icon, gallery, tagline)
- [ ] Founder Twitter/X thread scheduled for launch day
- [ ] Warm outreach to 100 ICP contacts

## KPIs
| Period | Target |
|--------|--------|
| Week 1 | 500 signups · 50 activated accounts |
| Month 1 | $2,400 MRR · 10 paying customers |
| Month 3 | $10,000 MRR · NPS > 50 |
""",
            content_json=dict(
                icp=f"{ind} founder or team lead, 10–200 person company, budget authority for tools < $200/month",
                positioning=f"{p} — {t}",
                channels=[
                    dict(name="Product Hunt", rationale="High-intent early adopters",
                         tactics=["Launch-day campaign","2000 upvote target","Maker Q&A"]),
                    dict(name="Founder communities", rationale="Direct ICP access",
                         tactics=["YC alumni forums","Indie Hackers posts","Twitter/X threads"]),
                    dict(name="Content SEO", rationale="Organic long-term acquisition",
                         tactics=["Startup validation guides","Competitor comparisons","Case studies"]),
                ],
                messaging=dict(
                    tagline=t,
                    value_prop="From idea to investor-ready in days, not months",
                    objection_handling=[
                        "Integrates with your existing tools",
                        "No AI expertise required",
                        "Cancel anytime — keep all your data",
                    ],
                ),
                launch_checklist=[
                    "Waitlist landing page — 500 signups target",
                    "2-minute product demo video",
                    "3 beta user case studies with hard metrics",
                    "Product Hunt launch assets",
                    "Founder Twitter/X thread for launch day",
                    "Warm outreach to 100 ICP contacts",
                ],
                kpis=[
                    "Week 1: 500 signups, 50 activated",
                    "Month 1: $2,400 MRR, 10 customers",
                    "Month 3: $10,000 MRR, NPS > 50",
                ],
            ),
        ),
        # 8 ── investor_documentation
        dict(
            module_key="investor_documentation",
            artifact_type="investor_deck_outline",
            title=f"Investor Deck — {p} Seed Round",
            content_markdown=f"""# Investor Deck: {p}
## Seed Round — $500,000

---

### Slide 1 — Problem
Teams in {ind.lower()} waste 40 % of their time on fragmented manual work.
Existing tools are generic, disconnected, and expensive to integrate.

### Slide 2 — Solution
**{p}: {t}**
One AI-native workspace — generate, version, and connect every artifact your team needs.

### Slide 3 — Market Size
- **TAM** $4.8B growing 18 % YoY
- **SAM** $960M ({ind} segment)
- **SOM** $48M realistic 3-year capture

### Slide 4 — Product Demo
8 AI modules. Each produces real, editable artifacts. One connected workspace.
*[Demo video link]*

### Slide 5 — Business Model
SaaS: **$29/month** (Solo) · **$99/month** (Team)
82 % gross margin · 3-month payback · 8× LTV:CAC

### Slide 6 — Traction
- 240 waitlist signups (organic, zero spend)
- 3 design partners committed
- $4,200 early-access MRR

### Slide 7 — Team
**Ujjwal Verma** — CEO & Founder
Full-stack AI engineer, 2× builder background.

### Slide 8 — Financials
Break-even Month 7 · $85k MRR by Month 12 · Series A at $500k ARR

### Slide 9 — The Ask
**Raising $500,000 seed at $4M cap**
- 60 % product engineering
- 25 % GTM and sales
- 15 % operations

### Slide 10 — Vision
The AI-native operating system for every startup in the world.
""",
            content_json=dict(
                deck_title=f"{p} — Seed Round",
                ask=dict(
                    amount="$500,000",
                    use_of_funds=["60% product engineering","25% GTM and sales","15% operations"],
                    milestones=["$10k MRR by Month 3","$50k MRR by Month 9","Series A by Month 18"],
                ),
                slides=[
                    dict(number=i, title=title,
                         content_points=[f"Key insight for {title}", "Supporting data", "Memorable takeaway"],
                         speaker_notes=f"Deliver {title} with conviction and specific numbers.",
                         source_artifact="ai")
                    for i, title in enumerate([
                        "Problem","Solution","Market Size","Product Demo",
                        "Business Model","Traction & Validation","Team",
                        "Financials","The Ask","Vision & Roadmap",
                    ], 1)
                ],
            ),
        ),
    ]


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    async with Session() as db:
        # Get user
        row = (await db.execute(text("SELECT id FROM users WHERE email=:e"), {"e": USER_EMAIL})).fetchone()
        if not row:
            print("User not found"); return
        user_id = str(row[0])
        print(f"User: {USER_EMAIL} ({user_id})\n")

        # Get all projects for this user
        projects = (await db.execute(
            text("SELECT id, name, tagline, industry FROM projects WHERE user_id=:uid AND deleted_at IS NULL ORDER BY created_at"),
            {"uid": user_id}
        )).fetchall()

        print(f"Found {len(projects)} projects\n{'─'*60}")
        now = datetime.now(timezone.utc)

        for proj_row in projects:
            pid, name, tagline, industry = str(proj_row[0]), proj_row[1], proj_row[2] or "", proj_row[3] or "General"
            print(f"\n▶  {name} ({pid[:8]}…)")

            # ── 1. Mark all 8 modules as completed ──────────────────────────
            res = await db.execute(
                text("UPDATE project_modules SET status='completed', completed_at=:now, updated_at=:now "
                     "WHERE project_id=:pid"),
                {"pid": pid, "now": now}
            )
            print(f"   ✓ {res.rowcount} modules → completed")

            # ── 2. Upsert all 8 artifacts ────────────────────────────────────
            art_defs = artifacts_for(name, tagline, industry)
            added = updated = 0
            for art in art_defs:
                cj = json.dumps(art["content_json"])
                cm = art.get("content_markdown", "")
                # Check if artifact_type already exists for this project
                existing = (await db.execute(
                    text("SELECT id FROM artifacts WHERE project_id=:pid AND artifact_type=:at"),
                    {"pid": pid, "at": art["artifact_type"]}
                )).fetchone()

                if existing:
                    await db.execute(text("""
                        UPDATE artifacts
                        SET title=:title, content_json=CAST(:cj AS jsonb),
                            content_markdown=:cm, module_key=:mk,
                            updated_at=:now
                        WHERE project_id=:pid AND artifact_type=:at
                    """), {"title": art["title"], "cj": cj, "cm": cm,
                           "mk": art["module_key"], "now": now,
                           "pid": pid, "at": art["artifact_type"]})
                    updated += 1
                else:
                    await db.execute(text("""
                        INSERT INTO artifacts
                            (id, project_id, module_key, artifact_type,
                             title, content_json, content_markdown, source,
                             created_at, updated_at)
                        VALUES
                            (:id, :pid, :mk, :at,
                             :title, CAST(:cj AS jsonb), :cm, 'ai',
                             :now, :now)
                    """), {"id": str(uuid.uuid4()), "pid": pid,
                           "mk": art["module_key"], "at": art["artifact_type"],
                           "title": art["title"], "cj": cj, "cm": cm, "now": now})
                    added += 1

            print(f"   ✓ Artifacts — {added} added, {updated} updated")
            await db.commit()

        print(f"\n{'─'*60}")
        print("✅ All projects fully completed with all artifacts.\n")

        # ── Verify ────────────────────────────────────────────────────────────
        print("Verification:")
        for proj_row in projects:
            pid, name = str(proj_row[0]), proj_row[1]
            mod_count = (await db.execute(
                text("SELECT COUNT(*) FROM project_modules WHERE project_id=:pid AND status='completed'"),
                {"pid": pid}
            )).scalar()
            art_count = (await db.execute(
                text("SELECT COUNT(*) FROM artifacts WHERE project_id=:pid"),
                {"pid": pid}
            )).scalar()
            print(f"  {name:20s}  {mod_count}/8 modules completed  {art_count}/8 artifacts")

asyncio.run(main())
