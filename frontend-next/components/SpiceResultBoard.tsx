"use client";

import { RankedPick, RecommendResponse } from "@/lib/types";
import SpicePickCard, { ShortlistItem } from "@/components/SpicePickCard";

type Props = {
  visible: boolean;
  submitting: boolean;
  response: RecommendResponse | null;
  recommendError: string | null;
  shortlist: ShortlistItem[];
  onToggleShortlist: (item: ShortlistItem) => void;
  isShortlisted: (id: string) => boolean;
};

export default function SpiceResultBoard({
  visible,
  submitting,
  response,
  recommendError,
  shortlist,
  onToggleShortlist,
  isShortlisted,
}: Props) {
  if (!visible) {
    return null;
  }

  const result = response?.result ?? null;
  const picks: RankedPick[] = result?.picks ?? [];
  const emptyDefault = "No matches. Try broader filters.";

  return (
    <section className="results-pane card" id="results-board">
      {submitting ? (
        <div
          className="results-loading-overlay"
          role="status"
          aria-live="polite"
          aria-busy="true"
        >
          <div className="donut-spinner-wrap">
            <div className="donut-spinner" aria-hidden />
            <p className="donut-label">Processing your picks…</p>
          </div>
          <span className="sr-only">Loading recommendations, please wait.</span>
        </div>
      ) : null}
      <h2>Recommendation Board</h2>
      <p className="section-kicker">
        Ranked picks, cost cues, and AI blurbs — save favourites to your shortlist.
      </p>
      {recommendError ? <p className="error">{recommendError}</p> : null}
      {response ? (
        <p className="muted">
          Matched {response.matched_count} rows · sent {response.capped_count} to model
        </p>
      ) : null}
      {result?.summary ? <p className="summary">{result.summary}</p> : null}
      {response?.message ? (
        <div className="empty">{response.message}</div>
      ) : null}
      {!response?.message && picks.length === 0 && response && !recommendError ? (
        <div className="empty">{emptyDefault}</div>
      ) : null}
      <ul className="results">
        {picks.map((pick) => (
          <SpicePickCard
            key={`${pick.restaurant_id}-${pick.rank}`}
            pick={pick}
            shortlisted={isShortlisted(pick.restaurant_id)}
            onToggleShortlist={onToggleShortlist}
          />
        ))}
      </ul>
      <section className="shortlist-tools">
        <h3>Shortlist</h3>
        <p className="hint muted">Saved picks are visible here and kept in your browser.</p>
        <ul className="shortlist-list">
          {shortlist.length === 0 ? (
            <li className="muted">No shortlisted restaurants yet.</li>
          ) : (
            shortlist.map((x) => (
              <li key={x.restaurant_id}>
                <span>
                  {x.name}
                  {x.branch ? ` (${x.branch})` : ""}
                </span>
                <span className="muted">★ {x.rating ?? "—"}</span>
              </li>
            ))
          )}
        </ul>
      </section>
    </section>
  );
}
