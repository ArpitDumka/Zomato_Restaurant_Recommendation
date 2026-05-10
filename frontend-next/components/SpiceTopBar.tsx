"use client";

import LlmStatusBadge from "@/components/LlmStatusBadge";

type NavTarget = "discover" | "shortlist";

type Props = {
  activeNav: NavTarget;
  onNavigate: (target: NavTarget) => void;
  usedLlm: boolean | null;
  fallbackReason?: string | null;
  llmLoading: boolean;
};

export default function SpiceTopBar({
  activeNav,
  onNavigate,
  usedLlm,
  fallbackReason,
  llmLoading,
}: Props) {
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">SpiceRoute Select</div>
        <nav className="nav">
          <button
            type="button"
            className={`nav-btn${activeNav === "discover" ? " active" : ""}`}
            onClick={() => onNavigate("discover")}
          >
            Discover
          </button>
          <button
            type="button"
            className={`nav-btn${activeNav === "shortlist" ? " active" : ""}`}
            onClick={() => onNavigate("shortlist")}
          >
            Shortlist
          </button>
        </nav>
        <div className="ai-pill">
          <span className="dot" /> AI{" "}
          <LlmStatusBadge
            usedLlm={usedLlm}
            fallbackReason={fallbackReason}
            loading={llmLoading}
          />
        </div>
      </div>
    </header>
  );
}
