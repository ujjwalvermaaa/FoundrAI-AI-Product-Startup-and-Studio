import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { AmbientField } from "@/components/layout/ambient-field";

/** Consistent page padding + max width for app routes. */
export function AppPage({
  children,
  className,
  wide,
}: {
  children: ReactNode;
  className?: string;
  wide?: boolean;
}) {
  return (
    <div
      className={cn(
        "relative p-5 md:p-8 mx-auto space-y-8",
        wide ? "max-w-[1600px]" : "max-w-[1400px]",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Public marketing page wrapper with ambient atmosphere. */
export function PublicPage({
  children,
  className,
  withAmbient = true,
}: {
  children: ReactNode;
  className?: string;
  withAmbient?: boolean;
}) {
  return (
    <div className={cn("relative min-h-screen bg-background text-foreground overflow-x-hidden", className)}>
      {withAmbient && <AmbientField />}
      <div className="relative z-10">{children}</div>
    </div>
  );
}

export function PageHero({
  eyebrow,
  title,
  description,
  children,
  className,
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("relative pt-32 pb-16 md:pt-36 md:pb-20 overflow-hidden", className)}>
      <div className="pointer-events-none absolute inset-x-0 top-24 mx-auto size-[520px] rounded-full bg-primary/15 blur-[100px]" />
      <div className="relative max-w-3xl mx-auto px-6 text-center">
        {eyebrow && (
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-[10px] font-medium uppercase tracking-[0.2em] text-primary mb-5">
            <span className="size-1.5 rounded-full bg-primary pulse-core" />
            {eyebrow}
          </div>
        )}
        <h1 className="font-display text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight leading-[1.05]">
          {title}
        </h1>
        {description && (
          <p className="text-muted-foreground mt-5 text-base md:text-lg leading-relaxed max-w-2xl mx-auto">
            {description}
          </p>
        )}
        {children}
      </div>
    </section>
  );
}
