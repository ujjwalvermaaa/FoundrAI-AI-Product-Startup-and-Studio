import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { PublicPage, PageHero } from "@/components/layout/page-shell";
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
    <PublicPage>
      <PublicNav />
      <PageHero
        eyebrow="About"
        title={
          <>
            We believe every idea deserves <span className="gradient-text">a fair shot.</span>
          </>
        }
        description={
          <>
            FoundrAI was born from a simple observation: 90% of great startup ideas never leave a Notes app. Between validation, research,
            financials, architecture and pitching — the gap between "idea" and "company" is a stack of blank documents. We're closing that gap.
          </>
        }
      />

      <section className="pb-20 max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-6">
        {[
          {
            icon: (
              <div className="size-10 rounded-xl gradient-brand grid place-items-center shadow-glow mb-4">
                <Sparkles className="size-5 text-white" />
              </div>
            ),
            title: "Our mission",
            body: "Give every founder — anywhere in the world — the operational leverage of a full YC batch, on day one.",
          },
          {
            icon: (
              <div className="size-10 rounded-xl bg-accent/80 border border-primary/20 grid place-items-center mb-4 hologram-edge">
                <span className="font-display font-semibold">1M</span>
              </div>
            ),
            title: "Our target",
            body: "One million real, funded companies launched through FoundrAI by 2030.",
          },
        ].map((item, i) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.45, delay: i * 0.08 }}
          >
            <Card className="h-full">
              <CardContent className="p-6">
                {item.icon}
                <div className="font-display text-xl font-semibold">{item.title}</div>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{item.body}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </section>

      <section className="pb-24 max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-2">The team</div>
          <h2 className="font-display text-3xl font-semibold tracking-tight mb-8">Small team. Big leverage.</h2>
        </motion.div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {team.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.45, delay: i * 0.06 }}
            >
              <Card className="h-full">
                <CardContent className="p-5">
                  <div className="size-14 rounded-2xl gradient-brand grid place-items-center text-white font-display font-semibold text-lg mb-3 shadow-glow">
                    {t.name.split(" ").map((w) => w[0]).join("")}
                  </div>
                  <div className="font-display font-semibold">{t.name}</div>
                  <div className="text-xs text-primary tracking-wide mt-0.5">{t.role}</div>
                  <div className="text-sm text-muted-foreground mt-2 leading-relaxed">{t.bio}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>
      <PublicFooter />
    </PublicPage>
  );
}
