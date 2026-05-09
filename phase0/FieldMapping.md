# Field mapping (Phase 0)

One-page map: **user preferences → dataset columns**, **API recommendation object → sources**, and **grounding rule**. Dataset: `ManikaSaini/zomato-restaurant-recommendation` (see [DatasetSpikeReport.md](./DatasetSpikeReport.md) for null rates and raw value shapes).

**Input source (frozen):** the **basic web UI** (Phase 6) is the primary way users enter preferences. The backend may still expose a JSON API that mirrors the same fields for testing or future clients, but the product path is browser-first.

## Grounded-only rule (frozen)

- The LLM may **only** rank and explain restaurants **present in the candidate list** built from this dataset (after filters). It must **not** invent venues or factual fields not supplied in the prompt payload.
- Rows missing critical fields (`name`, or unparseable `rate` / cost when those filters apply) are handled in Phase 3–4 (drop, impute, or exclude)—documented separately.

## User preference → dataset column(s)

| User preference (web UI → backend) | Dataset column(s) | Notes |
|---------------------------|-------------------|--------|
| **Location (city)** | `listed_in(city)` | Primary city bucket (e.g. Banashankari, BTM, …). Align user-facing “Bangalore” with rows whose city/area names appear in this column (normalization TBD in Phase 3). |
| **Location (area, optional later)** | `location` | Neighborhood / locality; finer than city. Phase 4 can add optional area filter. |
| **Budget (low / medium / high)** | `approx_cost(for two people)` | Raw string INR for two (e.g. `800`). Parse to number in Phase 3; bucket thresholds in ADR/Phase 0 follow-up. |
| **Cuisine** | `cuisines` | Often multi-label, comma-separated (`North Indian, Mughlai, Chinese`). Match policy: substring / token overlap (Phase 4). |
| **Minimum rating** | `rate` | Raw like `4.1/5` or missing (~14% empty in 8k sample). Parse numeric part; decide treatment for empty (exclude row). |
| **Extras** (e.g. family-friendly, quick service) | `rest_type`, `online_order`, `book_table`; optional text in `dish_liked`, `reviews_list` | No single “family-friendly” column: **hard filters** only on structured fields where possible; else pass snippets to LLM as **unverified context** or ignore for strict filtering. |

## Stable identity (for LLM JSON `restaurant_id`)

| Internal id source | Columns | Notes |
|--------------------|---------|--------|
| Preferred | `url` | Unique per listing when present; stable. |
| Fallback | Hash of `name` + `address` + `listed_in(city)` | If `url` ever missing in other revisions. |

## One recommendation JSON (frozen shape for Phase 5–6)

| Response field | Source column(s) | Notes |
|----------------|------------------|--------|
| `restaurant_id` | Derived | e.g. stable id from table above (not raw HF row index unless frozen). |
| `name` | `name` | |
| `cuisine` | `cuisines` | Display string; may split later. |
| `rating` | `rate` | Normalize display (e.g. `4.1`) in Phase 3. |
| `cost` | `approx_cost(for two people)` | Keep label “for two” in UI copy if needed. |
| `explanation` | *LLM only* | Must reference only supplied fields / ids from candidate payload. |

Optional later fields (not required for Phase 0 freeze): `url`, `location`, `listed_in(type)`, `votes`—for UI or debugging.

## High-impact data quality flags (from spike)

- **`rate`**: ~14% null/empty in sample—filter and UX must handle “unknown rating.”
- **`dish_liked`**: ~56% empty—do not rely on it for required display.
- **`cuisines`**: rarely empty; primary signal for cuisine filter.
