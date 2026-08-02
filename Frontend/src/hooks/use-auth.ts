import { useAuthStore } from "@/store/auth.store";

/**
 * Thin hook wrapping the auth Zustand store.
 * Components should import this rather than `useAuthStore` directly.
 */
export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const accessToken = useAuthStore((s) => s.accessToken);
  const refreshToken = useAuthStore((s) => s.refreshToken);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);
  const logout = useAuthStore((s) => s.logout);
  const refreshTokens = useAuthStore((s) => s.refreshTokens);
  const loadFromStorage = useAuthStore((s) => s.loadFromStorage);
  const updateUser = useAuthStore((s) => s.updateUser);

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshTokens,
    loadFromStorage,
    updateUser,
  };
}
