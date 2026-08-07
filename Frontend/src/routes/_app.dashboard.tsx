import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  Sparkles,
  ArrowUpRight,
  TrendingUp,
  Zap,
  Clock,
  FileText,
  LineChart as LineIcon,
  CheckCircle2,
  Loader2,
  Plus,
  MessageCircle,
  Activity,
  Hexagon,
} from "lucide-react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AI_ACTIVITY, MOCK_ACTIVITY, MOCK_ARTIFACTS } from "@/lib/mock-data";
import { formatDistanceToNow } from "date-fns";
import { useProjects } from "@/hooks/use-projects";
import { useAuth } from "@/hooks/use-auth";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/dashboard")({
  component: DashboardPage,
});

const ACTIONS = [
  { label: "Business model", icon: Sparkles, to: "/canvas" as const },
  { label: "Market research", icon: LineIcon, to: "/competitors" as const },
  { label: "Investor deck", icon: FileText, to: "/projects" as const },
  { label: "Forecast", icon: TrendingUp, to: "/analytics" as const },
];

function RingMetric({
  value,
  label,
  sub,
  delay = 0,
}: {
  value: string;
  label: string;
  sub: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, type: "spring", stiffness: 200, damping: 20 }}
      className="relative flex flex-col items-center text-center"
    >
      <div className="relative size-24 md:size-28">
        <svg className="size-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="42" fill="none" className="stroke-muted/60" strokeWidth="6" />
          <motion.circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            className="stroke-primary"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray="264"
            initial={{ strokeDashoffset: 264 }}
            animate={{ strokeDashoffset: 264 * (1 - 0.62) }}
            transition={{ delay: delay + 0.2, duration: 1.2, ease: "easeOut" }}
            style={{ filter: "drop-shadow(0 0 8px var(--brand))" }}
          />
        </svg>
        <div className="absolute inset-0 grid place-items-center">
          <span className="font-display text-xl md:text-2xl font-semibold tracking-tight">{value}</span>
        </div>
      </div>
      <div className="mt-2 text-xs font-medium">{label}</div>
      <div className="text-[10px] font-mono text-primary/80">{sub}</div>
    </motion.div>
  );
}

function DashboardPage() {
  const { user } = useAuth();
  const { data: backendProjects, isLoading: projectsLoading } = useProjects();
  const projects = (backendProjects ?? []).map(mapBackendProjectToDisplay).slice(0, 5);
  const firstName = user?.full_name?.split(" ")[0] ?? "Founder";
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="relative p-4 md:p-6 lg:p-8 max-w-[1500px] mx-auto space-y-5 md:space-y-6">
      {/* ── Mission Control Header ── */}
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-[1.75rem] hologram-edge"
      >
        <div className="absolute inset-0 gradient-brand opacity-[0.18]" />
        <div className="absolute inset-0 mesh-ambient opacity-70" />
        <div className="absolute inset-0 grid-bg opacity-20" />
        <div className="scan-line absolute inset-0 opacity-30" />
        <div className="pointer-events-none absolute -right-20 -top-20 size-72 rounded-full bg-brand-glow/30 blur-[80px]" />
        <div className="pointer-events-none absolute -left-16 bottom-0 size-56 rounded-full bg-primary/25 blur-[70px]" />

        <div className="relative z-10 grid lg:grid-cols-[1.4fr_auto_1fr] gap-8 p-6 md:p-8 items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/20 px-3 py-1 text-[10px] uppercase tracking-[0.22em] text-white/80 backdrop-blur-md">
              <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Mission control · online
            </div>
            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight mt-4 leading-[1.02] text-foreground">
              {greeting},
              <br />
              <span className="gradient-text">{firstName}</span>
            </h1>
            <p className="mt-3 text-sm md:text-base text-muted-foreground max-w-md">
              Your studio is humming. Pick up a venture, launch an agent, or ask Foundr what to ship next.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              <Button asChild className="h-11 px-5 shadow-glow">
                <Link to="/projects/new">
                  <Plus className="size-4" /> New venture
                </Link>
              </Button>
              <Button variant="outline" asChild className="h-11 px-5 border-white/20 bg-white/5 backdrop-blur-md">
                <Link to="/chat">
                  <MessageCircle className="size-4" /> Ask Foundr
                </Link>
              </Button>
              <Button variant="ghost" asChild className="h-11 px-4">
                <Link to="/health">
                  <Activity className="size-4" /> Health
                </Link>
              </Button>
            </div>
          </div>

          <div className="hidden lg:flex items-center justify-center">
            <div className="relative size-40">
              <div className="absolute inset-0 rounded-full pulse-core bg-primary/30 blur-xl" />
              <svg className="absolute inset-0 size-full orbit-ring text-primary/40" viewBox="0 0 160 160" fill="none">
                <circle cx="80" cy="80" r="72" stroke="currentColor" strokeWidth="1" strokeDasharray="8 12" />
              </svg>
              <svg className="absolute inset-3 size-[calc(100%-24px)] orbit-ring-reverse text-brand-glow/35" viewBox="0 0 140 140" fill="none">
                <circle cx="70" cy="70" r="62" stroke="currentColor" strokeWidth="1" strokeDasharray="3 10" />
              </svg>
              <div className="absolute inset-8 rounded-full overflow-hidden ring-2 ring-primary/40 shadow-glow">
                <img src="/founder-bot.jpg" alt="" className="size-full object-cover" />
              </div>
              <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full border border-primary/30 bg-background/80 px-2.5 py-0.5 text-[10px] font-mono text-primary backdrop-blur-md">
                co-pilot ready
              </div>
            </div>
          </div>

          <div className="flex justify-around lg:justify-end gap-4 md:gap-6">
            <RingMetric value="4" label="Ventures" sub="+2 wk" delay={0.1} />
            <RingMetric value="47%" label="Progress" sub="avg" delay={0.2} />
            <RingMetric value="1.2k" label="Generations" sub="+18%" delay={0.3} />
          </div>
        </div>
      </motion.section>

      {/* ── Mid row: neural pulse + agent launcher ── */}
      <div className="grid lg:grid-cols-[1.7fr_1fr] gap-4 md:gap-5">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative overflow-hidden rounded-[1.5rem] glass-depth hologram-edge min-h-[300px]"
        >
          <div className="scan-line absolute inset-0 opacity-20" />
          <div className="relative z-10 flex items-start justify-between p-5 md:p-6 pb-0">
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90">Neural pulse</div>
              <h2 className="font-display text-2xl font-semibold tracking-tight mt-1">AI activity · 30d</h2>
            </div>
            <Badge variant="outline" className="gap-1.5 border-primary/30 text-primary">
              <span className="size-1.5 rounded-full bg-primary animate-pulse" /> Live feed
            </Badge>
          </div>
          <div className="relative z-10 h-56 md:h-64 px-2 pb-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={AI_ACTIVITY}>
                <defs>
                  <linearGradient id="dashGen" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.55} />
                    <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Tooltip
                  contentStyle={{
                    background: "color-mix(in oklab, var(--popover) 90%, transparent)",
                    border: "1px solid var(--border)",
                    borderRadius: 12,
                    fontSize: 12,
                    backdropFilter: "blur(12px)",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="generations"
                  stroke="var(--brand)"
                  strokeWidth={2.5}
                  fill="url(#dashGen)"
                  dot={false}
                />
                <Area
                  type="monotone"
                  dataKey="edits"
                  stroke="var(--brand-glow)"
                  strokeWidth={1.5}
                  fill="transparent"
                  strokeDasharray="4 4"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="relative overflow-hidden rounded-[1.5rem] glass-depth hologram-edge p-5 md:p-6"
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90">Agent bay</div>
          <h2 className="font-display text-2xl font-semibold tracking-tight mt-1 mb-5">Launch</h2>
          <div className="grid grid-cols-2 gap-2.5">
            {ACTIONS.map((a, i) => (
              <motion.div
                key={a.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + i * 0.05 }}
              >
                <Link
                  to={a.to}
                  className="group relative flex aspect-square flex-col items-center justify-center gap-2.5 rounded-2xl border border-border/60 bg-muted/20 p-3 text-center transition-all hover:border-primary/45 hover:bg-primary/10 hover:shadow-glow"
                >
                  <div className="size-11 rounded-2xl bg-background/60 border border-border/50 grid place-items-center group-hover:gradient-brand group-hover:text-white group-hover:border-transparent transition-all">
                    <a.icon className="size-5" />
                  </div>
                  <span className="text-xs font-medium leading-tight">{a.label}</span>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* ── Project constellation (horizontal rail, not card grid) ── */}
      <section>
        <div className="flex items-end justify-between gap-4 mb-4 px-1">
          <div>
            <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90">Constellation</div>
            <h2 className="font-display text-2xl md:text-3xl font-semibold tracking-tight mt-1">
              Active <span className="gradient-text">ventures</span>
            </h2>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              All projects <ArrowUpRight className="size-4" />
            </Link>
          </Button>
        </div>

        <div className="relative -mx-1">
          <div className="flex gap-4 overflow-x-auto pb-3 px-1 snap-x snap-mandatory scrollbar-thin">
            {projectsLoading &&
              Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="snap-start shrink-0 w-[280px] h-[200px] rounded-[1.35rem] bg-muted/40 animate-pulse"
                />
              ))}
            {!projectsLoading &&
              projects.map((p, i) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, x: 24 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.08 * i }}
                  className="snap-start shrink-0 w-[min(86vw,300px)]"
                >
                  <Link to="/projects/$id" params={{ id: p.id }} className="block group">
                    <div className="relative h-[210px] overflow-hidden rounded-[1.35rem] hologram-edge transition-transform duration-300 group-hover:-translate-y-1 group-hover:shadow-glow">
                      <div className="absolute inset-0" style={{ background: p.cover }} />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/35 to-transparent" />
                      <div className="scan-line absolute inset-0 opacity-25" />
                      <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
                        <Badge className="bg-black/40 text-white border-white/20 backdrop-blur-md capitalize text-[10px]">
                          {p.stage}
                        </Badge>
                        <span className="font-mono text-[11px] text-white/80">{p.progress}%</span>
                      </div>
                      <div className="absolute bottom-0 left-0 right-0 p-4">
                        <div className="font-display text-xl font-semibold text-white tracking-tight">{p.name}</div>
                        <p className="text-xs text-white/70 line-clamp-2 mt-1">{p.tagline}</p>
                        <div className="mt-3 h-1 rounded-full bg-white/20 overflow-hidden">
                          <motion.div
                            className="h-full bg-white"
                            initial={{ width: 0 }}
                            animate={{ width: `${p.progress}%` }}
                            transition={{ delay: 0.3 + i * 0.05, duration: 0.8 }}
                          />
                        </div>
                        <div className="mt-2 text-[10px] uppercase tracking-wider text-white/50">{p.industry}</div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}

            <Link
              to="/projects/new"
              className="snap-start shrink-0 w-[180px] h-[210px] rounded-[1.35rem] border border-dashed border-primary/35 bg-primary/5 grid place-items-center text-center p-4 hover:bg-primary/10 hover:border-primary/55 transition-colors"
            >
              <div>
                <div className="size-12 mx-auto rounded-2xl border border-primary/30 grid place-items-center mb-3">
                  <Plus className="size-5 text-primary" />
                </div>
                <div className="text-sm font-medium">New venture</div>
                <div className="text-[11px] text-muted-foreground mt-1">Start from an idea</div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Mission log + artifact stream ── */}
      <div className="grid lg:grid-cols-5 gap-4 md:gap-5">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-3 relative overflow-hidden rounded-[1.5rem] glass-depth hologram-edge p-5 md:p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90">Mission log</div>
              <h2 className="font-display text-xl font-semibold tracking-tight mt-1">Workflow timeline</h2>
            </div>
            <Hexagon className="size-4 text-primary/50" />
          </div>
          <div className="space-y-0">
            {MOCK_ACTIVITY.map((a, i) => (
              <div key={a.id} className="relative flex gap-4 pb-6 last:pb-0">
                {i < MOCK_ACTIVITY.length - 1 && (
                  <div className="absolute left-[11px] top-7 bottom-0 w-px bg-gradient-to-b from-primary/40 to-transparent" />
                )}
                <div className="relative z-10 mt-1 size-[22px] shrink-0 rounded-full gradient-brand shadow-glow grid place-items-center">
                  <div className="size-1.5 rounded-full bg-white" />
                </div>
                <div className="min-w-0 flex-1 rounded-xl border border-border/40 bg-muted/15 px-3.5 py-3 hover:border-primary/30 transition-colors">
                  <div className="flex flex-wrap items-baseline gap-2">
                    <span className="text-sm font-medium">{a.title}</span>
                    <Badge variant="outline" className="text-[10px] capitalize">
                      {a.kind}
                    </Badge>
                    <span className="text-[11px] text-muted-foreground ml-auto font-mono">
                      {formatDistanceToNow(new Date(a.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    <Link to="/projects/$id" params={{ id: a.projectId }} className="text-primary/90 hover:underline">
                      {a.projectName}
                    </Link>
                    <span> — {a.detail}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="lg:col-span-2 relative overflow-hidden rounded-[1.5rem] glass-depth hologram-edge p-5 md:p-6"
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90">Artifact stream</div>
          <h2 className="font-display text-xl font-semibold tracking-tight mt-1 mb-5">Recent docs</h2>
          <div className="space-y-2">
            {MOCK_ARTIFACTS.slice(0, 5).map((a, i) => (
              <motion.div
                key={a.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.04 }}
                className={cn(
                  "flex items-center gap-3 rounded-xl border border-border/40 bg-muted/10 p-2.5",
                  "hover:border-primary/35 hover:bg-primary/5 transition-colors",
                )}
              >
                <div className="size-10 rounded-xl border border-primary/20 bg-primary/10 grid place-items-center shrink-0">
                  <FileText className="size-4 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium truncate">{a.title}</div>
                  <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 mt-0.5">
                    {a.author === "AI" ? <Sparkles className="size-3 text-primary" /> : <CheckCircle2 className="size-3" />}
                    <span>{a.author}</span>
                    <span>·</span>
                    <Clock className="size-3" />
                    {formatDistanceToNow(new Date(a.updatedAt), { addSuffix: true })}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
          <div className="mt-4 flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-3 py-2.5 text-xs text-primary">
            <Loader2 className="size-3.5 animate-spin" />
            2 documents generating in the neural queue…
          </div>
        </motion.div>
      </div>
    </div>
  );
}
