"""Load the full HF split once; share normalized rows for UI options and recommend."""

from __future__ import annotations

import gc
import logging
import os
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass

from zomato_canonical import RestaurantRecord, normalize_raw_row
from zomato_raw_ingest import iter_raw_rows

from zomato_surface.filter_options import FilterOptionsSnapshot, build_filter_snapshot

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_bundle: CatalogBundle | None = None


def _catalog_row_cap() -> int | None:
    """
    Optional cap for low-RAM hosts (e.g. small cloud instances).

    Set ``ZOMATO_MAX_CATALOG_ROWS`` to a positive int to load at most that many
    normalized rows. Omit or empty for full split (~52k rows).
    """
    raw = os.environ.get("ZOMATO_MAX_CATALOG_ROWS", "").strip()
    if not raw:
        return None
    try:
        n = int(raw)
    except ValueError:
        return None
    return max(1, min(n, 500_000))


@dataclass(frozen=True, slots=True)
class CatalogBundle:
    """In-memory full catalog after one Hub materialized load + normalize."""

    records: tuple[RestaurantRecord, ...]
    filter_snapshot: FilterOptionsSnapshot


def get_catalog(*, force_refresh: bool = False) -> CatalogBundle:
    """
    Return cached catalog, loading the full split on first use.

    Thread-safe; concurrent first callers block on a single load.
    """
    global _bundle
    with _lock:
        if _bundle is not None and not force_refresh:
            return _bundle
        t0 = time.perf_counter()
        cap = _catalog_row_cap()
        recs: list[RestaurantRecord] = []
        raw_seen = 0
        # Stream rows from Hugging Face (no second full copy as a Python list of dicts).
        for raw in iter_raw_rows(streaming=True):
            raw_seen += 1
            rec = normalize_raw_row(raw)
            if rec is None:
                continue
            recs.append(rec)
            if cap is not None and len(recs) >= cap:
                logger.warning(
                    "catalog stopped at %s normalized rows "
                    "(ZOMATO_MAX_CATALOG_ROWS=%s); filter options are subset-only",
                    len(recs),
                    cap,
                )
                break
        elapsed = time.perf_counter() - t0
        snapshot = build_filter_snapshot(recs, scan_seconds=round(elapsed, 3))
        _bundle = CatalogBundle(
            records=tuple(recs),
            filter_snapshot=snapshot,
        )
        gc.collect()
        logger.info(
            "catalog materialized: raw_iter=%s normalized=%s in %.2fs (streamed%s)",
            raw_seen,
            len(recs),
            elapsed,
            f", cap={cap}" if cap is not None else "",
        )
        return _bundle


def all_records() -> Sequence[RestaurantRecord]:
    """Shorthand for the frozen record tuple (full split, normalized)."""
    return get_catalog().records
