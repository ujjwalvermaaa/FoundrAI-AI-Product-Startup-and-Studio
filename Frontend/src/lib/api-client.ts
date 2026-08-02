import { toast } from "sonner";
import type {
  AuthResponse,
  BackendArtifact,
  BackendArtifactVersion,
  BackendProjectWithModules,
  BackendWorkflowRun,
  CreateProjectInput,
  EditArtifactInput,
  PaginatedResponse,
  RefreshResponse,
  TriggerWorkflowResponse,
  UpdateProjectInput,
} from "./types";

const API_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000/api/v1";

const ACCESS_TOKEN_KEY = "foundrai_access_token";
const REFRESH_TOKEN_KEY = "foundrai_refresh_token";

// ─── Token helpers ────────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
  skipErrorToast?: boolean;
}

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

async function attemptTokenRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) {
      clearTokens();
      return null;
    }

    const data = (await res.json()) as RefreshResponse;
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { skipAuth = false, skipErrorToast = false, ...fetchOptions } = options;

  const headers = new Headers(fetchOptions.headers);

  if (!headers.has("Content-Type") && !(fetchOptions.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (!skipAuth) {
    const token = getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const url = `${API_URL}${path}`;
  let res = await fetch(url, { ...fetchOptions, headers });

  // 401 → try refresh once
  if (res.status === 401 && !skipAuth) {
    if (isRefreshing) {
      // Wait for the in-flight refresh
      const newToken = await new Promise<string | null>((resolve) => {
        refreshQueue.push(resolve);
      });
      if (newToken) {
        headers.set("Authorization", `Bearer ${newToken}`);
        res = await fetch(url, { ...fetchOptions, headers });
      }
    } else {
      isRefreshing = true;
      const newToken = await attemptTokenRefresh();
      isRefreshing = false;

      // Drain queue
      refreshQueue.forEach((cb) => cb(newToken));
      refreshQueue = [];

      if (newToken) {
        headers.set("Authorization", `Bearer ${newToken}`);
        res = await fetch(url, { ...fetchOptions, headers });
      } else {
        // Refresh failed — redirect to login
        clearTokens();
        window.location.href = "/auth/login";
        throw new Error("Session expired. Please sign in again.");
      }
    }
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const err = await res.json();
      message = err?.detail ?? err?.message ?? message;
    } catch {
      // ignore
    }
    if (!skipErrorToast) {
      toast.error(message);
    }
    throw new Error(message);
  }

  // 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string, full_name: string) =>
    apiFetch<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
      skipAuth: true,
      skipErrorToast: true,
    }),

  login: (email: string, password: string) =>
    apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      skipAuth: true,
      skipErrorToast: true,
    }),

  refresh: (refresh_token: string) =>
    apiFetch<RefreshResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
      skipAuth: true,
    }),

  logout: () =>
    apiFetch<void>("/auth/logout", {
      method: "POST",
    }),

  me: () =>
    apiFetch<AuthResponse["user"]>("/auth/me", {
      skipErrorToast: true,
    }),
};

// ─── Projects ─────────────────────────────────────────────────────────────────

export const projectsApi = {
  list: (skip = 0, limit = 50) =>
    apiFetch<PaginatedResponse<BackendProjectWithModules>>(
      `/projects?skip=${skip}&limit=${limit}`,
    ),

  get: (id: string) =>
    apiFetch<BackendProjectWithModules>(`/projects/${id}`),

  create: (data: CreateProjectInput) =>
    apiFetch<BackendProjectWithModules>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: UpdateProjectInput) =>
    apiFetch<BackendProjectWithModules>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    apiFetch<void>(`/projects/${id}`, {
      method: "DELETE",
    }),
};

// ─── Artifacts ────────────────────────────────────────────────────────────────

export const artifactsApi = {
  list: (projectId: string, skip = 0, limit = 50) =>
    apiFetch<PaginatedResponse<BackendArtifact>>(
      `/projects/${projectId}/artifacts?skip=${skip}&limit=${limit}`,
    ),

  get: (projectId: string, artifactId: string) =>
    apiFetch<BackendArtifact>(`/projects/${projectId}/artifacts/${artifactId}`),

  edit: (projectId: string, artifactId: string, data: EditArtifactInput) =>
    apiFetch<BackendArtifact>(`/projects/${projectId}/artifacts/${artifactId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  listVersions: (projectId: string, artifactId: string) =>
    apiFetch<BackendArtifactVersion[]>(
      `/projects/${projectId}/artifacts/${artifactId}/versions`,
    ),
};

// ─── Workflows ────────────────────────────────────────────────────────────────

export const workflowsApi = {
  trigger: (projectId: string, moduleKey: string) =>
    apiFetch<TriggerWorkflowResponse>(
      `/projects/${projectId}/workflows/${moduleKey}/run`,
      { method: "POST" },
    ),

  listRuns: (projectId: string, skip = 0, limit = 50) =>
    apiFetch<PaginatedResponse<BackendWorkflowRun>>(
      `/projects/${projectId}/workflows/runs?skip=${skip}&limit=${limit}`,
    ),

  getRun: (projectId: string, runId: string) =>
    apiFetch<BackendWorkflowRun>(
      `/projects/${projectId}/workflows/runs/${runId}`,
    ),

  cancelRun: (projectId: string, runId: string) =>
    apiFetch<void>(
      `/projects/${projectId}/workflows/runs/${runId}/cancel`,
      { method: "POST" },
    ),

  /** Returns an EventSource connected to the run's SSE stream. Caller must close it. */
  streamUrl: (projectId: string, runId: string): string =>
    `${API_URL}/projects/${projectId}/workflows/runs/${runId}/stream`,
};

export default apiFetch;
