import type { ReactNode } from "react";
import { Card } from "../ui/Card";
import "./KpiCard.css";

interface KpiCardProps {
  label: string;
  value: ReactNode;
  accentColor?: string;
}

export function KpiCard({ label, value, accentColor }: KpiCardProps) {
  return (
    <Card className="kpi-card">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value mono" style={accentColor ? { color: accentColor } : undefined}>
        {value}
      </span>
    </Card>
  );
}
