import { createFileRoute } from "@tanstack/react-router";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Mail, MessageSquare, MapPin } from "lucide-react";

export const Route = createFileRoute("/contact")({
  component: ContactPage,
});

function ContactPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PublicNav />
      <section className="pt-32 pb-20 max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-10">
        <div>
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground font-medium">Contact</div>
          <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight mt-3">Say hi. We're founders too.</h1>
          <p className="text-muted-foreground mt-4">Product feedback, partnership ideas, or press — we read everything.</p>
          <div className="mt-8 space-y-4 text-sm">
            <div className="flex items-center gap-3"><Mail className="size-4 text-primary" /> hello@foundrai.app</div>
            <div className="flex items-center gap-3"><MessageSquare className="size-4 text-primary" /> Twitter @foundrai</div>
            <div className="flex items-center gap-3"><MapPin className="size-4 text-primary" /> San Francisco · Bangalore</div>
          </div>
        </div>
        <Card><CardContent className="p-6">
          <form className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-3">
              <div className="space-y-1.5"><Label>Name</Label><Input /></div>
              <div className="space-y-1.5"><Label>Email</Label><Input type="email" /></div>
            </div>
            <div className="space-y-1.5"><Label>Subject</Label><Input /></div>
            <div className="space-y-1.5"><Label>Message</Label>
              <textarea className="w-full min-h-32 rounded-md border border-input bg-background px-3 py-2 text-sm" />
            </div>
            <Button className="w-full">Send message</Button>
          </form>
        </CardContent></Card>
      </section>
      <PublicFooter />
    </div>
  );
}