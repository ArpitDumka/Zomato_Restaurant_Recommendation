"""Distinct filter values for the UI, derived from the materialized catalog."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from zomato_canonical import RawFilterScanAcc, RestaurantRecord
from zomato_canonical.policy import LOW_MAX_INR, MEDIUM_MAX_INR

logger = logging.getLogger(__name__)

_BUDGET_ORDER = ("low", "medium", "high", "unknown")

# Drop rare / niche cuisine tags from filter dropdowns only (search still matches raw
# data). Tokens use str.casefold(); canonical tokens from CSV are usually lowercase.
_NICHE_CUISINE_EXCLUSIONS_CASEFOLD: frozenset[str] = frozenset(
    {
        "afghan",
        "afghani",
        "african",
        "arabian",
        "armenian",
        "belgian",
        "burmese",
        "cambodian",
        "caribbean",
        "croatian",
        "czech",
        "danish",
        "dutch",
        "ethiopian",
        "filipino",
        "finnish",
        "georgian",
        "hungarian",
        "icelandic",
        "indonesian",
        "iranian",
        "iraqi",
        "irish",
        "israeli",
        "jamaican",
        "kazakh",
        "laotian",
        "lebanese",
        "libyan",
        "middle eastern",
        "mongolian",
        "moroccan",
        "nigerian",
        "north african",
        "norwegian",
        "omani",
        "peruvian",
        "persian",
        "polish",
        "portuguese",
        "qatari",
        "romanian",
        "scandinavian",
        "slovak",
        "sudanese",
        "swedish",
        "syrian",
        "tunisian",
        "ukrainian",
        "uzbek",
        "venezuelan",
        "yemeni",
    }
)


def _visible_cuisines_sorted(cuisines: set[str]) -> tuple[str, ...]:
    kept = [
        c
        for c in cuisines
        if (s := c.strip()) and s.casefold() not in _NICHE_CUISINE_EXCLUSIONS_CASEFOLD
    ]
    return tuple(sorted(kept, key=str.casefold))


@dataclass(frozen=True, slots=True)
class FilterOptionsSnapshot:
    """Distinct values observed from normalized restaurant rows."""

    cities: tuple[str, ...]
    cuisines: tuple[str, ...]
    min_ratings: tuple[float, ...]
    budget_bands: tuple[str, ...]
    cost_for_two_inr_min: int | None
    cost_for_two_inr_max: int | None
    normalized_row_count: int
    scan_seconds: float


def budget_band_label(band: str) -> str:
    """Human-readable budget band with INR ranges (see zomato_canonical.policy)."""
    if band == "low":
        return f"Low — up to {LOW_MAX_INR} INR (two)"
    if band == "medium":
        return f"Medium — {LOW_MAX_INR + 1}–{MEDIUM_MAX_INR} INR (two)"
    if band == "high":
        return f"High — above {MEDIUM_MAX_INR} INR (two)"
    return "Unknown — cost not listed or unparsed"


def build_filter_snapshot(
    records: Sequence[RestaurantRecord],
    *,
    scan_seconds: float,
) -> FilterOptionsSnapshot:
    """Compute dropdown distincts from already-normalized rows."""
    cities: set[str] = set()
    cuisines: set[str] = set()
    ratings_rounded: set[float] = set()
    bands: set[str] = set()
    cost_min: int | None = None
    cost_max: int | None = None

    for rec in records:
        c = rec.city_listed.strip()
        if c:
            cities.add(c)
        for tok in rec.cuisines_tokens:
            t = tok.strip()
            if t:
                cuisines.add(t)
        if rec.rating is not None:
            ratings_rounded.add(round(rec.rating, 1))
        bands.add(rec.budget_band)
        if rec.cost_for_two_inr is not None:
            v = rec.cost_for_two_inr
            cost_min = v if cost_min is None else min(cost_min, v)
            cost_max = v if cost_max is None else max(cost_max, v)

    cities_sorted = tuple(sorted(cities, key=str.casefold))
    cuisines_sorted = _visible_cuisines_sorted(cuisines)
    ratings_sorted = tuple(sorted(ratings_rounded))
    bands_sorted = tuple(b for b in _BUDGET_ORDER if b in bands)
    n = len(records)

    logger.info(
        "filter snapshot: rows=%s cities=%s cuisines=%s ratings=%s bands=%s",
        n,
        len(cities_sorted),
        len(cuisines_sorted),
        len(ratings_sorted),
        len(bands_sorted),
    )

    return FilterOptionsSnapshot(
        cities=cities_sorted,
        cuisines=cuisines_sorted,
        min_ratings=ratings_sorted,
        budget_bands=bands_sorted,
        cost_for_two_inr_min=cost_min,
        cost_for_two_inr_max=cost_max,
        normalized_row_count=n,
        scan_seconds=round(scan_seconds, 3),
    )


def filter_snapshot_from_full_scan_accumulator(
    acc: RawFilterScanAcc,
    *,
    normalized_row_count: int,
    scan_seconds: float,
) -> FilterOptionsSnapshot:
    """
    Build dropdown snapshot from a scan over **all** raw rows.

    ``normalized_row_count`` is the in-memory catalog size (may be capped); distincts
    reflect the full stream passed into ``acc``.
    """
    cities_sorted = tuple(sorted(acc.cities, key=str.casefold))
    cuisines_sorted = _visible_cuisines_sorted(acc.cuisines)
    ratings_sorted = tuple(sorted(acc.ratings))
    bands_sorted = tuple(b for b in _BUDGET_ORDER if b in acc.bands)

    logger.info(
        "filter snapshot (full scan): normalized_stored=%s cities=%s cuisines=%s "
        "ratings=%s bands=%s",
        normalized_row_count,
        len(cities_sorted),
        len(cuisines_sorted),
        len(ratings_sorted),
        len(bands_sorted),
    )

    return FilterOptionsSnapshot(
        cities=cities_sorted,
        cuisines=cuisines_sorted,
        min_ratings=ratings_sorted,
        budget_bands=bands_sorted,
        cost_for_two_inr_min=acc.cost_min,
        cost_for_two_inr_max=acc.cost_max,
        normalized_row_count=normalized_row_count,
        scan_seconds=round(scan_seconds, 3),
    )


def get_filter_options(*, force_refresh: bool = False) -> FilterOptionsSnapshot:
    """Distincts from the shared in-memory catalog (loads full split on first use)."""
    from zomato_surface.catalog import get_catalog

    return get_catalog(force_refresh=force_refresh).filter_snapshot


def filter_options_response_dict(snapshot: FilterOptionsSnapshot) -> dict:
    """JSON-serializable payload for GET /api/filter-options."""
    budget_options = [
        {"value": b, "label": budget_band_label(b)} for b in snapshot.budget_bands
    ]
    return {
        "ok": True,
        "cities": list(snapshot.cities),
        "cuisines": list(snapshot.cuisines),
        "min_ratings": list(snapshot.min_ratings),
        "budget_options": budget_options,
        "cost_for_two_inr_min": snapshot.cost_for_two_inr_min,
        "cost_for_two_inr_max": snapshot.cost_for_two_inr_max,
        "normalized_row_count": snapshot.normalized_row_count,
        "scan_seconds": snapshot.scan_seconds,
    }
