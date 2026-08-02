import { projectsApi } from "@/lib/api-client";
import type {
  BackendProjectWithModules,
  CreateProjectInput,
  PaginatedResponse,
  UpdateProjectInput,
} from "@/lib/types";

export const projectService = {
  listProjects: (skip = 0, limit = 50): Promise<PaginatedResponse<BackendProjectWithModules>> =>
    projectsApi.list(skip, limit),

  getProject: (id: string): Promise<BackendProjectWithModules> =>
    projectsApi.get(id),

  createProject: (data: CreateProjectInput): Promise<BackendProjectWithModules> =>
    projectsApi.create(data),

  updateProject: (id: string, data: UpdateProjectInput): Promise<BackendProjectWithModules> =>
    projectsApi.update(id, data),

  deleteProject: (id: string): Promise<void> =>
    projectsApi.delete(id),
};
