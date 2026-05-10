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
| `CORS_ORIGINS` | Optional; comma-separated origins, e.g. `https://your-app.vercel.app`. If unset on **Railway**, the API defaults to **allow any origin** (`*`) so Vercel works without config |
| `CORS_ORIGIN_REGEX` | Optional; e.g. `https://[^/]+\.vercel\.app$`. Setting this **or** `CORS_ORIGINS` disables the permissive Railway default |
| `ZOMATO_STRICT_CORS` | Set **`1`** on Railway to **disable** permissive CORS when you are not setting `CORS_*` (local testing only; browsers will need explicit origins) |
| `ZOMATO_MAX_CATALOG_ROWS` | Optional; explicit cap. On **Railway**, if unset, defaults to **`ZOMATO_RAILWAY_DEFAULT_CAP`** (default **12000**) to avoid OOM |
| `ZOMATO_RAILWAY_DEFAULT_CAP` | Optional; overrides the Railway-only default cap (min 1000, max 500000). Raise (e.g. **20000**) if you add RAM |
| `ZOMATO_FULL_CATALOG` | Set to `1` on a **large** Railway instance to load the full ~52k rows (no cap) |
| `ZOMATO_HF_STREAMING` | **`1`** = stream HF (lower peak RAM). **`0`** = materialized Arrow (faster after cache). On **Railway**, default **`1`**; locally, default **`0`** |
| `ZOMATO_CATALOG_WARMUP` | Set **`1`** to load the catalog during startup (first UI request is faster). Default **off** so deploy/health succeed immediately; the first `/api/filter-options` may take 1–3 minutes on a cold Hugging Face cache |
| `ZOMATO_FILTER_MAX_CITIES` | Optional; max city dropdown entries (frequency order). Unset = **all** cities from the split |
| `ZOMATO_FILTER_MAX_CUISINES` | Optional; max cuisine dropdown entries. Unset = **all** cuisines |

The catalog does **one** pass over the split (normalize up to the cap, then light merges for remaining rows). After load, logs include **`catalog footprint`**. **`ZOMATO_FULL_CATALOG=1`** needs enough memory for ~52k normalized rows.

5. [ ] **Deploy**, then open **Settings → Networking → Generate Domain** (or attach your domain). Copy the **HTTPS** URL (**no trailing slash**).
6. [ ] Smoke test: `https://<your-railway-host>/api/health` → JSON with `"ok": true`.

**If the Vercel UI shows “Failed to fetch” for filter options:** (1) Confirm **`NEXT_PUBLIC_API_BASE_URL`** is the Railway **https** public URL (no trailing slash) — not an internal hostname. (2) Open **`/api/health`** in the browser; if that fails, fix Railway networking / deploy. (3) CORS is **permissive by default on Railway** unless you set `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` / `ZOMATO_STRICT_CORS`. (4) If **`/api/filter-options`** hangs, check logs (Hugging Face / memory); the Next app retries for several minutes.

**Note:** `https://<host>/` on Railway serves a **minimal** Phase 6 UI (`minimal.css`): version line, HF/LLM pipeline copy, deploy (`NEXT_PUBLIC_API_BASE_URL` / CORS), and **Terms**. **[Vercel](https://vercel.com/)** serves the **SpiceRoute** hub (Zomato-inspired visuals, hero + pick images, **additional preferences**, shortlist, **donut loading overlay** during recommend; Privacy in footer). Both call the same API.

---

## Checklist — Vercel (frontend)

1. [ ] New project → same Git repo.
2. [ ] **Root Directory:** `frontend-next`.
3. [ ] Framework: Next.js ([`vercel.json`](../frontend-next/vercel.json)).
4. [ ] **Env:** `NEXT_PUBLIC_API_BASE_URL` = your Railway public URL (Production; add Preview if needed).
5. [ ] Redeploy after changing `NEXT_PUBLIC_*` (baked at build time).
6. [ ] If the browser reports CORS errors, fix `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` on Railway and redeploy the API.

**UX:** After **Get Recommendations**, the Vercel UI shows a **donut spinner** overlay on the recommendation board until `POST /api/recommend` returns (slow when the LLM runs).

---

## Checklist — verify

- [ ] Dropdowns load (`GET /api/filter-options`).
- [ ] Recommendations work (`POST /api/recommend`).
- [ ] Railway deployment stays healthy in logs.

---

## Local: port 3000 + 8765

1. **Backend:** from repo root, `.\run.ps1 -Surface` → **http://127.0.0.1:8765** (full pipeline, same as production API).
2. **Frontend:** `cd frontend-next`, set `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8765` (see [`.env.example`](../frontend-next/.env.example)), then `npm install` and `npm run dev` → **http://localhost:3000**.
