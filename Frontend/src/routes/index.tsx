import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Lightbulb,
  LineChart,
  Layers,
  Compass,
  Network,
  Wallet,
  Megaphone,
  FileText,
  Check,
  Star,
  MessageCircle,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PublicFooter, PublicNav } from "@/components/public-chrome";
import { cn } from "@/lib/utils";

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

const quotes = [
  { name: "Devon Park", role: "Orbit", quote: "More thorough than my fractional CFO — in 4 minutes." },
  { name: "Aisha Patel", role: "Lumen", quote: "Surfaced a wedge my team missed for 6 months." },
  { name: "Jonas Weber", role: "Kelp", quote: "Every module ends with something I can send." },
  { name: "Marcus Chen", role: "2x founder", quote: "The co-founder that never loses context." },
];

function Landing() {
  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* Single continuous atmosphere — no section borders */}
      <div aria-hidden className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-10%,color-mix(in_oklab,var(--brand)_22%,transparent),transparent_55%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_90%_40%,color-mix(in_oklab,var(--brand-glow)_14%,transparent),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_50%_at_10%_80%,color-mix(in_oklab,var(--brand)_10%,transparent),transparent_45%)]" />
      </div>

      <div className="relative z-10">
        <PublicNav />
        <Hero />
        <ModulesFlow />
        <CopilotFlow />
        <ProofFlow />
        <PricingFlow />
        <FinalCta />
        <PublicFooter />
      </div>
    </div>
  );
}

function Hero() {
  return (
    <section className="relative min-h-[100svh] flex items-center px-6 pt-28 pb-16 md:pt-32 md:pb-20">
      <div className="mx-auto w-full max-w-7xl grid lg:grid-cols-[1.05fr_0.95fr] gap-12 lg:gap-8 items-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-[10px] font-medium uppercase tracking-[0.22em] text-primary mb-6">
            <Sparkles className="size-3" />
            Neural startup studio
          </div>
          <h1 className="font-display font-semibold tracking-[-0.045em] leading-[0.88] text-[clamp(3.75rem,12vw,8.5rem)]">
            Foundr
            <span className="gradient-text">AI</span>
          </h1>
          <p className="mt-6 max-w-md text-base md:text-lg text-muted-foreground leading-relaxed">
            Eight autonomous agents. One workspace. Turn a raw idea into a fundable company.
          </p>
          <div className="mt-8">
            <Button size="lg" asChild className="h-12 px-8 shadow-glow text-base">
              <Link to="/auth/signup">
                Start building free <ArrowRight className="size-4" />
              </Link>
            </Button>
            <p className="mt-3 text-xs text-muted-foreground">Free forever · No credit card</p>
          </div>
        </motion.div>

        {/* 3D floating core — dominant visual, not a browser mock / video */}
        <motion.div
          initial={{ opacity: 0, scale: 0.88, rotateY: -12 }}
          animate={{ opacity: 1, scale: 1, rotateY: 0 }}
          transition={{ delay: 0.15, duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          className="relative mx-auto w-full max-w-md aspect-square perspective-stage"
          style={{ transformStyle: "preserve-3d" }}
        >
          <div className="absolute inset-[8%] rounded-full bg-primary/30 blur-[60px] pulse-core" />
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0"
          >
            <div className="absolute inset-0 rounded-full border border-primary/20 border-dashed" />
          </motion.div>
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
            className="absolute inset-[12%]"
          >
            <div className="absolute inset-0 rounded-full border border-brand-glow/25" />
            {modules.slice(0, 6).map((m, i) => {
              const angle = (i / 6) * Math.PI * 2 - Math.PI / 2;
              const x = 50 + Math.cos(angle) * 48;
              const y = 50 + Math.sin(angle) * 48;
              return (
                <div
                  key={m.name}
                  className="absolute size-9 -translate-x-1/2 -translate-y-1/2 rounded-xl bg-background/80 backdrop-blur-md border border-primary/25 grid place-items-center shadow-glow"
                  style={{ left: `${x}%`, top: `${y}%` }}
                >
                  <m.icon className="size-3.5 text-primary" />
                </div>
              );
            })}
          </motion.div>
          <div className="absolute inset-[28%] rounded-[2rem] overflow-hidden shadow-glow ring-1 ring-primary/40 float-y">
            <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

/** Modules continue the same scroll — no section borders */
function ModulesFlow() {
  return (
    <section id="modules" className="relative px-6 pb-8 md:pb-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-2xl mb-10"
        >
          <h2 className="font-display text-3xl md:text-5xl font-semibold tracking-tight leading-[1.08]">
            Eight agents.
            <span className="gradient-text"> One company.</span>
          </h2>
          <p className="mt-3 text-muted-foreground text-base md:text-lg">
            Each ships a real artifact — research, canvas, deck — ready to edit and share.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {modules.map((m, i) => (
            <motion.div
              key={m.name}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: i * 0.04 }}
              whileHover={{ y: -6, rotateX: 4, rotateY: -4 }}
              style={{ transformStyle: "preserve-3d" }}
              className="group rounded-3xl bg-card/40 backdrop-blur-xl p-5 md:p-6 shadow-[0_20px_50px_-30px_oklch(0_0_0/0.5)] ring-1 ring-white/5 hover:ring-primary/30 hover:shadow-glow transition-shadow"
            >
              <div className="flex items-center justify-between mb-5">
                <div className="size-11 rounded-2xl bg-primary/15 grid place-items-center group-hover:gradient-brand group-hover:text-white transition-all">
                  <m.icon className="size-5" />
                </div>
                <span className="font-mono text-[10px] text-muted-foreground/70">0{i + 1}</span>
              </div>
              <h3 className="font-display text-lg font-semibold tracking-tight">{m.name}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed">{m.copy}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CopilotFlow() {
  const messages = [
    { from: "you", text: "Can we raise on this traction?" },
    { from: "foundr", text: "Yes — I'll draft the ask and use-of-funds from your model." },
    { from: "you", text: "Also check pricing vs competitors." },
    { from: "foundr", text: "Pricing looks solid. Deck draft is ready." },
  ];

  return (
    <section className="relative px-6 py-20 md:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="grid lg:grid-cols-[1fr_1.15fr] gap-10 lg:gap-14 items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="order-2 lg:order-1"
          >
            <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-3">
              Always on
            </div>
            <h2 className="font-display text-3xl md:text-5xl font-semibold tracking-tight leading-[1.08]">
              Your co-founder
              <br />
              <span className="gradient-text">never sleeps.</span>
            </h2>
            <p className="mt-5 text-muted-foreground text-base md:text-lg leading-relaxed max-w-md">
              Foundr holds the context of your whole company. Ask about pricing, hiring, or pitching — get answers with
              artifacts attached.
            </p>
            <Button size="lg" asChild className="mt-8 h-12 shadow-glow">
              <Link to="/chat">
                <MessageCircle className="size-4" /> Open chat
              </Link>
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="order-1 lg:order-2 relative"
          >
            <div className="absolute -inset-6 rounded-[2rem] bg-primary/15 blur-3xl pointer-events-none" />
            <div className="relative rounded-[1.75rem] bg-card/50 backdrop-blur-xl ring-1 ring-white/10 shadow-[0_30px_80px_-40px_oklch(0_0_0/0.7)] overflow-hidden">
              <div className="flex items-center gap-3 px-5 py-4 bg-muted/30">
                <div className="relative size-11 shrink-0">
                  <div className="absolute inset-0 rounded-full pulse-core bg-primary/35 blur-md" />
                  <div className="relative size-11 rounded-full overflow-hidden ring-2 ring-primary/40 shadow-glow">
                    <img src="/founder-bot.jpg" alt="Foundr" className="size-full object-cover" />
                  </div>
                  <span className="absolute bottom-0 right-0 size-2.5 rounded-full bg-emerald-400 ring-2 ring-background" />
                </div>
                <div className="min-w-0">
                  <div className="font-display font-semibold text-sm">Foundr</div>
                  <div className="text-[11px] text-emerald-400/90">Online · co-pilot</div>
                </div>
              </div>

              <div className="p-5 space-y-3 min-h-[260px]">
                {messages.map((m, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.15 + i * 0.08 }}
                    className={cn("flex", m.from === "you" ? "justify-end" : "justify-start")}
                  >
                    <div
                      className={cn(
                        "max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed",
                        m.from === "you"
                          ? "bg-primary text-primary-foreground rounded-br-md"
                          : "bg-muted/60 text-foreground rounded-bl-md ring-1 ring-white/5",
                      )}
                    >
                      {m.text}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function ProofFlow() {
  return (
    <section className="relative px-6 py-16 md:py-24">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-10"
        >
          <h2 className="font-display text-3xl md:text-5xl font-semibold tracking-tight">
            Built with real founders.
          </h2>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {quotes.map((q, i) => (
            <motion.blockquote
              key={q.name}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="rounded-3xl bg-card/35 backdrop-blur-xl p-5 min-h-[180px] flex flex-col ring-1 ring-white/5"
            >
              <div className="flex gap-0.5 mb-3">
                {Array.from({ length: 5 }).map((_, j) => (
                  <Star key={j} className="size-3 text-primary fill-primary" />
                ))}
              </div>
              <p className="text-sm leading-relaxed flex-1">"{q.quote}"</p>
              <footer className="mt-4">
                <div className="text-sm font-medium">{q.name}</div>
                <div className="text-[11px] text-muted-foreground">{q.role}</div>
              </footer>
            </motion.blockquote>
          ))}
        </div>

        {/* Soft comparison — no harsh table lines */}
        <div className="mt-14 md:mt-20 grid md:grid-cols-2 gap-4 max-w-3xl">
          <div className="rounded-3xl bg-primary/10 p-6 ring-1 ring-primary/20">
            <div className="text-[10px] uppercase tracking-[0.2em] text-primary mb-3">With FoundrAI</div>
            <ul className="space-y-2.5 text-sm">
              {["First artifact in 45 min", "Living workspace", "Investor-ready drafts"].map((t) => (
                <li key={t} className="flex items-center gap-2">
                  <Check className="size-4 text-primary shrink-0" /> {t}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-3xl bg-muted/30 p-6 ring-1 ring-white/5">
            <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground mb-3">Without</div>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              {["Weeks of blank docs", "Scattered Notion pages", "20+ deck rewrites"].map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

function PricingFlow() {
  const tiers = [
    { name: "Explorer", price: "Free", desc: "Explore an idea.", features: ["1 project", "3 modules", "Community"], featured: false },
    { name: "Founder", price: "$29", desc: "Launch for real.", features: ["Unlimited projects", "All 8 modules", "Exports"], featured: true },
    { name: "Team", price: "$99", desc: "Multiple ventures.", features: ["Unlimited seats", "Priority compute", "SSO"], featured: false },
  ];
  return (
    <section id="pricing" className="relative px-6 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-12">
          <h2 className="font-display text-3xl md:text-5xl font-semibold tracking-tight">
            Simple pricing for founders.
          </h2>
          <p className="mt-3 text-muted-foreground">Start free. Upgrade when you raise.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-4 items-stretch">
          {tiers.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07 }}
              className={cn(
                "relative rounded-3xl bg-card/40 backdrop-blur-xl p-6 flex flex-col ring-1 ring-white/5",
                t.featured && "md:scale-[1.03] ring-primary/40 shadow-glow bg-card/60",
              )}
            >
              {t.featured && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 gradient-brand text-white border-0 gap-1">
                  <Star className="size-3" /> Popular
                </Badge>
              )}
              <div className="font-display text-lg font-semibold">{t.name}</div>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="font-display text-5xl font-semibold tracking-tight">{t.price}</span>
                {t.price !== "Free" && <span className="text-muted-foreground text-sm">/mo</span>}
              </div>
              <p className="text-sm text-muted-foreground mt-2">{t.desc}</p>
              <ul className="mt-6 space-y-2.5 text-sm flex-1">
                {t.features.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <Check className="size-4 text-primary" /> {f}
                  </li>
                ))}
              </ul>
              <Button className="w-full mt-6" variant={t.featured ? "default" : "outline"} asChild>
                <Link to="/auth/signup">Get started</Link>
              </Button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="relative px-6 py-24 md:py-32">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative mx-auto max-w-3xl text-center rounded-[2rem] bg-primary/10 px-8 py-16 md:py-20 ring-1 ring-primary/20 shadow-glow overflow-hidden"
      >
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,color-mix(in_oklab,var(--brand)_25%,transparent),transparent_70%)]" />
        <div className="relative z-10">
          <h2 className="font-display text-4xl md:text-6xl font-semibold tracking-tight leading-[1.02]">
            One prompt.
            <br />
            <span className="gradient-text">A real company.</span>
          </h2>
          <p className="mt-5 text-muted-foreground">Free forever to start. No card required.</p>
          <Button size="lg" asChild className="mt-8 h-12 px-9 shadow-glow">
            <Link to="/auth/signup">
              Start building free <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </motion.div>
    </section>
  );
}
