import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Star, X } from "lucide-react";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { PublicPage, PageHero } from "@/components/layout/page-shell";

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
    <PublicPage>
      <PublicNav />
      <PageHero
        eyebrow="Pricing"
        title={
          <>
            Priced for <span className="gradient-text">first-check founders.</span>
          </>
        }
        description="Free while you explore. Fair when you scale. Never per-seat gouging."
      />

      <section className="pb-16 max-w-6xl mx-auto px-6">
        <div className="grid md:grid-cols-3 gap-4">
          {tiers.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.45, delay: i * 0.08 }}
            >
              <Card className={t.featured ? "border-primary/50 shadow-glow relative h-full hologram-edge" : "h-full"}>
                {t.featured && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                    <Badge className="gradient-brand text-white border-transparent gap-1 rounded-xl shadow-glow">
                      <Star className="size-3" /> Most popular
                    </Badge>
                  </div>
                )}
                <CardContent className="p-6">
                  <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium">{t.name}</div>
                  <div className="mt-3 flex items-baseline gap-1">
                    <span className="font-display text-4xl font-semibold">{t.price}</span>
                    {t.price !== "Free" && <span className="text-muted-foreground text-sm">/ month</span>}
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{t.desc}</p>
                  <ul className="mt-6 space-y-2.5 text-sm">
                    {t.features.map((f) => (
                      <li key={f} className="flex items-center gap-2">
                        <Check className="size-4 text-primary shrink-0" /> {f}
                      </li>
                    ))}
                  </ul>
                  <Button
                    className="w-full mt-6 rounded-xl"
                    variant={t.featured ? "default" : "outline"}
                    asChild
                  >
                    <Link to="/auth/signup">{t.cta}</Link>
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="pb-24 max-w-5xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-2">Compare</div>
          <h2 className="font-display text-3xl font-semibold tracking-tight">Compare plans</h2>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45 }}
        >
          <Card>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border/60">
                    <th className="text-left p-4 font-medium text-muted-foreground">Feature</th>
                    {tiers.map((t) => (
                      <th key={t.name} className="p-4 text-center font-display">{t.name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map(([label, a, b, c]) => (
                    <tr key={label} className="border-b border-border/40 last:border-0">
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
        </motion.div>
      </section>

      <section className="pb-24 max-w-3xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-2">FAQ</div>
          <h2 className="font-display text-3xl font-semibold tracking-tight">Questions</h2>
        </motion.div>
        <div className="space-y-3">
          {[
            ["Do I need a credit card to start?", "No — Explorer is free forever, no card required."],
            ["Can I cancel any time?", "Yes. Cancel from Settings, no questions asked."],
            ["What happens to my projects if I downgrade?", "Everything stays — you'll just hit generation and module limits."],
            ["Do you offer non-profit or student pricing?", "Yes. Email hello@foundrai.app."],
          ].map(([q, a], i) => (
            <motion.details
              key={q}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.35, delay: i * 0.05 }}
              className="group rounded-2xl border border-border/60 p-4 glass-depth hologram-edge"
            >
              <summary className="cursor-pointer font-medium list-none flex items-center justify-between">
                {q}
                <span className="text-muted-foreground group-open:rotate-45 transition-transform">+</span>
              </summary>
              <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{a}</p>
            </motion.details>
          ))}
        </div>
      </section>

      <PublicFooter />
    </PublicPage>
  );
}
