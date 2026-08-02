import { Link } from "@tanstack/react-router";
import { Sparkles, ArrowRight, Github, Twitter, Linkedin, MessageCircle, Activity, Map, LayoutGrid, Target, ListChecks, Zap } from "lucide-react";
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
    <header className="fixed top-0 inset-x-0 z-40 backdrop-blur-xl bg-background/70 border-b border-border/60">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-8">
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <div className="size-8 rounded-lg gradient-brand grid place-items-center shadow-glow">
            <Sparkles className="size-4 text-white" />
          </div>
          <span className="font-display text-base font-semibold tracking-tight">FoundrAI</span>
          <span className="hidden lg:inline-flex ml-1 text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">Beta</span>
        </Link>

        <NavigationMenu className="hidden md:flex">
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger className="bg-transparent text-sm h-9">Product</NavigationMenuTrigger>
              <NavigationMenuContent>
                <div className="grid grid-cols-2 gap-1 p-3 w-[520px]">
                  {FEATURES.map((f) => (
                    <NavigationMenuLink asChild key={f.to}>
                      <Link to={f.to} className="flex items-start gap-3 rounded-md p-2.5 hover:bg-accent transition-colors">
                        <div className="size-8 rounded-md gradient-brand grid place-items-center shrink-0"><f.icon className="size-4 text-white" /></div>
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

        <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
          <Link to="/pricing" className="hover:text-foreground transition-colors">Pricing</Link>
          <Link to="/docs" className="hover:text-foreground transition-colors">Docs</Link>
          <Link to="/about" className="hover:text-foreground transition-colors">About</Link>
          <Link to="/contact" className="hover:text-foreground transition-colors">Contact</Link>
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
            <Link to="/chat"><MessageCircle className="size-3.5" /> Ask Foundr</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild><Link to="/auth/login">Sign in</Link></Button>
          <Button size="sm" asChild className="shadow-glow"><Link to="/auth/signup"><Zap className="size-3.5" /> Start free <ArrowRight className="size-3.5" /></Link></Button>
        </div>
      </div>
    </header>
  );
}

export function PublicFooter() {
  return (
    <footer className="border-t border-border/60 bg-sidebar/40">
      <div className="max-w-7xl mx-auto px-6 py-14 grid md:grid-cols-4 gap-8">
        <div>
          <Link to="/" className="flex items-center gap-2">
            <div className="size-7 rounded-md gradient-brand grid place-items-center"><Sparkles className="size-3.5 text-white" /></div>
            <span className="font-display font-semibold">FoundrAI</span>
          </Link>
          <p className="text-sm text-muted-foreground mt-3 max-w-xs">The AI-native workspace for founders. Turn an idea into a company, module by module.</p>
          <div className="flex gap-2 mt-4">
            <a className="size-8 grid place-items-center rounded-md border border-border hover:border-primary/50 hover:text-foreground text-muted-foreground transition-colors"><Twitter className="size-3.5" /></a>
            <a className="size-8 grid place-items-center rounded-md border border-border hover:border-primary/50 hover:text-foreground text-muted-foreground transition-colors"><Github className="size-3.5" /></a>
            <a className="size-8 grid place-items-center rounded-md border border-border hover:border-primary/50 hover:text-foreground text-muted-foreground transition-colors"><Linkedin className="size-3.5" /></a>
          </div>
        </div>
        <FooterCol title="Product" links={[["Modules", "/pricing"], ["Workspace", "/dashboard"], ["Pricing", "/pricing"], ["Chat with Foundr", "/chat"]]} />
        <FooterCol title="Company" links={[["About", "/about"], ["Contact", "/contact"], ["Careers", "/about"], ["Changelog", "/about"]]} />
        <FooterCol title="Legal" links={[["Privacy", "/privacy"], ["Terms", "/terms"], ["Security", "/privacy"], ["DPA", "/terms"]]} />
      </div>
      <div className="border-t border-border/60">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
          <span>© {new Date().getFullYear()} FoundrAI Inc. All rights reserved.</span>
          <span>Made in India 🇮🇳</span>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-muted-foreground font-medium mb-3">{title}</div>
      <ul className="space-y-2 text-sm">
        {links.map(([l, to]) => (
          <li key={l}><Link to={to} className="text-foreground/80 hover:text-foreground">{l}</Link></li>
        ))}
      </ul>
    </div>
  );
}