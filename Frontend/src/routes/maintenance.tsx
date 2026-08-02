import { createFileRoute, Link } from "@tanstack/react-router";
import { Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/maintenance")({
  component: Page,
});

function Page() {
  return (
    <div className="min-h-screen grid place-items-center bg-background text-foreground p-6">
      <div className="text-center max-w-md">
        <div className="size-16 mx-auto rounded-2xl gradient-brand grid place-items-center shadow-glow"><Wrench className="size-7 text-white" /></div>
        <h1 className="font-display text-3xl font-semibold tracking-tight mt-6">We'll be right back.</h1>
        <p className="text-muted-foreground mt-2">FoundrAI is deploying a small upgrade. This usually takes under 5 minutes.</p>
        <Button className="mt-6" asChild><Link to="/">Refresh</Link></Button>
      </div>
    </div>
  );
}