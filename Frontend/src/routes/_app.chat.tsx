import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, Lightbulb, LineChart, Wallet, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FounderBotAvatar } from "@/components/founder-bot-avatar";
import { getAccessToken } from "@/lib/api-client";

export const Route = createFileRoute("/_app/chat")({ component: ChatPage });

const API_URL = (import.meta.env.VITE_API_URL as string) || "http://localhost:8000/api/v1";

type Msg = { id: string; role: "user" | "bot"; text: string; ts: number };

const STARTERS = [
  { icon: Lightbulb, label: "Validate my idea", prompt: "I want to build an async standup tool for AI teams. How do I validate it in 2 weeks?" },
  { icon: LineChart, label: "Estimate my TAM", prompt: "Help me size the TAM/SAM/SOM for a carbon-negative last-mile delivery product." },
  { icon: Wallet, label: "Model my pricing", prompt: "What pricing model should I choose for a per-seat SaaS aimed at 10–200 person teams?" },
  { icon: FileText, label: "Draft my pitch", prompt: "Draft me a 60-second elevator pitch for an ambient clinical scribe for outpatient practices." },
];

async function streamChat(
  message: string,
  history: { role: string; content: string }[],
  onToken: (t: string) => void,
  onDone: () => void,
  onError: (e: string) => void,
) {
  const token = getAccessToken();
  if (!token) { onError("Not authenticated"); return; }

  let res: Response;
  try {
    res = await fetch(`${API_URL}/chat/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ message, history }),
    });
  } catch {
    onError("Cannot reach server. Is the backend running?");
    return;
  }

  if (!res.ok || !res.body) {
    onError(`Server error (${res.status})`);
    return;
  }

  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      try {
        const data = JSON.parse(line.slice(6));
        if (data.token) onToken(data.token);
        if (data.done) { onDone(); return; }
        if (data.error) { onError(data.error); return; }
      } catch { /* ignore malformed */ }
    }
  }
  onDone();
}

function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([{
    id: "greet", role: "bot", ts: Date.now(),
    text: "Hey — I'm Foundr, your AI co-founder. Tell me about the startup you're building, or pick a starter below. I'll help you validate, plan and pitch it.",
  }]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const botMsgIdRef = useRef<string | null>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || typing) return;

    const userMsg: Msg = { id: `u_${Date.now()}`, role: "user", text: trimmed, ts: Date.now() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setTyping(true);

    // Build history for context (last 10 exchanges)
    const history = messages.slice(-20).map((m) => ({
      role: m.role === "user" ? "user" : "assistant",
      content: m.text,
    }));

    // Create placeholder bot message for streaming
    const botId = `b_${Date.now()}`;
    botMsgIdRef.current = botId;
    setMessages((m) => [...m, { id: botId, role: "bot", text: "", ts: Date.now() }]);

    await streamChat(
      trimmed,
      history,
      (token) => {
        setMessages((m) =>
          m.map((msg) =>
            msg.id === botId ? { ...msg, text: msg.text + token } : msg,
          ),
        );
      },
      () => {
        setTyping(false);
        botMsgIdRef.current = null;
      },
      (err) => {
        setMessages((m) =>
          m.map((msg) =>
            msg.id === botId
              ? { ...msg, text: `⚠️ ${err}` }
              : msg,
          ),
        );
        setTyping(false);
        botMsgIdRef.current = null;
      },
    );
  };

  return (
    <div className="relative min-h-[calc(100vh-56px)] flex flex-col">
      <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none" />
      <div className="absolute top-20 left-1/2 -translate-x-1/2 size-[600px] rounded-full bg-primary/10 blur-[120px] pointer-events-none" />

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
        className="relative border-b border-border/60 bg-background/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 py-5 flex items-center gap-4">
          <motion.div initial={{ scale: 0, rotate: -30 }} animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 180, damping: 14, delay: 0.15 }}>
            <FounderBotAvatar size="lg" speaking={typing} />
          </motion.div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-2xl font-semibold tracking-tight">
                <span className="gradient-text">Foundr</span>
              </h1>
              <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-emerald-500/40 text-emerald-500 bg-emerald-500/5 gap-1">
                <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" /> Online
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">Your always-on AI co-founder. Ask anything about your startup.</p>
          </div>
        </div>
      </motion.div>

      {/* Messages */}
      <div ref={scrollRef} className="relative flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div key={m.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
                {m.role === "bot" && <div className="shrink-0 mt-1"><FounderBotAvatar size="sm" /></div>}
                <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-primary text-primary-foreground rounded-br-sm"
                    : "surface-panel rounded-tl-sm"
                }`}>
                  {m.text || (m.role === "bot" && typing && m.id === botMsgIdRef.current
                    ? <span className="inline-flex items-center gap-1">
                        {[0,1,2].map((i) => (
                          <motion.span key={i} className="size-1.5 rounded-full bg-primary inline-block"
                            animate={{ y: [0,-4,0], opacity: [0.4,1,0.4] }}
                            transition={{ repeat: Infinity, duration: 0.9, delay: i*0.15 }} />
                        ))}
                      </span>
                    : "")}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Starter prompts */}
          {messages.length === 1 && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="pt-4">
              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-3">Try a starter</div>
              <div className="grid sm:grid-cols-2 gap-2">
                {STARTERS.map((s) => (
                  <button key={s.label} onClick={() => send(s.prompt)}
                    className="text-left p-3 rounded-xl border border-border/60 bg-card/40 hover:border-primary/40 hover:bg-accent/40 transition-all group">
                    <div className="flex items-center gap-2 font-medium text-sm">
                      <s.icon className="size-4 text-primary" />{s.label}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1 line-clamp-2">{s.prompt}</div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Composer */}
      <div className="relative border-t border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <Card className="p-2 flex items-end gap-2 shadow-glow">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
              placeholder="Ask Foundr anything about your startup…"
              rows={1}
              className="flex-1 resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-muted-foreground max-h-40"
            />
            <Button size="sm" onClick={() => send(input)} disabled={!input.trim() || typing} className="h-9 gap-1.5">
              {typing ? <Loader2 className="size-3.5 animate-spin" /> : <Send className="size-3.5" />}
              {typing ? "Thinking…" : "Send"}
            </Button>
          </Card>
          <div className="text-[11px] text-muted-foreground mt-2 flex items-center gap-1.5">
            <Sparkles className="size-3 text-primary" />
            Powered by Ollama · Foundr has full context of your workspace
          </div>
        </div>
      </div>
    </div>
  );
}
