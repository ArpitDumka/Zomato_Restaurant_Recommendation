"""Load the full HF split once; share normalized rows for UI options and recommend."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass

from zomato_canonical import RestaurantRecord, normalize_raw_row
from zomato_raw_ingest import load_materialized_split

from zomato_surface.filter_options import FilterOptionsSnapshot, build_filter_snapshot

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_bundle: CatalogBundle | None = None


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
        raw_rows = load_materialized_split()
        recs: list[RestaurantRecord] = []
        for raw in raw_rows:
            rec = normalize_raw_row(raw)
            if rec is not None:
                recs.append(rec)
        elapsed = time.perf_counter() - t0
        snapshot = build_filter_snapshot(recs, scan_seconds=round(elapsed, 3))
        _bundle = CatalogBundle(
            records=tuple(recs),
            filter_snapshot=snapshot,
        )
        logger.info(
            "catalog materialized: raw_rows=%s normalized=%s in %.2fs",
            len(raw_rows),
            len(recs),
            elapsed,
        )
        return _bundle


def all_records() -> Sequence[RestaurantRecord]:
    """Shorthand for the frozen record tuple (full split, normalized)."""
    return get_catalog().records
