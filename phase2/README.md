# Phase 2 — Raw ingestion

Implements **Phase 2** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): load the Zomato-style Hugging Face dataset into memory as **raw rows** (dicts or optional DataFrame). **No normalization** — that is Phase 3.

## API

| Symbol | Purpose |
|--------|---------|
| `iter_raw_rows(...)` | Iterator of `dict` rows (streaming by default). |
| `load_raw_rows(max_rows, ...)` | List of up to `max_rows` dicts (streaming under the hood). |
| `load_raw_dataframe(max_rows, ...)` | Same, as pandas DataFrame (`[pandas]` extra). |
| `DATASET_ID` | `ManikaSaini/zomato-restaurant-recommendation` |

## Cache and reproducibility

- First run **downloads** via the Hugging Face Hub; later runs reuse the **local Hub cache** (default: user cache dir, e.g. `%USERPROFILE%\.cache\huggingface` on Windows). Same load path twice is **idempotent** with respect to network (cache hit).
- Optional: set `HF_HOME` to a folder (see `.env.example`) to keep cache next to the project; optional `HF_TOKEN` for rate limits.
- Optional `revision=` on loaders pins a dataset **git revision** (commit SHA) for reproducible snapshots.

## Install

```powershell
cd path\to\Zomato_1\phase2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
# ``[dev]`` includes pandas so ``load_raw_dataframe`` works in tests.
# Minimal runtime without pandas: pip install -e . && pip install datasets huggingface_hub
```

## Tests

```powershell
pytest
ruff check src tests
```

Tests call the real Hub (small `max_rows`); first run needs **network**.

## Exit criteria (Phase 2)

- [x] Download/stream from Hugging Face; documented cache / optional `HF_HOME`.
- [x] Single module exposes **load raw rows** as list of dicts and optional DataFrame.
- [x] Smoke tests: load **N** rows twice without crash; stable keys.

Next: **Phase 3** normalization in [`phase3/`](../phase3/README.md) (see architecture doc).
