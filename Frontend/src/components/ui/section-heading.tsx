import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
  className,
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-end justify-between gap-4 mb-6", className)}>
      <div className="min-w-0">
        {eyebrow && (
          <div className="inline-flex items-center gap-2 text-[10px] uppercase tracking-[0.22em] text-primary/90 mb-2.5 font-medium">
            <span className="h-px w-4 bg-primary/60" />
            {eyebrow}
          </div>
        )}
        <h2 className="font-display text-2xl md:text-3xl font-semibold tracking-tight">{title}</h2>
        {description && <p className="text-muted-foreground mt-1.5 max-w-2xl text-sm md:text-base">{description}</p>}
      </div>
      {action}
    </div>
  );
}
