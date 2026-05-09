# Phase 1 — Repository scaffold

Implements **Phase 1** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): layout, dependencies, env template, health CLI, **preview web UI** (`[web]` extra), and tests. Filtering/LLM are later phases.

To run **health**, **web UI**, or **full repo scripts** from the root, see [README.md](../README.md) and `run.ps1` (`-Web` starts the browser UI).

## Layout

| Path | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata; extras `[dev]`, `[web]` (FastAPI, uvicorn, Jinja2); console script `zomato-recommend`. |
| `src/zomato_recommend/` | Package (`__version__`, CLI, `web/` templates + static). |
| `tests/` | Health + web API smoke tests. |
| `.env.example` | Reserved variable names for later phases (not loaded in Phase 1). |

## Phase 1: clone and install

```powershell
cd path\to\Zomato_1\phase1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e "../phase2"
pip install -e ".[dev,web]"
```

### Preview web UI

Requires Phase 2 installed (`zomato_raw_ingest`) for live data.

```powershell
python -m zomato_recommend serve
```

Open **http://127.0.0.1:8000/** — implementation status, **Load sample** (raw HF rows).

### Health entrypoint

Either of:

```powershell
python -m zomato_recommend
zomato-recommend
```

Expected output:

```text
zomato-recommend 0.1.0 | health: ok
```

Exit code `0`.

### Tests and lint (optional)

```powershell
pytest
ruff check src tests
```

## Exit criteria (Phase 1)

- [x] Repo layout under `phase1/` with dependency file (`pyproject.toml`).
- [x] `.env.example` with key names only.
- [x] `.gitignore` for secrets and local venv/cache.
- [x] Fresh install runs a **health** entrypoint (`python -m zomato_recommend` or `zomato-recommend`).
- [x] Optional **web** preview (`pip install -e ".[web]"`, `zomato-recommend serve`).
- [x] CI stub at repo [`.github/workflows/phase1-ci.yml`](../.github/workflows/phase1-ci.yml).

Product app: **Phase 6** [`phase6/`](../phase6/README.md) (`.\run.ps1 -Surface`). Phases 5–6 are implemented in separate folders per architecture.
