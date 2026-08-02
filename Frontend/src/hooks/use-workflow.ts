import { useEffect, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { workflowService, type WorkflowStreamCallbacks } from "@/services/workflow.service";
import { projectKeys } from "./use-projects";
import { artifactKeys } from "./use-artifacts";
import { useAuthStore } from "@/store/auth.store";

export const workflowKeys = {
  all: ["workflows"] as const,
  runs: (projectId: string) => [...workflowKeys.all, "runs", projectId] as const,
  run: (projectId: string, runId: string) =>
    [...workflowKeys.all, "run", projectId, runId] as const,
};

/** List all workflow runs for a project. */
export function useWorkflowRuns(projectId: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: workflowKeys.runs(projectId),
    queryFn: () => workflowService.listRuns(projectId),
    enabled: isAuthenticated && !!projectId,
    select: (data) => data.items,
  });
}

/** Get a single run detail. */
export function useWorkflowRun(projectId: string, runId: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: workflowKeys.run(projectId, runId),
    queryFn: () => workflowService.getRun(projectId, runId),
    enabled: isAuthenticated && !!projectId && !!runId,
  });
}

/** Trigger a workflow run for a module. */
export function useTriggerWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      moduleKey,
    }: {
      projectId: string;
      moduleKey: string;
    }) => workflowService.triggerWorkflow(projectId, moduleKey),
    onSuccess: (_, { projectId }) => {
      // Invalidate project to pick up updated module status
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      queryClient.invalidateQueries({ queryKey: workflowKeys.runs(projectId) });
      toast.success("Workflow started");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to start workflow");
    },
  });
}

/** Cancel a workflow run. */
export function useCancelWorkflow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ projectId, runId }: { projectId: string; runId: string }) =>
      workflowService.cancelRun(projectId, runId),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: workflowKeys.runs(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
      toast.success("Workflow cancelled");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to cancel workflow");
    },
  });
}

/**
 * Subscribes to an SSE run stream and calls the provided callbacks.
 * Automatically invalidates project + artifact queries when the run completes.
 *
 * @param projectId  - Project UUID (pass empty string to disable)
 * @param runId      - Run UUID (pass empty string to disable)
 * @param callbacks  - SSE event handlers
 */
export function useWorkflowStream(
  projectId: string,
  runId: string,
  callbacks: WorkflowStreamCallbacks,
) {
  const queryClient = useQueryClient();
  const callbacksRef = useRef<WorkflowStreamCallbacks>(callbacks);
  callbacksRef.current = callbacks;

  useEffect(() => {
    if (!projectId || !runId) return;

    const cleanup = workflowService.subscribeToRun(projectId, runId, {
      onStepStarted: (stepKey, event) => {
        callbacksRef.current.onStepStarted?.(stepKey, event);
      },
      onStepCompleted: (stepKey, event) => {
        callbacksRef.current.onStepCompleted?.(stepKey, event);
      },
      onRunCompleted: (event) => {
        callbacksRef.current.onRunCompleted?.(event);
        // Refresh project (module statuses) and artifacts
        queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
        queryClient.invalidateQueries({ queryKey: artifactKeys.list(projectId) });
        queryClient.invalidateQueries({ queryKey: workflowKeys.runs(projectId) });
        queryClient.invalidateQueries({
          queryKey: workflowKeys.run(projectId, runId),
        });
      },
      onRunFailed: (event) => {
        callbacksRef.current.onRunFailed?.(event);
        queryClient.invalidateQueries({ queryKey: projectKeys.detail(projectId) });
        queryClient.invalidateQueries({ queryKey: workflowKeys.runs(projectId) });
        toast.error(event.error_message ?? "Workflow run failed");
      },
      onError: (err) => {
        callbacksRef.current.onError?.(err);
      },
      onOpen: () => {
        callbacksRef.current.onOpen?.();
      },
    });

    return cleanup;
  }, [projectId, runId, queryClient]);
}
