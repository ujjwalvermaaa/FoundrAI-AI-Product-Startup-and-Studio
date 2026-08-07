/** Soft atmospheric depth behind the app chrome — decorative only. */
export function AmbientField() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="absolute inset-0 mesh-ambient" />
      <div className="absolute inset-0 grid-bg grid-fade opacity-[0.35] dark:opacity-[0.22]" />
      <div className="absolute -left-24 top-1/4 size-[420px] rounded-full bg-primary/15 blur-[100px] float-y" />
      <div
        className="absolute -right-16 bottom-0 size-[360px] rounded-full bg-brand-glow/10 blur-[90px] float-y"
        style={{ animationDelay: "-3s" }}
      />
      <div className="absolute left-1/2 top-0 h-px w-[60%] -translate-x-1/2 bg-gradient-to-r from-transparent via-primary/40 to-transparent" />
    </div>
  );
}
