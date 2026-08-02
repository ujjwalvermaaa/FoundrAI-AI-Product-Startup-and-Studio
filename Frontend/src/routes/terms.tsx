import { createFileRoute } from "@tanstack/react-router";
import { PublicNav, PublicFooter } from "@/components/public-chrome";

export const Route = createFileRoute("/terms")({
  component: Page,
});

function Page() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PublicNav />
      <article className="pt-32 pb-20 max-w-3xl mx-auto px-6">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Legal</div>
        <h1 className="font-display text-4xl font-semibold tracking-tight mt-2">Terms & Conditions</h1>
        <p className="text-muted-foreground text-sm mt-2">Last updated: January 2026</p>
        <div className="mt-8 space-y-6 text-sm leading-relaxed text-foreground/90">
          {["Acceptance","Use of the service","Your content","AI outputs","Payment","Termination","Disclaimers","Limitation of liability","Governing law"].map((h, i) => (
            <section key={h}>
              <h2 className="font-display text-xl font-semibold mb-2">{i + 1}. {h}</h2>
              <p className="text-muted-foreground">Placeholder terms for the FoundrAI preview build. Replace with your production legal copy before launch.</p>
            </section>
          ))}
        </div>
      </article>
      <PublicFooter />
    </div>
  );
}