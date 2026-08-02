import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sparkles, Loader2, PlayCircle } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

export const Route = createFileRoute("/auth/login")({
  component: Login,
});

const DEMO_EMAIL = "ujjwalvermauv2004@gmail.com";
const DEMO_PASSWORD = "Ujjwal@123";

function Login() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [demoLoading, setDemoLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!email || !password) { setError("Email and password are required."); return; }
    try {
      await login(email, password);
      toast.success("Welcome back!");
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Invalid email or password.");
    }
  }

  async function handleDemoLogin() {
    setDemoLoading(true);
    setError(null);
    try {
      await login(DEMO_EMAIL, DEMO_PASSWORD);
      toast.success("Exploring demo workspace…");
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      setError("Demo login failed. Please try manual login.");
    } finally {
      setDemoLoading(false);
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to continue building your startup."
      footer={
        <>
          Don&apos;t have an account?{" "}
          <Link to="/auth/signup" className="text-primary hover:underline">
            Create one
          </Link>
        </>
      }
    >
      <form className="space-y-4" onSubmit={handleSubmit} noValidate>
        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        <Button className="w-full" type="submit" disabled={isLoading}>
          {isLoading ? <Loader2 className="size-4 animate-spin" /> : null}
          Sign in
        </Button>
      </form>
      <div className="relative my-5">
        <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-border" /></div>
        <div className="relative flex justify-center text-xs text-muted-foreground"><span className="bg-background px-3">or</span></div>
      </div>
      <Button
        type="button"
        variant="outline"
        className="w-full gap-2 border-primary/30 hover:border-primary/60 hover:bg-primary/5"
        onClick={handleDemoLogin}
        disabled={demoLoading}
      >
        {demoLoading ? <Loader2 className="size-4 animate-spin" /> : <PlayCircle className="size-4 text-primary" />}
        Try demo workspace
      </Button>
      <p className="text-[11px] text-muted-foreground text-center mt-2">
        Explore 5 fully-seeded projects — no signup needed
      </p>
    </AuthShell>
  );
}

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:block relative overflow-hidden bg-sidebar">
        <div className="absolute inset-0 grid-bg opacity-40" />
        <div className="absolute -top-40 -left-40 size-[520px] rounded-full gradient-brand opacity-40 blur-3xl" />
        <div className="absolute bottom-0 right-0 size-[420px] rounded-full bg-brand-glow opacity-30 blur-3xl" />
        <div className="relative p-10 h-full flex flex-col">
          <Link to="/" className="flex items-center gap-2">
            <div className="size-8 rounded-lg overflow-hidden shadow-glow shrink-0">
              <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
            </div>
            <span className="font-display text-lg font-semibold">FoundrAI</span>
          </Link>
          <div className="mt-auto max-w-md">
            <div className="font-display text-3xl font-semibold tracking-tight">
              "FoundrAI turned my Sunday afternoon idea into a Monday morning
              company."
            </div>
            <div className="mt-4 text-sm text-muted-foreground">
              Maya Chen — founder, Kelp
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center p-6 md:p-10">
        <div className="w-full max-w-sm">
          <Link to="/" className="lg:hidden flex items-center gap-2 mb-8">
            <div className="size-8 rounded-lg overflow-hidden shadow-glow shrink-0">
              <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
            </div>
            <span className="font-display text-lg font-semibold">FoundrAI</span>
          </Link>
          <h1 className="font-display text-3xl font-semibold tracking-tight">
            {title}
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5">{subtitle}</p>
          <div className="mt-8">{children}</div>
          {footer && (
            <div className="text-sm text-muted-foreground mt-6 text-center">
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
