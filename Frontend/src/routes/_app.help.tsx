import { createFileRoute, Link } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { LifeBuoy, MessageCircle, Mail, BookOpen } from "lucide-react";
import { motion } from "framer-motion";
import { AppPage } from "@/components/layout/page-shell";

export const Route = createFileRoute("/_app/help")({
  component: HelpPage,
});

const FAQ = [
  ["How are AI credits calculated?", "Each module generation, chat message and document export consumes credits based on the model and length of the output. You can see per-action cost in the AI Gateway logs."],
  ["Can I invite my team?", "Team seats are available on the Studio plan. You can invite up to 10 collaborators and assign roles per project."],
  ["Where is my data stored?", "Your workspace lives on encrypted infrastructure in the region you selected during onboarding. We never train foundation models on your content."],
  ["Can I export my artifacts?", "Yes. Every artifact can be exported to PDF, Markdown, DOCX or PPTX. Investor decks also export to Figma-ready formats."],
  ["How do I cancel?", "Head to Billing → Manage plan → Cancel. You keep access until the end of the billing period."],
];

function HelpPage() {
  return (
    <AppPage className="max-w-5xl">
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
        <div className="text-xs uppercase tracking-[0.18em] text-primary/90 font-medium">Support</div>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mt-1">
          How can we <span className="gradient-text">help</span>?
        </h1>
        <p className="text-muted-foreground mt-2">Answers in seconds, or a real human within an hour.</p>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { icon: MessageCircle, title: "Chat with Foundr", desc: "Ask your AI co-founder anything about the product or your startup.", cta: <Button size="sm" variant="outline" className="mt-3" asChild><Link to="/chat">Open chat</Link></Button> },
          { icon: BookOpen, title: "Browse docs", desc: "Guides, playbooks and integration references.", cta: <Button size="sm" variant="outline" className="mt-3" asChild><Link to="/docs">Read docs</Link></Button> },
          { icon: Mail, title: "Email us", desc: "Priority reply for Founder & Studio plans.", cta: <Button size="sm" variant="outline" className="mt-3" asChild><a href="mailto:support@foundrai.com">support@foundrai.com</a></Button> },
        ].map((item, i) => (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="rounded-xl h-full">
              <CardContent className="p-5">
                <item.icon className="size-5 text-primary" />
                <div className="font-display font-semibold mt-3">{item.title}</div>
                <p className="text-sm text-muted-foreground mt-1">{item.desc}</p>
                {item.cta}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Card className="rounded-xl">
        <CardHeader><CardTitle className="font-display flex items-center gap-2"><LifeBuoy className="size-4 text-primary" /> Contact support</CardTitle></CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-4">
          <Input placeholder="Subject" />
          <Input placeholder="Related project (optional)" />
          <Textarea placeholder="Describe your issue…" className="md:col-span-2 min-h-32" />
          <Button className="md:col-span-2 md:w-fit">Send message</Button>
        </CardContent>
      </Card>

      <div>
        <h2 className="font-display text-xl font-semibold mb-3">Frequently asked</h2>
        <Accordion type="single" collapsible className="w-full">
          {FAQ.map(([q, a], i) => (
            <AccordionItem key={i} value={`i-${i}`}>
              <AccordionTrigger>{q}</AccordionTrigger>
              <AccordionContent>{a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </AppPage>
  );
}
