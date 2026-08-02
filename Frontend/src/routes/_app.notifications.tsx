import { createFileRoute } from "@tanstack/react-router";
import { Sparkles, Bell, Users, CheckCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MOCK_NOTIFICATIONS } from "@/lib/mock-data";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/notifications")({
  component: NotificationsPage,
});

const iconFor = { ai: Sparkles, system: Bell, collab: Users } as const;

function NotificationsPage() {
  return (
    <div className="max-w-3xl mx-auto p-6 md:p-8">
      <div className="flex items-end justify-between mb-6">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Inbox</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">Notifications</h1>
        </div>
        <Button variant="outline" size="sm"><CheckCheck className="size-4" /> Mark all read</Button>
      </div>
      <Card>
        <CardContent className="p-0 divide-y divide-border">
          {MOCK_NOTIFICATIONS.map((n) => {
            const Icon = iconFor[n.kind];
            return (
              <div key={n.id} className={cn("flex gap-4 p-4 hover:bg-accent/40 transition-colors", n.unread && "bg-accent/20")}>
                <div className={cn("size-9 rounded-md grid place-items-center shrink-0", n.kind === "ai" ? "gradient-brand text-white" : "bg-muted")}>
                  <Icon className="size-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{n.title}</span>
                    {n.unread && <Badge variant="secondary" className="text-[10px]">New</Badge>}
                  </div>
                  <div className="text-sm text-muted-foreground mt-0.5">{n.detail}</div>
                  <div className="text-xs text-muted-foreground mt-1">{formatDistanceToNow(new Date(n.timestamp), { addSuffix: true })}</div>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}