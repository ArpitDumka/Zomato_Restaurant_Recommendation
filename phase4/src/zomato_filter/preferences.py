"""User preference payload (web UI / API shape for Phase 4)."""

from __future__ import annotations

from dataclasses import dataclass

from zomato_canonical.model import BudgetBand


@dataclass(frozen=True, slots=True)
class UserPreferences:
    """
    Filters applied to :class:`zomato_canonical.RestaurantRecord`.

    ``None`` means no constraint for that field.
    ``min_rating`` is only enforced when it is set.
    """

    city: str | None = None
    cuisine_query: str | None = None
    additional_preferences: str | None = None
    min_rating: float | None = None
    budget_band: BudgetBand | None = None
