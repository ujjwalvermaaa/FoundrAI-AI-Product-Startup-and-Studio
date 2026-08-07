import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { AppPage } from "@/components/layout/page-shell";
import { useCreateProject } from "@/hooks/use-projects";

export const Route = createFileRoute("/_app/projects/new")({
  component: NewProject,
});

function NewProject() {
  const nav = useNavigate();
  const createProject = useCreateProject();
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [ideaBrief, setIdeaBrief] = useState("");
  const [industry, setIndustry] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Please give your startup a working name.");
      return;
    }
    if (!ideaBrief.trim()) {
      setError("Please describe your startup idea.");
      return;
    }

    try {
      const project = await createProject.mutateAsync({
        name: name.trim(),
        idea_brief: ideaBrief.trim(),
        tagline: tagline.trim() || undefined,
        industry: industry.trim() || undefined,
      });
      nav({ to: "/projects/$id", params: { id: project.id } });
    } catch {
      setError("Failed to create project. Please try again.");
    }
  }

  return (
    <AppPage className="max-w-2xl">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <Link
          to="/projects"
          className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-1.5 mb-6"
        >
          <ArrowLeft className="size-3.5" /> Projects
        </Link>
        <div className="mb-8">
          <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">New project</div>
          <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
            Describe your <span className="gradient-text">startup idea</span>
          </h1>
          <p className="text-muted-foreground mt-2">
            FoundrAI will turn it into a validated, planned, and documented company.
          </p>
        </div>
        <Card className="rounded-xl">
          <CardContent className="p-6 space-y-5">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1.5">
                <Label htmlFor="name">Working name *</Label>
                <Input
                  id="name"
                  placeholder="e.g. Orbit"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="tagline">One-liner</Label>
                <Input
                  id="tagline"
                  placeholder="Async standups for distributed teams."
                  value={tagline}
                  onChange={(e) => setTagline(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  placeholder="e.g. Productivity, FinTech, Healthcare…"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="idea-brief">The idea *</Label>
                <Textarea
                  id="idea-brief"
                  rows={7}
                  placeholder="What are you building? Who is it for? Why now?"
                  value={ideaBrief}
                  onChange={(e) => setIdeaBrief(e.target.value)}
                  required
                />
              </div>
              {error && (
                <p className="text-sm text-destructive" role="alert">
                  {error}
                </p>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="ghost" asChild>
                  <Link to="/projects">Cancel</Link>
                </Button>
                <Button type="submit" disabled={createProject.isPending}>
                  {createProject.isPending ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <Sparkles className="size-4" />
                  )}
                  Generate startup
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </AppPage>
  );
}
