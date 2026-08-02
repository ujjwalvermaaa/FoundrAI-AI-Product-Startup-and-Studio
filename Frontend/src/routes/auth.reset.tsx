import { createFileRoute, Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthShell } from "./auth.login";

export const Route = createFileRoute("/auth/reset")({
  component: Reset,
});

function Reset() {
  return (
    <AuthShell
      title="Set a new password"
      subtitle="At least 12 characters. A phrase you'll remember is best."
      footer={<Link to="/auth/login" className="text-primary hover:underline">Back to sign in</Link>}
    >
      <form className="space-y-4">
        <div className="space-y-1.5"><Label>New password</Label><Input type="password" /></div>
        <div className="space-y-1.5"><Label>Confirm password</Label><Input type="password" /></div>
        <Button className="w-full" asChild><Link to="/auth/login">Save password</Link></Button>
      </form>
    </AuthShell>
  );
}