import type { ActivityEvent, Artifact, NotificationItem, Project, StartupModule, ModuleId } from "./types";

// Stable base timestamp to avoid SSR/client hydration mismatches.
const BASE = new Date("2026-07-23T14:00:00Z").getTime();

const MODULE_META: Array<Pick<StartupModule, "id" | "name" | "description" | "icon">> = [
  { id: "idea-validation", name: "Idea Validation", description: "Test the core hypothesis with signals and evidence.", icon: "Lightbulb" },
  { id: "market-research", name: "Market Research", description: "TAM, SAM, SOM, competitors and positioning.", icon: "LineChart" },
  { id: "business-model", name: "Business Model", description: "Revenue, pricing, unit economics and canvas.", icon: "Layers" },
  { id: "product-strategy", name: "Product Strategy", description: "Roadmap, MVP scope and success metrics.", icon: "Compass" },
  { id: "technical-architecture", name: "Technical Architecture", description: "Stack, systems, data model and diagrams.", icon: "Network" },
  { id: "financial-planning", name: "Financial Planning", description: "3-year forecast, burn, runway, hiring plan.", icon: "Wallet" },
  { id: "marketing-strategy", name: "Marketing Strategy", description: "Positioning, channels, launch and content.", icon: "Megaphone" },
  { id: "investor-documentation", name: "Investor Documentation", description: "Deck, memo, data room and one-pager.", icon: "FileText" },
];

type StatusPattern = StartupModule["status"][];

function buildModules(pattern: StatusPattern): StartupModule[] {
  return MODULE_META.map((m, i) => {
    const s = pattern[i] ?? "locked";
    const progress = s === "complete" ? 100 : s === "review" ? 82 : s === "in_progress" ? 46 : s === "not_started" ? 0 : 0;
    return {
      ...m,
      status: s,
      progress,
      artifacts: s === "complete" ? 5 + i : s === "in_progress" ? 3 : s === "review" ? 4 : 0,
      updatedAt: new Date(BASE - i * 3.6e6 - 8.64e7).toISOString(),
    };
  });
}

function aggregate(modules: StartupModule[]) {
  return Math.round(modules.reduce((a, m) => a + m.progress, 0) / modules.length);
}

const covers = [
  "linear-gradient(135deg, oklch(0.55 0.22 275), oklch(0.72 0.18 320))",
  "linear-gradient(135deg, oklch(0.5 0.2 200), oklch(0.7 0.18 155))",
  "linear-gradient(135deg, oklch(0.55 0.22 25), oklch(0.72 0.2 60))",
  "linear-gradient(135deg, oklch(0.4 0.15 260), oklch(0.65 0.2 300))",
  "linear-gradient(135deg, oklch(0.45 0.2 310), oklch(0.68 0.18 340))",
];

// ─── PROJECT DEFINITIONS ────────────────────────────────────────────────────

const rawProjects = [
  {
    id: "prj_orbit",
    name: "Orbit",
    tagline: "Async standups for distributed AI teams.",
    industry: "Productivity",
    stage: "mvp" as const,
    cover: covers[0],
    pattern: ["complete","complete","in_progress","review","not_started","not_started","locked","locked"] as StatusPattern,
    updatedAt: new Date(BASE - 1000 * 60 * 42).toISOString(),
  },
  {
    id: "prj_kelp",
    name: "Kelp",
    tagline: "Carbon-negative delivery routing for last-mile fleets.",
    industry: "Climate",
    stage: "validation" as const,
    cover: covers[1],
    pattern: ["complete","complete","complete","in_progress","not_started","not_started","locked","locked"] as StatusPattern,
    updatedAt: new Date(BASE - 1000 * 60 * 60 * 4).toISOString(),
  },
  {
    id: "prj_ember",
    name: "Ember",
    tagline: "AI creative director for indie brands.",
    industry: "Marketing",
    stage: "ideation" as const,
    cover: covers[2],
    pattern: ["complete","in_progress","not_started","not_started","not_started","not_started","locked","locked"] as StatusPattern,
    updatedAt: new Date(BASE - 1000 * 60 * 60 * 22).toISOString(),
  },
  {
    id: "prj_lumen",
    name: "Lumen Health",
    tagline: "Ambient clinical scribe for outpatient practices.",
    industry: "Healthcare",
    stage: "launch" as const,
    cover: covers[3],
    pattern: ["complete","complete","complete","complete","complete","review","in_progress","not_started"] as StatusPattern,
    updatedAt: new Date(BASE - 1000 * 60 * 60 * 60).toISOString(),
  },
  {
    id: "prj_nexus",
    name: "Nexus",
    tagline: "Embedded finance infrastructure for B2B SaaS companies.",
    industry: "FinTech",
    stage: "growth" as const,
    cover: covers[4],
    pattern: ["complete","complete","complete","complete","complete","complete","complete","review"] as StatusPattern,
    updatedAt: new Date(BASE - 1000 * 60 * 60 * 120).toISOString(),
  },
];

export const MOCK_PROJECTS: Project[] = rawProjects.map(({ pattern, ...p }) => {
  const modules = buildModules(pattern);
  return { ...p, modules, progress: aggregate(modules) };
});

export function getProject(id: string): Project | undefined {
  return MOCK_PROJECTS.find((p) => p.id === id);
}

// ─── ARTIFACTS ──────────────────────────────────────────────────────────────

export const MOCK_ARTIFACTS: Artifact[] = [
  // ORBIT
  { id: "art_orb_1", projectId: "prj_orbit", moduleId: "idea-validation", title: "Validation Report — Orbit", type: "document", words: 2840, author: "AI", updatedAt: new Date(BASE - 15 * 24 * 3600000).toISOString() },
  { id: "art_orb_2", projectId: "prj_orbit", moduleId: "idea-validation", title: "Problem/Solution Interview Guide", type: "document", words: 1120, author: "You", updatedAt: new Date(BASE - 14 * 24 * 3600000).toISOString() },
  { id: "art_orb_3", projectId: "prj_orbit", moduleId: "market-research", title: "TAM/SAM/SOM Analysis — Async Collaboration", type: "document", words: 3420, author: "AI", updatedAt: new Date(BASE - 12 * 24 * 3600000).toISOString() },
  { id: "art_orb_4", projectId: "prj_orbit", moduleId: "market-research", title: "Competitive Matrix — 14 Competitors", type: "canvas", words: 1880, author: "AI", updatedAt: new Date(BASE - 11 * 24 * 3600000).toISOString() },
  { id: "art_orb_5", projectId: "prj_orbit", moduleId: "business-model", title: "Business Model Canvas", type: "canvas", words: 1240, author: "AI", updatedAt: new Date(BASE - 720 * 60000).toISOString() },
  { id: "art_orb_6", projectId: "prj_orbit", moduleId: "business-model", title: "Pricing Model — Per-Seat Analysis", type: "document", words: 980, author: "AI", updatedAt: new Date(BASE - 480 * 60000).toISOString() },
  { id: "art_orb_7", projectId: "prj_orbit", moduleId: "product-strategy", title: "Product Roadmap v2", type: "document", words: 3210, author: "You", updatedAt: new Date(BASE - 2 * 3600000).toISOString() },
  { id: "art_orb_8", projectId: "prj_orbit", moduleId: "technical-architecture", title: "System Architecture Diagram", type: "diagram", words: 640, author: "AI", updatedAt: new Date(BASE - 26 * 3600000).toISOString() },
  { id: "art_orb_9", projectId: "prj_orbit", moduleId: "financial-planning", title: "3-Year Financial Forecast", type: "spreadsheet", words: 980, author: "AI", updatedAt: new Date(BASE - 3 * 24 * 3600000).toISOString() },
  { id: "art_orb_10", projectId: "prj_orbit", moduleId: "investor-documentation", title: "Seed Deck — Draft v1", type: "deck", words: 1820, author: "AI", updatedAt: new Date(BASE - 5 * 24 * 3600000).toISOString() },

  // KELP
  { id: "art_klp_1", projectId: "prj_kelp", moduleId: "idea-validation", title: "Climate Delivery Hypothesis Report", type: "document", words: 3100, author: "AI", updatedAt: new Date(BASE - 20 * 24 * 3600000).toISOString() },
  { id: "art_klp_2", projectId: "prj_kelp", moduleId: "idea-validation", title: "Fleet Operator Discovery Interviews (12)", type: "document", words: 2200, author: "You", updatedAt: new Date(BASE - 19 * 24 * 3600000).toISOString() },
  { id: "art_klp_3", projectId: "prj_kelp", moduleId: "market-research", title: "Last-Mile Logistics Market Analysis — $130B TAM", type: "document", words: 4100, author: "AI", updatedAt: new Date(BASE - 16 * 24 * 3600000).toISOString() },
  { id: "art_klp_4", projectId: "prj_kelp", moduleId: "market-research", title: "42-Competitor Teardown", type: "canvas", words: 2800, author: "AI", updatedAt: new Date(BASE - 15 * 24 * 3600000).toISOString() },
  { id: "art_klp_5", projectId: "prj_kelp", moduleId: "market-research", title: "Differentiation Wedge — Carbon-Neutral Routing", type: "document", words: 1500, author: "AI", updatedAt: new Date(BASE - 14 * 24 * 3600000).toISOString() },
  { id: "art_klp_6", projectId: "prj_kelp", moduleId: "business-model", title: "SaaS + Carbon Credit Revenue Model", type: "document", words: 2100, author: "AI", updatedAt: new Date(BASE - 10 * 24 * 3600000).toISOString() },
  { id: "art_klp_7", projectId: "prj_kelp", moduleId: "business-model", title: "Business Model Canvas — Kelp", type: "canvas", words: 1320, author: "AI", updatedAt: new Date(BASE - 9 * 24 * 3600000).toISOString() },
  { id: "art_klp_8", projectId: "prj_kelp", moduleId: "product-strategy", title: "MVP Roadmap — Route Optimisation Engine", type: "document", words: 2900, author: "AI", updatedAt: new Date(BASE - 5 * 24 * 3600000).toISOString() },

  // EMBER
  { id: "art_emb_1", projectId: "prj_ember", moduleId: "idea-validation", title: "Indie Brand Creative AI — Validation Report", type: "document", words: 2400, author: "AI", updatedAt: new Date(BASE - 8 * 24 * 3600000).toISOString() },
  { id: "art_emb_2", projectId: "prj_ember", moduleId: "idea-validation", title: "ICP Definition — 0-to-1 Brand Founders", type: "document", words: 1100, author: "You", updatedAt: new Date(BASE - 7 * 24 * 3600000).toISOString() },

  // LUMEN HEALTH
  { id: "art_lmn_1", projectId: "prj_lumen", moduleId: "idea-validation", title: "Physician Burnout Problem Validation", type: "document", words: 3800, author: "AI", updatedAt: new Date(BASE - 30 * 24 * 3600000).toISOString() },
  { id: "art_lmn_2", projectId: "prj_lumen", moduleId: "market-research", title: "Clinical NLP Market — $8.2B SAM", type: "document", words: 4200, author: "AI", updatedAt: new Date(BASE - 27 * 24 * 3600000).toISOString() },
  { id: "art_lmn_3", projectId: "prj_lumen", moduleId: "business-model", title: "Per-Physician SaaS + EHR Integration Model", type: "document", words: 2600, author: "AI", updatedAt: new Date(BASE - 24 * 24 * 3600000).toISOString() },
  { id: "art_lmn_4", projectId: "prj_lumen", moduleId: "business-model", title: "Business Model Canvas — Lumen Health", type: "canvas", words: 1400, author: "AI", updatedAt: new Date(BASE - 23 * 24 * 3600000).toISOString() },
  { id: "art_lmn_5", projectId: "prj_lumen", moduleId: "product-strategy", title: "Ambient Scribe MVP — 10-Week Build Plan", type: "document", words: 3400, author: "AI", updatedAt: new Date(BASE - 20 * 24 * 3600000).toISOString() },
  { id: "art_lmn_6", projectId: "prj_lumen", moduleId: "technical-architecture", title: "HIPAA-Compliant Architecture — Epic & Athena Integration", type: "diagram", words: 1800, author: "AI", updatedAt: new Date(BASE - 17 * 24 * 3600000).toISOString() },
  { id: "art_lmn_7", projectId: "prj_lumen", moduleId: "financial-planning", title: "Seed Financial Model — 3-Year Projection", type: "spreadsheet", words: 1200, author: "AI", updatedAt: new Date(BASE - 14 * 24 * 3600000).toISOString() },
  { id: "art_lmn_8", projectId: "prj_lumen", moduleId: "marketing-strategy", title: "Clinical Champion GTM Strategy", type: "document", words: 2800, author: "AI", updatedAt: new Date(BASE - 7 * 24 * 3600000).toISOString() },
  { id: "art_lmn_9", projectId: "prj_lumen", moduleId: "investor-documentation", title: "Seed Deck — Lumen Health v3", type: "deck", words: 2100, author: "AI", updatedAt: new Date(BASE - 4 * 3600000).toISOString() },

  // NEXUS
  { id: "art_nxs_1", projectId: "prj_nexus", moduleId: "idea-validation", title: "Embedded Finance Opportunity Analysis", type: "document", words: 3600, author: "AI", updatedAt: new Date(BASE - 45 * 24 * 3600000).toISOString() },
  { id: "art_nxs_2", projectId: "prj_nexus", moduleId: "market-research", title: "B2B SaaS Embedded Finance — $220B Opportunity", type: "document", words: 5200, author: "AI", updatedAt: new Date(BASE - 40 * 24 * 3600000).toISOString() },
  { id: "art_nxs_3", projectId: "prj_nexus", moduleId: "business-model", title: "API-First Revenue Architecture", type: "document", words: 2800, author: "AI", updatedAt: new Date(BASE - 35 * 24 * 3600000).toISOString() },
  { id: "art_nxs_4", projectId: "prj_nexus", moduleId: "product-strategy", title: "Developer SDK Roadmap — 3 Phases", type: "document", words: 3900, author: "AI", updatedAt: new Date(BASE - 30 * 24 * 3600000).toISOString() },
  { id: "art_nxs_5", projectId: "prj_nexus", moduleId: "technical-architecture", title: "Microservices Architecture — Payment Rails", type: "diagram", words: 2100, author: "AI", updatedAt: new Date(BASE - 25 * 24 * 3600000).toISOString() },
  { id: "art_nxs_6", projectId: "prj_nexus", moduleId: "financial-planning", title: "Series A Financial Model — 5-Year Projection", type: "spreadsheet", words: 1800, author: "AI", updatedAt: new Date(BASE - 18 * 24 * 3600000).toISOString() },
  { id: "art_nxs_7", projectId: "prj_nexus", moduleId: "marketing-strategy", title: "Developer-First GTM — Documentation & DevRel", type: "document", words: 3200, author: "AI", updatedAt: new Date(BASE - 12 * 24 * 3600000).toISOString() },
  { id: "art_nxs_8", projectId: "prj_nexus", moduleId: "investor-documentation", title: "Series A Deck — Nexus v4 (Current)", type: "deck", words: 2800, author: "AI", updatedAt: new Date(BASE - 4 * 24 * 3600000).toISOString() },
  { id: "art_nxs_9", projectId: "prj_nexus", moduleId: "investor-documentation", title: "Data Room Index — 23 Documents", type: "document", words: 980, author: "You", updatedAt: new Date(BASE - 2 * 24 * 3600000).toISOString() },
];

export function projectArtifacts(projectId: string, moduleId?: ModuleId) {
  return MOCK_ARTIFACTS.filter((a) => a.projectId === projectId && (!moduleId || a.moduleId === moduleId));
}

// ─── ACTIVITY ────────────────────────────────────────────────────────────────

export const MOCK_ACTIVITY: ActivityEvent[] = [
  { id: "a1", projectId: "prj_orbit", projectName: "Orbit", kind: "generated", title: "Business Model Canvas", detail: "AI produced 9 blocks with unit economics", timestamp: new Date(BASE - 12 * 60000).toISOString() },
  { id: "a2", projectId: "prj_kelp", projectName: "Kelp", kind: "completed", title: "Market Research", detail: "TAM $130B / SAM $18B / SOM $420M identified", timestamp: new Date(BASE - 55 * 60000).toISOString() },
  { id: "a3", projectId: "prj_orbit", projectName: "Orbit", kind: "edited", title: "Product Roadmap v2", detail: "You revised the MVP scope and timeline", timestamp: new Date(BASE - 2 * 3600000).toISOString() },
  { id: "a4", projectId: "prj_lumen", projectName: "Lumen Health", kind: "started", title: "Investor Deck Drafting", detail: "AI is generating seed narrative — ETA 4 min", timestamp: new Date(BASE - 5 * 3600000).toISOString() },
  { id: "a5", projectId: "prj_ember", projectName: "Ember", kind: "generated", title: "Positioning Statement", detail: "3 variants ready for review", timestamp: new Date(BASE - 20 * 3600000).toISOString() },
  { id: "a6", projectId: "prj_nexus", projectName: "Nexus", kind: "completed", title: "Series A Deck", detail: "Deck v4 exported and shared with 8 investors", timestamp: new Date(BASE - 28 * 3600000).toISOString() },
  { id: "a7", projectId: "prj_lumen", projectName: "Lumen Health", kind: "completed", title: "Technical Architecture", detail: "HIPAA-compliant design reviewed and approved", timestamp: new Date(BASE - 36 * 3600000).toISOString() },
];

// ─── NOTIFICATIONS ────────────────────────────────────────────────────────────

export const MOCK_NOTIFICATIONS: NotificationItem[] = [
  { id: "n1", title: "Orbit — Business Model ready for review", detail: "AI completed 9/9 blocks with financial modeling.", timestamp: new Date(BASE - 8 * 60000).toISOString(), unread: true, kind: "ai" },
  { id: "n2", title: "Kelp — Market Research complete", detail: "42 competitors analyzed. 3 whitespace opportunities identified.", timestamp: new Date(BASE - 55 * 60000).toISOString(), unread: true, kind: "ai" },
  { id: "n3", title: "Weekly digest", detail: "You made progress across 4 projects this week.", timestamp: new Date(BASE - 26 * 3600000).toISOString(), unread: false, kind: "system" },
  { id: "n4", title: "Lumen Health — Investor deck drafting", detail: "Seed narrative in progress. ETA 4 minutes.", timestamp: new Date(BASE - 4 * 3600000).toISOString(), unread: false, kind: "ai" },
  { id: "n5", title: "Nexus — Series A Deck exported", detail: "PDF sent to 8 investors via data room link.", timestamp: new Date(BASE - 28 * 3600000).toISOString(), unread: true, kind: "ai" },
  { id: "n6", title: "Ember — ICP validation complete", detail: "Your ideal customer profile has been refined with 12 signals.", timestamp: new Date(BASE - 7 * 24 * 3600000).toISOString(), unread: false, kind: "ai" },
];

// ─── AI ACTIVITY CHART DATA ───────────────────────────────────────────────────

export const AI_ACTIVITY = Array.from({ length: 30 }, (_, i) => ({
  day: i + 1,
  generations: Math.round(30 + Math.sin(i / 3) * 12 + (((i * 7 + 11) % 13) / 13) * 8),
  edits: Math.round(15 + Math.cos(i / 4) * 8 + (((i * 5 + 3) % 9) / 9) * 5),
}));

export const MODULE_LIST = MODULE_META;
