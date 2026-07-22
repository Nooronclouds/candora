import { Mascot, type MascotState } from "./Mascot";
import "./MascotCallout.css";

interface MascotCalloutProps {
  state: MascotState;
  text: string;
  tone?: "neutral" | "confident" | "low-confidence" | "conflict";
}

export function MascotCallout({ state, text, tone = "neutral" }: MascotCalloutProps) {
  return (
    <div className={`mascot-callout mascot-callout-${tone}`}>
      <Mascot state={state} size={64} />
      <span className="mascot-callout-text">{text}</span>
    </div>
  );
}
