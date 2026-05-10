# Next.js frontend (Vercel)

Production layout: **API on [Railway](https://railway.app/)**, **this app on [Vercel](https://vercel.com/)** from the same Git repo with **root directory `frontend-next`**. Full checklist: [`Docs/Deployment.md`](../Docs/Deployment.md).

For a single-process demo you can instead use Phase 6 only at `http://127.0.0.1:8765/` (`.\run.ps1 -Surface` from repo root).

## Prerequisites

- **Local:** backend at `http://127.0.0.1:8765` (`.\run.ps1 -Surface`)
- Node.js 18+

## Local setup

```powershell
cd frontend-next
copy .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Vercel setup (summary)

1. New project → this repository → **Root Directory:** `frontend-next`.
2. **Environment variables:** `NEXT_PUBLIC_API_BASE_URL` = your Railway API URL (HTTPS, no trailing slash). Set for Production (and Preview if needed).
3. Redeploy after any change to `NEXT_PUBLIC_*`.
4. On Railway, configure **`CORS_ORIGIN_REGEX`** (and optionally **`CORS_ORIGINS`**) so `*.vercel.app` (or your custom domain) can call the API — see [`Docs/Deployment.md`](../Docs/Deployment.md).

## API integration

- `GET /api/filter-options`
- `POST /api/recommend`

Base URL: **`NEXT_PUBLIC_API_BASE_URL`** in `.env.local` (local) or Vercel project settings (production).

## What this app includes

- **SpiceRoute Select** UI (top bar, hero, Preference Studio, recommendation board, shortlist in `localStorage`)
- LLM pill in the header
- Loading, empty, and error states

The **Railway** root URL uses a lighter **Next.js-style** single-column UI; deploy this folder to **Vercel** for the full SpiceRoute experience.
