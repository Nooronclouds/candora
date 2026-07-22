import type { ReactNode } from "react";
import "./EmptyState.css";

interface EmptyStateProps {
  mascot: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ mascot, title, description, action }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-mascot">{mascot}</div>
      <h3>{title}</h3>
      <p className="empty-state-desc">{description}</p>
      {action}
    </div>
  );
}
