#!/usr/bin/env python3
"""
Seed 4 complete demo projects with realistic artifacts directly into the DB.
Run from the backend directory:
  cd /Users/ujjwal/Desktop/FoundrAI/backend
  poetry run python ../scripts/seed_demo_projects.py
"""
import asyncio, sys, os, uuid
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/backend")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://foundrai:foundrai_dev@127.0.0.1:5432/foundrai"
USER_EMAIL = "ujjwalvermauv2004@gmail.com"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

MODULE_KEYS = [
    "idea_validation", "market_research", "business_model",
    "product_strategy", "technical_architecture",
    "financial_planning", "marketing_strategy", "investor_documentation",
]
MODULE_NAMES = {
    "idea_validation": "Idea Validation",
    "market_research": "Market Research",
    "business_model": "Business Model",
    "product_strategy": "Product Strategy",
    "technical_architecture": "Technical Architecture",
    "financial_planning": "Financial Planning",
    "marketing_strategy": "Marketing Strategy",
    "investor_documentation": "Investor Documentation",
}

PROJECTS = [
    {
        "name": "Orbit",
        "tagline": "Async standups for distributed AI teams.",
        "industry": "Productivity",
        "stage": "mvp",
        "idea_brief": "Orbit is an async standup tool for distributed AI-first teams. AI collects updates via Slack, summarises blockers, and surfaces action items — saving each team 2+ hours/week. Target: 10-200 person AI-native startups. $12/seat/month.",
        "complete_modules": ["idea_validation", "market_research"],
        "inprogress_module": "business_model",
    },
    {
        "name": "Kelp",
        "tagline": "Carbon-negative delivery routing for last-mile fleets.",
        "industry": "Climate",
        "stage": "validation",
        "idea_brief": "Kelp optimises last-mile delivery routes to minimise carbon emissions, partnering with carbon credit registries to generate offsets for every tonne saved. Fleet operators get lower fuel costs and a verified sustainability badge.",
        "complete_modules": ["idea_validation", "market_research", "business_model"],
        "inprogress_module": "product_strategy",
    },
    {
        "name": "Lumen Health",
        "tagline": "Ambient clinical scribe for outpatient practices.",
        "industry": "Healthcare",
        "stage": "launch",
        "idea_brief": "Lumen Health is an ambient AI clinical scribe that listens to patient-physician conversations and auto-generates SOAP notes integrated with Epic and Athena. Physicians spend 2 hours/day on documentation — Lumen cuts that by 70%. HIPAA-compliant. $149/physician/month.",
        "complete_modules": ["idea_validation", "market_research", "business_model", "product_strategy", "technical_architecture"],
        "inprogress_module": "financial_planning",
    },
    {
        "name": "Nexus",
        "tagline": "Embedded finance infrastructure for vertical SaaS companies.",
        "industry": "FinTech",
        "stage": "growth",
        "idea_brief": "Nexus provides a developer SDK that lets any vertical SaaS company embed payments, lending, and insurance in days. Revenue: 0.4% take rate on payment volume. Target: SaaS companies with 500+ SMB customers. Series A stage, $2M ARR.",
        "complete_modules": ["idea_validation", "market_research", "business_model", "product_strategy", "technical_architecture", "financial_planning", "marketing_strategy"],
        "inprogress_module": "investor_documentation",
    },
]

def make_artifact_for_module(module_key: str, project_name: str, tagline: str, industry: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    base = {"project_name": project_name, "tagline": tagline, "industry": industry}

    if module_key == "idea_validation":
        return {
            "artifact_type": "validation_report",
            "title": f"Validation Report — {project_name}",
            "content_markdown": f"# Validation Report: {project_name}\n\n**Problem:** {tagline}\n\n**Validation Score: 87/100**\n\n**Risks:**\n1. CAC may exceed early projections\n2. Regulatory headwinds in {industry}\n3. Enterprise sales cycles longer than expected\n\n**Go/No-Go: GO**",
            "content_json": {"problem_statement": tagline, "validation_score": 87, "go_no_go": "go", "target_customer": f"{industry} teams and founders", "proposed_solution": f"AI-powered platform for {tagline.lower()}", "risks": ["CAC may exceed projections", f"Regulatory headwinds in {industry}", "Enterprise sales cycles longer than expected"], "recommendations": ["Run 20 customer discovery calls", "Build concierge MVP first", "Validate willingness to pay before full build"]},
        }
    if module_key == "market_research":
        return {
            "artifact_type": "market_analysis",
            "title": f"Market Analysis — {project_name}",
            "content_markdown": f"# Market Research: {project_name}\n\n**TAM:** $4.2B growing 18% YoY\n**SAM:** $820M ({industry} segment)\n**SOM:** $41M (3-year target)\n\n## Competitors\n- Competitor A: $29/seat, weak analytics\n- Competitor B: Free/$19, shallow modules\n- Competitor C: $99/mo, enterprise-only\n\n## Entry Strategy\nPLG via freemium. Target team leads with viral adoption mechanics.",
            "content_json": {"tam": "$4.2B global market", "sam": "$820M serviceable market", "som": "$41M 3-year target", "market_segments": [f"Growth-stage {industry} startups", "Enterprise innovation teams"], "entry_strategy": "Product-led growth via freemium", "trends": ["AI adoption accelerating", "Remote-first teams growing", "Vertical SaaS consolidation"], "competitors": [{"name": "Competitor A", "description": "Legacy solution", "strengths": ["Fast onboarding"], "weaknesses": ["No AI copilot", "Weak analytics"]}, {"name": "Competitor B", "description": "Freemium tool", "strengths": ["Great community"], "weaknesses": ["Shallow modules", "No investor tooling"]}, {"name": "Competitor C", "description": "Enterprise platform", "strengths": ["Enterprise features", "Mentor network"], "weaknesses": ["Slow AI", "Enterprise-only"]}]},
        }
    if module_key == "business_model":
        return {
            "artifact_type": "business_model_canvas",
            "title": f"Business Model Canvas — {project_name}",
            "content_markdown": f"# Business Model Canvas: {project_name}\n\n| Block | Content |\n|---|---|\n| Value Props | AI automation, 10x speed, measurable ROI |\n| Segments | SMB teams, growth startups, innovation labs |\n| Channels | PLG, content SEO, communities |\n| Revenue | $29/$99/mo SaaS, usage-based upsell |\n| Costs | AI inference, engineering, GTM |",
            "content_json": {"value_propositions": ["AI-powered automation", "10x faster workflows", "Measurable ROI in 30 days"], "customer_segments": ["SMB teams 10-200 employees", "Growth-stage startups", "Innovation labs"], "channels": ["PLG via freemium", "Content SEO", "Developer communities"], "customer_relationships": ["Self-serve product", "Dedicated CSM for enterprise"], "revenue_streams": ["$29/month Solo", "$99/month Team", "Usage-based AI credits"], "key_resources": ["AI models", "Engineering team", "Founder network"], "key_activities": ["Product development", "Customer success", "AI model fine-tuning"], "key_partnerships": ["Cloud providers", "Integration partners", "Accelerator programs"], "cost_structure": ["AI inference ($0.002/call)", "Engineering payroll", "Sales and marketing"]},
        }
    if module_key == "product_strategy":
        return {
            "artifact_type": "product_roadmap",
            "title": f"Product Roadmap — {project_name}",
            "content_markdown": f"# Product Roadmap: {project_name}\n\n**Vision:** Default AI workspace for {industry} teams.\n\n## Phase 1 — MVP (Weeks 1-6)\n- Core AI workflow\n- Slack integration\n- Basic analytics\n*Target: 50 users, 40% weekly retention*\n\n## Phase 2 — Growth (Weeks 7-16)\n- Team collaboration\n- API + webhooks\n*Target: $10k MRR, NPS > 50*\n\n## Phase 3 — Scale (Weeks 17-26)\n- Enterprise SSO\n- Mobile app\n*Target: $50k MRR*",
            "content_json": {"vision": f"Default AI-native workspace for {industry} teams", "phases": [{"name": "MVP", "duration": "Weeks 1-6", "features": ["Core AI workflow automation", f"Integration with {industry} tools", "Basic analytics dashboard"], "success_metrics": ["50 active users", "40% weekly retention"], "assumptions": ["Users prefer async over meetings", "Slack is primary work surface"]}, {"name": "Growth", "duration": "Weeks 7-16", "features": ["Team collaboration features", "Advanced AI customisation", "Public API + webhooks"], "success_metrics": ["$10k MRR", "NPS > 50"], "assumptions": ["Teams pay for collaboration features"]}, {"name": "Scale", "duration": "Weeks 17-26", "features": ["Enterprise SSO and audit logs", "White-label options", "Mobile app"], "success_metrics": ["$50k MRR", "3 enterprise contracts"], "assumptions": ["Enterprise buyers exist in segment"]}]},
        }
    if module_key == "technical_architecture":
        return {
            "artifact_type": "architecture_doc",
            "title": f"Technical Architecture — {project_name}",
            "content_markdown": f"# Technical Architecture: {project_name}\n\n## Stack\n- **Frontend:** Next.js 15 + React 19 + TypeScript\n- **Backend:** FastAPI + Python 3.12 + SQLAlchemy (async)\n- **Database:** PostgreSQL 16 + Redis\n- **AI:** LangGraph + Ollama (Qwen3 4B) + FAISS\n- **Infra:** Docker + Railway\n\n## Security\n- JWT auth (15min access + 7day refresh rotation)\n- Row-level security — users only see their own data\n- AES-256 at rest, TLS 1.3 in transit",
            "content_json": {"overview": f"Modern AI-native stack for {project_name}", "tech_stack": {"frontend": "Next.js 15 + React 19 + TypeScript + Tailwind", "backend": "FastAPI + Python 3.12 + SQLAlchemy async", "database": "PostgreSQL 16 + Redis cache", "infrastructure": "Docker + Railway + Cloudflare CDN"}, "components": [{"name": "API Gateway", "responsibility": "Auth, rate limiting, CORS handling", "technology": "FastAPI"}, {"name": "AI Pipeline", "responsibility": "8-node LangGraph workflow with SSE streaming", "technology": "LangGraph + Ollama"}, {"name": "Vector Store", "responsibility": "Semantic search over project artifacts", "technology": "FAISS + BGE-base-en-v1.5"}], "data_flows": ["User → API → JWT Auth → Service Layer → PostgreSQL", "Workflow trigger → LangGraph nodes → SSE events → Frontend"], "security": {"authentication": "JWT access tokens (15min) + refresh rotation (7 days)", "authorization": "Row-level security, users only access own data", "data_protection": "AES-256 at rest, TLS 1.3 in transit, HTTPS-only"}, "scalability_notes": "Stateless API with horizontal scaling, async throughout"},
        }
    if module_key == "financial_planning":
        return {
            "artifact_type": "financial_model",
            "title": f"Financial Model — {project_name}",
            "content_markdown": f"# Financial Model: {project_name}\n\n## Unit Economics\n- **CAC:** $180 | **LTV:** $1,440 | **LTV:CAC:** 8x\n- **Payback:** 3 months | **Gross Margin:** 82%\n\n## Projections\n| Month | Revenue | Costs | Profit |\n|---|---|---|---|\n| 3 | $7,200 | $12,000 | -$4,800 |\n| 6 | $22,000 | $18,000 | +$4,000 |\n| 9 | $48,000 | $28,000 | +$20,000 |\n| 12 | $85,000 | $40,000 | +$45,000 |\n\n**Funding Required:** $500k seed. Break-even: Month 7.",
            "content_json": {"revenue_model": "SaaS subscription $29/$99/month with annual discount", "assumptions": ["5% monthly churn rate", "CAC $180 via PLG-assisted", "82% gross margin on SaaS", "20-month average customer lifetime", "3-month payback period"], "unit_economics": {"cac": "$180", "ltv": "$1,440", "payback_period": "3 months", "gross_margin": "82%"}, "monthly_projections": [{"month": i, "revenue": int(2400*(1.28**(i-1))), "costs": int(8000+i*2800), "profit": int(2400*(1.28**(i-1)))-int(8000+i*2800)} for i in range(1,13)], "funding_required": "$500,000 seed round", "break_even_month": 7},
        }
    if module_key == "marketing_strategy":
        return {
            "artifact_type": "marketing_plan",
            "title": f"Marketing Strategy — {project_name}",
            "content_markdown": f"# Marketing Strategy: {project_name}\n\n## ICP\n{industry} team lead or founder, resource-constrained, wants to move fast without expensive consultants.\n\n## Channels\n1. **Product Hunt** — launch day, 2,000+ upvote target\n2. **Founder communities** — YC, Indie Hackers, Twitter/X\n3. **Content SEO** — startup how-to cluster\n\n## Launch Checklist\n- Build waitlist page (500 signups)\n- Record 2-min demo video\n- 3 beta user case studies\n- Product Hunt assets\n- Founder Twitter thread\n- 100-contact warm outreach\n\n## KPIs: $2.4k MRR Month 1 → $10k MRR Month 3",
            "content_json": {"icp": f"{industry} founder or team lead, 10-200 person company, wants AI leverage without consultant overhead", "positioning": f"{project_name} — {tagline}", "channels": [{"name": "Product Hunt", "rationale": "High-intent early adopters", "tactics": ["Launch day campaign", "2000 upvote target", "Maker Q&A"]}, {"name": "Founder communities", "rationale": "Direct ICP access", "tactics": ["YC alumni forums", "Indie Hackers posts", "Twitter/X threads"]}, {"name": "Content SEO", "rationale": "Organic long-term acquisition", "tactics": ["Startup validation guides", "Competitor comparisons", "How-to tutorials"]}], "messaging": {"tagline": tagline, "value_prop": "From idea to investor-ready in days, not months", "objection_handling": ["Integrates with your existing tools", "No AI expertise required", "Cancel anytime, keep all your data"]}, "launch_checklist": ["Build waitlist landing page targeting 500 signups", "Record 2-minute product demo video", "Collect 3 beta user case studies with hard metrics", "Prepare complete Product Hunt launch assets", "Schedule founder Twitter/X thread for launch day", "Execute warm outreach to 100 ICP contacts"], "kpis": ["Week 1: 500 signups, 50 activated", "Month 1: $2,400 MRR, 10 customers", "Month 3: $10,000 MRR, NPS > 50"]},
        }
    if module_key == "investor_documentation":
        return {
            "artifact_type": "investor_deck_outline",
            "title": f"Investor Deck — {project_name} Seed Round",
            "content_markdown": f"# Investor Deck: {project_name}\n\n## Slide 1 — Problem\nTeams in {industry} waste 40% of time on manual work. Existing tools are fragmented and require expensive consultants.\n\n## Slide 2 — Solution\n{project_name}: {tagline}\n\n## Slide 3 — Market\nTAM $4.2B | SAM $820M | Growing 18% YoY\n\n## Slide 4 — Traction\n240 waitlist · 3 design partners · $4.2k MRR\n\n## Slide 5 — Team\nUjjwal Verma — CEO & Founder\n\n## Slide 6 — The Ask\n**$500,000 seed** at $4M cap.\n60% product · 25% GTM · 15% ops",
            "content_json": {"deck_title": f"{project_name} — Seed Round", "ask": {"amount": "$500,000", "use_of_funds": ["60% product engineering and AI", "25% GTM and sales", "15% operations and legal"], "milestones": ["$10k MRR by Month 3", "$50k MRR by Month 9", "Series A by Month 18"]}, "slides": [{"number": i, "title": t, "content_points": [f"Key insight for {t}", "Supporting data point", "Memorable takeaway"], "speaker_notes": f"Deliver {t} with conviction and specific numbers", "source_artifact": "ai"} for i, t in enumerate(["Problem", "Solution", "Market Size", "Product Demo", "Business Model", "Traction & Validation", "Team", "Financials", "The Ask", "Vision & Roadmap"], 1)]},
        }
    return {}


async def seed():
    async with SessionLocal() as db:
        # Get user id
        result = await db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": USER_EMAIL})
        row = result.fetchone()
        if not row:
            print(f"User {USER_EMAIL} not found"); return
        user_id = str(row[0])
        print(f"Seeding for user: {USER_EMAIL} ({user_id})\n")

        for proj_def in PROJECTS:
            name = proj_def["name"]
            print(f"Creating: {name}")

            # Insert project
            pid = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            await db.execute(text("""
                INSERT INTO projects (id, user_id, name, tagline, idea_brief, industry, stage, created_at, updated_at)
                VALUES (:id, :uid, :name, :tagline, :brief, :industry, :stage, :now, :now)
                ON CONFLICT DO NOTHING
            """), {"id": pid, "uid": user_id, "name": name,
                   "tagline": proj_def["tagline"], "brief": proj_def["idea_brief"],
                   "industry": proj_def["industry"], "stage": proj_def["stage"], "now": now})

            # Insert 8 modules
            completed = proj_def["complete_modules"]
            inprog = proj_def["inprogress_module"]
            for i, mk in enumerate(MODULE_KEYS):
                if mk in completed:
                    status = "completed"
                elif mk == inprog:
                    status = "in_progress"
                elif i == 0 or MODULE_KEYS[i-1] in completed:
                    status = "available"
                else:
                    status = "locked"
                mid = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO project_modules (id, project_id, module_key, display_name, status, sort_order, created_at, updated_at)
                    VALUES (:id, :pid, :mk, :dn, :status, :order, :now, :now)
                    ON CONFLICT DO NOTHING
                """), {"id": mid, "pid": pid, "mk": mk, "dn": MODULE_NAMES[mk],
                       "status": status, "order": i, "now": now})

            # Insert artifacts for completed + in-progress modules
            art_modules = completed + ([inprog] if inprog else [])
            for mk in art_modules:
                art = make_artifact_for_module(mk, name, proj_def["tagline"], proj_def["industry"])
                if not art:
                    continue
                aid = str(uuid.uuid4())
                import json
                cj = json.dumps(art["content_json"])
                # Check unique constraint (project_id, artifact_type)
                exists = await db.execute(text(
                    "SELECT id FROM artifacts WHERE project_id=:pid AND artifact_type=:at"),
                    {"pid": pid, "at": art["artifact_type"]})
                if exists.fetchone():
                    continue
                await db.execute(text("""
                    INSERT INTO artifacts (id, project_id, module_key, artifact_type, title,
                        content_json, content_markdown, source, created_at, updated_at)
                    VALUES (:id, :pid, :mk, :at, :title, :cj, :cm, 'ai', :now, :now)
                """), {"id": aid, "pid": pid, "mk": mk, "at": art["artifact_type"],
                       "title": art["title"], "cj": cj,
                       "cm": art.get("content_markdown"), "now": now})
                print(f"  + {art['title']}")

            await db.commit()
            print(f"  Done: {name} ({pid})\n")

    print("All projects seeded successfully!")

asyncio.run(seed())
