"""Load the full HF split once; share normalized rows for UI options and recommend."""

from __future__ import annotations

import gc
import logging
import os
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass

from zomato_canonical import (
    RawFilterScanAcc,
    RestaurantRecord,
    merge_raw_row_into_filter_scan,
    merge_record_into_filter_scan,
    normalize_raw_row,
)
from zomato_raw_ingest import iter_raw_rows

from zomato_surface.filter_options import (
    FilterOptionsSnapshot,
    filter_snapshot_from_full_scan_accumulator,
)

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_bundle: CatalogBundle | None = None

# Railway: without an explicit cap, stay under typical small-instance RAM.
_DEFAULT_RAILWAY_CATALOG_CAP = 25_000
_MAX_CAP = 500_000


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _running_on_railway() -> bool:
    return bool(
        os.environ.get("RAILWAY_ENVIRONMENT_ID")
        or os.environ.get("RAILWAY_PROJECT_ID")
        or os.environ.get("RAILWAY_SERVICE_ID")
    )


def _catalog_row_cap() -> tuple[int | None, str | None]:
    """
    Return (max normalized rows or None for unlimited, reason label for logs).

    - ``ZOMATO_FULL_CATALOG=1`` → no cap (needs enough RAM, ~52k rows).
    - ``ZOMATO_MAX_CATALOG_ROWS=N`` (N > 0) → cap at N.
    - ``ZOMATO_MAX_CATALOG_ROWS=0`` → treat as "use host default" (Railway default cap).
    - On Railway, if nothing above applies → ``ZOMATO_RAILWAY_DEFAULT_CAP`` or
      :data:`_DEFAULT_RAILWAY_CATALOG_CAP`.
    - Elsewhere → no cap unless ``ZOMATO_MAX_CATALOG_ROWS`` is set.
    """
    if _env_truthy("ZOMATO_FULL_CATALOG"):
        return None, "ZOMATO_FULL_CATALOG"
    raw = os.environ.get("ZOMATO_MAX_CATALOG_ROWS", "").strip()
    if raw:
        try:
            n = int(raw)
        except ValueError:
            return None, None
        if n <= 0:
            if _running_on_railway():
                cap = _railway_default_cap()
                return cap, "railway default (ZOMATO_MAX_CATALOG_ROWS<=0)"
            return None, None
        return max(1, min(n, _MAX_CAP)), "ZOMATO_MAX_CATALOG_ROWS"
    if _running_on_railway():
        cap = _railway_default_cap()
        return cap, "railway default"
    return None, None


def _railway_default_cap() -> int:
    raw = os.environ.get("ZOMATO_RAILWAY_DEFAULT_CAP", "").strip()
    if raw:
        try:
            return max(1000, min(int(raw), _MAX_CAP))
        except ValueError:
            pass
    return _DEFAULT_RAILWAY_CATALOG_CAP


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
        cap, cap_reason = _catalog_row_cap()
        recs: list[RestaurantRecord] = []
        raw_seen = 0
        scan_acc = RawFilterScanAcc()
        # One stream: all-row filter distincts; normalize only until memory cap.
        for raw in iter_raw_rows(streaming=True):
            raw_seen += 1
            at_cap = cap is not None and len(recs) >= cap
            if at_cap:
                merge_raw_row_into_filter_scan(raw, scan_acc)
                continue
            rec = normalize_raw_row(raw)
            if rec is None:
                continue
            merge_record_into_filter_scan(rec, scan_acc)
            recs.append(rec)
            if cap is not None and len(recs) >= cap:
                logger.warning(
                    "catalog normalized rows capped at %s (cap=%s, reason=%s); "
                    "filter dropdowns still reflect full streamed split; "
                    "ZOMATO_FULL_CATALOG=1 for full ~52k in memory",
                    len(recs),
                    cap,
                    cap_reason,
                )
        elapsed = time.perf_counter() - t0
        snapshot = filter_snapshot_from_full_scan_accumulator(
            scan_acc,
            normalized_row_count=len(recs),
            scan_seconds=round(elapsed, 3),
        )
        _bundle = CatalogBundle(
            records=tuple(recs),
            filter_snapshot=snapshot,
        )
        del recs
        gc.collect()
        logger.info(
            "catalog materialized: raw_iter=%s normalized=%s in %.2fs (streamed%s)",
            raw_seen,
            len(_bundle.records),
            elapsed,
            f", cap={cap} ({cap_reason})" if cap is not None else "",
        )
        return _bundle


def all_records() -> Sequence[RestaurantRecord]:
    """Shorthand for the frozen record tuple (full split, normalized)."""
    return get_catalog().records
