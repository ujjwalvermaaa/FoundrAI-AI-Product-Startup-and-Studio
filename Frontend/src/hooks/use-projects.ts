import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { projectService } from "@/services/project.service";
import type { CreateProjectInput, UpdateProjectInput } from "@/lib/types";
import { useAuthStore } from "@/store/auth.store";

export const projectKeys = {
  all: ["projects"] as const,
  lists: () => [...projectKeys.all, "list"] as const,
  detail: (id: string) => [...projectKeys.all, "detail", id] as const,
};

/** List all projects for the authenticated user. */
export function useProjects() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: projectKeys.lists(),
    queryFn: () => projectService.listProjects(),
    enabled: isAuthenticated,
    select: (data) => data.items,
  });
}

/** Get a single project with its modules. */
export function useProject(id: string) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: () => projectService.getProject(id),
    enabled: isAuthenticated && !!id,
  });
}

/** Create a new project. */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectInput) => projectService.createProject(data),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success(`Project "${project.name}" created`);
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to create project");
    },
  });
}

/** Update a project. */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectInput }) =>
      projectService.updateProject(id, data),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(project.id) });
      toast.success("Project updated");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update project");
    },
  });
}

/** Delete a project. */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectService.deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.lists() });
      toast.success("Project deleted");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to delete project");
    },
  });
}
