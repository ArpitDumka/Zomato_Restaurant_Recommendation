# Deployment: split frontend (Next.js) + backend (FastAPI)

**Local dev (same as before):**

| Role | Stack | URL |
|------|--------|-----|
| **Frontend** | Next.js in [`frontend-next`](../frontend-next/) | `http://localhost:3000` |
| **Backend** | FastAPI Phase 6 — catalog, filters, LLM, APIs | `http://127.0.0.1:8765` |

The Next app calls the API using **`NEXT_PUBLIC_API_BASE_URL`** (defaults to `http://127.0.0.1:8765` in code). **Streamlit is not used.**

**Production:** host the backend on **Render** and the frontend on **Vercel**. Deploy **Render first**, then point Vercel at the public API URL.

**Repo files:** [`render.yaml`](../render.yaml), root [`requirements.txt`](../requirements.txt), [`frontend-next/vercel.json`](../frontend-next/vercel.json).

The Blueprint sets **`CORS_ORIGIN_REGEX`** so any **`*.vercel.app`** origin can call the API (see [`render.yaml`](../render.yaml)). Add **`CORS_ORIGINS`** in the Render dashboard for a fixed production URL or a custom domain.

---

## Checklist — Render (backend)

1. [ ] Create a **Web Service** from this repo, or use **Blueprint** with [`render.yaml`](../render.yaml).
2. [ ] **Root directory:** repo root (where `requirements.txt` lives).
3. [ ] **Build:** `pip install --upgrade pip && pip install -r requirements.txt`
4. [ ] **Start:** `uvicorn zomato_surface.app:create_app --factory --host 0.0.0.0 --port $PORT`
5. [ ] **Health check path:** `/api/health`
6. [ ] **Python:** 3.11.x (Blueprint sets `PYTHON_VERSION`).
7. [ ] **Env vars** (Render → Environment):

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Optional; LLM explanations |
| `GROQ_API_KEY` | Optional; Groq (OpenAI-compatible client in phase5) |
| `HF_TOKEN` | Optional; Hugging Face Hub |
| `CORS_ORIGINS` | **For Vercel:** comma-separated origins, e.g. `https://your-app.vercel.app` |
| `CORS_ORIGIN_REGEX` | Optional; e.g. `https://.*\.vercel\.app` for all preview URLs |
| `ZOMATO_MAX_CATALOG_ROWS` | Optional; cap in-memory rows (e.g. `40000`) for **512MB** hosts. Omit for full ~52k rows on larger RAM. |

The API **streams** the Hugging Face split (no second full copy of raw dicts). If Render still hits OOM, lower **`ZOMATO_MAX_CATALOG_ROWS`** (try `32000`) or upgrade RAM. [`render.yaml`](../render.yaml) sets `40000` by default on the free tier.

8. [ ] Deploy; **first boot** may download the dataset (watch RAM on free tier).
9. [ ] Copy the service URL (**no trailing slash**). Smoke test: `https://<host>/api/health` → `"ok": true`.

**Note:** `https://<host>/` on Render still serves the Phase 6 Jinja UI from the same FastAPI process. Vercel is only for the Next.js client.

---

## Checklist — Vercel (frontend)

1. [ ] New project → same Git repo.
2. [ ] **Root Directory:** `frontend-next`.
3. [ ] Framework: Next.js ([`vercel.json`](../frontend-next/vercel.json)).
4. [ ] **Env:** `NEXT_PUBLIC_API_BASE_URL` = your Render URL (Production; add Preview if needed).
5. [ ] Redeploy after changing `NEXT_PUBLIC_*` (baked at build time).
6. [ ] If the browser reports CORS errors, fix `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` on Render and redeploy the API.

---

## Checklist — verify

- [ ] Dropdowns load (`GET /api/filter-options`).
- [ ] Recommendations work (`POST /api/recommend`).
- [ ] Render service stays healthy in logs.

---

## Local: port 3000 + 8765

1. **Backend:** from repo root, `.\run.ps1 -Surface` → **http://127.0.0.1:8765** (full pipeline, same as production API).
2. **Frontend:** `cd frontend-next`, set `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8765` (see [`.env.example`](../frontend-next/.env.example)), then `npm install` and `npm run dev` → **http://localhost:3000**.
