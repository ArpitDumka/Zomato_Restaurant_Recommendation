# Phase 3 — Normalization and canonical record

Implements **Phase 3** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): one internal type (`RestaurantRecord`), parsers for rating/cost, **low / medium / high** buckets, stable `restaurant_id`, optional dedupe. **No filtering** (Phase 4).

## Design

- **Input:** raw `dict` rows from Phase 2 / Hugging Face (column names unchanged).
- **Output:** `RestaurantRecord` or `None` if `name` is empty (row dropped).
- **IDs:** use `url` when present; else `h:` + 24-hex SHA-256 of `name`, `address`, `listed_in(city)` (see [FieldMapping.md](../phase0/FieldMapping.md)).
- **Budget bands (INR for two):** `low` ≤ 500, `medium` ≤ 1000, else `high`; `unknown` if cost unparseable (`policy.py`).

## Install

```powershell
cd path\to\Zomato_1\phase3
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## API (import `zomato_canonical`)

| Symbol | Purpose |
|--------|---------|
| `RestaurantRecord` | Frozen dataclass — all downstream fields. |
| `normalize_raw_row(dict)` | `RestaurantRecord \| None` |
| `dedupe_restaurant_records(iterable)` | First-wins by `restaurant_id`. |
| `parse_rating`, `parse_cost_inr`, `cost_to_budget_band` | Tested parsers. |
| `LOW_MAX_INR`, `MEDIUM_MAX_INR` | Bucket thresholds. |

## Tests

```powershell
pytest
ruff check src tests
```

## Exit criteria (Phase 3)

- [x] Single canonical model; parsers + bucket tests.
- [x] Stable id and dedupe helpers.
- [x] Rows without name dropped.

Next: **Phase 4** deterministic filters in [`phase4/`](../phase4/README.md) (see architecture doc).
