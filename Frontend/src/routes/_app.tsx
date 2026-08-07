import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { AppTopbar } from "@/components/layout/app-topbar";
import { AmbientField } from "@/components/layout/ambient-field";
import { MobileDock } from "@/components/layout/mobile-dock";
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
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    // On mount, validate the stored token and populate the user object.
    loadFromStorage();
  }, [loadFromStorage]);

  // While validating, show a minimal loading state.
  if (isLoading && !isAuthenticated) {
    return (
      <div className="relative min-h-screen flex items-center justify-center bg-background overflow-hidden">
        <AmbientField />
        <div className="relative z-10 flex flex-col items-center gap-4">
          <div className="relative size-14">
            <div className="absolute inset-0 rounded-2xl pulse-core bg-primary/40 blur-md" />
            <div className="absolute inset-0 rounded-2xl gradient-brand animate-pulse" />
            <svg className="absolute inset-0 size-full orbit-ring text-primary/60" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="28" r="26" stroke="currentColor" strokeWidth="1" strokeDasharray="4 8" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground font-mono tracking-widest uppercase">Initializing…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex bg-background text-foreground overflow-x-hidden">
      <AmbientField />
      <AppSidebar />
      <div className="relative z-10 flex min-w-0 flex-1 flex-col">
        <AppTopbar onOpenMobileNav={() => setMobileNavOpen(true)} />
        <motion.main
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.05 }}
          className="relative flex-1 min-w-0 pb-24 md:pb-0"
        >
          <Outlet />
        </motion.main>
      </div>
      <MobileDock moreOpen={mobileNavOpen} onMoreOpenChange={setMobileNavOpen} />
    </div>
  );
}
