import { RankedPick } from "@/lib/types";

type Props = {
  pick: RankedPick;
};

export default function ResultCard({ pick }: Props) {
  return (
    <li className="pick">
      <div className="pick-top">
        <span className="rank">#{pick.rank}</span>
        <span className="title">
          {pick.name}
          {pick.branch ? ` (${pick.branch})` : ""}
        </span>
      </div>
      <div className="meta2">
        {pick.cuisine} · rating {pick.rating ?? "-"} · cost{" "}
        {pick.cost_for_two_inr ?? "-"} INR (two)
      </div>
      <p className="why">{pick.explanation}</p>
    </li>
  );
}
