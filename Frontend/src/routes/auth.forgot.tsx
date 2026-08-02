import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthShell } from "./auth.login";

export const Route = createFileRoute("/auth/forgot")({
  component: Forgot,
});

function Forgot() {
  return (
    <AuthShell
      title="Forgot your password?"
      subtitle="We'll email you a secure link to reset it."
      footer={<>Remembered it? <Link to="/auth/login" className="text-primary hover:underline">Sign in</Link></>}
    >
      <form className="space-y-4">
        <div className="space-y-1.5"><Label>Email</Label><Input type="email" placeholder="you@company.com" /></div>
        <Button className="w-full" asChild><Link to="/auth/reset">Send reset link</Link></Button>
      </form>
    </AuthShell>
  );
}