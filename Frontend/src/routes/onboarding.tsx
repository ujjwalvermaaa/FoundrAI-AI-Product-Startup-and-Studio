import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Sparkles, Rocket, Building2, Users, Target, PartyPopper } from "lucide-react";

export const Route = createFileRoute("/onboarding")({
  component: Onboarding,
});

const STEPS = ["Welcome", "About you", "Stage", "Focus", "Ready"] as const;

function Onboarding() {
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [stage, setStage] = useState<string>("");
  const [focus, setFocus] = useState<string[]>([]);
  const navigate = useNavigate();
  const total = STEPS.length;

  const next = () => setStep((s) => Math.min(s + 1, total - 1));
  const back = () => setStep((s) => Math.max(s - 1, 0));

  return (
    <div className="min-h-screen bg-background text-foreground grid place-items-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-20" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 size-[700px] rounded-full bg-primary/15 blur-[140px]" />
      <div className="relative w-full max-w-lg">
        <div className="flex items-center gap-2 mb-6 justify-center">
          <div className="size-8 rounded-lg overflow-hidden shadow-glow shrink-0">
            <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
          </div>
          <span className="font-display font-semibold text-lg">FoundrAI</span>
        </div>
        <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
          <span>Step {step + 1} of {total}</span>
          <span>{STEPS[step]}</span>
        </div>
        <Progress value={((step + 1) / total) * 100} className="h-1 mb-6" />

        <Card>
          <CardContent className="p-8 min-h-[380px] flex flex-col">
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
                className="flex-1"
              >
                {step === 0 && <>
                  <Rocket className="size-8 text-primary mb-3" />
                  <h1 className="font-display text-3xl font-semibold tracking-tight">Welcome to FoundrAI.</h1>
                  <p className="text-muted-foreground mt-2">Let's set up your studio in under 60 seconds. We'll personalise Foundr around your goals.</p>
                </>}
                {step === 1 && <>
                  <Building2 className="size-8 text-primary mb-3" />
                  <h1 className="font-display text-2xl font-semibold tracking-tight">About you</h1>
                  <div className="mt-6 space-y-4">
                    <div className="space-y-1.5"><Label>Your name</Label><Input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Alex Morgan" /></div>
                    <div className="space-y-1.5"><Label>Role</Label><Input value={role} onChange={(e)=>setRole(e.target.value)} placeholder="Solo founder / CTO / PM" /></div>
                  </div>
                </>}
                {step === 2 && <>
                  <Users className="size-8 text-primary mb-3" />
                  <h1 className="font-display text-2xl font-semibold tracking-tight">Where are you today?</h1>
                  <div className="mt-6 grid grid-cols-2 gap-2">
                    {["Just an idea","Validating","Building MVP","Launched","Growing"].map((s) => (
                      <button key={s} onClick={()=>setStage(s)} className={`p-3 rounded-xl border text-sm text-left transition-all ${stage===s?"border-primary bg-primary/5":"border-border hover:border-primary/40"}`}>{s}</button>
                    ))}
                  </div>
                </>}
                {step === 3 && <>
                  <Target className="size-8 text-primary mb-3" />
                  <h1 className="font-display text-2xl font-semibold tracking-tight">What matters most right now?</h1>
                  <p className="text-sm text-muted-foreground mt-1">Pick up to 3. Foundr will bias recommendations toward these.</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {["Validation","Positioning","Roadmap","Architecture","Financials","Fundraising","Marketing","Hiring"].map((f) => {
                      const on = focus.includes(f);
                      return (
                        <button key={f} onClick={()=>setFocus(on ? focus.filter(x=>x!==f) : focus.length<3?[...focus,f]:focus)}
                          className={`px-3 py-1.5 rounded-full text-sm border transition-all ${on?"gradient-brand text-white border-transparent":"border-border hover:border-primary/40"}`}>{f}</button>
                      );
                    })}
                  </div>
                </>}
                {step === 4 && <>
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }} className="size-16 rounded-full gradient-brand grid place-items-center shadow-glow mb-4">
                    <PartyPopper className="size-7 text-white" />
                  </motion.div>
                  <h1 className="font-display text-3xl font-semibold tracking-tight">You're set{name?`, ${name.split(" ")[0]}`:""}.</h1>
                  <p className="text-muted-foreground mt-2">Your studio is personalised. Let's meet Foundr and start your first project.</p>
                </>}
              </motion.div>
            </AnimatePresence>

            <div className="mt-6 flex items-center gap-2">
              <Button variant="ghost" onClick={back} disabled={step===0}>Back</Button>
              {step < total-1 && <Button className="ml-auto" onClick={next}>Continue</Button>}
              {step === total-1 && (
                <>
                  <Button variant="outline" className="ml-auto" asChild><Link to="/dashboard">Skip to dashboard</Link></Button>
                  <Button onClick={()=>navigate({ to: "/chat" })}>Meet Foundr</Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}