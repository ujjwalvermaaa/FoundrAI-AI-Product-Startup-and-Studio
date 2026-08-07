import { createFileRoute, Link } from "@tanstack/react-router";
import { Card, CardContent } from "@/components/ui/card";
import { BookOpen, Rocket, Sparkles, Layers, Code2, Shield, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";

export const Route = createFileRoute("/_app/docs")({
  component: DocsPage,
});

const SECTIONS = [
  { icon: Rocket, title: "Getting started", desc: "Create your first project and generate an idea validation in 5 minutes.", topics: ["Quickstart", "Onboarding", "Your first module"] },
  { icon: Layers, title: "Modules", desc: "Deep-dive into each of the 8 startup modules and how AI drafts them.", topics: ["Idea Validation", "Market Research", "Business Model", "Financial Planning"] },
  { icon: Sparkles, title: "Foundr AI Copilot", desc: "Get the most out of your context-aware AI co-founder.", topics: ["Prompting tips", "Project memory", "Artifacts & citations"] },
  { icon: Code2, title: "API & integrations", desc: "Connect FoundrAI to Notion, Slack, GitHub and more.", topics: ["REST API", "Webhooks", "Zapier"] },
  { icon: Shield, title: "Security & privacy", desc: "How we store, encrypt and train (never) on your data.", topics: ["Data handling", "SOC 2", "SSO & SAML"] },
  { icon: BookOpen, title: "Playbooks", desc: "Battle-tested templates from YC, Sequoia and Stripe teardowns.", topics: ["Seed pitch", "PLG launch", "B2B GTM"] },
];

function DocsPage() {
  return (
    <AppPage className="max-w-6xl">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Documentation</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
          Everything you need to <span className="gradient-text">build</span>.
        </h1>
        <p className="text-muted-foreground mt-2 max-w-2xl">Guides, references and playbooks for turning FoundrAI into your startup operating system.</p>
      </motion.div>
      <div className="relative max-w-xl">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input placeholder="Search the docs…" className="pl-9" />
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {SECTIONS.map((s, i) => (
          <motion.div
            key={s.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="hover:border-primary/40 transition-colors group rounded-xl h-full">
              <CardContent className="p-5 space-y-3">
                <div className="size-10 rounded-xl gradient-brand grid place-items-center shadow-glow"><s.icon className="size-5 text-white" /></div>
                <div>
                  <div className="font-display font-semibold">{s.title}</div>
                  <div className="text-sm text-muted-foreground mt-1">{s.desc}</div>
                </div>
                <ul className="text-sm space-y-1 pt-2 border-t border-border/60">
                  {s.topics.map((t) => (
                    <li key={t}><Link to="/help" className="text-muted-foreground hover:text-foreground">→ {t}</Link></li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </AppPage>
  );
}
