import "./Mascot.css";

export type MascotState =
  | "hello"
  | "searching"
  | "thinking"
  | "reading"
  | "happy"
  | "conflict"
  | "empty";

interface MascotProps {
  state?: MascotState;
  size?: number;
  className?: string;
}

/**
 * Original duck mascot (not Psyduck) — round tuft of three feathers instead of
 * a swirl, and a distinct silhouette/palette, while keeping the "endearingly
 * confused researcher" spirit the moodboard called for.
 */
export function Mascot({ state = "hello", size = 96, className }: MascotProps) {
  return (
    <svg
      className={["mascot", className].filter(Boolean).join(" ")}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label={`Candora mascot: ${state}`}
    >
      <ellipse cx="60" cy="108" rx="30" ry="6" fill="var(--color-cassis)" opacity="0.08" />
      <DuckBody state={state} />
      <DuckFace state={state} />
      <StateProp state={state} />
    </svg>
  );
}

function DuckBody({ state }: { state: MascotState }) {
  const leaning = state === "thinking" || state === "conflict";
  return (
    <g transform={leaning ? "rotate(-4 60 70)" : undefined}>
      {/* feet */}
      <path d="M48 96 L44 104 L52 104 Z" fill="var(--color-topaze)" />
      <path d="M72 96 L68 104 L76 104 Z" fill="var(--color-topaze)" />
      {/* body */}
      <ellipse cx="60" cy="76" rx="26" ry="24" fill="var(--color-duck)" stroke="var(--color-cassis)" strokeWidth="2.5" />
      {/* wing */}
      <path
        d="M78 68 Q92 72 86 90 Q76 92 74 78 Z"
        fill="var(--color-duck-shade)"
        stroke="var(--color-cassis)"
        strokeWidth="2"
      />
      {/* head */}
      <circle cx="52" cy="42" r="26" fill="var(--color-duck)" stroke="var(--color-cassis)" strokeWidth="2.5" />
      {/* feather tuft */}
      <path d="M42 20 L40 8" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M50 16 L50 4" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M58 20 L62 9" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" />
    </g>
  );
}

function DuckFace({ state }: { state: MascotState }) {
  if (state === "happy") {
    return (
      <g>
        <path d="M40 40 Q44 36 48 40" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M54 40 Q58 36 62 40" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M38 50 Q52 60 64 48" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M34 46 L44 48 L48 42" fill="var(--color-topaze)" stroke="var(--color-cassis)" strokeWidth="2" />
      </g>
    );
  }
  if (state === "conflict") {
    return (
      <g>
        <circle cx="43" cy="40" r="3.4" fill="var(--color-cassis)" />
        <circle cx="61" cy="40" r="3.4" fill="var(--color-cassis)" />
        <path d="M37 32 L48 35" stroke="var(--color-cassis)" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M67 32 L56 35" stroke="var(--color-cassis)" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M44 54 Q52 50 60 54" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M34 46 L44 48 L48 42" fill="var(--color-topaze)" stroke="var(--color-cassis)" strokeWidth="2" />
      </g>
    );
  }
  if (state === "empty") {
    return (
      <g>
        <path d="M39 41 Q43 45 47 41" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M57 41 Q61 45 65 41" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M44 54 Q52 51 60 54" stroke="var(--color-cassis)" strokeWidth="2.2" strokeLinecap="round" fill="none" />
        <path d="M34 46 L44 48 L48 42" fill="var(--color-topaze)" stroke="var(--color-cassis)" strokeWidth="2" />
      </g>
    );
  }
  /* hello / searching / thinking / reading share the default curious face */
  return (
    <g>
      <circle cx="43" cy="40" r="3.4" fill="var(--color-cassis)" />
      <circle cx="61" cy="40" r="3.4" fill="var(--color-cassis)" />
      <path d="M46 52 Q52 56 58 52" stroke="var(--color-cassis)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <path d="M34 46 L44 48 L48 42" fill="var(--color-topaze)" stroke="var(--color-cassis)" strokeWidth="2" />
    </g>
  );
}

function StateProp({ state }: { state: MascotState }) {
  switch (state) {
    case "searching":
      return (
        <g transform="translate(78 56) rotate(20)">
          <circle cx="0" cy="0" r="10" fill="none" stroke="var(--color-prussian)" strokeWidth="3.5" />
          <line x1="7" y1="7" x2="16" y2="16" stroke="var(--color-prussian)" strokeWidth="4" strokeLinecap="round" />
        </g>
      );
    case "thinking":
      return (
        <text x="76" y="30" fontSize="20" fontWeight="700" fill="var(--color-prussian)">
          ?
        </text>
      );
    case "reading":
      return (
        <g transform="translate(28 68)">
          <rect x="0" y="0" width="26" height="18" rx="2" fill="var(--color-cool-blue)" stroke="var(--color-prussian)" strokeWidth="2" />
          <line x1="13" y1="2" x2="13" y2="16" stroke="var(--color-prussian)" strokeWidth="1.5" />
        </g>
      );
    case "conflict":
      return (
        <text x="80" y="34" fontSize="22" fontWeight="700" fill="var(--color-cassis)">
          !
        </text>
      );
    case "empty":
      return (
        <g transform="translate(38 92)">
          <path d="M0 0 L44 0 L38 16 L6 16 Z" fill="none" stroke="var(--color-cassis)" strokeWidth="2.5" opacity="0.5" />
        </g>
      );
    default:
      return null;
  }
}
