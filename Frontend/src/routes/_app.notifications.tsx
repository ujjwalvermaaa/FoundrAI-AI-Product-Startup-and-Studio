import { createFileRoute } from "@tanstack/react-router";
import { Sparkles, Bell, Users, CheckCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MOCK_NOTIFICATIONS } from "@/lib/mock-data";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";

export const Route = createFileRoute("/_app/notifications")({
  component: NotificationsPage,
});

const iconFor = { ai: Sparkles, system: Bell, collab: Users } as const;

function NotificationsPage() {
  return (
    <AppPage className="max-w-3xl">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-end justify-between"
      >
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Inbox</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
            <span className="gradient-text">Notifications</span>
          </h1>
        </div>
        <Button variant="outline" size="sm"><CheckCheck className="size-4" /> Mark all read</Button>
      </motion.div>
      <Card className="rounded-xl overflow-hidden">
        <CardContent className="p-0 divide-y divide-border">
          {MOCK_NOTIFICATIONS.map((n, i) => {
            const Icon = iconFor[n.kind];
            return (
              <motion.div
                key={n.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn("flex gap-4 p-4 hover:bg-accent/40 transition-colors", n.unread && "bg-accent/20")}
              >
                <div className={cn("size-9 rounded-xl grid place-items-center shrink-0", n.kind === "ai" ? "gradient-brand text-white" : "bg-muted")}>
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
              </motion.div>
            );
          })}
        </CardContent>
      </Card>
    </AppPage>
  );
}
