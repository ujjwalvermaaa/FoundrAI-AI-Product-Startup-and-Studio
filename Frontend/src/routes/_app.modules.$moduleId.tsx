import { createFileRoute, Link } from "@tanstack/react-router";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { MODULE_LIST } from "@/lib/mock-data";
import { motion } from "framer-motion";
import { Sparkles, RefreshCw, ThumbsUp, ThumbsDown, Download, Wand2, ArrowLeft, CheckCircle2 } from "lucide-react";

export const Route = createFileRoute("/_app/modules/$moduleId")({
  component: ModulePage,
});

const SECTIONS: Record<string, { title: string; body: string[] }[]> = {
  "idea-validation": [
    { title: "Problem statement", body: ["Distributed AI teams lose 6-8 hours/week to synchronous standups that don't produce usable artifacts."] },
    { title: "Target user", body: ["Engineering managers (10-200 person teams) at AI-first startups working across 3+ timezones."] },
    { title: "Hypothesis", body: ["If we replace live standups with an AI-summarised async thread, teams will recover 5+ hours/week and retain 90%+ after 30 days."] },
    { title: "SWOT", body: ["Strengths: async-native, low friction.", "Weaknesses: relies on Slack adoption.", "Opportunities: AI-team boom.", "Threats: incumbent Slack Huddles."] },
  ],
  default: [
    { title: "Overview", body: ["Foundr has generated the first pass of this module. Review and edit inline or ask for a rewrite."] },
    { title: "Key insights", body: ["Insight 1 grounded in your project context.", "Insight 2 mapping to your target user.", "Insight 3 competitive positioning."] },
    { title: "Recommendations", body: ["Ship a 2-week validation sprint.", "Prioritise 3 features for the MVP.", "Draft investor narrative around the wedge."] },
  ],
};

function ModulePage() {
  const { moduleId } = Route.useParams();
  const meta = MODULE_LIST.find((m) => m.id === moduleId) ?? MODULE_LIST[0];
  const sections = SECTIONS[moduleId] ?? SECTIONS.default;

  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto">
      <Link to="/projects" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4">
        <ArrowLeft className="size-3" /> Back to projects
      </Link>

      <div className="grid lg:grid-cols-[1fr_320px] gap-6">
        <div>
          <div className="flex items-center gap-3 mb-6">
            <div className="size-12 rounded-xl gradient-brand grid place-items-center shadow-glow">
              <Sparkles className="size-5 text-white" />
            </div>
            <div>
              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Module</div>
              <h1 className="font-display text-3xl font-semibold tracking-tight">{meta.name}</h1>
              <p className="text-sm text-muted-foreground">{meta.description}</p>
            </div>
            <Badge variant="outline" className="ml-auto bg-primary/5 border-primary/30 text-primary gap-1">
              <span className="size-1.5 rounded-full bg-primary animate-pulse" /> Draft ready
            </Badge>
          </div>

          <Card className="mb-4">
            <CardContent className="p-4 flex flex-wrap gap-2">
              <Button size="sm" className="gap-1.5"><Wand2 className="size-3.5" /> Regenerate</Button>
              <Button size="sm" variant="outline" className="gap-1.5"><RefreshCw className="size-3.5" /> Rewrite section</Button>
              <Button size="sm" variant="outline" className="gap-1.5"><Download className="size-3.5" /> Export</Button>
              <div className="ml-auto flex items-center gap-1 text-muted-foreground">
                <Button size="sm" variant="ghost" className="h-8 gap-1"><ThumbsUp className="size-3.5" /></Button>
                <Button size="sm" variant="ghost" className="h-8 gap-1"><ThumbsDown className="size-3.5" /></Button>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            {sections.map((s, i) => (
              <motion.div
                key={s.title}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
              >
                <Card>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="size-4 text-emerald-500" />
                      <div className="font-display font-semibold">{s.title}</div>
                    </div>
                    <div className="space-y-2 text-sm text-muted-foreground leading-relaxed">
                      {s.body.map((b, j) => <p key={j}>{b}</p>)}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        <aside className="space-y-4">
          <Card>
            <CardContent className="p-4">
              <div className="font-display font-semibold mb-3">AI status</div>
              <div className="text-xs text-muted-foreground mb-2">Confidence</div>
              <Progress value={82} className="h-1.5" />
              <div className="mt-1 text-xs">82% — high signal</div>
              <div className="text-xs text-muted-foreground mt-4 mb-2">Sources</div>
              <ul className="text-xs space-y-1">
                <li className="hover:text-foreground cursor-pointer">crunchbase.com/orgs/…</li>
                <li className="hover:text-foreground cursor-pointer">ycombinator.com/rfs</li>
                <li className="hover:text-foreground cursor-pointer">gartner.com/reports/…</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="font-display font-semibold mb-3">Next best action</div>
              <p className="text-sm text-muted-foreground">Run 10 discovery calls and paste transcripts here — Foundr will refine the wedge.</p>
              <Button size="sm" className="w-full mt-3 gap-1.5"><Sparkles className="size-3.5" /> Start</Button>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="font-display font-semibold mb-3">Version history</div>
              <div className="space-y-2 text-xs">
                {["v3 · 2m ago · AI", "v2 · yesterday · You", "v1 · 3 days ago · AI"].map((v) => (
                  <div key={v} className="flex items-center justify-between hover:bg-accent/40 rounded px-2 py-1 cursor-pointer">
                    <span>{v}</span>
                    <span className="text-muted-foreground">restore</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}