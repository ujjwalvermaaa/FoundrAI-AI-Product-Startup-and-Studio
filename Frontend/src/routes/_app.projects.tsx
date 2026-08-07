import { createFileRoute, Link, Outlet, useMatchRoute } from "@tanstack/react-router";
import { Plus, Search, Grid3x3, List, Sparkles, Loader2, AlertCircle } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";
import { useProjects } from "@/hooks/use-projects";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";

export const Route = createFileRoute("/_app/projects")({
  component: ProjectsLayout,
});

function ProjectsLayout() {
  const matchRoute = useMatchRoute();
  const isChild =
    !!matchRoute({ to: "/projects/$id", fuzzy: true }) ||
    !!matchRoute({ to: "/projects/new" });
  if (isChild) return <Outlet />;
  return <ProjectsIndex />;
}

function ProjectsIndex() {
  const [search, setSearch] = useState("");
  const { data: backendProjects, isLoading, isError, error } = useProjects();

  const projects = (backendProjects ?? []).map(mapBackendProjectToDisplay);

  const filtered = projects.filter(
    (p) =>
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.tagline.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <AppPage>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-end justify-between gap-4"
      >
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Workspace</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
            Your <span className="gradient-text">projects</span>
          </h1>
          <p className="text-muted-foreground mt-1">All the startups you're building with FoundrAI.</p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="relative">
            <Search className="size-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search projects…"
              className="pl-8 w-56"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="hidden md:flex rounded-md border border-border p-0.5">
            <Button size="sm" variant="ghost" className="h-7 px-2"><Grid3x3 className="size-3.5" /></Button>
            <Button size="sm" variant="ghost" className="h-7 px-2"><List className="size-3.5" /></Button>
          </div>
          <Button asChild>
            <Link to="/projects/new"><Plus className="size-4" /> New project</Link>
          </Button>
        </div>
      </motion.div>

      {isLoading && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="overflow-hidden h-[280px] animate-pulse">
              <div className="h-32 bg-muted" />
              <CardContent className="p-4 space-y-3">
                <div className="h-4 bg-muted rounded w-1/2" />
                <div className="h-3 bg-muted rounded w-3/4" />
                <div className="h-2 bg-muted rounded w-full mt-4" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {isError && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <AlertCircle className="size-10 text-destructive mb-3" />
          <div className="font-medium">Failed to load projects</div>
          <div className="text-sm text-muted-foreground mt-1">
            {(error as Error)?.message ?? "Something went wrong. Please try again."}
          </div>
        </div>
      )}

      {!isLoading && !isError && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p, i) => (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link to="/projects/$id" params={{ id: p.id }}>
                <Card className="overflow-hidden hover:border-primary/40 hover:shadow-glow transition-all h-full group">
                  <div className="h-32 relative" style={{ background: p.cover }}>
                    <div className="absolute inset-0 bg-gradient-to-t from-card via-card/40 to-transparent" />
                    <div className="absolute top-3 right-3 flex gap-1.5">
                      <Badge variant="secondary" className="capitalize backdrop-blur-md">{p.stage}</Badge>
                    </div>
                    <div className="absolute bottom-3 left-4">
                      <div className="text-xs text-white/80">{p.industry}</div>
                      <div className="font-display text-xl font-semibold text-white">{p.name}</div>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground line-clamp-2 min-h-10">{p.tagline}</p>
                    <div className="mt-4 flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{p.progress}% complete</span>
                      <span className="flex items-center gap-1 text-muted-foreground">
                        <Sparkles className="size-3" />
                        {p.modules.filter((m) => m.status !== "locked").length}/{p.modules.length} modules
                      </span>
                    </div>
                    <Progress value={p.progress} className="h-1 mt-2" />
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}

          <Link to="/projects/new">
            <Card className="border-dashed h-full min-h-[280px] flex items-center justify-center hover:border-primary/60 hover:bg-accent/30 transition-all cursor-pointer">
              <div className="text-center">
                <div className="size-12 rounded-full gradient-brand grid place-items-center mx-auto shadow-glow">
                  <Plus className="size-5 text-white" />
                </div>
                <div className="mt-3 font-display font-medium">Start a new startup</div>
                <div className="text-xs text-muted-foreground mt-1">Describe your idea, we do the rest.</div>
              </div>
            </Card>
          </Link>
        </div>
      )}
    </AppPage>
  );
}
