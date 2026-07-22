import { useState, type ReactNode } from "react";
import "./Expander.css";

interface ExpanderProps {
  label: string;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function Expander({ label, children, defaultOpen = false }: ExpanderProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="expander">
      <button type="button" className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-chevron${open ? " expander-chevron-open" : ""}`}>›</span>
        {label}
      </button>
      {open && <div className="expander-body">{children}</div>}
    </div>
  );
}
