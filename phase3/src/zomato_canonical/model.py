"""Canonical restaurant record — downstream phases use this, not raw HF dicts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BudgetBand = Literal["low", "medium", "high", "unknown"]


@dataclass(frozen=True, slots=True)
class RestaurantRecord:
    """Stable, normalized row aligned with phase0 FieldMapping."""

    restaurant_id: str
    name: str
    city_listed: str
    location_area: str | None
    cuisines_display: str
    cuisines_tokens: tuple[str, ...]
    rating: float | None
    cost_for_two_inr: int | None
    budget_band: BudgetBand
    url: str | None
    address: str
    votes: int | None
    rest_type: str | None
    online_order: str | None
    book_table: str | None
