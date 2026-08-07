import { Link, useRouterState } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Bell, Command, Moon, Sun, Search, ChevronRight, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/providers/theme-provider";
import { useCommandPalette } from "@/components/providers/command-palette-provider";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MOCK_PROJECTS } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

function useCrumbs() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const parts = pathname.split("/").filter(Boolean);
  const crumbs: { label: string; to?: string }[] = [];
  let acc = "";
  for (const part of parts) {
    acc += "/" + part;
    const proj = MOCK_PROJECTS.find((p) => p.id === part);
    crumbs.push({ label: proj ? proj.name : part.charAt(0).toUpperCase() + part.slice(1), to: acc });
  }
  return crumbs;
}

export function AppTopbar({ onOpenMobileNav }: { onOpenMobileNav?: () => void }) {
  const { resolvedTheme, setTheme } = useTheme();
  const { setOpen } = useCommandPalette();
  const crumbs = useCrumbs();

  return (
    <header className="sticky top-0 z-30 px-3 pt-3 md:px-4 md:pt-3">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className="relative h-14 overflow-hidden rounded-2xl glass-depth hologram-edge"
      >
        <div className="scan-line absolute inset-0 opacity-25" />
        <div className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

        <div className="relative z-10 flex h-full items-center gap-3 px-3 md:px-4">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden shrink-0 rounded-xl"
            onClick={onOpenMobileNav}
            aria-label="Open navigation"
          >
            <Menu className="size-4" />
          </Button>

          <nav className="flex min-w-0 items-center gap-1.5 text-sm">
            <Link
              to="/dashboard"
              className="shrink-0 font-display text-xs font-semibold tracking-wide text-muted-foreground transition-colors hover:text-primary"
            >
              FoundrAI
            </Link>
            {crumbs.map((c, i) => (
              <div key={i} className="flex min-w-0 items-center gap-1.5">
                <ChevronRight className="size-3.5 shrink-0 text-muted-foreground/60" />
                <span
                  className={cn(
                    "truncate",
                    i === crumbs.length - 1
                      ? "font-medium text-foreground"
                      : "text-muted-foreground",
                  )}
                >
                  {c.label}
                </span>
              </div>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-1">
            <button
              type="button"
              onClick={() => setOpen(true)}
              className="hidden lg:flex items-center gap-2 rounded-xl border border-border/70 bg-background/40 px-2.5 py-1.5 text-xs text-muted-foreground transition-all hover:border-primary/40 hover:bg-accent/50 hover:text-foreground"
            >
              <Search className="size-3.5" />
              <span>Search…</span>
              <kbd className="rounded-md border border-border/60 bg-background/80 px-1.5 py-0.5 font-mono text-[10px]">
                ⌘K
              </kbd>
            </button>
            <Button variant="ghost" size="icon" onClick={() => setOpen(true)} className="lg:hidden rounded-xl">
              <Command className="size-4" />
            </Button>
            <Button variant="ghost" size="icon" className="rounded-xl relative" asChild>
              <Link to="/notifications">
                <Bell className="size-4" />
                <span className="absolute right-2 top-2 size-1.5 rounded-full bg-primary shadow-[0_0_8px_var(--brand)]" />
              </Link>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="rounded-xl"
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            >
              {resolvedTheme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>
            <div className="mx-1 hidden h-6 w-px bg-border/70 sm:block" />
            <Link
              to="/profile"
              aria-label="Profile"
              className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary"
            >
              <Avatar className="size-8 ring-1 ring-primary/30 transition hover:ring-2 hover:ring-primary/50 hover:shadow-glow">
                <AvatarFallback className="bg-gradient-to-br from-primary to-brand-glow text-xs font-medium text-primary-foreground">
                  AV
                </AvatarFallback>
              </Avatar>
            </Link>
          </div>
        </div>
      </motion.div>
    </header>
  );
}
