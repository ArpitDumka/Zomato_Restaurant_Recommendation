# Phase 4 — Deterministic filter and candidate cap

Implements **Phase 4** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): **pure** preference filters over `RestaurantRecord`, **rating-based ranking**, cap to **M** candidates, and a **stub** explanation string. **No LLM** (Phase 5).

## Dependency

Install **Phase 3** first (same venv):

```powershell
pip install -e ../phase3
pip install -e ".[dev]"
```

## API (`zomato_filter`)

| Symbol | Purpose |
|--------|---------|
| `UserPreferences` | Optional `city`, `cuisine_query`, `min_rating`, `budget_band`. |
| `record_matches_preferences` / `filter_restaurant_records` | Predicate + list filter (input order kept). |
| `rank_by_rating_cap(records, max_candidates)` | Sort by rating desc (unknown last), tie-break name + id; slice. |
| `filter_rank_cap(records, prefs, max_candidates)` | Filter then rank/cap. |
| `stub_explanation()` | Returns `"Ranked by rating."` |

### Matching rules

- **City:** case-insensitive equality on `city_listed` (whitespace-normalized).
- **Cuisine:** case-insensitive substring on `cuisines_display`, or token prefix/substring match.
- **Min rating:** rows with `rating is None` are excluded when `min_rating` is set.
- **Budget:** exact match on `budget_band` when set (`unknown` only matches if user selects `unknown`).

## Tests

```powershell
pytest
ruff check src tests
```

## Exit criteria (Phase 4)

- [x] Pure functions; fixture tests with in-memory `RestaurantRecord` rows.
- [x] Cap + stable ordering; stub explanation helper.

Next: **Phase 5** LLM in [`phase5/`](../phase5/README.md) ([PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md)).
