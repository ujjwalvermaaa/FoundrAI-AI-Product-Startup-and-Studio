import { Link, useRouterState } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  FolderKanban,
  MessageCircle,
  Activity,
  MoreHorizontal,
  Map,
  Target,
  LayoutGrid,
  ListChecks,
  BarChart3,
  Bell,
  User,
  Settings,
  BookOpen,
  LifeBuoy,
  CreditCard,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

const DOCK = [
  { to: "/dashboard", label: "Home", icon: LayoutDashboard },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/chat", label: "Chat", icon: MessageCircle },
  { to: "/health", label: "Health", icon: Activity },
] as const;

const MORE_LINKS = [
  { to: "/roadmap", label: "AI Roadmap", icon: Map },
  { to: "/competitors", label: "Competitors", icon: Target },
  { to: "/canvas", label: "Business Canvas", icon: LayoutGrid },
  { to: "/checklist", label: "Checklist", icon: ListChecks },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/notifications", label: "Notifications", icon: Bell },
  { to: "/profile", label: "Profile", icon: User },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/docs", label: "Docs", icon: BookOpen },
  { to: "/help", label: "Help", icon: LifeBuoy },
  { to: "/billing", label: "Billing", icon: CreditCard },
] as const;

function isActivePath(pathname: string, to: string) {
  return pathname === to || (to !== "/dashboard" && pathname.startsWith(to));
}

export function MobileDock({
  moreOpen,
  onMoreOpenChange,
}: {
  moreOpen: boolean;
  onMoreOpenChange: (open: boolean) => void;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <>
      <div className="pointer-events-none fixed inset-x-0 bottom-0 z-40 md:hidden">
        <div className="pointer-events-auto mx-auto mb-3 max-w-md px-3">
          <nav className="relative flex items-center justify-around gap-1 overflow-hidden rounded-2xl px-1 py-2 glass-depth hologram-edge">
            <div className="scan-line absolute inset-0 opacity-20" />
            {DOCK.map((item) => {
              const active = isActivePath(pathname, item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    "relative flex flex-1 flex-col items-center gap-0.5 rounded-xl px-2 py-1.5 text-[10px] font-medium transition-colors",
                    active ? "text-primary" : "text-muted-foreground",
                  )}
                >
                  {active && (
                    <motion.span
                      layoutId="mobile-dock-glow"
                      className="absolute inset-0 rounded-xl bg-primary/15"
                      transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                  )}
                  <item.icon className={cn("relative z-10 size-5", active && "drop-shadow-[0_0_8px_var(--brand)]")} />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              );
            })}
            <button
              type="button"
              onClick={() => onMoreOpenChange(true)}
              className="relative flex flex-1 flex-col items-center gap-0.5 rounded-xl px-2 py-1.5 text-[10px] font-medium text-muted-foreground"
            >
              <MoreHorizontal className="size-5" />
              <span>More</span>
            </button>
          </nav>
        </div>
      </div>

      <Sheet open={moreOpen} onOpenChange={onMoreOpenChange}>
        <SheetContent
          side="bottom"
          className="rounded-t-3xl border-border/60 bg-card/95 backdrop-blur-xl pb-8"
        >
          <SheetHeader className="text-left">
            <SheetTitle className="font-display">Command deck</SheetTitle>
          </SheetHeader>
          <div className="mt-4 grid grid-cols-3 gap-2">
            {MORE_LINKS.map((item) => {
              const active = isActivePath(pathname, item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => onMoreOpenChange(false)}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-2xl border px-2 py-4 text-center transition-all",
                    active
                      ? "border-primary/40 bg-primary/10 text-foreground shadow-glow"
                      : "border-border/60 bg-background/40 text-muted-foreground hover:border-primary/30 hover:text-foreground",
                  )}
                >
                  <item.icon className={cn("size-5", active && "text-primary")} />
                  <span className="text-[11px] font-medium leading-tight">{item.label}</span>
                </Link>
              );
            })}
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
