"""Load the full HF split once; share normalized rows for UI options and recommend."""

from __future__ import annotations

import logging
import os
import sys
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

# Railway: small plans OOM with ~25k full RestaurantRecord rows + materialized HF.
# Override with ZOMATO_RAILWAY_DEFAULT_CAP or ZOMATO_MAX_CATALOG_ROWS when you have RAM.
_DEFAULT_RAILWAY_CATALOG_CAP = 12_000
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


def warm_catalog_at_startup() -> bool:
    """
    Load the catalog during app startup (async executor) so the first HTTP client
    does not hit a long blocking load or worker kill mid-request.

    On Railway, default **on**. Set ``ZOMATO_CATALOG_WARMUP=0`` to skip (faster
    process boot; first API call pays the load cost).
    """
    raw = os.environ.get("ZOMATO_CATALOG_WARMUP", "").strip().lower()
    if raw in ("0", "false", "no", "off"):
        return False
    if raw in ("1", "true", "yes", "on"):
        return True
    return _running_on_railway()


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


def _process_max_rss_bytes() -> int | None:
    """Best-effort peak RSS for this process (platform-dependent)."""
    try:
        import resource

        ru = resource.getrusage(resource.RUSAGE_SELF)
        rss = ru.ru_maxrss
        if sys.platform == "darwin":
            return rss
        if sys.platform.startswith("linux"):
            return rss * 1024
        if rss > 0:
            return rss
    except (AttributeError, OSError, ValueError):
        pass
    return None


def _log_catalog_footprint(
    *,
    normalized_rows: int,
    raw_rows: int,
    cap: int | None,
) -> None:
    """Heuristic size + RSS after load (for Railway OOM triage)."""
    approx_mb = normalized_rows * 1.1 / 1024.0
    rss = _process_max_rss_bytes()
    rss_mb = f"{rss / (1024 * 1024):.1f} MiB" if rss else "n/a"
    logger.info(
        "catalog footprint: normalized_rows=%s raw_rows_seen=%s cap=%s "
        "heuristic_heap-ish≈%.1f MiB ru_maxrss≈%s",
        normalized_rows,
        raw_rows,
        cap,
        approx_mb,
        rss_mb,
    )


def _railway_default_cap() -> int:
    raw = os.environ.get("ZOMATO_RAILWAY_DEFAULT_CAP", "").strip()
    if raw:
        try:
            return max(1000, min(int(raw), _MAX_CAP))
        except ValueError:
            pass
    return _DEFAULT_RAILWAY_CATALOG_CAP


def _catalog_hf_streaming() -> bool:
    """
    Hugging Face iteration mode for the catalog load.

    On **Railway**, default ``True`` (streaming): lower peak RAM — avoids holding the
    full Arrow table plus tens of thousands of dict rows at once.

    Elsewhere, default ``False`` (materialized): faster iteration after cache is warm.

    Override with ``ZOMATO_HF_STREAMING=0`` or ``1`` in any environment.
    """
    raw = os.environ.get("ZOMATO_HF_STREAMING", "").strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return _running_on_railway()


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
        hf_stream = _catalog_hf_streaming()
        logger.info("catalog HF load: streaming=%s", hf_stream)
        # One pass: all-row filter distincts; normalize only until memory cap.
        for raw in iter_raw_rows(streaming=hf_stream):
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
        logger.info(
            "catalog materialized: raw_iter=%s normalized=%s in %.2fs (streamed%s)",
            raw_seen,
            len(_bundle.records),
            elapsed,
            f", cap={cap} ({cap_reason})" if cap is not None else "",
        )
        _log_catalog_footprint(
            normalized_rows=len(_bundle.records),
            raw_rows=raw_seen,
            cap=cap,
        )
        return _bundle


def all_records() -> Sequence[RestaurantRecord]:
    """Shorthand for the frozen record tuple (full split, normalized)."""
    return get_catalog().records
