import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { AuthShell } from "./auth.login";
import { Mail } from "lucide-react";

export const Route = createFileRoute("/auth/verify")({
  component: Verify,
});

function Verify() {
  return (
    <AuthShell
      title="Check your inbox"
      subtitle="We sent a verification link to your email."
      footer={<>Wrong email? <Link to="/auth/signup" className="text-primary hover:underline">Change it</Link></>}
    >
      <div className="flex flex-col items-center text-center gap-4">
        <div className="size-16 rounded-full gradient-brand grid place-items-center shadow-glow">
          <Mail className="size-7 text-white" />
        </div>
        <p className="text-sm text-muted-foreground max-w-xs">Click the link in the email to activate your studio. The link expires in 15 minutes.</p>
        <div className="flex gap-2 w-full">
          <Button variant="outline" className="flex-1">Resend</Button>
          <Button className="flex-1" asChild><Link to="/onboarding">I verified</Link></Button>
        </div>
      </div>
    </AuthShell>
  );
}