import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { artifactService } from "@/services/artifact.service";
import type { EditArtifactInput } from "@/lib/types";
import { useAuthStore } from "@/store/auth.store";

export const artifactKeys = {
  all: ["artifacts"] as const,
  list: (projectId: string) => [...artifactKeys.all, "list", projectId] as const,
  detail: (projectId: string, artifactId: string) =>
    [...artifactKeys.all, "detail", projectId, artifactId] as const,
  versions: (projectId: string, artifactId: string) =>
    [...artifactKeys.all, "versions", projectId, artifactId] as const,
};

/** List all artifacts for a project. */
export function useArtifacts(projectId: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: artifactKeys.list(projectId),
    queryFn: () => artifactService.listArtifacts(projectId),
    enabled: isAuthenticated && !!projectId,
    select: (data) => data.items,
  });
}

/** Get a single artifact. */
export function useArtifact(projectId: string, artifactId: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: artifactKeys.detail(projectId, artifactId),
    queryFn: () => artifactService.getArtifact(projectId, artifactId),
    enabled: isAuthenticated && !!projectId && !!artifactId,
  });
}

/** List artifact versions. */
export function useArtifactVersions(projectId: string, artifactId: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: artifactKeys.versions(projectId, artifactId),
    queryFn: () => artifactService.listVersions(projectId, artifactId),
    enabled: isAuthenticated && !!projectId && !!artifactId,
  });
}

/** Edit an artifact. */
export function useEditArtifact() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      artifactId,
      data,
    }: {
      projectId: string;
      artifactId: string;
      data: EditArtifactInput;
    }) => artifactService.editArtifact(projectId, artifactId, data),
    onSuccess: (artifact) => {
      queryClient.invalidateQueries({
        queryKey: artifactKeys.list(artifact.project_id),
      });
      queryClient.invalidateQueries({
        queryKey: artifactKeys.detail(artifact.project_id, artifact.id),
      });
      queryClient.invalidateQueries({
        queryKey: artifactKeys.versions(artifact.project_id, artifact.id),
      });
      toast.success("Artifact saved");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to save artifact");
    },
  });
}
