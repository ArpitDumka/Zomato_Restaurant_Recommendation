"""Convenience: filter then rank/cap."""

from __future__ import annotations

from collections.abc import Iterable

from zomato_canonical.model import RestaurantRecord

from zomato_filter.preferences import UserPreferences
from zomato_filter.rank import rank_by_rating_cap
from zomato_filter.rules import filter_restaurant_records


def filter_rank_cap(
    records: Iterable[RestaurantRecord],
    prefs: UserPreferences,
    max_candidates: int,
) -> list[RestaurantRecord]:
    """Apply :func:`filter_restaurant_records` then :func:`rank_by_rating_cap`."""
    filtered = filter_restaurant_records(records, prefs)
    return rank_by_rating_cap(filtered, max_candidates)
