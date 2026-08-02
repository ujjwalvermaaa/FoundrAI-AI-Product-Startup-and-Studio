import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Target, Plus, ExternalLink, Sparkles } from "lucide-react";

export const Route = createFileRoute("/_app/competitors")({
  component: CompetitorsPage,
});

const COMPETITORS = [
  { name: "Northwind Labs", url: "northwind.ai", pricing: "$29 / seat", audience: "SMB SaaS founders", funding: "$4M seed", strengths: ["Fast onboarding", "Notion export"], weaknesses: ["No AI copilot", "Weak analytics"] },
  { name: "Ideabench", url: "ideabench.io", pricing: "Free / $19", audience: "Solo indie hackers", funding: "Bootstrapped", strengths: ["Great community"], weaknesses: ["Shallow modules", "No investor tooling"] },
  { name: "Foundry OS", url: "foundryos.com", pricing: "$99 / mo", audience: "Accelerator cohorts", funding: "$12M Series A", strengths: ["Cohort features", "Mentor network"], weaknesses: ["Slow AI", "Enterprise-only"] },
];

function CompetitorsPage() {
  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Intelligence</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1 flex items-center gap-3"><Target className="size-8 text-primary" /> Competitors</h1>
          <p className="text-muted-foreground mt-2 max-w-xl">Track releases, pricing and positioning across the landscape. Foundr flags anything you should react to.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Sparkles className="size-4" /> Auto-discover</Button>
          <Button><Plus className="size-4" /> Add competitor</Button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {COMPETITORS.map((c) => (
          <Card key={c.name} className="hover:border-primary/40 transition-colors">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="font-display text-lg">{c.name}</CardTitle>
                <a className="text-muted-foreground hover:text-foreground text-xs inline-flex items-center gap-1">{c.url} <ExternalLink className="size-3" /></a>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div><div className="text-muted-foreground">Pricing</div><div className="font-medium">{c.pricing}</div></div>
                <div><div className="text-muted-foreground">Funding</div><div className="font-medium">{c.funding}</div></div>
                <div className="col-span-2"><div className="text-muted-foreground">Audience</div><div className="font-medium">{c.audience}</div></div>
              </div>
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Strengths</div>
                <div className="flex flex-wrap gap-1">{c.strengths.map((s) => <Badge key={s} variant="outline" className="text-emerald-500 border-emerald-500/40">{s}</Badge>)}</div>
              </div>
              <div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Weaknesses</div>
                <div className="flex flex-wrap gap-1">{c.weaknesses.map((s) => <Badge key={s} variant="outline" className="text-destructive border-destructive/40">{s}</Badge>)}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle className="font-display flex items-center gap-2"><Sparkles className="size-4 text-primary" /> Foundr's take</CardTitle></CardHeader>
        <CardContent className="text-sm text-muted-foreground leading-relaxed">
          Your wedge — an <span className="text-foreground">AI co-founder with project memory</span> — is uncontested. Northwind's Notion export is the only feature worth cloning; ship a lightweight version in Week 4. Foundry OS is on a different tier and not a near-term threat.
        </CardContent>
      </Card>
    </div>
  );
}