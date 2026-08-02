import { createFileRoute } from "@tanstack/react-router";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { Card, CardContent } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

export const Route = createFileRoute("/about")({
  component: AboutPage,
});

function AboutPage() {
  const team = [
    { name: "Ujjwal Verma", role: "Founder & CEO", bio: "Building FoundrAI to give every founder the leverage of a full YC batch on day one." },
  ];
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PublicNav />
      <section className="pt-32 pb-20 relative overflow-hidden">
        <div className="absolute inset-0 grid-bg opacity-20" />
        <div className="relative max-w-3xl mx-auto px-6 text-center">
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">About</div>
          <h1 className="font-display text-5xl md:text-6xl font-semibold tracking-tight mt-3">
            We believe every idea deserves <span className="gradient-text">a fair shot.</span>
          </h1>
          <p className="text-muted-foreground mt-6 text-lg leading-relaxed">
            FoundrAI was born from a simple observation: 90% of great startup ideas never leave a Notes app. Between validation, research,
            financials, architecture and pitching — the gap between "idea" and "company" is a stack of blank documents. We're closing that gap.
          </p>
        </div>
      </section>

      <section className="pb-20 max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-6">
        <Card><CardContent className="p-6">
          <div className="size-10 rounded-lg gradient-brand grid place-items-center shadow-glow mb-4"><Sparkles className="size-5 text-white" /></div>
          <div className="font-display text-xl font-semibold">Our mission</div>
          <p className="text-sm text-muted-foreground mt-2">Give every founder — anywhere in the world — the operational leverage of a full YC batch, on day one.</p>
        </CardContent></Card>
        <Card><CardContent className="p-6">
          <div className="size-10 rounded-lg bg-accent grid place-items-center mb-4"><span className="font-display font-semibold">1M</span></div>
          <div className="font-display text-xl font-semibold">Our target</div>
          <p className="text-sm text-muted-foreground mt-2">One million real, funded companies launched through FoundrAI by 2030.</p>
        </CardContent></Card>
      </section>

      <section className="pb-24 max-w-6xl mx-auto px-6">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium mb-2">The team</div>
        <h2 className="font-display text-3xl font-semibold tracking-tight mb-8">Small team. Big leverage.</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {team.map((t) => (
            <Card key={t.name}><CardContent className="p-5">
              <div className="size-14 rounded-full gradient-brand grid place-items-center text-white font-display font-semibold text-lg mb-3">{t.name.split(" ").map(w=>w[0]).join("")}</div>
              <div className="font-display font-semibold">{t.name}</div>
              <div className="text-xs text-primary">{t.role}</div>
              <div className="text-sm text-muted-foreground mt-2">{t.bio}</div>
            </CardContent></Card>
          ))}
        </div>
      </section>
      <PublicFooter />
    </div>
  );
}