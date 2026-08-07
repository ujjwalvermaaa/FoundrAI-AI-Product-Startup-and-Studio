import { createFileRoute, Link } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, TrendingUp, TrendingDown, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";

export const Route = createFileRoute("/_app/health")({
  component: HealthPage,
});

const DIMENSIONS = [
  { key: "Idea", score: 95, delta: +4, note: "Sharp wedge, clear ICP." },
  { key: "Market", score: 88, delta: +2, note: "TAM defensible, growth 18% YoY." },
  { key: "Revenue", score: 72, delta: +6, note: "Pricing tested with 8 design partners." },
  { key: "Competition", score: 81, delta: -1, note: "New entrant last week — monitor." },
  { key: "Execution", score: 69, delta: +3, note: "Ship cadence: 2.1 releases / wk." },
  { key: "Investor Readiness", score: 77, delta: +5, note: "Deck v3 shared with 12 partners." },
];

function color(score: number) {
  if (score >= 85) return "text-emerald-500";
  if (score >= 70) return "text-primary";
  if (score >= 55) return "text-amber-500";
  return "text-destructive";
}

function HealthPage() {
  const overall = Math.round(DIMENSIONS.reduce((a, d) => a + d.score, 0) / DIMENSIONS.length);
  const priorities = [...DIMENSIONS].sort((a, b) => a.score - b.score).slice(0, 3);

  return (
    <AppPage className="max-w-6xl">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-end justify-between gap-4"
      >
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Diagnostic</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
            Startup <span className="gradient-text">Health Score</span>
          </h1>
          <p className="text-muted-foreground mt-2 max-w-xl">A live diagnostic that reads your artifacts and tells you where to focus this week.</p>
        </div>
        <Button variant="outline" asChild><Link to="/chat"><Sparkles className="size-4" /> Ask Foundr to improve</Link></Button>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-1 relative overflow-hidden rounded-xl">
          <div className="absolute inset-0 gradient-brand opacity-10" />
          <CardContent className="p-8 relative text-center">
            <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Overall</div>
            <motion.div initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="mt-3 font-display text-7xl font-semibold gradient-text">{overall}</motion.div>
            <div className="text-sm text-muted-foreground">out of 100</div>
            <div className="mt-4 inline-flex items-center gap-1 text-sm text-emerald-500"><TrendingUp className="size-4" /> +3 this week</div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 rounded-xl">
          <CardHeader><CardTitle className="font-display flex items-center gap-2"><Activity className="size-4 text-primary" /> Breakdown</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {DIMENSIONS.map((d) => (
              <div key={d.key}>
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{d.key}</span>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs inline-flex items-center gap-0.5 ${d.delta >= 0 ? "text-emerald-500" : "text-destructive"}`}>
                      {d.delta >= 0 ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}{Math.abs(d.delta)}
                    </span>
                    <span className={`font-display font-semibold ${color(d.score)}`}>{d.score}</span>
                  </div>
                </div>
                <div className="mt-1.5 h-2 rounded-full bg-muted overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${d.score}%` }} transition={{ duration: 0.8 }} className="h-full gradient-brand" />
                </div>
                <div className="text-xs text-muted-foreground mt-1">{d.note}</div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-xl">
        <CardHeader><CardTitle className="font-display">Improve these three first</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-3 gap-3">
          {priorities.map((p, i) => (
            <motion.div
              key={p.key}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + i * 0.05 }}
              className="rounded-xl border border-border/60 p-4 bg-card/40"
            >
              <Badge variant="outline" className={color(p.score)}>{p.score}</Badge>
              <div className="font-display font-semibold mt-2">{p.key}</div>
              <div className="text-sm text-muted-foreground mt-1">{p.note}</div>
              <Button size="sm" variant="outline" className="mt-3" asChild><Link to="/roadmap">Add to roadmap</Link></Button>
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </AppPage>
  );
}
