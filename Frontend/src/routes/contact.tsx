import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { PublicNav, PublicFooter } from "@/components/public-chrome";
import { PublicPage, PageHero } from "@/components/layout/page-shell";
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
    <PublicPage>
      <PublicNav />
      <PageHero
        eyebrow="Contact"
        title="Say hi. We're founders too."
        description="Product feedback, partnership ideas, or press — we read everything."
        className="pb-10 md:pb-12"
      />

      <section className="pb-24 max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-10">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45 }}
          className="space-y-4"
        >
          <div className="text-[10px] uppercase tracking-[0.22em] text-primary/90 font-medium">Reach us</div>
          <div className="space-y-3 text-sm">
            {[
              { icon: Mail, label: "hello@foundrai.app" },
              { icon: MessageSquare, label: "Twitter @foundrai" },
              { icon: MapPin, label: "San Francisco · Bangalore" },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-3 rounded-2xl border border-border/60 bg-card/40 px-4 py-3 glass-depth"
              >
                <div className="size-9 rounded-xl gradient-brand grid place-items-center shadow-glow shrink-0">
                  <Icon className="size-4 text-white" />
                </div>
                <span>{label}</span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45, delay: 0.08 }}
        >
          <Card className="hologram-edge">
            <CardContent className="p-6">
              <form className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-3">
                  <div className="space-y-1.5">
                    <Label>Name</Label>
                    <Input className="rounded-xl" />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Email</Label>
                    <Input type="email" className="rounded-xl" />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label>Subject</Label>
                  <Input className="rounded-xl" />
                </div>
                <div className="space-y-1.5">
                  <Label>Message</Label>
                  <textarea className="w-full min-h-32 rounded-xl border border-input bg-background/60 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
                </div>
                <Button className="w-full rounded-xl shadow-glow">Send message</Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </section>
      <PublicFooter />
    </PublicPage>
  );
}
