import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { PublicPage, PageHero } from "@/components/layout/page-shell";
import { Card, CardContent } from "@/components/ui/card";

export const Route = createFileRoute("/privacy")({
  component: Page,
});

function Page() {
  const sections = [
    { title: "What we collect", body: "Account info (name, email), workspace content you create, and product analytics needed to operate the service." },
    { title: "How we use it", body: "To provide the service, generate AI outputs you request, improve reliability, and communicate about your account." },
    { title: "Sharing", body: "We do not sell personal data. We share limited data with subprocessors strictly to run the service." },
    { title: "Retention", body: "You can delete your projects and account at any time. Backups are purged within 30 days." },
    { title: "Your rights", body: "Access, correction, deletion and export. Contact privacy@foundrai.app." },
    { title: "Security", body: "Encryption in transit, least-privilege access controls, and audit logging on production systems." },
  ];

  return (
    <PublicPage>
      <PublicNav />
      <PageHero
        eyebrow="Legal"
        title="Privacy Policy"
        description="Last updated: January 2026"
        className="pb-10 md:pb-12"
      />

      <article className="pb-24 max-w-3xl mx-auto px-6">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-sm leading-relaxed text-foreground/90 mb-8"
        >
          This page is maintained by FoundrAI to explain what data we collect, why we collect it, and the choices you have. This is a demo policy for the current preview build and is not legal advice.
        </motion.p>
        <div className="space-y-4">
          {sections.map((s, i) => (
            <motion.div
              key={s.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-30px" }}
              transition={{ duration: 0.4, delay: i * 0.04 }}
            >
              <Card>
                <CardContent className="p-5">
                  <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium mb-2">
                    {String(i + 1).padStart(2, "0")}
                  </div>
                  <h2 className="font-display text-xl font-semibold mb-2">{s.title}</h2>
                  <p className="text-sm text-muted-foreground leading-relaxed">{s.body}</p>
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
