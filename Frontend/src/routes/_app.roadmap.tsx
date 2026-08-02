import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Map, Plus, CheckCircle2, Circle, Clock } from "lucide-react";
import { motion } from "framer-motion";

export const Route = createFileRoute("/_app/roadmap")({
  component: RoadmapPage,
});

const WEEKS = [
  { w: 1, title: "Validate idea", detail: "20 discovery calls, problem/solution memo.", status: "done" },
  { w: 2, title: "Research competitors", detail: "Competitor matrix + differentiation wedge.", status: "done" },
  { w: 3, title: "Build MVP", detail: "Ship the sharpest slice in 10 days.", status: "active" },
  { w: 4, title: "Launch beta", detail: "Onboard 8 design partners, weekly cadence.", status: "todo" },
  { w: 5, title: "Acquire users", detail: "Content + Product Hunt + hand-outreach.", status: "todo" },
  { w: 6, title: "Iterate on retention", detail: "Wire funnel, kill the 3 biggest drop-offs.", status: "todo" },
  { w: 7, title: "Case studies", detail: "3 flagship stories with hard metrics.", status: "todo" },
  { w: 8, title: "Prepare pitch deck", detail: "Narrative + financials + data room.", status: "todo" },
];

function icon(s: string) {
  if (s === "done") return <CheckCircle2 className="size-4 text-emerald-500" />;
  if (s === "active") return <Clock className="size-4 text-primary" />;
  return <Circle className="size-4 text-muted-foreground" />;
}

function RoadmapPage() {
  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Planning</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1 flex items-center gap-3"><Map className="size-8 text-primary" /> AI Roadmap</h1>
          <p className="text-muted-foreground mt-2 max-w-xl">8-week plan from validation to seed. Regenerate, edit or drag milestones — Foundr keeps it in sync with your artifacts.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Plus className="size-4" /> Add milestone</Button>
          <Button><Sparkles className="size-4" /> Regenerate</Button>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="font-display">Timeline</CardTitle></CardHeader>
        <CardContent>
          <ol className="relative border-l-2 border-dashed border-border ml-3 space-y-4">
            {WEEKS.map((w, i) => (
              <motion.li
                key={w.w}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="pl-6 relative"
              >
                <span className="absolute -left-[9px] top-3 size-4 rounded-full bg-background ring-2 ring-border grid place-items-center">{icon(w.status)}</span>
                <div className="rounded-lg border border-border/60 p-4 hover:border-primary/40 transition-colors">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">Week {w.w}</Badge>
                    <span className="font-display font-semibold">{w.title}</span>
                    {w.status === "active" && <Badge className="ml-auto">In progress</Badge>}
                    {w.status === "done" && <Badge variant="outline" className="ml-auto text-emerald-500 border-emerald-500/40">Done</Badge>}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">{w.detail}</div>
                </div>
              </motion.li>
            ))}
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}