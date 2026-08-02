import type {
  BackendModule,
  BackendModuleKey,
  BackendModuleStatus,
  BackendProjectWithModules,
  ModuleId,
  ModuleStatus,
  Project,
  StartupModule,
} from "./types";

// ─── Module key mappings ──────────────────────────────────────────────────────

const MODULE_KEY_TO_ID: Record<BackendModuleKey, ModuleId> = {
  idea_validation: "idea-validation",
  market_research: "market-research",
  business_model: "business-model",
  product_strategy: "product-strategy",
  technical_architecture: "technical-architecture",
  financial_planning: "financial-planning",
  marketing_strategy: "marketing-strategy",
  investor_documentation: "investor-documentation",
};

const MODULE_KEY_TO_DISPLAY: Record<BackendModuleKey, string> = {
  idea_validation: "Idea Validation",
  market_research: "Market Research",
  business_model: "Business Model",
  product_strategy: "Product Strategy",
  technical_architecture: "Technical Architecture",
  financial_planning: "Financial Planning",
  marketing_strategy: "Marketing Strategy",
  investor_documentation: "Investor Documentation",
};

const MODULE_KEY_TO_ICON: Record<BackendModuleKey, string> = {
  idea_validation: "Lightbulb",
  market_research: "LineChart",
  business_model: "Layers",
  product_strategy: "Compass",
  technical_architecture: "Network",
  financial_planning: "Wallet",
  marketing_strategy: "Megaphone",
  investor_documentation: "FileText",
};

const MODULE_KEY_TO_DESCRIPTION: Record<BackendModuleKey, string> = {
  idea_validation: "Test the core hypothesis with signals and evidence.",
  market_research: "TAM, SAM, SOM, competitors and positioning.",
  business_model: "Revenue, pricing, unit economics and canvas.",
  product_strategy: "Roadmap, MVP scope and success metrics.",
  technical_architecture: "Stack, systems, data model and diagrams.",
  financial_planning: "3-year forecast, burn, runway, hiring plan.",
  marketing_strategy: "Positioning, channels, launch and content.",
  investor_documentation: "Deck, memo, data room and one-pager.",
};

// ─── Status mappings ──────────────────────────────────────────────────────────

const STATUS_MAP: Record<BackendModuleStatus, ModuleStatus> = {
  locked: "locked",
  available: "not_started",
  in_progress: "in_progress",
  completed: "complete",
  failed: "not_started", // treat failed as not_started for display
};

/** Progress percentage per backend status */
const STATUS_PROGRESS: Record<BackendModuleStatus, number> = {
  locked: 0,
  available: 0,
  in_progress: 50,
  completed: 100,
  failed: 0,
};

// ─── Cover gradient palette ───────────────────────────────────────────────────

const COVERS = [
  "linear-gradient(135deg, oklch(0.55 0.22 275), oklch(0.72 0.18 320))",
  "linear-gradient(135deg, oklch(0.5 0.2 200), oklch(0.7 0.18 155))",
  "linear-gradient(135deg, oklch(0.55 0.22 25), oklch(0.72 0.2 60))",
  "linear-gradient(135deg, oklch(0.4 0.15 260), oklch(0.65 0.2 300))",
  "linear-gradient(135deg, oklch(0.45 0.2 310), oklch(0.68 0.18 340))",
];

function hashId(id: string): number {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) & 0xffffffff;
  }
  return Math.abs(hash);
}

function getCover(id: string): string {
  return COVERS[hashId(id) % COVERS.length];
}

// ─── Stage normalisation ──────────────────────────────────────────────────────

type DisplayStage = Project["stage"];

function normaliseStage(stage: string): DisplayStage {
  const map: Record<string, DisplayStage> = {
    ideation: "ideation",
    validation: "validation",
    mvp: "mvp",
    launch: "launch",
    growth: "growth",
  };
  return map[stage?.toLowerCase()] ?? "ideation";
}

// ─── Module mapper ────────────────────────────────────────────────────────────

export function mapBackendModule(m: BackendModule): StartupModule {
  const key = m.module_key as BackendModuleKey;
  const backendStatus = m.status as BackendModuleStatus;

  return {
    id: MODULE_KEY_TO_ID[key] ?? (m.module_key as ModuleId),
    name: MODULE_KEY_TO_DISPLAY[key] ?? m.display_name,
    description: MODULE_KEY_TO_DESCRIPTION[key] ?? "",
    status: STATUS_MAP[backendStatus] ?? "locked",
    progress: STATUS_PROGRESS[backendStatus] ?? 0,
    icon: MODULE_KEY_TO_ICON[key] ?? "Sparkles",
    artifacts: 0, // populated separately from artifacts API
    updatedAt: m.updated_at,
  };
}

// ─── Project mapper ───────────────────────────────────────────────────────────

export function mapBackendProjectToDisplay(p: BackendProjectWithModules): Project {
  const modules = [...p.modules]
    .sort((a, b) => a.sort_order - b.sort_order)
    .map(mapBackendModule);

  const progress = modules.length
    ? Math.round(modules.reduce((sum, m) => sum + m.progress, 0) / modules.length)
    : 0;

  return {
    id: p.id,
    name: p.name,
    tagline: p.tagline ?? "",
    industry: p.industry ?? "General",
    stage: normaliseStage(p.stage),
    progress,
    cover: getCover(p.id),
    updatedAt: p.updated_at,
    modules,
  };
}
