"""
Phase 0 throwaway spike: load a sample from Hugging Face and summarize schema.
Run from repo root:  python phase0/dataset_spike.py
Outputs: phase0/DatasetSpikeReport.md (overwritten each run)
"""
from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone

from datasets import load_dataset

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
SPLIT = "train"
MAX_ROWS = 8000  # streaming sample for null/rate/cost stats
REPORT_PATH = os.path.join(os.path.dirname(__file__), "DatasetSpikeReport.md")


def main() -> None:
    ds = load_dataset(DATASET_ID, split=SPLIT, streaming=True)
    keys: list[str] | None = None
    nullish = Counter()
    total = 0
    rate_samples: list[str] = []
    cost_samples: list[str] = []
    city_values: list[str] = []
    cuisine_samples: list[str] = []
    example_row: dict = {}

    for row in ds:
        if keys is None:
            keys = list(row.keys())
            example_row = {k: row[k] for k in keys}
        total += 1
        for k in keys:
            v = row.get(k)
            if v is None or (isinstance(v, str) and not v.strip()):
                nullish[k] += 1
        r = row.get("rate")
        if isinstance(r, str) and r.strip():
            rate_samples.append(r.strip())
        c = row.get("approx_cost(for two people)")
        if isinstance(c, str) and c.strip():
            cost_samples.append(c.strip())
        lc = row.get("listed_in(city)")
        if isinstance(lc, str) and lc.strip():
            city_values.append(lc.strip())
        cu = row.get("cuisines")
        if isinstance(cu, str) and cu.strip():
            cuisine_samples.append(cu.strip())

        if total >= MAX_ROWS:
            break

    # frequency snapshots (small)
    top_cities = Counter(city_values).most_common(15)
    rate_counter = Counter(rate_samples).most_common(12)
    cost_counter = Counter(cost_samples).most_common(12)

    def esc(s: str) -> str:
        return s.replace("|", "\\|").replace("\n", " ")[:500]

    lines = [
        "# Dataset spike report (Phase 0)",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat()}` (UTC)",
        "",
        "## Source",
        "",
        f"- **Dataset:** `{DATASET_ID}`",
        f"- **Split:** `{SPLIT}`",
        f"- **Rows sampled for stats:** {total} (streaming cap `{MAX_ROWS}`)",
        "",
        "## Column keys (authoritative for field mapping)",
        "",
        json.dumps(keys, indent=2),
        "",
        "## Null / empty counts (in sample)",
        "",
        "Column | Empty or null count | Share",
        "---|---:|---:",
    ]
    for k in keys or []:
        cnt = nullish.get(k, 0)
        share = f"{100.0 * cnt / total:.1f}%" if total else "n/a"
        lines.append(f"| `{k}` | {cnt} | {share} |")

    lines.extend(
        [
            "",
            "## Example row (first observed)",
            "",
            "```json",
            json.dumps(example_row, indent=2, default=str)[:12000],
            "```",
            "",
            "## `rate` — sample raw values (top frequencies in sample)",
            "",
            "| Value | Count |",
            "|---|---:|",
        ]
    )
    for val, cnt in rate_counter:
        lines.append(f"| {esc(val)} | {cnt} |")

    lines.extend(
        [
            "",
            "## `approx_cost(for two people)` — sample raw values (top frequencies)",
            "",
            "| Value | Count |",
            "|---|---:|",
        ]
    )
    for val, cnt in cost_counter:
        lines.append(f"| {esc(val)} | {cnt} |")

    lines.extend(
        [
            "",
            "## `listed_in(city)` — top values in sample",
            "",
            "| City | Count |",
            "|---|---:|",
        ]
    )
    for val, cnt in top_cities:
        lines.append(f"| {esc(val)} | {cnt} |")

    lines.extend(
        [
            "",
            "## `cuisines` — random variety (first 12 distinct in walk order)",
            "",
        ]
    )
    seen = set()
    for c in cuisine_samples:
        if c not in seen:
            seen.add(c)
            lines.append(f"- {esc(c)}")
        if len(seen) >= 12:
            break

    lines.append("")
    lines.append(
        "> Re-run `python phase0/dataset_spike.py` after pinning a dataset revision if you need a frozen snapshot."
    )
    lines.append("")

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {REPORT_PATH} ({total} rows analyzed)")


if __name__ == "__main__":
    main()
