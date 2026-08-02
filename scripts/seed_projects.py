#!/usr/bin/env python3
"""
Seed 4 complete demo projects with full artifacts via the backend API.
Usage:  python scripts/seed_projects.py
"""
import json, sys
import urllib.request, urllib.error

BASE = "http://localhost:8000/api/v1"
EMAIL = "ujjwalvermauv2004@gmail.com"
PASSWORD = "Ujjwal@123"

def call(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"  HTTP {e.code} {method} {path}: {msg[:200]}")
        return None

# ── Auth ──────────────────────────────────────────────────────────────────────
print("Logging in...")
auth = call("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
if not auth:
    sys.exit("Login failed")
TOKEN = auth["access_token"]
print(f"  Logged in as {auth['user']['full_name']}")


# ── Project definitions ────────────────────────────────────────────────────────
PROJECTS = [
    {
        "name": "Orbit",
        "tagline": "Async standups for distributed AI teams.",
        "industry": "Productivity",
        "stage": "mvp",
        "idea_brief": (
            "Orbit is an async standup tool built for distributed AI-first engineering teams. "
            "Instead of 30-minute daily syncs, Orbit uses AI to collect updates via Slack, "
            "summarise blockers, and surface action items — saving each team member 2+ hours per week. "
            "Target: 10-200 person AI-native startups. Revenue: $12/seat/month SaaS."
        ),
    },
    {
        "name": "Kelp",
        "tagline": "Carbon-negative delivery routing for last-mile fleets.",
        "industry": "Climate",
        "stage": "validation",
        "idea_brief": (
            "Kelp optimises last-mile delivery routes to minimise carbon emissions, partnering with "
            "carbon credit registries to generate offsets for every tonne saved. Fleet operators get "
            "lower fuel costs and a verified sustainability badge. The SaaS platform charges per-vehicle "
            "per-month with a revenue share on carbon credits sold."
        ),
    },
    {
        "name": "Lumen Health",
        "tagline": "Ambient clinical scribe for outpatient practices.",
        "industry": "Healthcare",
        "stage": "launch",
        "idea_brief": (
            "Lumen Health is an ambient AI clinical scribe that listens to patient-physician "
            "conversations and auto-generates SOAP notes in real time, integrated with Epic and Athena. "
            "Physicians spend 2 hours/day on documentation — Lumen cuts that by 70%. "
            "HIPAA-compliant, FDA-cleared pathway. $149/physician/month. Targeting outpatient clinics "
            "with 3-50 physicians."
        ),
    },
    {
        "name": "Nexus",
        "tagline": "Embedded finance infrastructure for vertical SaaS companies.",
        "industry": "FinTech",
        "stage": "growth",
        "idea_brief": (
            "Nexus provides a developer SDK that lets any vertical SaaS company embed payments, "
            "lending, and insurance into their product in days, not months. Revenue model: "
            "0.4% take rate on payment volume + origination fees on loans. "
            "Target: SaaS companies with 500+ SMB customers who want to monetise financial flows "
            "without building infrastructure. Series A stage, $2M ARR."
        ),
    },
]


# ── Artifacts per module ───────────────────────────────────────────────────────
# artifact_type must be unique per project (backend constraint)
# We use the module_key as the artifact_type prefix to make them unique

def make_artifacts(project_name, industry, tagline):
    return [
        {
            "module_key": "idea_validation",
            "artifact_type": "validation_report",
            "title": f"Validation Report — {project_name}",
            "source": "ai",
            "content_markdown": f"""# Validation Report: {project_name}

## Problem Statement
{tagline} The core problem is real, urgent, and underserved by existing solutions.

## Target Customer
Early-adopting teams in the {industry} space who feel acute pain from the status quo.

## Validation Score: 87/100

## Risks
1. Customer acquisition cost may exceed initial projections in competitive channels
2. Regulatory changes could impact go-to-market timeline
3. Enterprise sales cycles longer than expected for initial cohort

## Recommendations
- Run 20 discovery calls with target ICP in the next 2 weeks
- Build a concierge MVP to validate willingness to pay before full build
- Define the single sharpest wedge feature that proves the core hypothesis

## Go/No-Go: **GO**
""",
            "content_json": {
                "problem_statement": tagline,
                "validation_score": 87,
                "go_no_go": "go",
                "risks": [
                    "Customer acquisition cost may exceed initial projections",
                    "Regulatory changes could impact go-to-market timeline",
                    "Enterprise sales cycles longer than expected"
                ],
                "recommendations": [
                    "Run 20 discovery calls with target ICP",
                    "Build concierge MVP to validate willingness to pay",
                    "Define single sharpest wedge feature"
                ]
            }
        },
        {
            "module_key": "market_research",
            "artifact_type": "market_analysis",
            "title": f"Market Analysis — {project_name}",
            "source": "ai",
            "content_markdown": f"""# Market Research: {project_name}

## TAM / SAM / SOM
- **TAM**: $4.2B global addressable market growing at 18% YoY
- **SAM**: $820M — {industry} segment of early adopters and growth-stage companies
- **SOM**: $41M — realistic 5% capture in 3 years at current trajectory

## Top Competitors
| Company | Pricing | Weakness |
|---------|---------|----------|
| Competitor A | $29/seat | No AI, weak analytics |
| Competitor B | Free/$19 | Shallow modules, no enterprise |
| Competitor C | $99/mo | Slow, enterprise-only |

## Market Segments
1. Growth-stage startups (10-200 employees) — highest urgency, fastest sales cycle
2. Enterprise innovation teams — larger deals, longer cycle, strong retention

## Entry Strategy
Product-led growth via freemium, targeting team leads with viral adoption mechanics.
""",
            "content_json": {
                "tam": "$4.2B global market",
                "sam": "$820M serviceable market",
                "som": "$41M 3-year target",
                "market_segments": ["Growth-stage startups (10-200 employees)", "Enterprise innovation teams"],
                "entry_strategy": "Product-led growth via freemium with viral adoption mechanics",
                "competitors": [
                    {"name": "Competitor A", "strengths": ["Fast onboarding"], "weaknesses": ["No AI copilot"]},
                    {"name": "Competitor B", "strengths": ["Great community"], "weaknesses": ["Shallow modules"]},
                    {"name": "Competitor C", "strengths": ["Enterprise features"], "weaknesses": ["Slow AI"]}
                ]
            }
        },
    ]


def make_business_model_artifact(project_name):
    return {
        "module_key": "business_model",
        "artifact_type": "business_model_canvas",
        "title": f"Business Model Canvas — {project_name}",
        "source": "ai",
        "content_markdown": f"""# Business Model Canvas: {project_name}

| Block | Content |
|-------|---------|
| Value Propositions | AI-powered automation, 10x faster workflows, measurable ROI |
| Customer Segments | SMB teams, growth-stage startups, innovation teams |
| Channels | PLG, content marketing, developer communities |
| Customer Relationships | Self-serve + dedicated success for enterprise |
| Revenue Streams | SaaS subscriptions ($29/$99/mo), usage-based pricing |
| Key Resources | AI models, engineering team, founder network |
| Key Activities | Product development, customer success, AI training |
| Key Partners | Cloud providers, integration partners, accelerators |
| Cost Structure | AI inference, engineering payroll, sales & marketing |
""",
        "content_json": {
            "value_propositions": ["AI-powered automation", "10x faster workflows", "Measurable ROI"],
            "customer_segments": ["SMB teams", "Growth-stage startups", "Innovation teams"],
            "channels": ["PLG", "Content marketing", "Developer communities"],
            "customer_relationships": ["Self-serve", "Dedicated success for enterprise"],
            "revenue_streams": ["SaaS $29/$99/mo", "Usage-based pricing"],
            "key_resources": ["AI models", "Engineering team", "Founder network"],
            "key_activities": ["Product development", "Customer success", "AI training"],
            "key_partnerships": ["Cloud providers", "Integration partners", "Accelerators"],
            "cost_structure": ["AI inference", "Engineering payroll", "Sales and marketing"]
        }
    }

def make_product_strategy_artifact(project_name):
    return {
        "module_key": "product_strategy",
        "artifact_type": "product_roadmap",
        "title": f"Product Roadmap — {project_name}",
        "source": "ai",
        "content_markdown": f"""# Product Roadmap: {project_name}

## Vision
Become the default AI-native workspace for founders and teams in this space.

## Phase 1 — MVP (Weeks 1-6)
- Core AI workflow automation
- Slack/email integration
- Basic analytics dashboard
**Success metric**: 50 active users, 40% weekly retention

## Phase 2 — Growth (Weeks 7-16)
- Team collaboration features
- Advanced AI customisation
- API + webhooks
**Success metric**: $10k MRR, NPS > 50

## Phase 3 — Scale (Weeks 17-26)
- Enterprise SSO and audit logs
- White-label options
- Mobile app
**Success metric**: $50k MRR, 3 enterprise contracts
""",
        "content_json": {
            "vision": "Default AI-native workspace for this category",
            "phases": [
                {
                    "name": "MVP",
                    "duration": "Weeks 1-6",
                    "features": ["Core AI workflow automation", "Slack/email integration", "Basic analytics"],
                    "success_metrics": ["50 active users", "40% weekly retention"],
                    "assumptions": ["Users prefer async over sync", "Slack is primary work surface"]
                },
                {
                    "name": "Growth",
                    "duration": "Weeks 7-16",
                    "features": ["Team collaboration", "Advanced AI customisation", "API + webhooks"],
                    "success_metrics": ["$10k MRR", "NPS > 50"],
                    "assumptions": ["Teams will pay for collaboration features"]
                },
                {
                    "name": "Scale",
                    "duration": "Weeks 17-26",
                    "features": ["Enterprise SSO", "White-label options", "Mobile app"],
                    "success_metrics": ["$50k MRR", "3 enterprise contracts"],
                    "assumptions": ["Enterprise buyers exist in this category"]
                }
            ]
        }
    }


def make_technical_artifact(project_name):
    return {
        "module_key": "technical_architecture",
        "artifact_type": "architecture_doc",
        "title": f"Technical Architecture — {project_name}",
        "source": "ai",
        "content_markdown": f"""# Technical Architecture: {project_name}

## Stack
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.12 + SQLAlchemy (async)
- **Database**: PostgreSQL 16 + Redis (cache/queue)
- **AI**: LangGraph + Ollama (Qwen 3 4B) + FAISS vector store
- **Infrastructure**: Docker + Railway (prod) + Cloudflare CDN

## Components
1. **API Gateway** — FastAPI with JWT auth, rate limiting, CORS
2. **AI Pipeline** — LangGraph 8-node workflow with SSE streaming
3. **Vector Store** — FAISS per-project embeddings (BGE-base-en-v1.5)
4. **Background Jobs** — FastAPI BackgroundTasks with async DB sessions

## Security
- Authentication: JWT access tokens (15 min) + refresh rotation (7 days)
- Authorisation: Row-level security — users only access their own data
- Data protection: AES-256 at rest, TLS 1.3 in transit
""",
        "content_json": {
            "overview": f"Modern AI-native stack for {project_name}",
            "tech_stack": {
                "frontend": "Next.js 15 + React 19 + TypeScript",
                "backend": "FastAPI + Python 3.12 + SQLAlchemy",
                "database": "PostgreSQL 16 + Redis",
                "infrastructure": "Docker + Railway + Cloudflare"
            },
            "components": [
                {"name": "API Gateway", "responsibility": "Auth, rate limiting, CORS", "technology": "FastAPI"},
                {"name": "AI Pipeline", "responsibility": "LangGraph 8-node workflow", "technology": "LangGraph + Ollama"},
                {"name": "Vector Store", "responsibility": "Semantic search over artifacts", "technology": "FAISS"}
            ],
            "data_flows": ["User → API → Auth → Service → DB", "Workflow trigger → LangGraph → SSE → Frontend"],
            "security": {
                "authentication": "JWT access + refresh token rotation",
                "authorization": "Row-level security per user",
                "data_protection": "AES-256 at rest, TLS 1.3 in transit"
            },
            "scalability_notes": "Stateless API, horizontal scaling via container orchestration"
        }
    }

def make_financial_artifact(project_name):
    return {
        "module_key": "financial_planning",
        "artifact_type": "financial_model",
        "title": f"Financial Model — {project_name}",
        "source": "ai",
        "content_markdown": f"""# Financial Model: {project_name}

## Revenue Model
SaaS subscription with monthly and annual billing tiers.

## Unit Economics
- **CAC**: $180 (PLG-assisted)
- **LTV**: $1,440 (20-month avg retention × $72 ARPU)
- **LTV:CAC Ratio**: 8x
- **Payback Period**: 3 months
- **Gross Margin**: 82%

## 12-Month Projections
| Month | Revenue | Costs | Profit |
|-------|---------|-------|--------|
| 1 | $2,400 | $8,000 | -$5,600 |
| 3 | $7,200 | $12,000 | -$4,800 |
| 6 | $22,000 | $18,000 | $4,000 |
| 9 | $48,000 | $28,000 | $20,000 |
| 12 | $85,000 | $40,000 | $45,000 |

## Funding Required: $500,000 seed
Break-even at Month 7.
""",
        "content_json": {
            "revenue_model": "SaaS subscription $29/$99/month",
            "assumptions": [
                "5% monthly churn",
                "CAC of $180 via PLG",
                "82% gross margin",
                "20-month average LTV",
                "3-month sales cycle for SMB"
            ],
            "unit_economics": {
                "cac": "$180",
                "ltv": "$1,440",
                "payback_period": "3 months",
                "gross_margin": "82%"
            },
            "monthly_projections": [
                {"month": i, "revenue": int(2400 * (1.28 ** (i-1))), 
                 "costs": int(8000 + i * 2800),
                 "profit": int(2400 * (1.28 ** (i-1))) - int(8000 + i * 2800)}
                for i in range(1, 13)
            ],
            "funding_required": "$500,000 seed round",
            "break_even_month": 7
        }
    }

def make_marketing_artifact(project_name, tagline):
    return {
        "module_key": "marketing_strategy",
        "artifact_type": "marketing_plan",
        "title": f"Marketing Strategy — {project_name}",
        "source": "ai",
        "content_markdown": f"""# Marketing Strategy: {project_name}

## Ideal Customer Profile
Growth-stage founder or team lead who is resource-constrained and wants to move fast.
Pain: current tools are fragmented, slow, or require expensive consultants.

## Positioning
"{project_name} — {tagline}" 
The only tool that combines AI generation with a structured workspace.

## Channels
1. **Product Hunt** — launch day spike, 2,000+ upvotes target
2. **Founder communities** — YC alumni, Indie Hackers, Twitter/X
3. **Content SEO** — "how to validate a startup idea" cluster

## Launch Checklist
- [ ] Build waitlist landing page (500 signups target)
- [ ] Record 2-minute demo video
- [ ] Write 3 case studies from beta users
- [ ] Prepare Product Hunt assets
- [ ] Schedule founder Twitter thread on launch day
- [ ] Warm outreach to 100 ICP contacts

## KPIs
- Week 1: 500 signups, 50 activated accounts
- Month 1: $2,400 MRR, 10 paying customers
- Month 3: $10,000 MRR, NPS > 50
""",
        "content_json": {
            "icp": "Growth-stage founder or team lead, resource-constrained, wants to move fast",
            "positioning": f"{project_name} — {tagline}",
            "channels": [
                {"name": "Product Hunt", "rationale": "High-intent early adopters", "tactics": ["Launch day spike", "2000 upvote target"]},
                {"name": "Founder communities", "rationale": "Direct ICP access", "tactics": ["YC forums", "Twitter/X threads"]},
                {"name": "Content SEO", "rationale": "Organic long-term growth", "tactics": ["Startup validation guides", "Comparison articles"]}
            ],
            "messaging": {
                "tagline": tagline,
                "value_prop": "From idea to investor-ready in days, not months",
                "objection_handling": ["We integrate with your existing tools", "No AI expertise needed", "Cancel anytime"]
            },
            "launch_checklist": [
                "Build waitlist landing page (500 signups target)",
                "Record 2-minute demo video",
                "Write 3 case studies from beta users",
                "Prepare Product Hunt assets",
                "Schedule founder Twitter thread on launch day",
                "Warm outreach to 100 ICP contacts"
            ],
            "kpis": ["Week 1: 500 signups", "Month 1: $2,400 MRR", "Month 3: $10,000 MRR, NPS > 50"]
        }
    }

def make_investor_artifact(project_name, tagline, industry):
    return {
        "module_key": "investor_documentation",
        "artifact_type": "investor_deck_outline",
        "title": f"Investor Deck — {project_name} Seed Round",
        "source": "ai",
        "content_markdown": f"""# Investor Deck: {project_name}

## Slide 1 — Problem
Founders and teams in the {industry} space waste 40% of their time on manual work that AI can automate. Existing tools are fragmented, generic, and require expensive consultants.

## Slide 2 — Solution
{project_name}: {tagline}. An AI-native workspace that generates, organises, and connects every artifact a team needs to grow.

## Slide 3 — Market Size
- TAM: $4.2B global market
- SAM: $820M (our initial segment)
- Growing at 18% YoY

## Slide 4 — Product
8 AI modules. Each produces real, editable artifacts. One connected workspace.
Demo: [link]

## Slide 5 — Business Model
SaaS: $29/month (Solo) | $99/month (Team)
82% gross margin. 3-month payback period.

## Slide 6 — Traction
- 240 waitlist signups (organic)
- 3 design partners committed
- $4,200 MRR from early access

## Slide 7 — Team
- Ujjwal Verma — CEO & Founder. Builder, 2x founder background.

## Slide 8 — Financials
Break-even at Month 7. Projecting $85k MRR by Month 12.

## Slide 9 — The Ask
Raising $500,000 seed at $4M cap. Use of funds: 60% product, 25% GTM, 15% ops.

## Slide 10 — Vision
The AI-native operating system for every startup in the world.
""",
        "content_json": {
            "deck_title": f"{project_name} — Seed Round",
            "ask": {
                "amount": "$500,000",
                "use_of_funds": ["60% product engineering", "25% GTM and sales", "15% operations"],
                "milestones": ["$10k MRR by Month 3", "$50k MRR by Month 9", "Series A by Month 18"]
            },
            "slides": [
                {"number": i, "title": t, "content_points": [f"Key point for {t}"], "speaker_notes": f"Speak to {t} with conviction", "source_artifact": "ai"}
                for i, t in enumerate([
                    "Problem", "Solution", "Market Size", "Product Demo",
                    "Business Model", "Traction", "Team", "Financials",
                    "The Ask", "Vision"
                ], 1)
            ]
        }
    }


# ── Module status progression per project ────────────────────────────────────
# Maps project index → which modules to mark completed
MODULE_KEYS = [
    "idea_validation", "market_research", "business_model",
    "product_strategy", "technical_architecture",
    "financial_planning", "marketing_strategy", "investor_documentation"
]

# Project 0 (Orbit/mvp): first 3 completed, #4 in_progress
# Project 1 (Kelp/validation): first 2 completed, #3 in_progress
# Project 2 (Lumen/launch): first 6 completed, #7 in_progress
# Project 3 (Nexus/growth): all 8 completed
COMPLETIONS = [
    ["idea_validation", "market_research"],              # Orbit — 2 done, biz model in progress
    ["idea_validation"],                                  # Kelp — 1 done, market research in progress
    ["idea_validation", "market_research", "business_model", "product_strategy", "technical_architecture"],  # Lumen — 5 done
    ["idea_validation", "market_research", "business_model", "product_strategy", "technical_architecture", "financial_planning", "marketing_strategy"],  # Nexus — 7 done
]

def get_artifacts_for_project(idx, project_name, tagline, industry):
    """Return the artifacts to create based on how complete each project is."""
    artifacts = make_artifacts(project_name, industry, tagline)
    artifacts.append(make_business_model_artifact(project_name))
    if idx >= 1:
        artifacts.append(make_product_strategy_artifact(project_name))
    if idx >= 2:
        artifacts.append(make_technical_artifact(project_name))
        artifacts.append(make_financial_artifact(project_name))
    if idx >= 3:
        artifacts.append(make_marketing_artifact(project_name, tagline))
        artifacts.append(make_investor_artifact(project_name, tagline, industry))
    return artifacts

# ── Main seeding loop ─────────────────────────────────────────────────────────
print(f"\nSeeding {len(PROJECTS)} projects...\n")

created_ids = []
for idx, proj_def in enumerate(PROJECTS):
    print(f"[{idx+1}/{len(PROJECTS)}] Creating project: {proj_def['name']}")

    # Create the project
    proj = call("POST", "/projects", {
        "name": proj_def["name"],
        "tagline": proj_def["tagline"],
        "industry": proj_def["industry"],
        "idea_brief": proj_def["idea_brief"],
    }, TOKEN)

    if not proj:
        print(f"  SKIP — failed to create project")
        continue

    pid = proj["id"]
    created_ids.append(pid)
    print(f"  Created project {pid}")

    # Update stage (patch)
    updated = call("PATCH", f"/projects/{pid}", {"stage": proj_def["stage"]}, TOKEN)
    if updated:
        print(f"  Stage set to: {proj_def['stage']}")

    # Create artifacts
    artifacts = get_artifacts_for_project(idx, proj_def["name"], proj_def["tagline"], proj_def["industry"])
    for art in artifacts:
        result = call("POST", f"/projects/{pid}/artifacts", art, TOKEN)
        if result:
            print(f"  + Artifact: {art['title']}")
        else:
            print(f"  ! Failed to create artifact: {art['title']}")

    print()

print(f"Done! Created {len(created_ids)} projects.")
print("Project IDs:", created_ids)
