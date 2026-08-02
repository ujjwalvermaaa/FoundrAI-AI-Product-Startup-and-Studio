import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Star, X } from "lucide-react";
import { PublicNav, PublicFooter } from "@/components/public-chrome";

export const Route = createFileRoute("/pricing")({
  component: PricingPage,
});

const tiers = [
  { name: "Explorer", price: "Free", desc: "For curious founders exploring an idea.", features: ["1 active project", "3 modules included", "Community support"], cta: "Start free" },
  { name: "Founder", price: "$29", desc: "Everything you need to launch.", features: ["Unlimited projects", "All 8 modules", "Version history", "Export anywhere"], cta: "Start 14-day trial", featured: true },
  { name: "Team", price: "$99", desc: "For teams building multiple ventures.", features: ["Unlimited seats", "Priority AI compute", "SSO & audit log", "Dedicated support"], cta: "Talk to sales" },
];

const rows: [string, boolean | string, boolean | string, boolean | string][] = [
  ["Active projects", "1", "Unlimited", "Unlimited"],
  ["AI modules", "3", "8", "8"],
  ["AI generations / mo", "200", "10,000", "50,000"],
  ["Version history", "7 days", "Unlimited", "Unlimited"],
  ["Export to PDF / Notion", false, true, true],
  ["Custom brand voice", false, true, true],
  ["Team collaboration", false, false, true],
  ["SSO / SAML", false, false, true],
  ["Audit log", false, false, true],
  ["Dedicated CSM", false, false, true],
];

function Cell({ v }: { v: boolean | string }) {
  if (v === true) return <Check className="size-4 text-primary mx-auto" />;
  if (v === false) return <X className="size-4 text-muted-foreground/50 mx-auto" />;
  return <span className="text-sm">{v}</span>;
}

function PricingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PublicNav />
      <section className="pt-32 pb-16 text-center relative overflow-hidden">
        <div className="absolute inset-0 grid-bg opacity-20" />
        <div className="relative max-w-3xl mx-auto px-6">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Pricing</div>
          <h1 className="font-display text-5xl md:text-6xl font-semibold tracking-tight mt-3">
            Priced for <span className="gradient-text">first-check founders.</span>
          </h1>
          <p className="text-muted-foreground mt-4 text-lg">Free while you explore. Fair when you scale. Never per-seat gouging.</p>
        </div>
      </section>

      <section className="pb-16 max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-3 gap-4">
          {tiers.map((t) => (
            <Card key={t.name} className={t.featured ? "border-primary/50 shadow-glow relative" : ""}>
              {t.featured && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="gradient-brand text-white border-transparent gap-1"><Star className="size-3" /> Most popular</Badge>
                </div>
              )}
              <CardContent className="p-6">
                <div className="font-display font-semibold">{t.name}</div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="font-display text-4xl font-semibold">{t.price}</span>
                  {t.price !== "Free" && <span className="text-muted-foreground text-sm">/ month</span>}
                </div>
                <p className="text-sm text-muted-foreground mt-2">{t.desc}</p>
                <ul className="mt-6 space-y-2.5 text-sm">
                  {t.features.map((f) => <li key={f} className="flex items-center gap-2"><Check className="size-4 text-primary" /> {f}</li>)}
                </ul>
                <Button className="w-full mt-6" variant={t.featured ? "default" : "outline"} asChild>
                  <Link to="/auth/signup">{t.cta}</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="pb-24 max-w-5xl mx-auto px-6">
        <div className="text-center mb-8">
          <h2 className="font-display text-3xl font-semibold tracking-tight">Compare plans</h2>
        </div>
        <Card>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-medium text-muted-foreground">Feature</th>
                  {tiers.map((t) => (
                    <th key={t.name} className="p-4 text-center font-display">{t.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map(([label, a, b, c]) => (
                  <tr key={label} className="border-b border-border/60 last:border-0">
                    <td className="p-3 text-muted-foreground">{label}</td>
                    <td className="p-3 text-center"><Cell v={a} /></td>
                    <td className="p-3 text-center"><Cell v={b} /></td>
                    <td className="p-3 text-center"><Cell v={c} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </section>

      <section className="pb-24 max-w-3xl mx-auto px-6">
        <h2 className="font-display text-3xl font-semibold tracking-tight text-center mb-8">Questions</h2>
        <div className="space-y-3">
          {[
            ["Do I need a credit card to start?", "No — Explorer is free forever, no card required."],
            ["Can I cancel any time?", "Yes. Cancel from Settings, no questions asked."],
            ["What happens to my projects if I downgrade?", "Everything stays — you'll just hit generation and module limits."],
            ["Do you offer non-profit or student pricing?", "Yes. Email hello@foundrai.app."],
          ].map(([q, a]) => (
            <details key={q} className="group rounded-xl border border-border/60 p-4 bg-card/40">
              <summary className="cursor-pointer font-medium list-none flex items-center justify-between">
                {q}<span className="text-muted-foreground group-open:rotate-45 transition-transform">+</span>
              </summary>
              <p className="text-sm text-muted-foreground mt-2">{a}</p>
            </details>
          ))}
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}