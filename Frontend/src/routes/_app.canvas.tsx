import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LayoutGrid, Sparkles, Download } from "lucide-react";

export const Route = createFileRoute("/_app/canvas")({
  component: CanvasPage,
});

const BLOCKS = [
  { title: "Key Partners", items: ["OpenAI, Anthropic", "Design partner startups", "Notion, Slack integrations"], span: "md:row-span-2" },
  { title: "Key Activities", items: ["Model orchestration", "Artifact generation", "Weekly playbook curation"] },
  { title: "Value Propositions", items: ["AI co-founder with memory", "8 modules, one workspace", "Ship investor-ready docs in a day"], span: "md:row-span-2 md:col-span-1 border-primary/40" },
  { title: "Customer Relationships", items: ["Self-serve product", "Foundr AI chat", "Studio-tier concierge"] },
  { title: "Customer Segments", items: ["Solo founders (0→1)", "Pre-seed teams", "Accelerator cohorts"], span: "md:row-span-2" },
  { title: "Key Resources", items: ["Founder knowledge graph", "Curated pitch playbooks", "Managed AI infra"] },
  { title: "Channels", items: ["Product Hunt & YC", "Founder content", "Accelerator partnerships"] },
  { title: "Cost Structure", items: ["Inference credits", "Engineering payroll", "Playbook research"], span: "md:col-span-2" },
  { title: "Revenue Streams", items: ["Subscriptions ($29 / $99)", "Team seats", "One-time investor bundle"], span: "md:col-span-2" },
];

function CanvasPage() {
  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Business Model</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1 flex items-center gap-3"><LayoutGrid className="size-8 text-primary" /> Interactive Canvas</h1>
          <p className="text-muted-foreground mt-2 max-w-xl">Click any block to edit. Foundr keeps unit economics, pricing and positioning in sync across your workspace.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Download className="size-4" /> Export</Button>
          <Button><Sparkles className="size-4" /> Regenerate</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 auto-rows-[minmax(140px,auto)]">
        {BLOCKS.map((b) => (
          <Card key={b.title} className={`hover:border-primary/50 transition-colors cursor-pointer ${b.span ?? ""}`}>
            <CardContent className="p-4">
              <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground font-medium">{b.title}</div>
              <ul className="mt-2 space-y-1.5 text-sm">
                {b.items.map((i) => (
                  <li key={i} className="rounded-md bg-muted/40 px-2 py-1.5 border border-border/50">{i}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}