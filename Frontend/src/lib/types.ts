// ─── DISPLAY / FRONTEND TYPES (kept intact) ─────────────────────────────────

export type ModuleId =
  | "idea-validation"
  | "market-research"
  | "business-model"
  | "product-strategy"
  | "technical-architecture"
  | "financial-planning"
  | "marketing-strategy"
  | "investor-documentation";

export type ModuleStatus = "locked" | "not_started" | "in_progress" | "review" | "complete";

export interface StartupModule {
  id: ModuleId;
  name: string;
  description: string;
  status: ModuleStatus;
  progress: number; // 0..100
  icon: string; // lucide icon name key
  artifacts: number;
  updatedAt: string;
}

export interface Project {
  id: string;
  name: string;
  tagline: string;
  industry: string;
  stage: "ideation" | "validation" | "mvp" | "launch" | "growth";
  progress: number; // aggregate 0..100
  cover: string; // hex or gradient token
  updatedAt: string;
  modules: StartupModule[];
}

export interface Artifact {
  id: string;
  projectId: string;
  moduleId: ModuleId;
  title: string;
  type: "document" | "diagram" | "spreadsheet" | "deck" | "canvas";
  words: number;
  updatedAt: string;
  author: "AI" | "You";
}

export interface ActivityEvent {
  id: string;
  projectId: string;
  projectName: string;
  kind: "generated" | "edited" | "commented" | "completed" | "started";
  title: string;
  detail: string;
  timestamp: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  detail: string;
  timestamp: string;
  unread: boolean;
  kind: "ai" | "system" | "collab";
}

// ─── BACKEND API TYPES ───────────────────────────────────────────────────────

export type BackendModuleKey =
  | "idea_validation"
  | "market_research"
  | "business_model"
  | "product_strategy"
  | "technical_architecture"
  | "financial_planning"
  | "marketing_strategy"
  | "investor_documentation";

export type BackendModuleStatus =
  | "locked"
  | "available"
  | "in_progress"
  | "completed"
  | "failed";

export interface BackendUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: BackendUser;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
}

export interface BackendModule {
  id: string;
  project_id: string;
  module_key: BackendModuleKey;
  display_name: string;
  status: BackendModuleStatus;
  sort_order: number;
  last_run_id: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendProject {
  id: string;
  user_id: string;
  name: string;
  tagline: string | null;
  idea_brief: string;
  industry: string | null;
  stage: string;
  created_at: string;
  updated_at: string;
}

export interface BackendProjectWithModules extends BackendProject {
  modules: BackendModule[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface BackendArtifact {
  id: string;
  project_id: string;
  module_key: string;
  artifact_type: string;
  title: string;
  content_json: Record<string, unknown>;
  content_markdown: string | null;
  source: "ai" | "user";
  workflow_run_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendArtifactVersion {
  id: string;
  artifact_id: string;
  version_number: number;
  content_json: Record<string, unknown>;
  content_markdown: string | null;
  change_summary: string | null;
  created_at: string;
}

export interface WorkflowRunStep {
  id: string;
  step_key: string;
  status: string;
  sequence: number;
}

export interface BackendWorkflowRun {
  id: string;
  project_id: string;
  module_key: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  error_code: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  steps: WorkflowRunStep[];
}

export interface TriggerWorkflowResponse {
  run_id: string;
  status: string;
  stream_url: string;
}

export interface CreateProjectInput {
  name: string;
  idea_brief: string;
  tagline?: string;
  industry?: string;
}

export interface UpdateProjectInput {
  name?: string;
  idea_brief?: string;
  tagline?: string;
  industry?: string;
  stage?: string;
}

export interface EditArtifactInput {
  content_json: Record<string, unknown>;
  content_markdown?: string;
  change_summary?: string;
}

// SSE event payload
export interface SSEEvent {
  type: "step_started" | "step_completed" | "run_completed" | "run_failed";
  step_key?: string;
  run_id?: string;
  status?: string;
  error_message?: string;
  timestamp?: string;
}
