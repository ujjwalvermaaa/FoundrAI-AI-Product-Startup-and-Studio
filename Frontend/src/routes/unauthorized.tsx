import { createFileRoute, Link } from "@tanstack/react-router";
import { Lock } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/unauthorized")({
  component: Page,
});

function Page() {
  return (
    <div className="min-h-screen grid place-items-center bg-background text-foreground p-6">
      <div className="text-center max-w-md">
        <div className="size-16 mx-auto rounded-2xl bg-destructive/10 grid place-items-center"><Lock className="size-7 text-destructive" /></div>
        <h1 className="font-display text-3xl font-semibold tracking-tight mt-6">You don't have access.</h1>
        <p className="text-muted-foreground mt-2">Ask a workspace admin to invite you, or sign in with a different account.</p>
        <div className="mt-6 flex gap-2 justify-center">
          <Button variant="outline" asChild><Link to="/">Go home</Link></Button>
          <Button asChild><Link to="/auth/login">Sign in</Link></Button>
        </div>
      </div>
    </div>
  );
}