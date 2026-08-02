import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  Sparkles, ArrowUpRight, TrendingUp, Zap, Clock, FileText,
  LineChart as LineIcon, CheckCircle2, Loader2, Plus,
} from "lucide-react";
import {
  Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { SectionHeading } from "@/components/ui/section-heading";
import { AI_ACTIVITY, MOCK_ACTIVITY, MOCK_ARTIFACTS } from "@/lib/mock-data";
import { formatDistanceToNow } from "date-fns";
import { useProjects } from "@/hooks/use-projects";
import { useAuth } from "@/hooks/use-auth";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";

export const Route = createFileRoute("/_app/dashboard")({
  component: DashboardPage,
});

const stats = [
  { label: "Active projects", value: "4", delta: "+2", icon: Sparkles },
  { label: "AI generations", value: "1,284", delta: "+18%", icon: Zap },
  { label: "Docs created", value: "128", delta: "+12", icon: FileText },
  { label: "Avg. progress", value: "47%", delta: "+6%", icon: TrendingUp },
];

function DashboardPage() {
  const { user } = useAuth();
  const { data: backendProjects, isLoading: projectsLoading } = useProjects();

  const projects = (backendProjects ?? []).map(mapBackendProjectToDisplay).slice(0, 4);

  const greeting = user?.full_name
    ? `Good evening, ${user.full_name.split(" ")[0]}`
    : "Good evening";

  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto space-y-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-sm text-muted-foreground">{greeting}</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
            Your <span className="gradient-text">startup studio</span>
          </h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/chat"><Sparkles className="size-4" /> Ask FoundrAI</Link>
          </Button>
          <Button asChild>
            <Link to="/projects/new">
              <Plus className="size-4" /> New project
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="relative overflow-hidden group hover:border-primary/40 transition-colors">
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div className="text-xs text-muted-foreground">{s.label}</div>
                  <s.icon className="size-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <div className="mt-3 flex items-end justify-between">
                  <div className="font-display text-3xl font-semibold tracking-tight">{s.value}</div>
                  <Badge variant="secondary" className="text-[10px]">{s.delta}</Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2 overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="font-display">AI activity</CardTitle>
              <p className="text-sm text-muted-foreground">Generations and edits over the last 30 days.</p>
            </div>
            <Badge variant="outline" className="gap-1"><LineIcon className="size-3" /> Live</Badge>
          </CardHeader>
          <CardContent className="pl-2">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={AI_ACTIVITY}>
                  <defs>
                    <linearGradient id="gGen" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--brand)" stopOpacity={0.6} />
                      <stop offset="100%" stopColor="var(--brand)" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gEdit" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="var(--brand-glow)" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="var(--brand-glow)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="day" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "var(--popover)",
                      border: "1px solid var(--border)",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Area type="monotone" dataKey="generations" stroke="var(--brand)" strokeWidth={2} fill="url(#gGen)" />
                  <Area type="monotone" dataKey="edits" stroke="var(--brand-glow)" strokeWidth={2} fill="url(#gEdit)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">Quick actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { label: "Generate business model", icon: Sparkles },
              { label: "Run market research", icon: LineIcon },
              { label: "Draft investor deck", icon: FileText },
              { label: "Financial forecast", icon: TrendingUp },
            ].map((a) => (
              <button
                key={a.label}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-md border border-border hover:border-primary/40 hover:bg-accent/40 transition-colors text-sm text-left group"
              >
                <div className="size-8 rounded-md bg-accent grid place-items-center group-hover:gradient-brand group-hover:text-white transition-all">
                  <a.icon className="size-4" />
                </div>
                <span className="flex-1">{a.label}</span>
                <ArrowUpRight className="size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
              </button>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Recent projects — real data */}
      <div>
        <SectionHeading
          eyebrow="Recent"
          title="Your projects"
          description="Continue where you left off."
          action={
            <Button variant="ghost" asChild>
              <Link to="/projects">View all <ArrowUpRight className="size-4" /></Link>
            </Button>
          }
        />
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {projectsLoading &&
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="overflow-hidden h-[200px] animate-pulse">
                <div className="h-24 bg-muted" />
                <CardContent className="p-4 space-y-2">
                  <div className="h-4 bg-muted rounded w-1/2" />
                  <div className="h-3 bg-muted rounded w-3/4" />
                </CardContent>
              </Card>
            ))}
          {!projectsLoading &&
            projects.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
              >
                <Link to="/projects/$id" params={{ id: p.id }}>
                  <Card className="overflow-hidden hover:border-primary/40 hover:shadow-glow transition-all group h-full">
                    <div className="h-24 relative" style={{ background: p.cover }}>
                      <div className="absolute inset-0 bg-gradient-to-t from-card to-transparent" />
                      <div className="absolute top-3 right-3">
                        <Badge variant="secondary" className="capitalize backdrop-blur-md">{p.stage}</Badge>
                      </div>
                    </div>
                    <CardContent className="p-4 -mt-6 relative">
                      <div className="font-display text-lg font-semibold">{p.name}</div>
                      <p className="text-xs text-muted-foreground line-clamp-2 mt-1 min-h-8">{p.tagline}</p>
                      <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                        <span>{p.progress}% complete</span>
                        <span>{p.industry}</span>
                      </div>
                      <Progress value={p.progress} className="h-1 mt-1.5" />
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-display">Workflow timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="relative border-l border-border ml-2 space-y-5">
              {MOCK_ACTIVITY.map((a) => (
                <li key={a.id} className="pl-6 relative">
                  <span className="absolute -left-[7px] top-1.5 size-3 rounded-full gradient-brand ring-4 ring-background" />
                  <div className="flex flex-wrap items-baseline gap-2">
                    <span className="text-sm font-medium">{a.title}</span>
                    <Badge variant="outline" className="text-[10px] capitalize">{a.kind}</Badge>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {formatDistanceToNow(new Date(a.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    <Link to="/projects/$id" params={{ id: a.projectId }} className="hover:text-foreground">
                      {a.projectName}
                    </Link>
                    <span> — {a.detail}</span>
                  </div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">Recent documents</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {MOCK_ARTIFACTS.slice(0, 5).map((a) => (
              <div
                key={a.id}
                className="flex items-center gap-3 p-2 -mx-2 rounded-md hover:bg-accent/50 transition-colors"
              >
                <div className="size-9 rounded-md bg-accent grid place-items-center shrink-0">
                  <FileText className="size-4 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium truncate">{a.title}</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1.5">
                    {a.author === "AI" ? <Sparkles className="size-3" /> : <CheckCircle2 className="size-3" />}
                    <span>{a.author}</span>
                    <span>•</span>
                    <Clock className="size-3" />
                    {formatDistanceToNow(new Date(a.updatedAt), { addSuffix: true })}
                  </div>
                </div>
              </div>
            ))}
            <div className="pt-2 flex items-center gap-2 text-xs text-primary">
              <Loader2 className="size-3 animate-spin" /> 2 documents being generated…
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
