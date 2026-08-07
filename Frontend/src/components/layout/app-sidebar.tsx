import { useState, type ComponentType } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  FolderKanban,
  Bell,
  Settings,
  Sparkles,
  Search,
  Plus,
  BookOpen,
  LifeBuoy,
  MessageCircle,
  BarChart3,
  User,
  Activity,
  Map,
  Target,
  LayoutGrid,
  ListChecks,
  Loader2,
  PanelLeftClose,
  PanelLeftOpen,
  CreditCard,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useCommandPalette } from "@/components/providers/command-palette-provider";
import { useProjects } from "@/hooks/use-projects";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const NAV_GROUPS = [
  {
    id: "studio",
    label: "Studio",
    items: [
      { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { to: "/projects", label: "Projects", icon: FolderKanban },
      { to: "/chat", label: "Chat with Foundr", icon: MessageCircle },
    ],
  },
  {
    id: "intel",
    label: "Intelligence",
    items: [
      { to: "/health", label: "Startup Health", icon: Activity },
      { to: "/roadmap", label: "AI Roadmap", icon: Map },
      { to: "/competitors", label: "Competitors", icon: Target },
      { to: "/canvas", label: "Business Canvas", icon: LayoutGrid },
      { to: "/checklist", label: "Checklist", icon: ListChecks },
      { to: "/analytics", label: "Analytics", icon: BarChart3 },
    ],
  },
  {
    id: "account",
    label: "Account",
    items: [
      { to: "/notifications", label: "Notifications", icon: Bell },
      { to: "/profile", label: "Profile", icon: User },
      { to: "/settings", label: "Settings", icon: Settings },
    ],
  },
] as const;

function isActivePath(pathname: string, to: string) {
  return pathname === to || (to !== "/dashboard" && pathname.startsWith(to));
}

function BrandCore({ expanded }: { expanded: boolean }) {
  return (
    <Link to="/" className="relative flex items-center gap-3 group outline-none">
      <div className="relative size-11 shrink-0">
        <div className="absolute inset-0 rounded-2xl pulse-core bg-primary/30 blur-md" />
        <svg className="absolute inset-0 size-full orbit-ring text-primary/50" viewBox="0 0 44 44" fill="none">
          <circle cx="22" cy="22" r="20" stroke="currentColor" strokeWidth="1" strokeDasharray="4 6" />
        </svg>
        <svg
          className="absolute inset-1 size-[calc(100%-8px)] orbit-ring-reverse text-brand-glow/40"
          viewBox="0 0 36 36"
          fill="none"
        >
          <circle cx="18" cy="18" r="16" stroke="currentColor" strokeWidth="1" strokeDasharray="2 8" />
        </svg>
        <div className="absolute inset-2 rounded-xl overflow-hidden shadow-glow ring-1 ring-primary/30">
          <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
        </div>
      </div>
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, x: -8, width: 0 }}
            animate={{ opacity: 1, x: 0, width: "auto" }}
            exit={{ opacity: 0, x: -8, width: 0 }}
            transition={{ duration: 0.22 }}
            className="overflow-hidden whitespace-nowrap"
          >
            <div className="font-display text-lg font-semibold tracking-tight leading-none">FoundrAI</div>
            <div className="mt-1 text-[10px] uppercase tracking-[0.2em] text-primary/80">Neural Studio</div>
          </motion.div>
        )}
      </AnimatePresence>
    </Link>
  );
}

function NavOrb({
  to,
  label,
  icon: Icon,
  active,
  expanded,
}: {
  to: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  active: boolean;
  expanded: boolean;
}) {
  const link = (
    <Link
      to={to}
      data-active={active}
      className={cn(
        "nav-orb relative flex items-center gap-3 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-primary/60",
        expanded ? "px-2.5 py-2" : "size-10 justify-center mx-auto",
        active
          ? "bg-primary/15 text-foreground"
          : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
      )}
    >
      {active && (
        <motion.span
          layoutId="nav-active-glow"
          className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary/20 via-brand-glow/10 to-transparent"
          transition={{ type: "spring", stiffness: 380, damping: 32 }}
        />
      )}
      {active && (
        <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-primary shadow-[0_0_12px_var(--brand)]" />
      )}
      <span
        className={cn(
          "relative z-10 flex size-8 shrink-0 items-center justify-center rounded-lg transition-colors",
          active ? "bg-primary/20 text-primary" : "bg-muted/40",
        )}
      >
        <Icon className="size-4" />
      </span>
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.span
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -6 }}
            className="relative z-10 text-sm font-medium truncate"
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>
    </Link>
  );

  if (expanded) return link;

  return (
    <Tooltip delayDuration={80}>
      <TooltipTrigger asChild>{link}</TooltipTrigger>
      <TooltipContent side="right" className="font-medium">
        {label}
      </TooltipContent>
    </Tooltip>
  );
}

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { setOpen } = useCommandPalette();
  const [expanded, setExpanded] = useState(true);

  const { data: backendProjects, isLoading: projectsLoading } = useProjects();
  const projects = backendProjects?.map(mapBackendProjectToDisplay) ?? [];

  return (
    <TooltipProvider delayDuration={80}>
      <aside
        className={cn(
          "hidden md:flex sticky top-0 z-40 h-screen shrink-0 flex-col p-3 perspective-stage",
          expanded ? "w-[17.5rem]" : "w-[5.25rem]",
        )}
      >
        <motion.div
          layout
          className="relative flex h-full flex-col overflow-hidden rounded-[1.35rem] glass-depth hologram-edge"
          transition={{ type: "spring", stiffness: 320, damping: 34 }}
        >
          {/* Holographic scan + corner accents */}
          <div className="scan-line absolute inset-0 opacity-40" />
          <div className="pointer-events-none absolute left-3 top-3 size-2 border-l border-t border-primary/50" />
          <div className="pointer-events-none absolute right-3 top-3 size-2 border-r border-t border-primary/50" />
          <div className="pointer-events-none absolute bottom-3 left-3 size-2 border-b border-l border-primary/50" />
          <div className="pointer-events-none absolute bottom-3 right-3 size-2 border-b border-r border-primary/50" />

          <div className={cn("relative z-10 flex items-center gap-2 p-3", expanded ? "justify-between" : "flex-col")}>
            <BrandCore expanded={expanded} />
            <button
              type="button"
              onClick={() => setExpanded((v) => !v)}
              className="flex size-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
            >
              {expanded ? <PanelLeftClose className="size-4" /> : <PanelLeftOpen className="size-4" />}
            </button>
          </div>

          <div className={cn("relative z-10 px-3", !expanded && "px-2")}>
            <button
              type="button"
              onClick={() => setOpen(true)}
              className={cn(
                "group flex w-full items-center gap-2 rounded-xl border border-border/70 bg-background/30 text-xs text-muted-foreground transition-all hover:border-primary/40 hover:bg-accent/60 hover:text-foreground",
                expanded ? "px-3 py-2.5" : "size-10 justify-center mx-auto",
              )}
            >
              <Search className="size-3.5 shrink-0 group-hover:text-primary transition-colors" />
              {expanded && (
                <>
                  <span>Search…</span>
                  <kbd className="ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded-md bg-muted/80 text-muted-foreground border border-border/50">
                    ⌘K
                  </kbd>
                </>
              )}
            </button>
          </div>

          <nav className="relative z-10 mt-3 flex-1 overflow-y-auto overflow-x-hidden px-2 pb-2 scrollbar-thin">
            {NAV_GROUPS.map((group) => (
              <div key={group.id} className="mb-4">
                {expanded ? (
                  <div className="mb-1.5 px-2.5 text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground/70">
                    {group.label}
                  </div>
                ) : (
                  <div className="mx-auto mb-2 h-px w-6 bg-border/80" />
                )}
                <div className="space-y-0.5">
                  {group.items.map((item) => (
                    <NavOrb
                      key={item.to}
                      to={item.to}
                      label={item.label}
                      icon={item.icon}
                      active={isActivePath(pathname, item.to)}
                      expanded={expanded}
                    />
                  ))}
                </div>
              </div>
            ))}

            <div className="mb-2">
              <div className={cn("mb-1.5 flex items-center", expanded ? "justify-between px-2.5" : "justify-center")}>
                {expanded && (
                  <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground/70">
                    Projects
                  </span>
                )}
                <Link
                  to="/projects/new"
                  className="flex size-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-primary"
                  aria-label="New project"
                >
                  <Plus className="size-3.5" />
                </Link>
              </div>
              <div className="space-y-0.5">
                {projectsLoading && (
                  <div
                    className={cn(
                      "flex items-center gap-2 text-xs text-muted-foreground",
                      expanded ? "px-2.5 py-1.5" : "justify-center py-2",
                    )}
                  >
                    <Loader2 className="size-3 animate-spin" />
                    {expanded && "Loading…"}
                  </div>
                )}
                {projects.slice(0, expanded ? 6 : 4).map((p) => {
                  const active = pathname.startsWith(`/projects/${p.id}`);
                  const row = (
                    <Link
                      key={p.id}
                      to="/projects/$id"
                      params={{ id: p.id }}
                      data-active={active}
                      className={cn(
                        "nav-orb flex items-center gap-2.5 rounded-xl text-sm transition-colors",
                        expanded ? "px-2.5 py-1.5" : "size-10 justify-center mx-auto",
                        active
                          ? "bg-primary/15 text-foreground"
                          : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
                      )}
                    >
                      <span
                        className="size-2.5 rounded-full shrink-0 ring-2 ring-background shadow-[0_0_8px_currentColor]"
                        style={{ background: p.cover, color: p.cover }}
                      />
                      {expanded && (
                        <>
                          <span className="truncate flex-1">{p.name}</span>
                          <span className="text-[10px] font-mono text-muted-foreground">{p.progress}%</span>
                        </>
                      )}
                    </Link>
                  );
                  if (expanded) return row;
                  return (
                    <Tooltip key={p.id} delayDuration={80}>
                      <TooltipTrigger asChild>{row}</TooltipTrigger>
                      <TooltipContent side="right">{p.name}</TooltipContent>
                    </Tooltip>
                  );
                })}
              </div>
            </div>
          </nav>

          <div className={cn("relative z-10 mt-auto space-y-2 border-t border-border/50 p-3", !expanded && "px-2")}>
            <div
              className={cn(
                "relative overflow-hidden rounded-xl border border-primary/20 bg-gradient-to-br from-primary/15 via-transparent to-brand-glow/10",
                expanded ? "p-3" : "p-2",
              )}
            >
              <div className="pointer-events-none absolute -right-4 -top-4 size-16 rounded-full bg-primary/20 blur-xl" />
              {expanded ? (
                <>
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Sparkles className="size-3.5 text-primary" />
                    AI credits
                  </div>
                  <div className="mt-2.5 h-1.5 rounded-full bg-muted/80 overflow-hidden">
                    <motion.div
                      className="h-full gradient-brand"
                      initial={{ width: 0 }}
                      animate={{ width: "62%" }}
                      transition={{ duration: 1.1, ease: "easeOut" }}
                    />
                  </div>
                  <div className="mt-1.5 flex justify-between text-[11px] text-muted-foreground">
                    <span className="font-mono">6,200 / 10,000</span>
                    <Link to="/billing" className="hover:text-primary transition-colors">
                      Upgrade
                    </Link>
                  </div>
                </>
              ) : (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Link to="/billing" className="flex flex-col items-center gap-1" aria-label="AI credits">
                      <div className="relative size-9">
                        <svg className="size-full -rotate-90" viewBox="0 0 36 36">
                          <circle cx="18" cy="18" r="14" fill="none" className="stroke-muted" strokeWidth="3" />
                          <circle
                            cx="18"
                            cy="18"
                            r="14"
                            fill="none"
                            className="stroke-primary"
                            strokeWidth="3"
                            strokeDasharray={`${62 * 0.88} 88`}
                            strokeLinecap="round"
                          />
                        </svg>
                        <Sparkles className="absolute inset-0 m-auto size-3.5 text-primary" />
                      </div>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right">6,200 / 10,000 credits</TooltipContent>
                </Tooltip>
              )}
            </div>

            <div className={cn("flex items-center gap-1", !expanded && "flex-col")}>
              <Link
                to="/docs"
                className="flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                <BookOpen className="size-3.5" />
                {expanded && "Docs"}
              </Link>
              <Link
                to="/help"
                className="flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                <LifeBuoy className="size-3.5" />
                {expanded && "Help"}
              </Link>
              {!expanded && (
                <Link
                  to="/billing"
                  className="flex items-center justify-center rounded-lg px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                  aria-label="Billing"
                >
                  <CreditCard className="size-3.5" />
                </Link>
              )}
            </div>
          </div>
        </motion.div>
      </aside>
    </TooltipProvider>
  );
}
