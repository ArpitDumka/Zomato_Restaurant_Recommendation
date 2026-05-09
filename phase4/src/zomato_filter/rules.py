"""Pure filter predicates over :class:`RestaurantRecord`."""

from __future__ import annotations

from collections.abc import Iterable

from zomato_canonical.model import RestaurantRecord

from zomato_filter.preferences import UserPreferences


def _norm_city(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def record_matches_preferences(
    record: RestaurantRecord,
    prefs: UserPreferences,
) -> bool:
    """Return True if ``record`` satisfies all non-null constraints in ``prefs``."""
    if prefs.city is not None and prefs.city.strip():
        if _norm_city(record.city_listed) != _norm_city(prefs.city):
            return False

    if prefs.cuisine_query is not None and prefs.cuisine_query.strip():
        if not _cuisine_matches(record, prefs.cuisine_query):
            return False

    if prefs.min_rating is not None:
        if record.rating is None:
            return False
        if record.rating < prefs.min_rating:
            return False

    if prefs.budget_band is not None:
        if record.budget_band != prefs.budget_band:
            return False

    return True


def _cuisine_matches(record: RestaurantRecord, query: str) -> bool:
    q = query.strip().casefold()
    if not q:
        return True
    disp = record.cuisines_display.casefold()
    if q in disp:
        return True
    return any(q in t or t.startswith(q) for t in record.cuisines_tokens)


def filter_restaurant_records(
    records: Iterable[RestaurantRecord],
    prefs: UserPreferences,
) -> list[RestaurantRecord]:
    """Deterministic filter; preserves input order among matches."""
    return [r for r in records if record_matches_preferences(r, prefs)]
