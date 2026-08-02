import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useEffect } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { AppTopbar } from "@/components/layout/app-topbar";
import { useAuthStore } from "@/store/auth.store";

export const Route = createFileRoute("/_app")({
  beforeLoad: () => {
    // If there's no access token at all, redirect immediately before rendering.
    const token = localStorage.getItem("foundrai_access_token");
    if (!token) {
      throw redirect({ to: "/auth/login" });
    }
  },
  component: AppLayout,
});

function AppLayout() {
  const { loadFromStorage, isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    // On mount, validate the stored token and populate the user object.
    loadFromStorage();
  }, [loadFromStorage]);

  // While validating, show a minimal loading state.
  if (isLoading && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="size-8 rounded-lg gradient-brand animate-pulse" />
          <p className="text-sm text-muted-foreground">Loading…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <AppSidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <AppTopbar />
        <main className="flex-1 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
