import { motion } from "framer-motion";
import founderBot from "@/assets/founder-bot.jpg";

type Size = "sm" | "md" | "lg" | "xl";
const sizeMap: Record<Size, string> = {
  sm: "size-10",
  md: "size-14",
  lg: "size-20",
  xl: "size-32",
};

export function FounderBotAvatar({
  size = "md",
  speaking = false,
  className = "",
}: {
  size?: Size;
  speaking?: boolean;
  className?: string;
}) {
  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      {/* Outer aura */}
      <motion.div
        className="absolute inset-[-25%] rounded-full gradient-brand opacity-30 blur-2xl"
        animate={speaking ? { scale: [1, 1.15, 1], opacity: [0.3, 0.55, 0.3] } : { scale: [1, 1.05, 1], opacity: [0.25, 0.35, 0.25] }}
        transition={{ repeat: Infinity, duration: speaking ? 1.4 : 3.2, ease: "easeInOut" }}
      />
      {/* Ring pulses when speaking */}
      {speaking && (
        <>
          <motion.span
            className="absolute inset-[-8%] rounded-full border border-primary/50"
            animate={{ scale: [1, 1.35], opacity: [0.6, 0] }}
            transition={{ repeat: Infinity, duration: 1.6, ease: "easeOut" }}
          />
          <motion.span
            className="absolute inset-[-8%] rounded-full border border-primary/40"
            animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
            transition={{ repeat: Infinity, duration: 1.6, ease: "easeOut", delay: 0.4 }}
          />
        </>
      )}
      {/* Rotating gradient border */}
      <motion.div
        className={`relative ${sizeMap[size]} rounded-full p-[2px] gradient-brand shadow-glow overflow-hidden`}
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 14, ease: "linear" }}
      >
        <div className="size-full rounded-full overflow-hidden bg-background" style={{ transform: "rotate(-0deg)" }}>
          <motion.img
            src={founderBot}
            alt="Foundr — your AI startup co-founder"
            width={512}
            height={512}
            loading="lazy"
            className="size-full object-cover"
            animate={{ rotate: -360 }}
            transition={{ repeat: Infinity, duration: 14, ease: "linear" }}
          />
        </div>
      </motion.div>
      {/* Live dot */}
      <span className="absolute bottom-0.5 right-0.5 size-3 rounded-full bg-emerald-400 border-2 border-background">
        <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-60" />
      </span>
    </div>
  );
}