import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { ListChecks } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";

export const Route = createFileRoute("/_app/checklist")({
  component: ChecklistPage,
});

const GROUPS = [
  { title: "Validate", items: ["Write the problem statement", "20 customer discovery calls", "Score problem severity 1–10", "Define ICP and buying trigger"] },
  { title: "Build", items: ["Ship MVP scope doc", "Onboard 3 design partners", "Instrument core funnel", "Weekly changelog"] },
  { title: "Launch", items: ["Positioning + hero copy", "Product Hunt asset kit", "Warm outreach list (100)", "Founder-led content 2× / wk"] },
  { title: "Grow", items: ["Wire retention cohort", "Kill top 3 funnel drop-offs", "Case study × 3", "Introduce paid pricing"] },
  { title: "Raise", items: ["Investor list (50)", "Deck v3 reviewed by 3 founders", "Data room ready", "Financial model 3 yr", "Term sheet targets"] },
];

function ChecklistPage() {
  const [done, setDone] = useState<Record<string, boolean>>({ "Write the problem statement": true, "20 customer discovery calls": true, "Ship MVP scope doc": true });
  const total = GROUPS.reduce((a, g) => a + g.items.length, 0);
  const completed = Object.values(done).filter(Boolean).length;
  return (
    <AppPage className="max-w-5xl">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-end justify-between gap-4"
      >
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Playbook</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1 flex items-center gap-3">
            <ListChecks className="size-8 text-primary" /> Startup <span className="gradient-text">Checklist</span>
          </h1>
          <p className="text-muted-foreground mt-2 max-w-xl">Every step from idea to seed. Tick items — Foundr updates your Health Score and Roadmap.</p>
        </div>
        <Badge variant="outline" className="text-sm px-3 py-1">{completed} / {total} done</Badge>
      </motion.div>
      <div className="grid md:grid-cols-2 gap-4">
        {GROUPS.map((g, i) => (
          <motion.div
            key={g.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="rounded-xl h-full">
              <CardHeader><CardTitle className="font-display">{g.title}</CardTitle></CardHeader>
              <CardContent className="space-y-2.5">
                {g.items.map((it) => (
                  <label key={it} className="flex items-start gap-3 text-sm cursor-pointer group">
                    <Checkbox checked={!!done[it]} onCheckedChange={(v) => setDone((d) => ({ ...d, [it]: !!v }))} className="mt-0.5" />
                    <span className={done[it] ? "line-through text-muted-foreground" : "group-hover:text-foreground"}>{it}</span>
                  </label>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </AppPage>
  );
}
