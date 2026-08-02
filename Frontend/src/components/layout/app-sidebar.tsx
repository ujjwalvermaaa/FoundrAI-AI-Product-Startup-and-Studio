import { Link, useRouterState } from "@tanstack/react-router";
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
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useCommandPalette } from "@/components/providers/command-palette-provider";
import { useProjects } from "@/hooks/use-projects";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/chat", label: "Chat with Foundr", icon: MessageCircle },
  { to: "/health", label: "Startup Health", icon: Activity },
  { to: "/roadmap", label: "AI Roadmap", icon: Map },
  { to: "/competitors", label: "Competitors", icon: Target },
  { to: "/canvas", label: "Business Canvas", icon: LayoutGrid },
  { to: "/checklist", label: "Checklist", icon: ListChecks },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/notifications", label: "Notifications", icon: Bell },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { setOpen } = useCommandPalette();

  const { data: backendProjects, isLoading: projectsLoading } = useProjects();
  const projects = backendProjects?.map(mapBackendProjectToDisplay) ?? [];

  return (
    <aside className="hidden md:flex flex-col w-64 shrink-0 border-r border-sidebar-border bg-sidebar text-sidebar-foreground h-screen sticky top-0">
      <div className="p-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="size-8 rounded-lg overflow-hidden shadow-glow shrink-0">
            <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
          </div>
          <div className="font-display text-lg font-semibold tracking-tight">FoundrAI</div>
        </Link>
      </div>

      <div className="px-3">
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-sidebar-border bg-background/40 text-xs text-muted-foreground hover:bg-accent transition-colors"
        >
          <Search className="size-3.5" />
          <span>Search…</span>
          <kbd className="ml-auto text-[10px] font-mono px-1.5 py-0.5 rounded bg-muted text-muted-foreground">⌘K</kbd>
        </button>
      </div>

      <nav className="px-3 mt-4 space-y-0.5">
        {NAV.map((item) => {
          const active = pathname === item.to || (item.to !== "/dashboard" && pathname.startsWith(item.to));
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors",
                active
                  ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                  : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/60",
              )}
            >
              <item.icon className="size-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-3 mt-6">
        <div className="flex items-center justify-between px-3 mb-1.5">
          <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-medium">Projects</span>
          <Link to="/projects/new" className="text-muted-foreground hover:text-foreground">
            <Plus className="size-3.5" />
          </Link>
        </div>
        <div className="space-y-0.5">
          {projectsLoading && (
            <div className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground">
              <Loader2 className="size-3 animate-spin" />
              Loading projects…
            </div>
          )}
          {projects.map((p) => {
            const active = pathname.startsWith(`/projects/${p.id}`);
            return (
              <Link
                key={p.id}
                to="/projects/$id"
                params={{ id: p.id }}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-1.5 rounded-md text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50",
                )}
              >
                <span className="size-2 rounded-full shrink-0" style={{ background: p.cover }} />
                <span className="truncate">{p.name}</span>
                <span className="ml-auto text-[10px] text-muted-foreground">{p.progress}%</span>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="mt-auto p-3 space-y-2">
        <div className="rounded-lg border border-sidebar-border p-3 bg-gradient-to-br from-accent/40 to-transparent">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Sparkles className="size-3.5 text-primary" />
            AI credits
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-muted overflow-hidden">
            <div className="h-full gradient-brand" style={{ width: "62%" }} />
          </div>
          <div className="mt-1.5 flex justify-between text-[11px] text-muted-foreground">
            <span>6,200 / 10,000</span>
            <Link to="/billing" className="hover:text-foreground">Upgrade</Link>
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" asChild>
            <Link to="/docs"><BookOpen className="size-3.5" /> Docs</Link>
          </Button>
          <Button variant="ghost" size="sm" className="h-7 px-2 text-xs" asChild>
            <Link to="/help"><LifeBuoy className="size-3.5" /> Help</Link>
          </Button>
        </div>
      </div>
    </aside>
  );
}
