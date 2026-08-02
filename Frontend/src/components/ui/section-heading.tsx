import type { ReactNode } from "react";

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
      <div className="min-w-0">
        {eyebrow && (
          <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground mb-2 font-medium">
            {eyebrow}
          </div>
        )}
        <h2 className="font-display text-2xl md:text-3xl font-semibold tracking-tight">{title}</h2>
        {description && <p className="text-muted-foreground mt-1.5 max-w-2xl">{description}</p>}
      </div>
      {action}
    </div>
  );
}