"""Rank by rating (desc) with stable tie-breakers; cap to M candidates."""

from __future__ import annotations

from collections.abc import Sequence

from zomato_canonical.model import RestaurantRecord

STUB_EXPLANATION = "Ranked by rating."


def stub_explanation() -> str:
    """Fixed copy for Phase 4 demos before the LLM (Phase 5)."""
    return STUB_EXPLANATION


def rank_by_rating_cap(
    records: Sequence[RestaurantRecord],
    max_candidates: int,
) -> list[RestaurantRecord]:
    """
    Sort by rating descending (unknown rating last), then name, then id.

    Raises:
        ValueError: if ``max_candidates`` < 1.
    """
    if max_candidates < 1:
        raise ValueError("max_candidates must be >= 1")

    def sort_key(r: RestaurantRecord) -> tuple[int, float, str, str]:
        if r.rating is None:
            return (1, 0.0, r.name.casefold(), r.restaurant_id)
        return (0, -r.rating, r.name.casefold(), r.restaurant_id)

    ordered = sorted(records, key=sort_key)
    return list(ordered[:max_candidates])
