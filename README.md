# Zomato-inspired restaurant recommendations

AI-assisted restaurant discovery using the [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) dataset and an LLM for grounded explanations. Product definition and roadmap live under [`Docs/`](Docs/ProblemStatement.md).

## What’s implemented

| Phase | Status | How to run |
|-------|--------|------------|
| **0** | Done — charter, field mapping, dataset spike | `python phase0/dataset_spike.py` (after `pip install -r phase0/requirements.txt`) |
| **1** | Done — installable package, health CLI | `python -m zomato_recommend` (after installing `phase1`; see below) |
| **2** | Done — raw HF ingestion (`zomato-raw-ingest`) | `pip install -e ./phase2` then `python -c "from zomato_raw_ingest import load_raw_rows; print(len(load_raw_rows(5)))"` (needs network first run) |
| **3** | Done — normalization (`zomato-canonical`) | `pip install -e ./phase3` then use `zomato_canonical.normalize_raw_row` (see [phase3/README.md](phase3/README.md)) |
| **4** | Done — filters + cap (`zomato-filter`) | `pip install -e ./phase3` then `pip install -e ./phase4` (see [phase4/README.md](phase4/README.md)) |
| **5** | Done — LLM layer (`zomato-llm`) | After phases 3–4: `pip install -e ./phase5` + `OPENAI_API_KEY` ([phase5/README.md](phase5/README.md)) |
| **6** | Done — product UI/API (`zomato-surface`) | Install phases 2–5 then `pip install -e ./phase6` ([phase6/README.md](phase6/README.md)) |
| **Deploy** | Optional — API on **Render**, Next.js on **Vercel** (local: **8765** API, **3000** Next) | [Docs/Deployment.md](Docs/Deployment.md), [`render.yaml`](render.yaml), [`frontend-next/vercel.json`](frontend-next/vercel.json) |

**Full pipeline app (single URL, Phase 6)** — filters, cap, grounded LLM top-K (set API key for real explanations):

```powershell
.\run.ps1 -Surface
```

Open **http://127.0.0.1:8765/**. This is the canonical UI + backend URL in one process.
The first request scans the full HF split (cached after download) and may take a while.

**Preview web UI (Phase 1)** — status + raw sample rows only:

```powershell
.\run.ps1 -Web
```

Then open **http://127.0.0.1:8000/**. First “Load sample” may take a minute while the Hub cache warms up.

## Quick run (Windows)

From the repo root, one script creates a root `.venv`, installs `phase1`, and runs the app health + status:

```powershell
.\run.ps1
```

Refresh the Phase 0 dataset report:

```powershell
.\run.ps1 -Spike
```

## Quick run (manual)

**Phase 1 (main app shell):**

```powershell
cd Zomato_1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e "./phase2"
pip install -e "phase1[dev,web]"
python -m zomato_recommend
python -m zomato_recommend serve
```

You can run the same `pip install` / `python -m zomato_recommend` from the repo root if your shell is activated. Use `serve` to start the web UI on port 8000.

**Phase 0 spike only:**

```powershell
pip install -r phase0/requirements.txt
python phase0/dataset_spike.py
```

**Tests (Phase 1):**

```powershell
cd phase1
pip install -e "../phase2"
pip install -e ".[dev,web]"
pytest
ruff check src tests
```

CI for `phase1` runs on push when files under `phase1/` change (see `.github/workflows/phase1-ci.yml`). CI for `phase2` runs similarly (`.github/workflows/phase2-ci.yml`; tests hit the Hub).

**Phase 2 tests:**

```powershell
cd phase2
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Docs

- [Problem statement](Docs/ProblemStatement.md)
- [Phase-wise architecture](Docs/PhaseWiseArchitecture.md)
- [Edge cases](Docs/EdgeCases.md)
- [Phase 0 deliverables](phase0/README.md)
- [Phase 1 deliverables](phase1/README.md)
- [Phase 2 deliverables](phase2/README.md)
- [Phase 3 deliverables](phase3/README.md)
- [Phase 4 deliverables](phase4/README.md)
- [Phase 5 deliverables](phase5/README.md)
- [Phase 6 deliverables](phase6/README.md)
- [Deployment — Render + Vercel, local 3000 + 8765](Docs/Deployment.md)
