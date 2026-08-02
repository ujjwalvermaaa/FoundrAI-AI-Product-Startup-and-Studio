import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Camera, Github, Twitter, Linkedin, LogOut, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/profile")({
  component: ProfilePage,
});

function ProfilePage() {
  const navigate = useNavigate();
  const { user, logout, updateUser } = useAuth();
  const [displayName, setDisplayName] = useState(user?.full_name ?? "");
  const [saving, setSaving] = useState(false);
  const [signingOut, setSigningOut] = useState(false);

  const initials = (user?.full_name ?? "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      // Optimistically update the local store — real PATCH /auth/me not in current backend
      updateUser({ full_name: displayName });
      toast.success("Profile updated");
    } finally {
      setSaving(false);
    }
  }

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await logout();
      navigate({ to: "/auth/login" });
    } finally {
      setSigningOut(false);
    }
  }

  return (
    <div className="p-6 md:p-8 max-w-[1000px] mx-auto">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Account</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">Profile</h1>
        <p className="text-muted-foreground mt-1">How you show up in the studio.</p>
      </div>

      <Card className="overflow-hidden mb-4">
        <div className="h-32 gradient-brand" />
        <CardContent className="p-6 -mt-14">
          <div className="flex items-end gap-4">
            <div className="size-24 rounded-2xl border-4 border-card bg-muted grid place-items-center shadow-glow relative">
              <span className="font-display text-3xl font-semibold gradient-text">{initials}</span>
              <button className="absolute -bottom-1 -right-1 size-7 rounded-full bg-primary text-primary-foreground grid place-items-center border-2 border-card">
                <Camera className="size-3.5" />
              </button>
            </div>
            <div className="pb-2">
              <div className="font-display text-xl font-semibold">{user?.full_name ?? "—"}</div>
              <div className="text-sm text-muted-foreground">{user?.email ?? "—"} · Founder</div>
            </div>
            <Badge variant="outline" className="ml-auto mb-2 gap-1 bg-primary/5 text-primary border-primary/30">
              Founder plan
            </Badge>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="font-display font-semibold">Details</div>
            <form onSubmit={handleSave} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="display-name">Display name</Label>
                <Input
                  id="display-name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Email</Label>
                <Input value={user?.email ?? ""} readOnly className="opacity-60 cursor-default" />
              </div>
              <div className="space-y-1.5">
                <Label>Bio</Label>
                <textarea
                  className="w-full min-h-24 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  defaultValue="Building an AI-native studio for founders."
                />
              </div>
              <Button type="submit" disabled={saving}>
                {saving && <Loader2 className="size-3.5 animate-spin" />}
                Save changes
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardContent className="p-6 space-y-3">
              <div className="font-display font-semibold">Preferences</div>
              <Row label="Language" value="English (US)" />
              <Row label="Timezone" value="America / New York" />
              <Row label="Startup stage" value="Building MVP" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 space-y-3">
              <div className="font-display font-semibold">Connected</div>
              <ConnectRow icon={Github} name="GitHub" connected />
              <ConnectRow icon={Twitter} name="X / Twitter" />
              <ConnectRow icon={Linkedin} name="LinkedIn" connected />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">Sign out everywhere</div>
                <div className="text-xs text-muted-foreground">End sessions on all devices.</div>
              </div>
              <Button
                variant="outline"
                className="gap-2"
                onClick={handleSignOut}
                disabled={signingOut}
              >
                {signingOut ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <LogOut className="size-3.5" />
                )}
                Sign out
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-sm py-1 border-b border-border/50 last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span>{value}</span>
    </div>
  );
}

function ConnectRow({
  icon: Icon,
  name,
  connected,
}: {
  icon: React.ElementType;
  name: string;
  connected?: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-sm py-1">
      <div className="flex items-center gap-2">
        <Icon className="size-4" />
        {name}
      </div>
      {connected ? (
        <Badge variant="outline" className="text-[10px] bg-emerald-500/5 border-emerald-500/30 text-emerald-500">
          Connected
        </Badge>
      ) : (
        <Button size="sm" variant="outline" className="h-7 text-xs">
          Connect
        </Button>
      )}
    </div>
  );
}
