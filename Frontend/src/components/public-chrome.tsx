import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Github,
  Twitter,
  Linkedin,
  MessageCircle,
  Activity,
  Map,
  LayoutGrid,
  Target,
  ListChecks,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";

const FEATURES = [
  { to: "/chat", icon: MessageCircle, title: "AI Copilot", desc: "Context-aware co-founder with project memory." },
  { to: "/health", icon: Activity, title: "Health Score", desc: "Live diagnostic across 6 startup dimensions." },
  { to: "/roadmap", icon: Map, title: "AI Roadmap", desc: "8-week plan from validation to seed." },
  { to: "/canvas", icon: LayoutGrid, title: "Business Canvas", desc: "Interactive 9-block canvas, always in sync." },
  { to: "/competitors", icon: Target, title: "Competitor Intel", desc: "Track releases, pricing and positioning." },
  { to: "/checklist", icon: ListChecks, title: "Startup Checklist", desc: "Every step from idea to seed round." },
];

export function PublicNav() {
  return (
    <header className="fixed top-0 inset-x-0 z-40 px-3 pt-3 md:px-6">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative mx-auto max-w-7xl overflow-hidden rounded-2xl glass-depth hologram-edge"
      >
        <div className="scan-line absolute inset-0 opacity-20" />
        <div className="relative flex h-14 items-center gap-6 px-4 md:px-5">
          <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
            <div className="relative size-8">
              <div className="absolute inset-0 rounded-lg pulse-core bg-primary/30 blur-md" />
              <div className="relative size-8 rounded-lg overflow-hidden shadow-glow ring-1 ring-primary/30">
                <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
              </div>
            </div>
            <span className="font-display text-base font-semibold tracking-tight">FoundrAI</span>
            <span className="hidden lg:inline-flex ml-0.5 text-[9px] uppercase tracking-[0.16em] px-1.5 py-0.5 rounded-md bg-primary/10 text-primary border border-primary/20">
              Beta
            </span>
          </Link>

          <NavigationMenu className="hidden md:flex">
            <NavigationMenuList>
              <NavigationMenuItem>
                <NavigationMenuTrigger className="bg-transparent text-sm h-9 rounded-xl">Product</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <div className="grid grid-cols-2 gap-1 p-3 w-[520px]">
                    {FEATURES.map((f) => (
                      <NavigationMenuLink asChild key={f.to}>
                        <Link
                          to={f.to}
                          className="flex items-start gap-3 rounded-xl p-2.5 hover:bg-accent transition-colors"
                        >
                          <div className="size-9 rounded-lg gradient-brand grid place-items-center shrink-0 shadow-glow">
                            <f.icon className="size-4 text-white" />
                          </div>
                          <div>
                            <div className="text-sm font-medium">{f.title}</div>
                            <div className="text-xs text-muted-foreground">{f.desc}</div>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                    ))}
                  </div>
                </NavigationMenuContent>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>

          <nav className="hidden md:flex items-center gap-5 text-sm text-muted-foreground">
            <Link to="/pricing" className="hover:text-foreground transition-colors">Pricing</Link>
            <Link to="/docs" className="hover:text-foreground transition-colors">Docs</Link>
            <Link to="/about" className="hover:text-foreground transition-colors">About</Link>
            <Link to="/contact" className="hover:text-foreground transition-colors">Contact</Link>
          </nav>
          <div className="ml-auto flex items-center gap-1.5">
            <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex rounded-xl">
              <Link to="/chat">
                <MessageCircle className="size-3.5" /> Ask Foundr
              </Link>
            </Button>
            <Button variant="ghost" size="sm" asChild className="rounded-xl">
              <Link to="/auth/login">Sign in</Link>
            </Button>
            <Button size="sm" asChild className="rounded-xl shadow-glow">
              <Link to="/auth/signup">
                <Zap className="size-3.5" /> Start free <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </motion.div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="relative mt-4">
      <div className="pointer-events-none absolute inset-0 mesh-ambient opacity-30" />
      <div className="relative max-w-7xl mx-auto px-6 py-14 grid md:grid-cols-4 gap-8">
        <div>
          <Link to="/" className="flex items-center gap-2.5">
            <div className="size-8 rounded-lg overflow-hidden shadow-glow ring-1 ring-primary/30 shrink-0">
              <img src="/founder-bot.jpg" alt="FoundrAI" className="size-full object-cover" />
            </div>
            <span className="font-display font-semibold">FoundrAI</span>
          </Link>
          <p className="text-sm text-muted-foreground mt-3 max-w-xs leading-relaxed">
            The AI-native workspace for founders. Turn an idea into a company, module by module.
          </p>
          <div className="flex gap-2 mt-5">
            {[Twitter, Github, Linkedin].map((Icon, i) => (
              <a
                key={i}
                className="size-9 grid place-items-center rounded-xl bg-card/40 text-muted-foreground hover:text-foreground hover:shadow-glow transition-all ring-1 ring-white/5"
              >
                <Icon className="size-3.5" />
              </a>
            ))}
          </div>
        </div>
        <FooterCol title="Product" links={[["Modules", "/pricing"], ["Workspace", "/dashboard"], ["Pricing", "/pricing"], ["Chat with Foundr", "/chat"]]} />
        <FooterCol title="Company" links={[["About", "/about"], ["Contact", "/contact"], ["Careers", "/about"], ["Changelog", "/about"]]} />
        <FooterCol title="Legal" links={[["Privacy", "/privacy"], ["Terms", "/terms"], ["Security", "/privacy"], ["DPA", "/terms"]]} />
      </div>
      <div className="relative">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
          <span>© {new Date().getFullYear()} FoundrAI Inc. All rights reserved.</span>
          <span className="font-mono tracking-wider uppercase text-[10px]">Neural Studio · Made in India</span>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-[0.2em] text-primary/80 font-medium mb-3">{title}</div>
      <ul className="space-y-2.5 text-sm">
        {links.map(([l, to]) => (
          <li key={l}>
            <Link to={to} className="text-foreground/75 hover:text-primary transition-colors">
              {l}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
