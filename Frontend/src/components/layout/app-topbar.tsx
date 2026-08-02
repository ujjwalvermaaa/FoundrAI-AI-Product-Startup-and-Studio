import { Link, useRouterState } from "@tanstack/react-router";
import { Bell, Command, Moon, Sun, Search, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/providers/theme-provider";
import { useCommandPalette } from "@/components/providers/command-palette-provider";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MOCK_PROJECTS } from "@/lib/mock-data";

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

export function AppTopbar() {
  const { resolvedTheme, setTheme } = useTheme();
  const { setOpen } = useCommandPalette();
  const crumbs = useCrumbs();

  return (
    <header className="h-14 border-b border-border/60 bg-background/70 backdrop-blur-xl sticky top-0 z-30">
      <div className="h-full px-4 md:px-6 flex items-center gap-3">
        <nav className="flex items-center gap-1.5 text-sm min-w-0">
          <Link to="/dashboard" className="text-muted-foreground hover:text-foreground shrink-0">
            FoundrAI
          </Link>
          {crumbs.map((c, i) => (
            <div key={i} className="flex items-center gap-1.5 min-w-0">
              <ChevronRight className="size-3.5 text-muted-foreground shrink-0" />
              <span className={i === crumbs.length - 1 ? "text-foreground font-medium truncate" : "text-muted-foreground truncate"}>
                {c.label}
              </span>
            </div>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <button
            onClick={() => setOpen(true)}
            className="hidden lg:flex items-center gap-2 px-2.5 py-1.5 rounded-md border border-border bg-muted/40 text-xs text-muted-foreground hover:bg-accent transition-colors"
          >
            <Search className="size-3.5" />
            <span>Search…</span>
            <kbd className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-background border border-border">⌘K</kbd>
          </button>
          <Button variant="ghost" size="icon" onClick={() => setOpen(true)} className="lg:hidden">
            <Command className="size-4" />
          </Button>
          <Button variant="ghost" size="icon" asChild>
            <Link to="/notifications">
              <Bell className="size-4" />
            </Link>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
          >
            {resolvedTheme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
          </Button>
          <div className="mx-1 h-6 w-px bg-border" />
          <Link to="/profile" aria-label="Profile" className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-primary">
            <Avatar className="size-8 hover:ring-2 hover:ring-primary/40 transition">
              <AvatarFallback className="bg-gradient-to-br from-primary to-brand-glow text-primary-foreground text-xs font-medium">
                AV
              </AvatarFallback>
            </Avatar>
          </Link>
        </div>
      </div>
    </header>
  );
}