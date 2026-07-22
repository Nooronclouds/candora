import type { HTMLAttributes, ReactNode } from "react";
import "./Card.css";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  accent?: "topaze" | "sage" | "cassis" | "none";
}

export function Card({ children, accent = "none", className, ...rest }: CardProps) {
  const classes = ["card", accent !== "none" ? `card-accent-${accent}` : "", className]
    .filter(Boolean)
    .join(" ");
  return (
    <div className={classes} {...rest}>
      {children}
    </div>
  );
}
