import { artifactsApi } from "@/lib/api-client";
import type {
  BackendArtifact,
  BackendArtifactVersion,
  EditArtifactInput,
  PaginatedResponse,
} from "@/lib/types";

export const artifactService = {
  listArtifacts: (
    projectId: string,
    skip = 0,
    limit = 50,
  ): Promise<PaginatedResponse<BackendArtifact>> =>
    artifactsApi.list(projectId, skip, limit),

  getArtifact: (projectId: string, artifactId: string): Promise<BackendArtifact> =>
    artifactsApi.get(projectId, artifactId),

  editArtifact: (
    projectId: string,
    artifactId: string,
    data: EditArtifactInput,
  ): Promise<BackendArtifact> => artifactsApi.edit(projectId, artifactId, data),

  listVersions: (
    projectId: string,
    artifactId: string,
  ): Promise<BackendArtifactVersion[]> =>
    artifactsApi.listVersions(projectId, artifactId),
};
