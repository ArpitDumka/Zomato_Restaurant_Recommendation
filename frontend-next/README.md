# Next.js Frontend (optional prototype)

This folder is an optional prototype frontend.

For normal project usage, run the single-port Phase 6 app at
`http://127.0.0.1:8765/` via `.\run.ps1 -Surface`.

## Prerequisites

- Backend running at `http://127.0.0.1:8765`:
  - From repo root: `.\run.ps1 -Surface`
- Node.js 18+ installed

## Setup

```powershell
cd frontend-next
copy .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## API integration

The app calls:

- `GET /api/filter-options`
- `POST /api/recommend`

Base URL is controlled by `NEXT_PUBLIC_API_BASE_URL` in `.env.local`.

## What this frontend includes

- Dropdown-based preference form
- LLM badge (`Idle` / `ON` / `OFF`)
- Result cards with rank, name, cuisine, rating, cost, explanation
- Loading, empty, and error states
