import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useTheme } from "@/components/providers/theme-provider";
import { Sun, Moon, Monitor, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

export const Route = createFileRoute("/_app/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [saving, setSaving] = useState(false);

  const initials = (user?.full_name ?? "U")
    .split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);

  const themes = [
    { id: "light", label: "Light", icon: Sun },
    { id: "dark", label: "Dark", icon: Moon },
    { id: "system", label: "System", icon: Monitor },
  ] as const;

  async function handleSaveProfile(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      updateUser({ full_name: fullName });
      toast.success("Profile updated");
    } finally {
      setSaving(false);
    }
  }

  async function handleSignOut() {
    await logout();
    navigate({ to: "/auth/login" });
  }

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Preferences</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">Settings</h1>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="ai">AI</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
          <TabsTrigger value="workspace">Workspace</TabsTrigger>
        </TabsList>

        {/* ── Profile ── */}
        <TabsContent value="profile">
          <Card>
            <CardHeader><CardTitle className="font-display">Profile</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleSaveProfile} className="space-y-5">
                <div className="flex items-center gap-4">
                  <Avatar className="size-16">
                    <AvatarFallback className="gradient-brand text-white text-lg">{initials}</AvatarFallback>
                  </Avatar>
                  <div>
                    <Button type="button" variant="outline" size="sm">Upload photo</Button>
                    <div className="text-xs text-muted-foreground mt-2">PNG or JPG, up to 2MB.</div>
                  </div>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="full-name">Full name</Label>
                    <Input id="full-name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Email</Label>
                    <Input value={user?.email ?? ""} readOnly className="opacity-60 cursor-default" />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Role</Label>
                    <Input defaultValue="Founder" />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Company</Label>
                    <Input defaultValue="" placeholder="Your company name" />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={handleSignOut}>Sign out</Button>
                  <Button type="submit" disabled={saving}>
                    {saving && <Loader2 className="size-3.5 animate-spin" />}
                    Save changes
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Appearance ── */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader><CardTitle className="font-display">Appearance</CardTitle></CardHeader>
            <CardContent className="space-y-5">
              <div>
                <Label>Theme</Label>
                <div className="grid grid-cols-3 gap-3 mt-2">
                  {themes.map((t) => (
                    <button key={t.id} type="button" onClick={() => setTheme(t.id)}
                      className={cn("border rounded-lg p-4 flex flex-col items-center gap-2 transition-all",
                        theme === t.id ? "border-primary bg-accent/50 shadow-glow" : "border-border hover:border-primary/40")}>
                      <t.icon className="size-5" />
                      <span className="text-sm font-medium">{t.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between py-3 border-t border-border">
                <div><div className="font-medium text-sm">Reduce motion</div><div className="text-xs text-muted-foreground">Minimize non-essential animations.</div></div>
                <Switch />
              </div>
              <div className="flex items-center justify-between py-3 border-t border-border">
                <div><div className="font-medium text-sm">Compact density</div><div className="text-xs text-muted-foreground">Denser layout for power users.</div></div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── AI ── */}
        <TabsContent value="ai">
          <Card>
            <CardHeader><CardTitle className="font-display">AI configuration</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-border">
                <div><div className="font-medium text-sm">Auto-run modules</div><div className="text-xs text-muted-foreground">Kick off the next module when the previous completes.</div></div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between py-3 border-b border-border">
                <div><div className="font-medium text-sm">Deep research</div><div className="text-xs text-muted-foreground">Use extended reasoning and web sources.</div></div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between py-3">
                <div><div className="font-medium text-sm">Reference tone</div><div className="text-xs text-muted-foreground">Match the writing style of prior artifacts.</div></div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Billing ── */}
        <TabsContent value="billing">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Current plan</div>
                  <div className="font-display text-2xl font-semibold mt-1">Founder <span className="gradient-text">Free</span></div>
                  <div className="text-sm text-muted-foreground">10,000 AI credits / month · unlimited projects</div>
                </div>
                <Button>Upgrade plan</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Workspace ── */}
        <TabsContent value="workspace">
          <Card>
            <CardHeader><CardTitle className="font-display">Workspace</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5"><Label>Workspace name</Label><Input defaultValue={user?.full_name ? `${user.full_name.split(" ")[0]}'s Studio` : "My Studio"} /></div>
              <div className="space-y-1.5"><Label>Slug</Label><Input defaultValue={user?.email?.split("@")[0] ?? "my-studio"} /></div>
              <Button>Save workspace</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
