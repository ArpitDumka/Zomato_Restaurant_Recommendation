"""Shared :class:`RestaurantRecord` fixtures for Phase 4 tests."""

from __future__ import annotations

import pytest
from zomato_canonical.model import RestaurantRecord


@pytest.fixture
def sample_records() -> list[RestaurantRecord]:
    return [
        RestaurantRecord(
            restaurant_id="u1",
            name="Alpha",
            city_listed="Banashankari",
            location_area="A1",
            cuisines_display="North Indian, Chinese",
            cuisines_tokens=("north indian", "chinese"),
            rating=4.2,
            cost_for_two_inr=600,
            budget_band="medium",
            url="https://a",
            address="1",
            votes=10,
            rest_type="Casual Dining",
            online_order="Yes",
            book_table="No",
        ),
        RestaurantRecord(
            restaurant_id="u2",
            name="Beta",
            city_listed="banashankari",
            location_area=None,
            cuisines_display="Italian, Cafe",
            cuisines_tokens=("italian", "cafe"),
            rating=3.5,
            cost_for_two_inr=400,
            budget_band="low",
            url="https://b",
            address="2",
            votes=5,
            rest_type=None,
            online_order=None,
            book_table=None,
        ),
        RestaurantRecord(
            restaurant_id="u3",
            name="Gamma",
            city_listed="BTM",
            location_area=None,
            cuisines_display="Chinese",
            cuisines_tokens=("chinese",),
            rating=None,
            cost_for_two_inr=None,
            budget_band="unknown",
            url=None,
            address="3",
            votes=None,
            rest_type=None,
            online_order=None,
            book_table=None,
        ),
        RestaurantRecord(
            restaurant_id="u4",
            name="Delta",
            city_listed="Banashankari",
            location_area=None,
            cuisines_display="Mughlai",
            cuisines_tokens=("mughlai",),
            rating=4.2,
            cost_for_two_inr=1200,
            budget_band="high",
            url="https://d",
            address="4",
            votes=1,
            rest_type=None,
            online_order=None,
            book_table=None,
        ),
    ]
