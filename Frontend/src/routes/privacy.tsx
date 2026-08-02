import { createFileRoute } from "@tanstack/react-router";
import { PublicNav, PublicFooter } from "@/components/public-chrome";

export const Route = createFileRoute("/privacy")({
  component: Page,
});

function Page() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PublicNav />
      <article className="pt-32 pb-20 max-w-3xl mx-auto px-6 prose prose-invert">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Legal</div>
        <h1 className="font-display text-4xl font-semibold tracking-tight mt-2">Privacy Policy</h1>
        <p className="text-muted-foreground text-sm mt-2">Last updated: January 2026</p>
        <div className="mt-8 space-y-6 text-sm leading-relaxed text-foreground/90">
          <p>This page is maintained by FoundrAI to explain what data we collect, why we collect it, and the choices you have. This is a demo policy for the current preview build and is not legal advice.</p>
          <Sect title="What we collect" body="Account info (name, email), workspace content you create, and product analytics needed to operate the service." />
          <Sect title="How we use it" body="To provide the service, generate AI outputs you request, improve reliability, and communicate about your account." />
          <Sect title="Sharing" body="We do not sell personal data. We share limited data with subprocessors strictly to run the service." />
          <Sect title="Retention" body="You can delete your projects and account at any time. Backups are purged within 30 days." />
          <Sect title="Your rights" body="Access, correction, deletion and export. Contact privacy@foundrai.app." />
          <Sect title="Security" body="Encryption in transit, least-privilege access controls, and audit logging on production systems." />
        </div>
      </article>
      <PublicFooter />
    </div>
  );
}

function Sect({ title, body }: { title: string; body: string }) {
  return (
    <section>
      <h2 className="font-display text-xl font-semibold mb-2">{title}</h2>
      <p className="text-muted-foreground">{body}</p>
    </section>
  );
}