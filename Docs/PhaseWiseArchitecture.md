# Phase-wise architecture (Phases 0–6 + optional Railway/Vercel deploy)

Companion to [ProblemStatement.md](./ProblemStatement.md).  
This file now reflects the **implemented system**, not a forward roadmap.  
For boundary handling and negative paths, see [EdgeCases.md](./EdgeCases.md).

## Backend and frontend (Phase 6 product)

The shipped product is a **single Python process**: a **FastAPI backend** that serves both **JSON APIs** and the **browser UI** (no separate Node/React build). Phase 1’s optional preview on port 8000 is a different, smaller app; the **main** backend+frontend pair lives in **Phase 6**.

### Backend (server)

| Layer | Role | Location (repo) |
| --- | --- | --- |
| **HTTP / routing** | FastAPI app; CORS for same-origin UI + optional Next.js (`CORS_ORIGINS` / `CORS_ORIGIN_REGEX` on hosts) | [`phase6/src/zomato_surface/app.py`](../phase6/src/zomato_surface/app.py) |
| **Recommendation orchestration** | Preferences → filter → shortlist → LLM | [`phase6/src/zomato_surface/service.py`](../phase6/src/zomato_surface/service.py) |
| **Data catalog** | One-time HF materialize + normalize; in-memory cache | [`phase6/src/zomato_surface/catalog.py`](../phase6/src/zomato_surface/catalog.py) |
| **Filter options API** | Distinct cities/cuisines/ratings/budgets from catalog | [`phase6/src/zomato_surface/filter_options.py`](../phase6/src/zomato_surface/filter_options.py) |
| **Request validation** | Pydantic bodies (e.g. `RecommendRequest`) | [`phase6/src/zomato_surface/api_schemas.py`](../phase6/src/zomato_surface/api_schemas.py) |
| **Domain libraries** | Ingest, normalize, filter, LLM (imported, not HTTP) | [`phase2/`](../phase2/README.md) → [`phase5/`](../phase5/README.md) |

**Backend endpoints (summary):**

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Serves main HTML (Jinja template) |
| GET | `/static/*` | CSS and future static assets |
| GET | `/api/health` | Liveness |
| GET | `/api/filter-options` | Dropdown data (from catalog) |
| POST | `/api/recommend` | Filter + shortlist + LLM; JSON result |
| GET | `/docs` | OpenAPI (FastAPI) |

### Frontend (browser)

| Layer | Role | Location (repo) |
| --- | --- | --- |
| **Page shell** | HTML structure, form, result list | [`phase6/src/zomato_surface/templates/index.html`](../phase6/src/zomato_surface/templates/index.html) |
| **Styling** | Layout, theme, LLM badge | [`phase6/src/zomato_surface/static/style.css`](../phase6/src/zomato_surface/static/style.css) |
| **Client logic** | `fetch('/api/filter-options')`, `fetch('/api/recommend')`, DOM updates | Embedded `<script>` in `index.html` (vanilla JS, no bundler) |

The canonical frontend is served by the same FastAPI app (Phase 6 template + JS),
so the product runs on a **single URL/port** in normal usage.

```mermaid
flowchart LR
  subgraph Frontend["Frontend (browser)"]
    HTML["index.html + style.css"]
    JS["Vanilla JS fetch"]
    HTML --> JS
  end
  subgraph Backend["Backend (FastAPI, Phase 6)"]
    API["/api/* routes"]
    SVC["service + catalog"]
    API --> SVC
    LIB["phase2–5 libraries"]
    SVC --> LIB
  end
  JS -->|GET filter-options POST recommend| API
  Backend -->|Jinja GET /| HTML
```

```mermaid
flowchart LR
  P0["Phase 0<br/>Charter + HF spike"] --> P1["Phase 1<br/>Repo + tooling"]
  P1 --> P2["Phase 2<br/>Raw ingest"]
  P2 --> P3["Phase 3<br/>Canonical normalize"]
  P3 --> P4["Phase 4<br/>Deterministic filter/rank"]
  P4 --> P5["Phase 5<br/>LLM rank + explanation"]
  P5 --> P6["Phase 6<br/>Backend (FastAPI) + frontend (HTML/JS)"]
  P6 --> P7["Deploy (optional)<br/>Railway API + Vercel Next.js"]
```

## End-to-end runtime architecture (current)

```mermaid
flowchart TD
  HF["Hugging Face dataset<br/>ManikaSaini/zomato-restaurant-recommendation"] --> RI["Phase 2: HF split (streamed into catalog)"]
  RI --> NM["Phase 3: normalize_raw_row() -> RestaurantRecord"]
  NM --> CAT["Phase 6 catalog cache<br/>(in-memory full normalized split)"]
  CAT --> OPT["/api/filter-options<br/>cities/cuisines/ratings/budgets"]
  CAT --> FIL["Phase 4: record_matches_preferences()"]
  FIL --> CAP["Phase 4: rank_by_rating_cap()<br/>shortlist 200-300"]
  CAP --> LLM["Phase 5: rank_and_explain()<br/>top_k up to 5"]
  LLM --> API["Phase 6: POST /api/recommend"]
  OPT --> UI["Browser: template + JS"]
  API --> UI
```

### Request lifecycle (Phase 6)

1. App receives user preferences from UI (`/`) and submits to `POST /api/recommend`.
2. Full dataset is loaded from HF and normalized once (first call), then cached in memory.
3. Phase 4 applies deterministic constraints: city, cuisine token match, minimum rating, budget band.
4. Candidates are sorted by rating and capped to `llm_candidate_cap` (**200–300**).
5. Phase 5 asks LLM to return grounded ranked picks (`top_k`, default **5**, max **5**).
6. If LLM fails or key is missing, fallback ranking/explanations are returned.

## Completed implementation phases (0–6)

## Phase 0 — Charter + dataset spike

**Implemented objective:** validate feasibility, freeze preference fields, and define grounded recommendation behavior.

**Delivered:** [`phase0/`](../phase0/README.md)
- `FieldMapping.md`
- `ADR-0001-runtime-and-llm.md`
- `dataset_spike.py`
- `DatasetSpikeReport.md`

**Outcome used by later phases:** fixed field mapping and normalization policy inputs.

---

## Phase 1 — Repository scaffold and runnable baseline

**Implemented objective:** create installable skeleton and CI-ready baseline.

**Delivered:** [`phase1/`](../phase1/README.md)
- Package `zomato_recommend`
- Health/no-op runnable entrypoint
- Tests and phase CI workflow

**Outcome used by later phases:** repeatable install/run path and repo conventions.

---

## Phase 2 — Raw ingestion from Hugging Face

**Implemented objective:** centralize dataset access (streaming and full-load variants).

**Delivered:** [`phase2/`](../phase2/README.md)
- Package `zomato_raw_ingest`
- `iter_raw_rows(...)` (streaming)
- `load_raw_rows(...)` (bounded)
- `load_materialized_split(...)` (**full split in memory**, non-streaming)

**Outcome used by later phases:** single source for all HF reads; local HF cache reuse across runs.

**Dependency note:** `zomato-raw-ingest` requires **`datasets>=4.4.0`** so **Python 3.14** runtimes do not hit legacy fingerprint/pickle failures inside `datasets` when loading builders.

---

## Phase 3 — Canonical model and normalization

**Implemented objective:** isolate downstream logic from raw HF schema.

**Delivered:** [`phase3/`](../phase3/README.md)
- Package `zomato_canonical`
- `RestaurantRecord` model
- `normalize_raw_row(...)`
- parsers for rating/cost, budget mapping policy constants

**Outcome used by later phases:** all filtering/ranking/LLM logic consumes canonical records only.

---

## Phase 4 — Deterministic filtering and shortlist ranking

**Implemented objective:** enforce hard constraints before any model call.

**Delivered:** [`phase4/`](../phase4/README.md)
- Package `zomato_filter`
- `UserPreferences`
- `record_matches_preferences(...)`
- `rank_by_rating_cap(...)`

**Outcome used by later phases:** explainable, testable pre-LLM narrowing.

---

## Phase 5 — LLM ranking, schema validation, fallback

**Implemented objective:** convert shortlist into grounded explanations with robust fallback.

**Delivered:** [`phase5/`](../phase5/README.md)
- Package `zomato_llm`
- Prompt construction with candidate IDs and preference context
- JSON parsing/validation
- deterministic fallback on error/missing key

**Outcome used by later phases:** production-safe recommendation text path.

---

## Phase 6 — Product surface (backend + frontend)

**Implemented objective:** ship a single deployable unit: **FastAPI backend** plus **browser UI**.

**Delivered:** [`phase6/`](../phase6/README.md)
- **Backend:** package `zomato_surface` — FastAPI app, `service`, `catalog`, `filter_options`, `api_schemas`
- **HTTP:** `/`, `/static/*`, `/api/health`, `/api/filter-options`, `/api/recommend`, `/docs`
- **Frontend:** Jinja template + static CSS + inline vanilla JS (dropdowns, LLM status badge, text-first results)
- Shared in-memory catalog for filter-options and recommend
- Input constraints: `top_k` 1–5, `llm_candidate_cap` 200–300

**Outcome:** proper **backend/frontend** split in one process: UI consumes JSON APIs; all business logic stays in Python.

---

## Production deployment (Railway + Vercel)

**Objective:** host the **FastAPI** service separately from the optional **Next.js** client.

**Delivered:** [`railway.toml`](../railway.toml) + [`frontend-next/vercel.json`](../frontend-next/vercel.json) + [`Docs/Deployment.md`](./Deployment.md)  
- **Railway:** `pip install -r requirements.txt` (editable phase installs) + `uvicorn zomato_surface.app:create_app --factory` on **`$PORT`**; health check `/api/health` (see `railway.toml`)
- **Vercel:** project **root directory** = `frontend-next`; `NEXT_PUBLIC_API_BASE_URL` points at the Railway public URL
- **CORS:** API reads **`CORS_ORIGINS`** (comma-separated) and optional **`CORS_ORIGIN_REGEX`** (e.g. `*.vercel.app`) — see Deployment doc
- **Secrets:** `OPENAI_API_KEY` / **`GROQ_API_KEY`** / optional **`HF_TOKEN`** in Railway variables (same semantics as local `phase6/.env`)

**Outcome:** split deployment while the in-repo Phase 6 Jinja UI remains available on the same API host at `/`.

---

## Current package dependency chain

```text
phase6 (surface)
  -> phase5 (llm)
  -> phase4 (filter)
  -> phase3 (canonical)
  -> phase2 (raw_ingest)
```

## Operational notes

- **Primary run path (single-port mode):** `.\run.ps1 -Surface`
- **Single canonical URL:** `http://127.0.0.1:8765/` (UI + API from same process)
- **Split stack (local):** Phase 6 API on `:8765` + `frontend-next` on `:3000` with `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8765`
- **Split stack (production):** see [`Deployment.md`](./Deployment.md) — Railway + Vercel; local dev **Next :3000** + **API :8765**
- **Environment loading:** `run.ps1 -Surface` loads `phase5/.env` then **`phase6/.env`** (phase6 overrides)
- **Live LLM (backend → provider):** `OPENAI_API_KEY` and/or **`GROQ_API_KEY`** (see `zomato_llm.config`); when provider limits or key issues occur, the app returns smart local fallback explanations
- **Optional for better HF rate limits:** `HF_TOKEN`
- **Dataset scope note:** current source dataset values for `listed_in(city)` are predominantly Bangalore localities.
- **Low memory:** catalog uses **streaming** ingest; optional **`ZOMATO_MAX_CATALOG_ROWS`** caps in-memory rows (see [`Deployment.md`](./Deployment.md)).

## Final phase summary

| Phase | Responsibility | Final artifact |
|---|---|---|
| 0 | Problem/data grounding | Spike reports + mapping + ADR |
| 1 | Project baseline | Installable scaffold + CI |
| 2 | Data acquisition | HF raw ingestion APIs |
| 3 | Data standardization | Canonical model + normalization |
| 4 | Deterministic relevance | Filter + shortlist ranking |
| 5 | Language reasoning | Grounded LLM rank/explain + fallback |
| 6 | Product delivery | **Backend** (FastAPI) + **frontend** (HTML/CSS/JS) + orchestration |
| — | Production (optional) | **Railway** (API + same-origin UI) + **Vercel** (Next.js) — [`Deployment.md`](./Deployment.md) |
