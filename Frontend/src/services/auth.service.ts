import { authApi } from "@/lib/api-client";
import type { AuthResponse, BackendUser, RefreshResponse } from "@/lib/types";

export const authService = {
  login: (email: string, password: string): Promise<AuthResponse> =>
    authApi.login(email, password),

  register: (email: string, password: string, fullName: string): Promise<AuthResponse> =>
    authApi.register(email, password, fullName),

  logout: (): Promise<void> => authApi.logout(),

  refresh: (refreshToken: string): Promise<RefreshResponse> =>
    authApi.refresh(refreshToken),

  me: (): Promise<BackendUser> => authApi.me(),
};
