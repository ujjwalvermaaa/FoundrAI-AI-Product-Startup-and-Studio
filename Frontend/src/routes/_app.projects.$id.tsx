import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import {
  Sparkles, Lightbulb, LineChart, Layers, Compass, Network,
  Wallet, Megaphone, FileText, ChevronRight, Play, MoreHorizontal,
  MessageSquare, History, Clock, CheckCircle2, Circle, Loader2,
  Lock, ArrowUpRight, XCircle, AlertCircle, X, Download, Copy,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useProject } from "@/hooks/use-projects";
import { useArtifacts } from "@/hooks/use-artifacts";
import { useTriggerWorkflow, useWorkflowRuns, useWorkflowStream } from "@/hooks/use-workflow";
import { mapBackendProjectToDisplay } from "@/lib/project-mapper";
import type { BackendArtifact, BackendModuleKey, ModuleStatus } from "@/lib/types";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Lightbulb, LineChart, Layers, Compass, Network, Wallet, Megaphone, FileText,
};

const ID_TO_MODULE_KEY: Record<string, BackendModuleKey> = {
  "idea-validation": "idea_validation",
  "market-research": "market_research",
  "business-model": "business_model",
  "product-strategy": "product_strategy",
  "technical-architecture": "technical_architecture",
  "financial-planning": "financial_planning",
  "marketing-strategy": "marketing_strategy",
  "investor-documentation": "investor_documentation",
};

export const Route = createFileRoute("/_app/projects/$id")({
  component: ProjectWorkspace,
  notFoundComponent: () => (
    <div className="p-10 text-center">
      <h1 className="font-display text-2xl font-semibold">Project not found</h1>
      <Link to="/projects" className="text-primary text-sm mt-2 inline-block">Back to projects</Link>
    </div>
  ),
});

function statusIcon(s: ModuleStatus) {
  if (s === "complete") return <CheckCircle2 className="size-3.5 text-emerald-500" />;
  if (s === "in_progress") return <Loader2 className="size-3.5 text-primary animate-spin" />;
  if (s === "review") return <Circle className="size-3.5 text-amber-500 fill-amber-500/30" />;
  if (s === "locked") return <Lock className="size-3.5 text-muted-foreground" />;
  return <Circle className="size-3.5 text-muted-foreground" />;
}

function statusLabel(s: ModuleStatus) {
  return { complete: "Complete", in_progress: "In progress", review: "Review", locked: "Locked", not_started: "Not started" }[s];
}

// ── Artifact Viewer Sheet ──────────────────────────────────────────────────

function renderContentJson(data: Record<string, unknown>): string {
  const lines: string[] = [];
  for (const [key, val] of Object.entries(data)) {
    const label = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    if (Array.isArray(val)) {
      lines.push(`**${label}**`);
      (val as unknown[]).forEach((item) => {
        if (typeof item === "object" && item !== null) {
          lines.push("  " + Object.entries(item as Record<string, unknown>).map(([k, v]) => `${k}: ${v}`).join(" · "));
        } else {
          lines.push(`  • ${item}`);
        }
      });
    } else if (typeof val === "object" && val !== null) {
      lines.push(`**${label}**`);
      Object.entries(val as Record<string, unknown>).forEach(([k, v]) => {
        lines.push(`  ${k.replace(/_/g, " ")}: ${v}`);
      });
    } else {
      lines.push(`**${label}:** ${val}`);
    }
    lines.push("");
  }
  return lines.join("\n");
}

function ArtifactViewer({
  artifact,
  open,
  onClose,
}: {
  artifact: BackendArtifact | null;
  open: boolean;
  onClose: () => void;
}) {
  if (!artifact) return null;

  const markdown = artifact.content_markdown || renderContentJson(artifact.content_json);

  function copyToClipboard() {
    navigator.clipboard.writeText(markdown);
    toast.success("Copied to clipboard");
  }

  function downloadMd() {
    const blob = new Blob([markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, "_").toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-2xl p-0 flex flex-col">
        {/* Header */}
        <SheetHeader className="px-6 py-5 border-b border-border flex-row items-start justify-between gap-4 space-y-0">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="text-[10px] capitalize">{artifact.artifact_type.replace(/_/g, " ")}</Badge>
              <Badge variant="secondary" className="text-[10px] capitalize">{artifact.source}</Badge>
            </div>
            <SheetTitle className="font-display text-xl leading-tight">{artifact.title}</SheetTitle>
            <p className="text-xs text-muted-foreground mt-1">
              Updated {formatDistanceToNow(new Date(artifact.updated_at), { addSuffix: true })}
            </p>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={copyToClipboard} title="Copy">
              <Copy className="size-3.5" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={downloadMd} title="Download .md">
              <Download className="size-3.5" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onClose}>
              <X className="size-3.5" />
            </Button>
          </div>
        </SheetHeader>

        {/* Content */}
        <ScrollArea className="flex-1 min-h-0">
          <div className="px-6 py-6">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <MarkdownRenderer content={markdown} />
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}

function MarkdownRenderer({ content }: { content: string }) {
  // Parse line by line for reliable rendering
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;
  let key = 0;

  const inlineFormat = (text: string) => {
    // Bold, code, preserve rest
    const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
    return parts.map((part, pi) => {
      if (part.startsWith("**") && part.endsWith("**"))
        return <strong key={pi}>{part.slice(2, -2)}</strong>;
      if (part.startsWith("`") && part.endsWith("`"))
        return <code key={pi} className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{part.slice(1, -1)}</code>;
      return part;
    });
  };

  while (i < lines.length) {
    const line = lines[i];

    // H1
    if (line.startsWith("# ")) {
      elements.push(<h1 key={key++} className="font-display text-2xl font-semibold mt-2 mb-4">{line.slice(2)}</h1>);
      i++; continue;
    }
    // H2
    if (line.startsWith("## ")) {
      elements.push(<h2 key={key++} className="font-display text-lg font-semibold mt-6 mb-2 border-b border-border pb-1">{line.slice(3)}</h2>);
      i++; continue;
    }
    // H3
    if (line.startsWith("### ")) {
      elements.push(<h3 key={key++} className="font-display text-base font-semibold mt-4 mb-1">{line.slice(4)}</h3>);
      i++; continue;
    }

    // Table — collect all pipe rows
    if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      // First row = header, second row = separator (skip), rest = body
      const parseRow = (r: string) => r.split("|").slice(1, -1).map((c) => c.trim());
      const headers = parseRow(tableLines[0]);
      const bodyRows = tableLines.slice(2); // skip separator row
      elements.push(
        <div key={key++} className="overflow-x-auto my-3">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-border">
                {headers.map((h, hi) => (
                  <th key={hi} className="text-left px-3 py-2 font-semibold text-foreground bg-muted/40 first:rounded-tl last:rounded-tr">{inlineFormat(h)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {bodyRows.map((row, ri) => (
                <tr key={ri} className="border-b border-border/50 hover:bg-muted/20 transition-colors">
                  {parseRow(row).map((cell, ci) => (
                    <td key={ci} className="px-3 py-2 text-foreground/90">{inlineFormat(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Checklist item
    if (line.startsWith("- [ ] ") || line.startsWith("- [x] ")) {
      const checked = line.startsWith("- [x] ");
      const text = line.slice(6);
      elements.push(
        <div key={key++} className="flex items-start gap-2 my-1">
          <span className={`mt-0.5 size-4 rounded border shrink-0 grid place-items-center text-[10px] ${checked ? "border-primary bg-primary text-white" : "border-border"}`}>
            {checked && "✓"}
          </span>
          <span className={`text-sm ${checked ? "line-through text-muted-foreground" : ""}`}>{inlineFormat(text)}</span>
        </div>
      );
      i++; continue;
    }

    // Bullet list
    if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <div key={key++} className="flex items-start gap-2 my-0.5">
          <span className="mt-2 size-1.5 rounded-full bg-primary shrink-0" />
          <span className="text-sm leading-relaxed">{inlineFormat(line.slice(2))}</span>
        </div>
      );
      i++; continue;
    }

    // Numbered list
    const numMatch = line.match(/^(\d+)\. (.+)/);
    if (numMatch) {
      elements.push(
        <div key={key++} className="flex items-start gap-2 my-0.5">
          <span className="text-xs text-muted-foreground shrink-0 w-5 text-right mt-0.5">{numMatch[1]}.</span>
          <span className="text-sm leading-relaxed">{inlineFormat(numMatch[2])}</span>
        </div>
      );
      i++; continue;
    }

    // Blank line
    if (line.trim() === "") {
      elements.push(<div key={key++} className="h-2" />);
      i++; continue;
    }

    // Horizontal rule
    if (line.trim() === "---" || line.trim() === "***") {
      elements.push(<hr key={key++} className="border-border my-3" />);
      i++; continue;
    }

    // Regular paragraph
    elements.push(
      <p key={key++} className="text-sm leading-relaxed text-foreground/90">{inlineFormat(line)}</p>
    );
    i++;
  }

  return <div className="space-y-0.5">{elements}</div>;
}

// ── Main workspace ─────────────────────────────────────────────────────────

function ProjectWorkspace() {
  const { id } = Route.useParams();
  const [activeModuleIndex, setActiveModuleIndex] = useState(0);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [streamSteps, setStreamSteps] = useState<Array<{ key: string; status: "started" | "completed" }>>([]);
  const [openArtifact, setOpenArtifact] = useState<BackendArtifact | null>(null);

  const { data: backendProject, isLoading, isError, error, refetch } = useProject(id);
  const { data: backendArtifacts } = useArtifacts(id);
  const triggerWorkflow = useTriggerWorkflow();
  const { data: runs } = useWorkflowRuns(id);

  useWorkflowStream(id, activeRunId ?? "", {
    onStepStarted: (stepKey) => {
      setStreamSteps((prev) => prev.find((s) => s.key === stepKey) ? prev : [...prev, { key: stepKey, status: "started" }]);
    },
    onStepCompleted: (stepKey) => {
      setStreamSteps((prev) => prev.map((s) => s.key === stepKey ? { ...s, status: "completed" } : s));
    },
    onRunCompleted: () => { setActiveRunId(null); setStreamSteps([]); toast.success("Workflow completed"); },
    onRunFailed: (event) => { setActiveRunId(null); setStreamSteps([]); toast.error(event.error_message ?? "Workflow failed"); },
  });

  if (isLoading) {
    return (
      <div className="p-8 max-w-[1400px] mx-auto space-y-4">
        <div className="h-48 rounded-xl bg-muted animate-pulse" />
        <div className="grid lg:grid-cols-[280px_1fr] gap-8">
          <div className="space-y-2">{Array.from({ length: 8 }).map((_, i) => <div key={i} className="h-14 rounded-lg bg-muted animate-pulse" />)}</div>
          <div className="h-96 rounded-xl bg-muted animate-pulse" />
        </div>
      </div>
    );
  }

  if (isError || !backendProject) {
    return (
      <div className="p-10 text-center flex flex-col items-center gap-3">
        <AlertCircle className="size-10 text-destructive" />
        <h1 className="font-display text-2xl font-semibold">Failed to load project</h1>
        <p className="text-sm text-muted-foreground">{(error as Error)?.message ?? "Something went wrong."}</p>
        <Button variant="outline" onClick={() => void refetch()}>Try again</Button>
        <Link to="/projects" className="text-primary text-sm">Back to projects</Link>
      </div>
    );
  }

  const project = mapBackendProjectToDisplay(backendProject);
  const artifacts = backendArtifacts ?? [];
  const active = project.modules[activeModuleIndex] ?? project.modules[0];
  const moduleKey = ID_TO_MODULE_KEY[active?.id ?? ""];
  const moduleArtifacts = artifacts.filter((a) => a.module_key === moduleKey);
  const activeBackendModule = backendProject.modules.find((m) => m.module_key === moduleKey);
  const isRunning = !!activeRunId || active?.status === "in_progress";

  async function handleRunModule() {
    if (!active || !moduleKey) return;
    try {
      const result = await triggerWorkflow.mutateAsync({ projectId: id, moduleKey });
      setActiveRunId(result.run_id);
      setStreamSteps([]);
    } catch { /* handled by hook */ }
  }

  return (
    <>
      <ArtifactViewer artifact={openArtifact} open={!!openArtifact} onClose={() => setOpenArtifact(null)} />

      <div className="min-h-full">
        {/* Project header */}
        <div className="relative overflow-hidden border-b border-border">
          <div className="absolute inset-0 opacity-40" style={{ background: project.cover }} />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background" />
          <div className="relative p-6 md:p-8 max-w-[1400px] mx-auto">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 text-xs">
                  <Badge variant="secondary" className="capitalize">{project.stage}</Badge>
                  <span className="text-muted-foreground">{project.industry}</span>
                  <span className="text-muted-foreground">•</span>
                  <span className="text-muted-foreground flex items-center gap-1">
                    <Clock className="size-3" /> updated {formatDistanceToNow(new Date(project.updatedAt), { addSuffix: true })}
                  </span>
                </div>
                <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">{project.name}</h1>
                <p className="text-muted-foreground mt-2 max-w-2xl">{project.tagline}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline"><MessageSquare className="size-4" /> Comments</Button>
                <Button variant="outline"><History className="size-4" /> Versions</Button>
                <Button onClick={handleRunModule} disabled={isRunning || triggerWorkflow.isPending}>
                  {isRunning ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
                  {isRunning ? "Running…" : "Generate next"}
                </Button>
              </div>
            </div>
            <div className="mt-8 flex items-center gap-4">
              <div className="flex-1 max-w-xl">
                <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
                  <span>Overall progress</span><span>{project.progress}%</span>
                </div>
                <Progress value={project.progress} className="h-2" />
              </div>
              {isRunning && (
                <div className="flex items-center gap-1 px-3 py-1.5 rounded-full border border-border bg-background/60 backdrop-blur text-xs">
                  <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  AI working on <span className="font-medium">{active?.name}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="max-w-[1400px] mx-auto p-6 md:p-8 grid lg:grid-cols-[280px_1fr] gap-8">
          {/* Module nav */}
          <aside className="space-y-1">
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground font-medium px-2 mb-2">Modules</div>
            {project.modules.map((m, i) => {
              const Icon = ICONS[m.icon] ?? Sparkles;
              const isActive = i === activeModuleIndex;
              return (
                <motion.button
                  key={m.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  onClick={() => setActiveModuleIndex(i)}
                  className={cn(
                    "w-full text-left px-3 py-2.5 rounded-lg border transition-all group",
                    isActive ? "border-primary/40 bg-accent/60 shadow-glow" : "border-transparent hover:border-border hover:bg-accent/40",
                    m.status === "locked" && "opacity-60",
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <div className={cn("size-8 rounded-md grid place-items-center shrink-0", isActive ? "gradient-brand text-white" : "bg-muted text-muted-foreground")}>
                      <Icon className="size-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="text-sm font-medium truncate">{m.name}</span>
                        {statusIcon(m.status)}
                      </div>
                      <div className="mt-1 h-1 rounded-full bg-muted overflow-hidden">
                        <div className="h-full gradient-brand transition-all" style={{ width: `${m.progress}%` }} />
                      </div>
                    </div>
                    <ChevronRight className="size-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition" />
                  </div>
                </motion.button>
              );
            })}
          </aside>

          {/* Main panel */}
          <div className="min-w-0 space-y-6">
            {active && (
              <Card>
                <CardHeader className="flex flex-row items-start justify-between gap-4">
                  <div>
                    <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">
                      Module {activeModuleIndex + 1} of {project.modules.length}
                    </div>
                    <CardTitle className="font-display text-2xl mt-1">{active.name}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">{active.description}</p>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Badge variant="outline" className="gap-1">{statusIcon(active.status)} {statusLabel(active.status)}</Badge>
                    {active.status !== "locked" && (
                      <Button size="sm" onClick={handleRunModule} disabled={isRunning || triggerWorkflow.isPending}>
                        {isRunning ? <Loader2 className="size-3.5 animate-spin" /> : <Play className="size-3.5" />}
                        {isRunning ? "Running" : "Run"}
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="artifacts">
                    <TabsList>
                      <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
                      <TabsTrigger value="workflow">Workflow</TabsTrigger>
                      <TabsTrigger value="preview">Preview</TabsTrigger>
                    </TabsList>

                    {/* Artifacts tab */}
                    <TabsContent value="artifacts" className="mt-4 space-y-2">
                      {moduleArtifacts.length === 0 ? (
                        <div className="border border-dashed rounded-lg p-10 text-center">
                          <Sparkles className="size-6 text-muted-foreground mx-auto" />
                          <div className="font-medium mt-3">No artifacts yet</div>
                          <div className="text-sm text-muted-foreground mt-1">Run this module to generate documents, diagrams and canvases.</div>
                          {active.status !== "locked" && (
                            <Button className="mt-4" onClick={handleRunModule} disabled={isRunning || triggerWorkflow.isPending}>
                              <Sparkles className="size-4" /> Generate
                            </Button>
                          )}
                        </div>
                      ) : (
                        moduleArtifacts.map((a) => (
                          <div key={a.id} className="flex items-center gap-3 p-3 border border-border rounded-lg hover:border-primary/40 transition-colors group cursor-pointer"
                            onClick={() => setOpenArtifact(a)}>
                            <div className="size-10 rounded-md bg-accent grid place-items-center shrink-0">
                              <FileText className="size-4 text-primary" />
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="text-sm font-medium truncate">{a.title}</div>
                              <div className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                                <span className="capitalize">{a.artifact_type.replace(/_/g, " ")}</span>
                                <span>•</span>
                                <span className="capitalize">{a.source === "ai" ? "AI" : "You"}</span>
                                <span>•</span>
                                <span>{formatDistanceToNow(new Date(a.updated_at), { addSuffix: true })}</span>
                              </div>
                            </div>
                            <Button variant="ghost" size="icon"
                              className="opacity-0 group-hover:opacity-100 transition-opacity"
                              onClick={(e) => { e.stopPropagation(); setOpenArtifact(a); }}>
                              <ArrowUpRight className="size-4" />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={(e) => e.stopPropagation()}>
                              <MoreHorizontal className="size-4" />
                            </Button>
                          </div>
                        ))
                      )}
                    </TabsContent>

                    {/* Workflow tab */}
                    <TabsContent value="workflow" className="mt-4">
                      {streamSteps.length > 0 ? (
                        <ol className="space-y-2">
                          {streamSteps.map((s, i) => (
                            <li key={s.key} className="flex items-center gap-3 p-3 rounded-md border border-border">
                              {s.status === "completed" ? <CheckCircle2 className="size-3.5 text-emerald-500" /> : <Loader2 className="size-3.5 text-primary animate-spin" />}
                              <span className="text-sm">{i + 1}. {s.key.replace(/_/g, " ")}</span>
                              {s.status === "started" && <Badge variant="outline" className="ml-auto">Now</Badge>}
                            </li>
                          ))}
                        </ol>
                      ) : runs && runs.find((r) => r.module_key === moduleKey) ? (
                        <ol className="space-y-2">
                          {(runs.find((r) => r.module_key === moduleKey)?.steps ?? [])
                            .sort((a, b) => a.sequence - b.sequence)
                            .map((step, i) => (
                              <li key={step.id} className="flex items-center gap-3 p-3 rounded-md border border-border">
                                {step.status === "completed" ? <CheckCircle2 className="size-3.5 text-emerald-500" /> :
                                  step.status === "failed" ? <XCircle className="size-3.5 text-destructive" /> :
                                  step.status === "running" ? <Loader2 className="size-3.5 text-primary animate-spin" /> :
                                  <Circle className="size-3.5 text-muted-foreground" />}
                                <span className={cn("text-sm", step.status === "pending" && "text-muted-foreground")}>
                                  {i + 1}. {step.step_key.replace(/_/g, " ")}
                                </span>
                              </li>
                            ))}
                        </ol>
                      ) : (
                        <div className="text-sm text-muted-foreground py-8 text-center border border-dashed rounded-lg">
                          No workflow runs yet for this module.
                          {active.status !== "locked" && (
                            <div className="mt-3">
                              <Button size="sm" variant="outline" onClick={handleRunModule} disabled={isRunning}>
                                <Play className="size-3.5" /> Run now
                              </Button>
                            </div>
                          )}
                        </div>
                      )}
                    </TabsContent>

                    {/* Preview tab */}
                    <TabsContent value="preview" className="mt-4">
                      {moduleArtifacts.length > 0 ? (
                        <div className="space-y-4">
                          {moduleArtifacts.slice(0, 1).map((a) => (
                            <div key={a.id} className="rounded-lg border border-border bg-muted/20 p-6">
                              <div className="flex items-center justify-between mb-4">
                                <h3 className="font-display text-lg font-semibold">{a.title}</h3>
                                <Button size="sm" variant="outline" onClick={() => setOpenArtifact(a)}>
                                  <ArrowUpRight className="size-3.5" /> Open full view
                                </Button>
                              </div>
                              <div className="prose prose-sm dark:prose-invert max-w-none">
                                <MarkdownRenderer content={(a.content_markdown || renderContentJson(a.content_json)).slice(0, 800) + (((a.content_markdown || "").length > 800) ? "\n\n*… click Open full view to read more*" : "")} />
                              </div>
                            </div>
                          ))}
                          {moduleArtifacts.length > 1 && (
                            <p className="text-xs text-muted-foreground text-center">
                              + {moduleArtifacts.length - 1} more artifact{moduleArtifacts.length > 2 ? "s" : ""} — click Artifacts tab to see all
                            </p>
                          )}
                        </div>
                      ) : (
                        <div className="rounded-lg border border-border bg-muted/20 p-6">
                          <h3 className="font-display text-xl font-semibold">{active.name} — Preview</h3>
                          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                            {project.name} operates in the {project.industry.toLowerCase()} space. Run this module to generate AI-powered insights and artifacts.
                          </p>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}

            {/* Bottom cards */}
            <div className="grid md:grid-cols-2 gap-4">
              <Card>
                <CardHeader><CardTitle className="font-display text-lg">Run history</CardTitle></CardHeader>
                <CardContent className="text-sm">
                  {!runs || runs.filter((r) => r.module_key === moduleKey).length === 0 ? (
                    <div className="text-xs text-muted-foreground py-4 text-center">No runs yet.</div>
                  ) : (
                    runs.filter((r) => r.module_key === moduleKey).slice(0, 5).map((run) => (
                      <div key={run.id} className="flex items-center justify-between py-2 border-b last:border-0 border-border">
                        <div>
                          <div className="font-medium capitalize">{run.status}</div>
                          <div className="text-xs text-muted-foreground">
                            {run.created_at ? formatDistanceToNow(new Date(run.created_at), { addSuffix: true }) : "—"}
                          </div>
                        </div>
                        <Badge variant="outline" className={cn("text-[10px]",
                          run.status === "completed" && "border-emerald-500/40 text-emerald-500",
                          run.status === "failed" && "border-destructive/40 text-destructive",
                          run.status === "running" && "border-primary/40 text-primary",
                        )}>{run.status}</Badge>
                      </div>
                    ))
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle className="font-display text-lg">Module details</CardTitle></CardHeader>
                <CardContent>
                  {activeBackendModule ? (
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between py-1.5 border-b border-border/50">
                        <span className="text-muted-foreground">Status</span>
                        <span className="font-medium capitalize">{activeBackendModule.status.replace("_", " ")}</span>
                      </div>
                      <div className="flex justify-between py-1.5 border-b border-border/50">
                        <span className="text-muted-foreground">Module key</span>
                        <code className="text-xs bg-muted px-1.5 py-0.5 rounded">{activeBackendModule.module_key}</code>
                      </div>
                      <div className="flex justify-between py-1.5 border-b border-border/50">
                        <span className="text-muted-foreground">Artifacts</span>
                        <span className="font-medium">{moduleArtifacts.length}</span>
                      </div>
                      {activeBackendModule.completed_at && (
                        <div className="flex justify-between py-1.5">
                          <span className="text-muted-foreground">Completed</span>
                          <span>{formatDistanceToNow(new Date(activeBackendModule.completed_at), { addSuffix: true })}</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground py-8 text-center border border-dashed rounded-lg">No details available.</div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
