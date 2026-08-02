import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import {
  LayoutDashboard,
  FolderKanban,
  Bell,
  Settings,
  Sparkles,
  Plus,
  Moon,
  Sun,
  Search,
  MessageCircle,
  BarChart3,
  User,
  Activity,
  Map,
  Target,
  LayoutGrid,
  ListChecks,
  CreditCard,
  BookOpen,
  LifeBuoy,
} from "lucide-react";
import { useTheme } from "./theme-provider";
import { MOCK_PROJECTS } from "@/lib/mock-data";

type Ctx = { open: boolean; setOpen: (v: boolean) => void };
const CommandPaletteContext = createContext<Ctx | null>(null);

export function CommandPaletteProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { resolvedTheme, setTheme } = useTheme();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", down);
    return () => window.removeEventListener("keydown", down);
  }, []);

  const go = (to: string) => {
    setOpen(false);
    navigate({ to });
  };

  return (
    <CommandPaletteContext.Provider value={{ open, setOpen }}>
      {children}
      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput placeholder="Search projects, modules, artifacts…" />
        <CommandList>
          <CommandEmpty>No results.</CommandEmpty>
          <CommandGroup heading="Navigate">
            <CommandItem onSelect={() => go("/dashboard")}>
              <LayoutDashboard /> Dashboard <CommandShortcut>G D</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go("/projects")}>
              <FolderKanban /> Projects <CommandShortcut>G P</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go("/chat")}>
              <MessageCircle /> Chat with Foundr <CommandShortcut>G C</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go("/health")}>
              <Activity /> Startup Health
            </CommandItem>
            <CommandItem onSelect={() => go("/roadmap")}>
              <Map /> AI Roadmap
            </CommandItem>
            <CommandItem onSelect={() => go("/competitors")}>
              <Target /> Competitors
            </CommandItem>
            <CommandItem onSelect={() => go("/canvas")}>
              <LayoutGrid /> Business Canvas
            </CommandItem>
            <CommandItem onSelect={() => go("/checklist")}>
              <ListChecks /> Startup Checklist
            </CommandItem>
            <CommandItem onSelect={() => go("/analytics")}>
              <BarChart3 /> Analytics
            </CommandItem>
            <CommandItem onSelect={() => go("/notifications")}>
              <Bell /> Notifications
            </CommandItem>
            <CommandItem onSelect={() => go("/profile")}>
              <User /> Profile
            </CommandItem>
            <CommandItem onSelect={() => go("/billing")}>
              <CreditCard /> Billing & credits
            </CommandItem>
            <CommandItem onSelect={() => go("/docs")}>
              <BookOpen /> Docs
            </CommandItem>
            <CommandItem onSelect={() => go("/help")}>
              <LifeBuoy /> Help & Support
            </CommandItem>
            <CommandItem onSelect={() => go("/settings")}>
              <Settings /> Settings
            </CommandItem>
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Projects">
            {MOCK_PROJECTS.map((p) => (
              <CommandItem key={p.id} onSelect={() => go(`/projects/${p.id}`)}>
                <Sparkles /> {p.name}
                <span className="ml-auto text-xs text-muted-foreground">{p.industry}</span>
              </CommandItem>
            ))}
          </CommandGroup>
          <CommandSeparator />
          <CommandGroup heading="Actions">
            <CommandItem onSelect={() => go("/projects/new")}>
              <Plus /> New project <CommandShortcut>N</CommandShortcut>
            </CommandItem>
            <CommandItem onSelect={() => go("/search")}>
              <Search /> Global search
            </CommandItem>
            <CommandItem
              onSelect={() => {
                setTheme(resolvedTheme === "dark" ? "light" : "dark");
                setOpen(false);
              }}
            >
              {resolvedTheme === "dark" ? <Sun /> : <Moon />} Toggle theme
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </CommandPaletteContext.Provider>
  );
}

export function useCommandPalette() {
  const ctx = useContext(CommandPaletteContext);
  if (!ctx) throw new Error("useCommandPalette must be used within CommandPaletteProvider");
  return ctx;
}