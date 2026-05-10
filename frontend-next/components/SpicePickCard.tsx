"use client";

import Image from "next/image";
import { RankedPick } from "@/lib/types";

export type ShortlistItem = {
  restaurant_id: string;
  name: string;
  branch: string | null;
  rating: number | null;
};

type Props = {
  pick: RankedPick;
  shortlisted: boolean;
  onToggleShortlist: (item: ShortlistItem) => void;
};

function coverSeed(pick: RankedPick): string {
  const raw = `${pick.restaurant_id}-${pick.name}`.replace(/[^a-zA-Z0-9]/g, "");
  return encodeURIComponent((raw || "food").slice(0, 48));
}

export default function SpicePickCard({
  pick,
  shortlisted,
  onToggleShortlist,
}: Props) {
  const item: ShortlistItem = {
    restaurant_id: pick.restaurant_id,
    name: pick.name,
    branch: pick.branch ?? null,
    rating: pick.rating,
  };

  const seed = coverSeed(pick);

  return (
    <li className="pick">
      <div className="pick-cover">
        <Image
          src={`https://picsum.photos/seed/${seed}/640/180`}
          alt=""
          width={640}
          height={180}
          className="pick-cover-img"
          unoptimized
        />
      </div>
      <div className="pick-body">
        <div className="pick-top">
          <span className="rank-label">RANK #{pick.rank}</span>
          <span className="cost-label">
            FOR TWO ₹{pick.cost_for_two_inr ?? "—"}
          </span>
        </div>
        <div className="title">
          {pick.name}
          {pick.branch ? ` (${pick.branch})` : ""}
        </div>
        <div className="meta2">
          {pick.cuisine} · ★ {pick.rating ?? "—"}
        </div>
        <div className="insight">AI INSIGHT</div>
        <p className="why">{pick.explanation}</p>
        <div className="pick-actions">
          <button
            type="button"
            className="btn mini-btn"
            onClick={() => onToggleShortlist(item)}
          >
            {shortlisted ? "Remove Shortlist" : "Add to Shortlist"}
          </button>
        </div>
      </div>
    </li>
  );
}
