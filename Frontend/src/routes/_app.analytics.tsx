import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AI_ACTIVITY, MOCK_PROJECTS } from "@/lib/mock-data";
import { AreaChart, Area, ResponsiveContainer, XAxis, YAxis, Tooltip, BarChart, Bar, LineChart, Line, CartesianGrid } from "recharts";
import { Activity, Sparkles, Target, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/_app/analytics")({
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const stats = [
    { label: "Generations this month", value: "1,284", change: "+18%", icon: Sparkles },
    { label: "Artifacts created", value: "342", change: "+12%", icon: Activity },
    { label: "Modules completed", value: "26", change: "+6", icon: Target },
    { label: "Startup maturity", value: "72%", change: "+9pts", icon: TrendingUp },
  ];

  const heatmap = Array.from({ length: 7 * 12 }, (_, i) => Math.round(Math.random() * 5));

  return (
    <div className="p-6 md:p-8 max-w-[1400px] mx-auto">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Insights</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">Analytics</h1>
        <p className="text-muted-foreground mt-1">How your ventures are progressing across the studio.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground">{s.label}</div>
                <s.icon className="size-3.5 text-primary" />
              </div>
              <div className="font-display text-3xl font-semibold mt-2">{s.value}</div>
              <Badge variant="outline" className="mt-2 text-[10px] text-emerald-500 border-emerald-500/30 bg-emerald-500/5">{s.change}</Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="font-display font-semibold">AI generations</div>
                <div className="text-xs text-muted-foreground">Last 30 days</div>
              </div>
              <Badge variant="outline" className="text-[10px]">+18%</Badge>
            </div>
            <div className="h-64">
              <ResponsiveContainer>
                <AreaChart data={AI_ACTIVITY}>
                  <defs>
                    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="oklch(0.7 0.19 280)" stopOpacity={0.5} />
                      <stop offset="100%" stopColor="oklch(0.7 0.19 280)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(1 0 0 / 6%)" />
                  <XAxis dataKey="day" fontSize={10} stroke="currentColor" opacity={0.4} />
                  <YAxis fontSize={10} stroke="currentColor" opacity={0.4} />
                  <Tooltip contentStyle={{ background: "oklch(0.18 0.025 265)", border: "1px solid oklch(1 0 0 / 8%)", borderRadius: 8, fontSize: 12 }} />
                  <Area type="monotone" dataKey="generations" stroke="oklch(0.7 0.19 280)" fill="url(#g1)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="font-display font-semibold mb-1">Project progress</div>
            <div className="text-xs text-muted-foreground mb-4">Aggregate completion</div>
            <div className="h-64">
              <ResponsiveContainer>
                <BarChart data={MOCK_PROJECTS.map((p) => ({ name: p.name, progress: p.progress }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(1 0 0 / 6%)" />
                  <XAxis dataKey="name" fontSize={10} stroke="currentColor" opacity={0.4} />
                  <YAxis fontSize={10} stroke="currentColor" opacity={0.4} />
                  <Tooltip contentStyle={{ background: "oklch(0.18 0.025 265)", border: "1px solid oklch(1 0 0 / 8%)", borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="progress" fill="oklch(0.7 0.19 280)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <div className="font-display font-semibold mb-1">Activity heatmap</div>
            <div className="text-xs text-muted-foreground mb-4">Sessions × time of day</div>
            <div className="grid grid-cols-12 gap-1">
              {heatmap.map((v, i) => (
                <div
                  key={i}
                  className="aspect-square rounded"
                  style={{ background: `color-mix(in oklab, oklch(0.7 0.19 280) ${v * 20}%, oklch(0.22 0.025 265))` }}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="font-display font-semibold mb-1">Edits vs generations</div>
            <div className="text-xs text-muted-foreground mb-4">Ratio trend</div>
            <div className="h-52">
              <ResponsiveContainer>
                <LineChart data={AI_ACTIVITY}>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(1 0 0 / 6%)" />
                  <XAxis dataKey="day" fontSize={10} stroke="currentColor" opacity={0.4} />
                  <YAxis fontSize={10} stroke="currentColor" opacity={0.4} />
                  <Tooltip contentStyle={{ background: "oklch(0.18 0.025 265)", border: "1px solid oklch(1 0 0 / 8%)", borderRadius: 8, fontSize: 12 }} />
                  <Line type="monotone" dataKey="generations" stroke="oklch(0.7 0.19 280)" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="edits" stroke="oklch(0.75 0.17 155)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}