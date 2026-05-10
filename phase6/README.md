# Phase 6 — Product surface (API + UI)

Implements **Phase 6** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): a **thin** FastAPI app with **validated** JSON input, **one** recommendation path, and a **browser UI** with empty / error states.

## Install (Phases 2–5, then 6)

From the repo root, same venv:

```powershell
pip install -e ./phase2
pip install -e ./phase3
pip install -e ./phase4
pip install -e ./phase5
cd phase6
pip install -e ".[dev]"
```

## Configuration

Create **`phase6/.env`** (see `phase6/.env.example`). Repo root **`run.ps1 -Surface`** loads **`phase5/.env` first**, then **`phase6/.env`**, so duplicate keys are **overridden by phase6**.

- **Groq:** `GROQ_API_KEY=gsk_...` (or `OPENAI_API_KEY=gsk_...`); base URL defaults to Groq’s OpenAI-compatible endpoint unless you set `OPENAI_BASE_URL`.
- **OpenAI:** `OPENAI_API_KEY=sk-...` and optional `OPENAI_BASE_URL`, `OPENAI_MODEL`.
- Without any LLM key, Phase 5 uses **fallback** explanations; the UI header still shows **LLM** status (**ON** / **OFF** / **Idle**) after each search.

- Hugging Face: optional `HF_TOKEN`; first materialization may download data (see `phase2` README).

## Run

```powershell
zomato-surface serve
```

Open **http://127.0.0.1:8765/**.

This is the **single canonical app URL** for Phase 6 (UI + backend API in one process).

## UI (this package)

- **Templates:** [`src/zomato_surface/templates/index.html`](src/zomato_surface/templates/index.html) — Jinja form + results (minimal layout).
- **Styles:** [`src/zomato_surface/static/minimal.css`](src/zomato_surface/static/minimal.css) — theme for `/`. (`style.css` is a reference / Spice theme used by the Next.js copy, not linked from Jinja.)

## API

- `POST /api/recommend` — body: `city`, `cuisine_query`, optional **`additional_preferences`**, `min_rating`, `budget_band`, `top_k` (1–5), `llm_candidate_cap` (200–300 shortlist; see `api_schemas.RecommendRequest`).
- `GET /api/filter-options` — dropdown values from the materialized catalog (`?refresh=true` to reload from Hub).
- `GET /api/health` — liveness.

## Tests

```powershell
pytest
ruff check src tests
```

## Pipeline (what happens on each request)

1. **First request** (or `/api/filter-options`): **materialize** the HF split (full **~52k** locally; on **Railway** a default row cap may apply unless overridden — see [`Docs/Deployment.md`](../Docs/Deployment.md)), **normalize** once, and keep the catalog in memory (`zomato_surface.catalog`).
2. **Each recommend**: **filter** in memory with `UserPreferences`.
3. **Shortlist** to at most `llm_candidate_cap` (200–300) by rating (`rank_by_rating_cap`).
4. **LLM** returns up to `top_k` picks (default 5) with JSON validation + fallback (`rank_and_explain`).

This matches [ProblemStatement.md](../Docs/ProblemStatement.md) success criteria when run with data + API key.
