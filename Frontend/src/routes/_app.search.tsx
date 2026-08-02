import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, FileText, FolderKanban, Sparkles } from "lucide-react";
import { MOCK_PROJECTS, MOCK_ARTIFACTS } from "@/lib/mock-data";

export const Route = createFileRoute("/_app/search")({
  component: SearchPage,
});

function SearchPage() {
  const [q, setQ] = useState("");
  const query = q.toLowerCase();
  const projects = MOCK_PROJECTS.filter((p) => !query || p.name.toLowerCase().includes(query) || p.tagline.toLowerCase().includes(query));
  const artifacts = MOCK_ARTIFACTS.filter((a) => !query || a.title.toLowerCase().includes(query));
  return (
    <div className="p-6 md:p-8 max-w-[1000px] mx-auto">
      <div className="mb-6">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Global search</h1>
        <p className="text-muted-foreground text-sm mt-1">Find projects, artifacts, and modules across your studio.</p>
      </div>
      <div className="relative mb-8">
        <Search className="size-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search everything…" className="pl-9 h-11" autoFocus />
      </div>

      <div className="space-y-6">
        <section>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
            <FolderKanban className="size-3" /> Projects <Badge variant="outline" className="text-[10px]">{projects.length}</Badge>
          </div>
          <div className="grid gap-2">
            {projects.map((p) => (
              <Link key={p.id} to="/projects/$id" params={{ id: p.id }}>
                <Card className="hover:border-primary/40 transition-all">
                  <CardContent className="p-3 flex items-center gap-3">
                    <span className="size-8 rounded-md" style={{ background: p.cover }} />
                    <div className="min-w-0">
                      <div className="font-medium truncate">{p.name}</div>
                      <div className="text-xs text-muted-foreground truncate">{p.tagline}</div>
                    </div>
                    <Badge variant="outline" className="ml-auto text-[10px] capitalize">{p.stage}</Badge>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        <section>
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-2">
            <FileText className="size-3" /> Artifacts <Badge variant="outline" className="text-[10px]">{artifacts.length}</Badge>
          </div>
          <div className="grid gap-2">
            {artifacts.map((a) => (
              <Card key={a.id} className="hover:border-primary/40 transition-all">
                <CardContent className="p-3 flex items-center gap-3">
                  <div className="size-8 rounded-md bg-accent grid place-items-center"><Sparkles className="size-3.5 text-primary" /></div>
                  <div className="min-w-0">
                    <div className="font-medium truncate">{a.title}</div>
                    <div className="text-xs text-muted-foreground">{a.type} · {a.words} words · by {a.author}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}