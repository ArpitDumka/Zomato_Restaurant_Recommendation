# Deployment: split frontend (Next.js) + backend (FastAPI)

**Local dev (same as before):**

| Role | Stack | URL |
|------|--------|-----|
| **Frontend** | Next.js in [`frontend-next`](../frontend-next/) | `http://localhost:3000` |
| **Backend** | FastAPI Phase 6 — catalog, filters, LLM, APIs | `http://127.0.0.1:8765` |

The Next app calls the API using **`NEXT_PUBLIC_API_BASE_URL`** (defaults to `http://127.0.0.1:8765` in code). **Streamlit is not used.**

**Production:** host the backend on **[Railway](https://railway.app/)** and the frontend on **[Vercel](https://vercel.com/)**. Deploy **Railway first**, copy the public API URL, then configure **Vercel**.

**Repo files:** [`railway.toml`](../railway.toml), root [`requirements.txt`](../requirements.txt), [`scripts/start-railway.sh`](../scripts/start-railway.sh), [`.python-version`](../.python-version) (Python **3.11.9** for Railpack), sample env [`railway.env.example`](../railway.env.example), [`frontend-next/vercel.json`](../frontend-next/vercel.json).

Set **`CORS_ORIGIN_REGEX`** (and optionally **`CORS_ORIGINS`**) on Railway so the Vercel origin can call the API — see the env table below. You can copy name/value pairs from [`railway.env.example`](../railway.env.example) into **Variables** (add **`PYTHONUNBUFFERED=1`** for readable logs).

---

## Checklist — Railway (backend)

1. [ ] [Railway](https://railway.app/) → **New Project** → **Deploy from GitHub repo** (this repository).
2. [ ] **Root directory:** repository root (where `requirements.txt` and `railway.toml` live).
3. [ ] Railway will use [`railway.toml`](../railway.toml): build runs `pip install … -r requirements.txt` (PyPI deps only; no local `-e ./phase*` paths), start runs [`scripts/start-railway.sh`](../scripts/start-railway.sh) so **`PYTHONPATH`** includes all `phase*/src` trees, then **uvicorn** on **`$PORT`**. Health check **`/api/health`** (5 min timeout).
4. [ ] **Variables** (service → **Variables**):

| Variable | Purpose |
|----------|---------|
| `PYTHONUNBUFFERED` | Set to `1` so API logs stream in Railway (see [`railway.env.example`](../railway.env.example)) |
| `OPENAI_API_KEY` | Optional; LLM explanations |
| `GROQ_API_KEY` | Optional; Groq (OpenAI-compatible client in phase5) |
| `HF_TOKEN` | Optional; Hugging Face Hub |
| `CORS_ORIGINS` | Optional; comma-separated origins, e.g. `https://your-app.vercel.app` |
| `CORS_ORIGIN_REGEX` | Recommended for Vercel: `https://[^/]+\.vercel\.app$` (all `*.vercel.app` hosts) |
| `ZOMATO_MAX_CATALOG_ROWS` | Optional; explicit cap (e.g. `40000`). On **Railway**, if unset, the app defaults to **`ZOMATO_RAILWAY_DEFAULT_CAP`** (default **25000**) to avoid OOM on small plans |
| `ZOMATO_RAILWAY_DEFAULT_CAP` | Optional; overrides the Railway-only default cap (min 1000, max 500000) |
| `ZOMATO_FULL_CATALOG` | Set to `1` on a **large** Railway instance to load the full ~52k rows (no cap) |

The API **streams** the Hugging Face split (no second full copy of raw dicts). On Railway, the automatic cap prevents most OOMs during catalog load; raise RAM and set **`ZOMATO_FULL_CATALOG=1`** (or a higher **`ZOMATO_MAX_CATALOG_ROWS`**) when you need the full dataset.

5. [ ] **Deploy**, then open **Settings → Networking → Generate Domain** (or attach your domain). Copy the **HTTPS** URL (**no trailing slash**).
6. [ ] Smoke test: `https://<your-railway-host>/api/health` → JSON with `"ok": true`.

**Note:** `https://<host>/` on Railway serves a **minimal** Phase 6 UI (`minimal.css`) aligned with the Next.js app layout. **[Vercel](https://vercel.com/)** serves the **SpiceRoute** hub UI (same features: filters, recommendations, shortlist in-browser). Both call the same API.

---

## Checklist — Vercel (frontend)

1. [ ] New project → same Git repo.
2. [ ] **Root Directory:** `frontend-next`.
3. [ ] Framework: Next.js ([`vercel.json`](../frontend-next/vercel.json)).
4. [ ] **Env:** `NEXT_PUBLIC_API_BASE_URL` = your Railway public URL (Production; add Preview if needed).
5. [ ] Redeploy after changing `NEXT_PUBLIC_*` (baked at build time).
6. [ ] If the browser reports CORS errors, fix `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` on Railway and redeploy the API.

---

## Checklist — verify

- [ ] Dropdowns load (`GET /api/filter-options`).
- [ ] Recommendations work (`POST /api/recommend`).
- [ ] Railway deployment stays healthy in logs.

---

## Local: port 3000 + 8765

1. **Backend:** from repo root, `.\run.ps1 -Surface` → **http://127.0.0.1:8765** (full pipeline, same as production API).
2. **Frontend:** `cd frontend-next`, set `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8765` (see [`.env.example`](../frontend-next/.env.example)), then `npm install` and `npm run dev` → **http://localhost:3000**.
