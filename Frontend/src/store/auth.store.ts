import { create } from "zustand";
import { toast } from "sonner";
import { authApi, clearTokens, setTokens } from "@/lib/api-client";
import type { BackendUser } from "@/lib/types";

interface AuthState {
  user: BackendUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshTokens: () => Promise<boolean>;
  loadFromStorage: () => Promise<void>;
  updateUser: (partial: Partial<BackendUser>) => void;
}

export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  accessToken: localStorage.getItem("foundrai_access_token"),
  refreshToken: localStorage.getItem("foundrai_refresh_token"),
  isAuthenticated: false,
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const data = await authApi.login(email, password);
      setTokens(data.access_token, data.refresh_token);
      set({
        user: data.user,
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (email: string, password: string, fullName: string) => {
    set({ isLoading: true });
    try {
      const data = await authApi.register(email, password, fullName);
      setTokens(data.access_token, data.refresh_token);
      set({
        user: data.user,
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // best-effort
    }
    clearTokens();
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },

  refreshTokens: async (): Promise<boolean> => {
    const refreshToken = get().refreshToken ?? localStorage.getItem("foundrai_refresh_token");
    if (!refreshToken) return false;

    try {
      const data = await authApi.refresh(refreshToken);
      localStorage.setItem("foundrai_access_token", data.access_token);
      set({ accessToken: data.access_token });
      return true;
    } catch {
      clearTokens();
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
      });
      return false;
    }
  },

  loadFromStorage: async () => {
    const token = localStorage.getItem("foundrai_access_token");
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authApi.me();
      set({
        user,
        accessToken: token,
        refreshToken: localStorage.getItem("foundrai_refresh_token"),
        isAuthenticated: true,
      });
    } catch {
      // Token invalid — try refresh
      const refreshed = await get().refreshTokens();
      if (refreshed) {
        try {
          const user = await authApi.me();
          set({ user, isAuthenticated: true });
        } catch {
          clearTokens();
          set({ user: null, isAuthenticated: false });
          toast.error("Session expired. Please sign in again.");
        }
      } else {
        clearTokens();
        set({ user: null, isAuthenticated: false });
      }
    } finally {
      set({ isLoading: false });
    }
  },

  updateUser: (partial: Partial<BackendUser>) => {
    const current = get().user;
    if (!current) return;
    set({ user: { ...current, ...partial } });
  },
}));
