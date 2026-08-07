import { createFileRoute, Link } from "@tanstack/react-router";
import { Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AmbientField } from "@/components/layout/ambient-field";

export const Route = createFileRoute("/maintenance")({
  component: Page,
});

function Page() {
  return (
    <div className="relative min-h-screen grid place-items-center bg-background text-foreground p-6 overflow-hidden">
      <AmbientField />
      <div className="relative z-10 text-center max-w-md rounded-2xl glass-depth hologram-edge p-8">
        <div className="scan-line absolute inset-0 opacity-20 rounded-2xl" />
        <div className="relative z-10">
          <div className="relative size-16 mx-auto">
            <div className="absolute inset-0 rounded-2xl pulse-core bg-primary/40 blur-md" />
            <div className="relative size-16 rounded-2xl gradient-brand grid place-items-center shadow-glow">
              <Wrench className="size-7 text-white" />
            </div>
          </div>
          <h1 className="font-display text-3xl font-semibold tracking-tight mt-6">We'll be right back.</h1>
          <p className="text-muted-foreground mt-2">
            FoundrAI is deploying a small upgrade. This usually takes under 5 minutes.
          </p>
          <Button className="mt-6 rounded-xl shadow-glow" asChild>
            <Link to="/">Refresh</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
