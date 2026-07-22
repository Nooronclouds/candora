import type { ReactNode } from "react";
import "./Badge.css";

type Tone = "confident" | "low-confidence" | "conflict" | "info" | "neutral";

interface BadgeProps {
  tone: Tone;
  children: ReactNode;
}

const ICONS: Record<Tone, string> = {
  confident: "✓",
  "low-confidence": "▲",
  conflict: "✕",
  info: "ⓘ",
  neutral: "•",
};

export function Badge({ tone, children }: BadgeProps) {
  return (
    <span className={`badge badge-${tone}`}>
      <span aria-hidden="true">{ICONS[tone]}</span>
      {children}
    </span>
  );
}
