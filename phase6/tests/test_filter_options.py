"""Filter snapshot helpers (optional env caps)."""

from __future__ import annotations

import pytest
from zomato_canonical import RawFilterScanAcc, RestaurantRecord
from zomato_canonical.normalize import cuisines_tokens_from_display

from zomato_surface.filter_options import (
    build_filter_snapshot,
    filter_snapshot_from_full_scan_accumulator,
)


def _minimal_record(
    *,
    city: str,
    cuisines_display: str,
    restaurant_id: str = "r1",
) -> RestaurantRecord:
    return RestaurantRecord(
        restaurant_id=restaurant_id,
        name="Test",
        city_listed=city,
        location_area=None,
        cuisines_display=cuisines_display,
        cuisines_tokens=cuisines_tokens_from_display(cuisines_display),
        rating=4.0,
        cost_for_two_inr=500,
        budget_band="medium",
        url=None,
        address="",
        votes=None,
        rest_type=None,
        online_order=None,
        book_table=None,
    )


def test_build_filter_snapshot_all_cuisines_keeps_cities() -> None:
    recs = [
        _minimal_record(
            city="Bangalore",
            cuisines_display="North Indian, Arabian, Italian",
            restaurant_id="a",
        ),
        _minimal_record(
            city="Mumbai",
            cuisines_display="Chinese, Lebanese",
            restaurant_id="b",
        ),
    ]
    snap = build_filter_snapshot(recs, scan_seconds=0.05)
    assert snap.cities == ("Bangalore", "Mumbai")
    assert snap.cuisines == (
        "arabian",
        "chinese",
        "italian",
        "lebanese",
        "north indian",
    )


def test_full_scan_snapshot_includes_all_cuisines() -> None:
    acc = RawFilterScanAcc()
    acc.cities.update({"Pune", "Delhi"})
    acc.city_counts.update({"Pune": 3, "Delhi": 2})
    acc.cuisines.update({"south indian", "moroccan", "biryani"})
    acc.cuisine_counts.update({"south indian": 2, "moroccan": 1, "biryani": 4})
    snap = filter_snapshot_from_full_scan_accumulator(
        acc, normalized_row_count=99, scan_seconds=0.1
    )
    assert snap.cities == ("Delhi", "Pune")
    assert snap.cuisines == ("biryani", "moroccan", "south indian")


def test_filter_snapshot_city_cap_by_frequency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOMATO_FILTER_MAX_CITIES", "2")
    for key in (
        "RAILWAY_ENVIRONMENT_ID",
        "RAILWAY_PROJECT_ID",
        "RAILWAY_SERVICE_ID",
    ):
        monkeypatch.delenv(key, raising=False)
    acc = RawFilterScanAcc()
    acc.cities.update({"Rareburg", "Metro", "Smallville"})
    acc.city_counts.update({"Rareburg": 1, "Metro": 100, "Smallville": 5})
    snap = filter_snapshot_from_full_scan_accumulator(
        acc, normalized_row_count=1, scan_seconds=0.0
    )
    assert snap.cities == ("Metro", "Smallville")


def test_city_cap_zero_means_unlimited_on_railway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ZOMATO_FILTER_MAX_CITIES", "0")
    monkeypatch.setenv("RAILWAY_ENVIRONMENT_ID", "x")
    acc = RawFilterScanAcc()
    acc.cities.update({"B", "A"})
    acc.city_counts.update({"A": 9, "B": 1})
    snap = filter_snapshot_from_full_scan_accumulator(
        acc, normalized_row_count=1, scan_seconds=0.0
    )
    assert snap.cities == ("A", "B")
