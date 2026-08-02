import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Sparkles, CreditCard, Download } from "lucide-react";

export const Route = createFileRoute("/_app/billing")({
  component: BillingPage,
});

const PLANS = [
  { id: "solo", name: "Solo", price: 0, credits: "1,000", features: ["1 project", "Core modules", "Community support"] },
  { id: "founder", name: "Founder", price: 29, credits: "10,000", features: ["5 projects", "All modules", "Priority AI", "Email support"], current: true },
  { id: "studio", name: "Studio", price: 99, credits: "50,000", features: ["Unlimited projects", "Team seats", "Custom models", "Slack support"] },
];

const INVOICES = [
  { id: "INV-1042", date: "Jul 01, 2026", amount: "$29.00", status: "Paid" },
  { id: "INV-1041", date: "Jun 01, 2026", amount: "$29.00", status: "Paid" },
  { id: "INV-1040", date: "May 01, 2026", amount: "$29.00", status: "Paid" },
];

function BillingPage() {
  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-8">
      <div>
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Account</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">Billing & credits</h1>
        <p className="text-muted-foreground mt-2">Manage your plan, AI credits and invoices.</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="font-display flex items-center gap-2"><Sparkles className="size-4 text-primary" /> AI credits</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <div className="text-4xl font-display font-semibold">6,200 <span className="text-lg text-muted-foreground">/ 10,000</span></div>
              <div className="text-sm text-muted-foreground mt-1">Renews Aug 1, 2026</div>
            </div>
            <Button>Buy more credits</Button>
          </div>
          <div className="mt-4 h-2 rounded-full bg-muted overflow-hidden">
            <div className="h-full gradient-brand" style={{ width: "62%" }} />
          </div>
        </CardContent>
      </Card>

      <div>
        <h2 className="font-display text-xl font-semibold mb-4">Plans</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {PLANS.map((p) => (
            <Card key={p.id} className={p.current ? "border-primary/60 shadow-glow" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="font-display">{p.name}</CardTitle>
                  {p.current && <Badge>Current</Badge>}
                </div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-display font-semibold">${p.price}</span>
                  <span className="text-sm text-muted-foreground">/mo</span>
                </div>
                <div className="text-xs text-muted-foreground">{p.credits} credits / month</div>
              </CardHeader>
              <CardContent className="space-y-3">
                <ul className="space-y-1.5 text-sm">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-2"><Check className="size-3.5 text-primary" /> {f}</li>
                  ))}
                </ul>
                <Button variant={p.current ? "outline" : "default"} className="w-full">
                  {p.current ? "Manage" : `Upgrade to ${p.name}`}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="font-display flex items-center gap-2"><CreditCard className="size-4" /> Payment method</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-14 rounded-md gradient-brand grid place-items-center text-white text-xs font-bold">VISA</div>
            <div>
              <div className="text-sm font-medium">•••• •••• •••• 4242</div>
              <div className="text-xs text-muted-foreground">Expires 08 / 2028</div>
            </div>
          </div>
          <Button variant="outline">Update</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="font-display">Invoices</CardTitle></CardHeader>
        <CardContent className="divide-y divide-border">
          {INVOICES.map((inv) => (
            <div key={inv.id} className="flex items-center justify-between py-3 text-sm">
              <div className="flex items-center gap-4">
                <span className="font-mono text-xs">{inv.id}</span>
                <span className="text-muted-foreground">{inv.date}</span>
              </div>
              <div className="flex items-center gap-4">
                <span>{inv.amount}</span>
                <Badge variant="outline" className="text-emerald-500 border-emerald-500/40">{inv.status}</Badge>
                <Button variant="ghost" size="sm"><Download className="size-3.5" /> PDF</Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}