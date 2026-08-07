import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { PublicPage, PageHero } from "@/components/layout/page-shell";
import { Card, CardContent } from "@/components/ui/card";

export const Route = createFileRoute("/terms")({
  component: Page,
});

function Page() {
  const headings = [
    "Acceptance",
    "Use of the service",
    "Your content",
    "AI outputs",
    "Payment",
    "Termination",
    "Disclaimers",
    "Limitation of liability",
    "Governing law",
  ];

  return (
    <PublicPage>
      <PublicNav />
      <PageHero
        eyebrow="Legal"
        title="Terms & Conditions"
        description="Last updated: January 2026"
        className="pb-10 md:pb-12"
      />

      <article className="pb-24 max-w-3xl mx-auto px-6">
        <div className="space-y-4">
          {headings.map((h, i) => (
            <motion.div
              key={h}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-30px" }}
              transition={{ duration: 0.4, delay: Math.min(i * 0.03, 0.2) }}
            >
              <Card>
                <CardContent className="p-5">
                  <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-2">
                    Section {String(i + 1).padStart(2, "0")}
                  </div>
                  <h2 className="font-display text-xl font-semibold mb-2">
                    {i + 1}. {h}
                  </h2>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Placeholder terms for the FoundrAI preview build. Replace with your production legal copy before launch.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </article>
      <PublicFooter />
    </PublicPage>
  );
}
