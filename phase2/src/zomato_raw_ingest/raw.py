"""Raw ingestion from Hugging Face (Phase 2 — no normalization)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from datasets import load_dataset

# See phase0/FieldMapping.md and phase0/DatasetSpikeReport.md
DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DEFAULT_SPLIT = "train"


def iter_raw_rows(
    *,
    split: str = DEFAULT_SPLIT,
    revision: str | None = None,
    streaming: bool = True,
) -> Iterator[dict[str, Any]]:
    """
    Yield raw dataset rows as plain dicts (HF column names unchanged).

    Uses streaming by default so large splits are not loaded entirely into RAM.
    Hugging Face Hub caches downloads under HF_HOME (~/.cache/huggingface by default);
    repeated runs reuse the cache (idempotent).

    Args:
        split: Dataset split name.
        revision: Optional dataset git revision (commit SHA) for reproducibility.
        streaming: If True, iterate without a full local materialized copy.
    """
    ds = load_dataset(
        DATASET_ID,
        split=split,
        revision=revision,
        streaming=streaming,
    )
    for row in ds:
        yield dict(row)


def load_materialized_split(
    *,
    split: str = DEFAULT_SPLIT,
    revision: str | None = None,
) -> list[dict[str, Any]]:
    """
    Load the entire split into a list of dicts (non-streaming).

    First call downloads via the Hugging Face Hub; later calls use the local Hub
    cache. Use this when the full table (~52k rows for this dataset) should live
    in memory for repeated filtering (e.g. Phase 6 catalog). For bounded memory
    or one-off scans, prefer :func:`iter_raw_rows` instead.
    """
    ds = load_dataset(
        DATASET_ID,
        split=split,
        revision=revision,
        streaming=False,
    )
    to_list = getattr(ds, "to_list", None)
    if callable(to_list):
        rows = to_list()
        return [dict(r) for r in rows]
    return [dict(ds[i]) for i in range(len(ds))]


def load_raw_rows(
    max_rows: int,
    *,
    split: str = DEFAULT_SPLIT,
    revision: str | None = None,
) -> list[dict[str, Any]]:
    """
    Load up to ``max_rows`` raw dicts using a streaming iterator (memory-safe cap).

    Raises:
        ValueError: if ``max_rows`` < 1.
    """
    if max_rows < 1:
        raise ValueError("max_rows must be >= 1")
    out: list[dict[str, Any]] = []
    for row in iter_raw_rows(split=split, revision=revision, streaming=True):
        out.append(row)
        if len(out) >= max_rows:
            break
    return out


def load_raw_dataframe(
    max_rows: int,
    *,
    split: str = DEFAULT_SPLIT,
    revision: str | None = None,
):
    """
    Load up to ``max_rows`` rows as a pandas DataFrame (optional dependency).

    Requires the ``pandas`` extra: ``pip install "zomato-raw-ingest[pandas]"``.
    """
    try:
        import pandas as pd
    except ImportError as e:
        msg = (
            "load_raw_dataframe requires pandas. "
            "Install: pip install 'zomato-raw-ingest[pandas]'"
        )
        raise ImportError(msg) from e
    rows = load_raw_rows(max_rows, split=split, revision=revision)
    return pd.DataFrame(rows)
