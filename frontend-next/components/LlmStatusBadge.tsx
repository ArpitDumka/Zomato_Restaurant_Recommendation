"use client";

type Props = {
  usedLlm: boolean | null;
  fallbackReason?: string | null;
  loading?: boolean;
};

export default function LlmStatusBadge({
  usedLlm,
  fallbackReason,
  loading = false,
}: Props) {
  if (loading) {
    return <span className="llm-badge llm-unknown">...</span>;
  }
  if (usedLlm === true) {
    return <span className="llm-badge llm-on">ON</span>;
  }
  if (usedLlm === false) {
    return (
      <span className="llm-badge llm-off">
        OFF{fallbackReason ? ` (${fallbackReason})` : ""}
      </span>
    );
  }
  return <span className="llm-badge llm-unknown">Idle</span>;
}
