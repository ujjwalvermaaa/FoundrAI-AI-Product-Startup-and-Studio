import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  Sparkles, ArrowRight, Lightbulb, LineChart, Layers, Compass, Network, Wallet, Megaphone, FileText,
  Check, Star, Command, Play, MessageCircle, Zap, X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FounderBotAvatar } from "@/components/founder-bot-avatar";
import { PublicFooter } from "@/components/public-chrome";

export const Route = createFileRoute("/")({
  component: Landing,
});

const modules = [
  { icon: Lightbulb, name: "Idea Validation", copy: "Pressure-test hypotheses with signals and evidence." },
  { icon: LineChart, name: "Market Research", copy: "TAM/SAM/SOM, competitors and positioning." },
  { icon: Layers, name: "Business Model", copy: "Revenue, pricing and unit economics." },
  { icon: Compass, name: "Product Strategy", copy: "MVP scope, roadmap and success metrics." },
  { icon: Network, name: "Technical Architecture", copy: "Stack, systems and data model." },
  { icon: Wallet, name: "Financial Planning", copy: "3-year forecast, burn and runway." },
  { icon: Megaphone, name: "Marketing Strategy", copy: "Positioning, channels and launch." },
  { icon: FileText, name: "Investor Documentation", copy: "Deck, memo and data room." },
];

function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <TopNav />
      <Hero />
      <QuoteStrip />
      <ModulesSection />
      <MeetFoundr />
      <VideoSection />
      <WorkspacePreview />
      <Testimonials />
      <VsSection />
      <Pricing />
      <Faq />
      <FinalCta />
      <PublicFooter />
    </div>
  );
}

function TopNav() {
  return (
    <header className="fixed top-0 inset-x-0 z-40 backdrop-blur-xl bg-background/60 border-b border-border/60">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center gap-8">
        <Link to="/" className="flex items-center gap-2">
          <div className="size-7 rounded-md overflow-hidden shadow-glow shrink-0">
            <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
          </div>
          <span className="font-display text-base font-semibold">FoundrAI</span>
        </Link>
        <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
          <a className="hover:text-foreground transition-colors" href="#modules">Modules</a>
          <Link to="/chat" className="hover:text-foreground transition-colors">Chat</Link>
          <Link to="/pricing" className="hover:text-foreground transition-colors">Pricing</Link>
          <Link to="/about" className="hover:text-foreground transition-colors">About</Link>
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild><Link to="/auth/login">Sign in</Link></Button>
          <Button size="sm" asChild><Link to="/auth/signup">Start free <ArrowRight className="size-3.5" /></Link></Button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative pt-40 pb-24 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-30" />
      <div className="absolute top-24 left-1/2 -translate-x-1/2 size-[800px] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="relative max-w-5xl mx-auto px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <Badge variant="outline" className="rounded-full border-primary/30 bg-primary/5 text-primary gap-2 py-1 px-3">
            <Sparkles className="size-3" /> Now with autonomous module agents
          </Badge>
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.05 }}
          className="font-display text-5xl md:text-7xl font-semibold tracking-tight mt-6 leading-[1.05]"
        >
          Turn an idea into a<br />
          <span className="gradient-text">real startup.</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="text-lg md:text-xl text-muted-foreground mt-6 max-w-2xl mx-auto leading-relaxed"
        >
          FoundrAI is the AI-native workspace for founders. Validate, plan, architect,
          finance, market and pitch — every artifact generated, versioned and organized.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="mt-8 flex flex-wrap gap-3 justify-center"
        >
          <Button size="lg" asChild className="h-11 px-6">
            <Link to="/auth/signup">Start building free <ArrowRight className="size-4" /></Link>
          </Button>
          <Button size="lg" variant="outline" className="h-11 px-6">
            <Command className="size-4" /> Watch the tour
          </Button>
        </motion.div>
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          className="mt-4 text-xs text-muted-foreground"
        >
          Free forever plan. No credit card required.
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4, duration: 0.8 }}
          className="relative mt-16"
        >
          <div className="absolute -inset-x-8 -inset-y-8 rounded-3xl gradient-brand opacity-20 blur-3xl" />
          <div className="relative rounded-2xl border border-border/60 overflow-hidden shadow-2xl surface-panel">
            <div className="h-8 border-b border-border/60 bg-muted/40 flex items-center gap-1.5 px-3">
              <div className="size-2.5 rounded-full bg-red-400/70" />
              <div className="size-2.5 rounded-full bg-yellow-400/70" />
              <div className="size-2.5 rounded-full bg-green-400/70" />
              <div className="ml-3 text-[11px] text-muted-foreground">foundrai.app / projects / orbit</div>
            </div>
            <div className="grid grid-cols-[180px_1fr] min-h-[380px]">
              <div className="border-r border-border/60 bg-sidebar/60 p-3 space-y-1.5">
                {["Dashboard", "Projects", "Orbit", "Kelp", "Ember"].map((n, i) => (
                  <div key={n} className={`text-xs px-2 py-1.5 rounded ${i === 2 ? "bg-accent text-foreground font-medium" : "text-muted-foreground"}`}>{n}</div>
                ))}
              </div>
              <div className="p-6">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Module 3 of 8</div>
                <div className="font-display text-2xl font-semibold mt-1">Business Model</div>
                <div className="mt-4 grid grid-cols-3 gap-2">
                  {Array.from({ length: 9 }).map((_, i) => (
                    <div key={i} className="h-16 rounded-md border border-border/60 bg-muted/40 p-2">
                      <div className="h-1 w-8 rounded bg-primary/50" />
                      <div className="h-1 w-16 rounded bg-muted mt-1.5" />
                      <div className="h-1 w-12 rounded bg-muted mt-1" />
                    </div>
                  ))}
                </div>
                <div className="mt-4 h-2 rounded-full bg-muted overflow-hidden">
                  <motion.div className="h-full gradient-brand" initial={{ width: 0 }} animate={{ width: "62%" }} transition={{ delay: 0.8, duration: 1 }} />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function QuoteStrip() {
  return (
    <section className="border-y border-border/60 bg-muted/20 py-10">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-4">
          Loved by founders shipping real companies
        </div>
        <p className="font-display text-xl md:text-2xl leading-relaxed">
          "I raised my seed round with a deck FoundrAI generated in an afternoon. My lead investor thought I'd hired a strategist."
        </p>
        <div className="mt-4 text-sm text-muted-foreground">— Maya Chen, founder of Kelp (backed by Long Journey Ventures)</div>
      </div>
    </section>
  );
}

function MeetFoundr() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-20" />
      <div className="relative max-w-6xl mx-auto px-6 grid lg:grid-cols-[auto_1fr] items-center gap-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ type: "spring", stiffness: 120, damping: 14 }}
          className="mx-auto"
        >
          <FounderBotAvatar size="xl" speaking />
        </motion.div>
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Meet Foundr</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3 leading-[1.1]">
            Your <span className="gradient-text">AI co-founder</span>, always in the room.
          </h2>
          <p className="text-muted-foreground mt-4 text-lg leading-relaxed max-w-xl">
            Foundr has read every YC essay, every Stripe teardown, and every seed memo you wish you had. Ask anything about your startup —
            validation, pricing, hiring, pitching — and get a straight answer with the artifacts to back it up.
          </p>
          <div className="mt-6 flex gap-3">
            <Button size="lg" asChild className="h-11 gap-2">
              <Link to="/chat"><MessageCircle className="size-4" /> Talk to Foundr</Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="h-11">
              <Link to="/auth/signup">Try free <ArrowRight className="size-4" /></Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function VideoSection() {
  return (
    <section className="pb-16">
      <div className="max-w-5xl mx-auto px-6">
        <div className="relative aspect-video rounded-2xl overflow-hidden border border-border/60 group cursor-pointer">
          <div className="absolute inset-0 gradient-brand opacity-30" />
          <div className="absolute inset-0 grid-bg opacity-40" />
          <div className="absolute inset-0 grid place-items-center">
            <motion.div whileHover={{ scale: 1.06 }} className="size-20 rounded-full bg-white/95 grid place-items-center shadow-2xl">
              <Play className="size-8 text-foreground fill-current ml-1" />
            </motion.div>
          </div>
          <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between">
            <div>
              <div className="text-xs uppercase tracking-wider text-white/70">Watch demo · 2 min</div>
              <div className="font-display text-white text-xl font-semibold mt-1">See FoundrAI take an idea from prompt to pitch deck.</div>
            </div>
            <Badge className="bg-black/40 text-white border-white/20 backdrop-blur-md">2:14</Badge>
          </div>
        </div>
      </div>
    </section>
  );
}

function Testimonials() {
  const quotes = [
    { name: "Devon Park", role: "Solo founder, Orbit", quote: "The financial model FoundrAI produced was more thorough than the one I built with a fractional CFO. And it took 4 minutes." },
    { name: "Aisha Patel", role: "CEO, Lumen Health", quote: "I was skeptical. Then Foundr generated a competitive teardown that surfaced a wedge my team had missed for 6 months." },
    { name: "Jonas Weber", role: "Founder, Kelp", quote: "It's the first tool that feels like it was built by founders. Every module ends with an actual artifact I can send to someone." },
    { name: "Sara Kim", role: "PM turned founder", quote: "The command palette alone is worth it. I switched from 4 tools to one." },
    { name: "Marcus Chen", role: "2x founder", quote: "Foundr is the co-founder I've been looking for on my 3rd company. Never sleeps, never runs out of context." },
    { name: "Rin Nakamura", role: "Angel & operator", quote: "I recommend FoundrAI to every first-time founder I invest in. Cuts 3 months off zero-to-one." },
  ];
  return (
    <section className="py-24 border-y border-border/60 bg-muted/10">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-2xl">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Founders</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">Built with real founders. Every week.</h2>
        </div>
        <div className="mt-10 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quotes.map((q, i) => (
            <motion.div
              key={q.name}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="h-full hover:border-primary/40 transition-all">
                <CardContent className="p-5">
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }).map((_, j) => <Star key={j} className="size-3.5 text-primary fill-primary" />)}
                  </div>
                  <p className="text-sm leading-relaxed mt-3">"{q.quote}"</p>
                  <div className="mt-5 flex items-center gap-3 pt-4 border-t border-border/50">
                    <div className="size-9 rounded-full gradient-brand grid place-items-center text-white font-display font-semibold text-sm">
                      {q.name.split(" ").map(n=>n[0]).join("")}
                    </div>
                    <div>
                      <div className="text-sm font-medium">{q.name}</div>
                      <div className="text-xs text-muted-foreground">{q.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function VsSection() {
  const rows = [
    ["Idea to first artifact", "45 minutes", "3-6 weeks"],
    ["Market research", "AI + live sources", "Google + guesswork"],
    ["Financial model", "Editable spreadsheet in 4 min", "Fractional CFO, $2k+"],
    ["Pitch deck", "Investor-ready first draft", "20+ template rewrites"],
    ["Living workspace", "Everything connected", "Scattered Notion pages"],
  ];
  return (
    <section className="py-24">
      <div className="max-w-5xl mx-auto px-6">
        <div className="text-center mb-10">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">The old way</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">
            FoundrAI vs. <span className="text-muted-foreground line-through">a stack of blank documents.</span>
          </h2>
        </div>
        <Card>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-4 font-medium text-muted-foreground w-1/3"></th>
                  <th className="p-4 text-left font-display">
                    <span className="inline-flex items-center gap-2"><Zap className="size-4 text-primary" /> With FoundrAI</span>
                  </th>
                  <th className="p-4 text-left font-display text-muted-foreground">Without</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(([l, a, b]) => (
                  <tr key={l} className="border-b border-border/60 last:border-0">
                    <td className="p-4 text-muted-foreground">{l}</td>
                    <td className="p-4 font-medium"><Check className="size-4 text-primary inline mr-2" />{a}</td>
                    <td className="p-4 text-muted-foreground"><X className="size-4 inline mr-2 opacity-50" />{b}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

function Faq() {
  const items = [
    ["Is FoundrAI right for me if I already have a company?", "Yes — most FoundrAI users are on their second or third venture. The modules cover repositioning, financial replanning, and raising follow-on rounds too."],
    ["What models power the AI?", "A mix of frontier chat models and specialised research agents. You never have to think about which — Foundr picks the best fit per module."],
    ["Do you train on my data?", "Never. Your workspace is private. We do not use your artifacts to train models."],
    ["Can I export everything?", "Yes. Markdown, PDF, Google Docs, Notion, and Slides. Your data is yours."],
    ["How is this different from just using ChatGPT?", "ChatGPT is a chat window. FoundrAI is a workspace, an artifact store, a versioning system, and eight specialised founder agents that share context across your whole company."],
  ];
  return (
    <section className="py-24 max-w-3xl mx-auto px-6">
      <div className="text-center mb-8">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Questions</div>
        <h2 className="font-display text-4xl font-semibold tracking-tight mt-2">Honest answers.</h2>
      </div>
      <div className="space-y-3">
        {items.map(([q, a]) => (
          <details key={q} className="group rounded-xl border border-border/60 p-5 bg-card/40 hover:border-primary/30 transition-colors">
            <summary className="cursor-pointer font-medium list-none flex items-center justify-between gap-4">
              <span>{q}</span>
              <span className="text-muted-foreground group-open:rotate-45 transition-transform text-lg leading-none">+</span>
            </summary>
            <p className="text-sm text-muted-foreground mt-3 leading-relaxed">{a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

function ModulesSection() {
  return (
    <section id="modules" className="py-28">
      <div className="max-w-7xl mx-auto px-6">
        <div className="max-w-2xl">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Modules</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">
            Everything you need to <span className="gradient-text">go from zero to one.</span>
          </h2>
          <p className="text-muted-foreground mt-4 text-lg">
            Eight structured AI modules. Each produces real, editable artifacts you can hand to a co-founder, investor or engineer.
          </p>
        </div>

        <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-4 gap-3">
          {modules.map((m, i) => (
            <motion.div
              key={m.name}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="h-full hover:border-primary/40 hover:shadow-glow transition-all group">
                <CardContent className="p-5">
                  <div className="size-10 rounded-lg bg-accent grid place-items-center group-hover:gradient-brand group-hover:text-white transition-all">
                    <m.icon className="size-5" />
                  </div>
                  <div className="font-display font-semibold mt-4">{m.name}</div>
                  <div className="text-sm text-muted-foreground mt-1">{m.copy}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function WorkspacePreview() {
  return (
    <section id="workspace" className="py-28 relative overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-20" />
      <div className="relative max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-14 items-center">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Workspace</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">
            A single home for every artifact.
          </h2>
          <p className="text-muted-foreground mt-4 text-lg leading-relaxed">
            Documents, canvases, financial models, technical diagrams and investor decks — all versioned,
            searchable, and connected. Command-K anything. Comment on everything.
          </p>
          <ul className="mt-8 space-y-3">
            {[
              "Notion-quality writing surface with AI generation",
              "Linear-fast navigation and command palette",
              "Real-time collaboration and version history",
              "Export to PDF, Notion, Slides and Google Docs",
            ].map((f) => (
              <li key={f} className="flex items-start gap-3">
                <div className="mt-0.5 size-5 rounded-full gradient-brand grid place-items-center shrink-0">
                  <Check className="size-3 text-white" />
                </div>
                <span className="text-sm">{f}</span>
              </li>
            ))}
          </ul>
          <div className="mt-8">
            <Button asChild><Link to="/dashboard">Explore the workspace <ArrowRight className="size-4" /></Link></Button>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-6 rounded-3xl gradient-brand opacity-20 blur-3xl" />
          <Card className="relative overflow-hidden">
            <CardContent className="p-0">
              <div className="p-4 border-b border-border flex items-center gap-2">
                <div className="size-6 rounded gradient-brand grid place-items-center"><Sparkles className="size-3 text-white" /></div>
                <span className="text-sm font-medium">FoundrAI is generating…</span>
                <Badge variant="outline" className="ml-auto text-[10px]">Business Model</Badge>
              </div>
              <div className="p-5 space-y-3 min-h-[300px]">
                {[
                  "Customer Segments — Distributed AI-first teams (10-200) needing async standups.",
                  "Value Proposition — Async, AI-summarized daily updates that replace 30-min meetings.",
                  "Channels — Product-led growth via Slack integration, developer communities, referrals.",
                  "Revenue Streams — SaaS per-seat, $12/user/mo with 20% annual discount.",
                ].map((line, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.2 }}
                    className="flex gap-3 text-sm"
                  >
                    <span className="text-xs font-mono text-muted-foreground mt-0.5 shrink-0">0{i + 1}</span>
                    <span>{line}</span>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const tiers = [
    { name: "Explorer", price: "Free", desc: "For curious founders exploring an idea.", features: ["1 active project", "3 modules included", "Community support"], cta: "Start free" },
    { name: "Founder", price: "$29", desc: "Everything you need to launch.", features: ["Unlimited projects", "All 8 modules", "Version history", "Export anywhere"], cta: "Start 14-day trial", featured: true },
    { name: "Team", price: "$99", desc: "For teams building multiple ventures.", features: ["Unlimited seats", "Priority AI compute", "SSO & audit log", "Dedicated support"], cta: "Talk to sales" },
  ];
  return (
    <section id="pricing" className="py-28">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center max-w-2xl mx-auto">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Pricing</div>
          <h2 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">Simple, founder-friendly.</h2>
          <p className="text-muted-foreground mt-4">Start free. Upgrade when you're ready to raise.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-4 mt-14">
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
                  {t.features.map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="size-4 text-primary" /> {f}
                    </li>
                  ))}
                </ul>
                <Button className="w-full mt-6" variant={t.featured ? "default" : "outline"} asChild>
                  <Link to="/auth/signup">{t.cta}</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="py-28 relative overflow-hidden">
      <div className="absolute inset-0 gradient-brand opacity-10" />
      <div className="relative max-w-3xl mx-auto px-6 text-center">
        <h2 className="font-display text-4xl md:text-6xl font-semibold tracking-tight leading-[1.05]">
          Your next company is <span className="gradient-text">one prompt away.</span>
        </h2>
        <p className="text-muted-foreground mt-5 text-lg">Join thousands of founders shipping with FoundrAI.</p>
        <div className="mt-8 flex justify-center gap-3">
          <Button size="lg" asChild className="h-12 px-8"><Link to="/auth/signup">Start building free <ArrowRight className="size-4" /></Link></Button>
          <Button size="lg" variant="outline" asChild className="h-12 px-8"><Link to="/dashboard">Explore demo</Link></Button>
        </div>
      </div>
    </section>
  );
}

// Footer moved to PublicFooter in @/components/public-chrome.