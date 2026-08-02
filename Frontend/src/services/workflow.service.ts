import { getAccessToken, workflowsApi } from "@/lib/api-client";
import type {
  BackendWorkflowRun,
  PaginatedResponse,
  SSEEvent,
  TriggerWorkflowResponse,
} from "@/lib/types";

export interface WorkflowStreamCallbacks {
  onStepStarted?: (stepKey: string, event: SSEEvent) => void;
  onStepCompleted?: (stepKey: string, event: SSEEvent) => void;
  onRunCompleted?: (event: SSEEvent) => void;
  onRunFailed?: (event: SSEEvent) => void;
  onError?: (err: Event) => void;
  onOpen?: () => void;
}

export const workflowService = {
  triggerWorkflow: (
    projectId: string,
    moduleKey: string,
  ): Promise<TriggerWorkflowResponse> =>
    workflowsApi.trigger(projectId, moduleKey),

  listRuns: (
    projectId: string,
    skip = 0,
    limit = 50,
  ): Promise<PaginatedResponse<BackendWorkflowRun>> =>
    workflowsApi.listRuns(projectId, skip, limit),

  getRun: (projectId: string, runId: string): Promise<BackendWorkflowRun> =>
    workflowsApi.getRun(projectId, runId),

  cancelRun: (projectId: string, runId: string): Promise<void> =>
    workflowsApi.cancelRun(projectId, runId),

  /**
   * Opens an SSE connection to the run's stream endpoint.
   * Returns a cleanup function that closes the EventSource.
   */
  subscribeToRun: (
    projectId: string,
    runId: string,
    callbacks: WorkflowStreamCallbacks,
  ): (() => void) => {
    const url = workflowsApi.streamUrl(projectId, runId);
    const token = getAccessToken();

    // EventSource doesn't support custom headers, so we append the token as a
    // query param if the backend supports it — fall back to URL only.
    const streamUrl = token ? `${url}?token=${encodeURIComponent(token)}` : url;

    const es = new EventSource(streamUrl);

    es.onopen = () => {
      callbacks.onOpen?.();
    };

    es.onerror = (err) => {
      callbacks.onError?.(err);
    };

    es.addEventListener("step_started", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SSEEvent;
        callbacks.onStepStarted?.(data.step_key ?? "", data);
      } catch {
        // ignore malformed events
      }
    });

    es.addEventListener("step_completed", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SSEEvent;
        callbacks.onStepCompleted?.(data.step_key ?? "", data);
      } catch {
        // ignore malformed events
      }
    });

    es.addEventListener("run_completed", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SSEEvent;
        callbacks.onRunCompleted?.(data);
        es.close();
      } catch {
        // ignore malformed events
      }
    });

    es.addEventListener("run_failed", (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SSEEvent;
        callbacks.onRunFailed?.(data);
        es.close();
      } catch {
        // ignore malformed events
      }
    });

    // Also handle generic "message" events as a fallback
    es.onmessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SSEEvent;
        if (data.type === "run_completed") {
          callbacks.onRunCompleted?.(data);
          es.close();
        } else if (data.type === "run_failed") {
          callbacks.onRunFailed?.(data);
          es.close();
        } else if (data.type === "step_started") {
          callbacks.onStepStarted?.(data.step_key ?? "", data);
        } else if (data.type === "step_completed") {
          callbacks.onStepCompleted?.(data.step_key ?? "", data);
        }
      } catch {
        // ignore malformed events
      }
    };

    return () => es.close();
  },
};
