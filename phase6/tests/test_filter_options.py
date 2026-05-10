"""Filter snapshot helpers (niche cuisine trimming for UI)."""

from __future__ import annotations

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


def test_build_filter_snapshot_drops_niche_cuisines_keeps_cities() -> None:
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
    assert snap.cuisines == ("chinese", "italian", "north indian")
    assert "arabian" not in snap.cuisines
    assert "lebanese" not in snap.cuisines


def test_full_scan_snapshot_drops_niche_cuisines() -> None:
    acc = RawFilterScanAcc()
    acc.cities.update({"Pune", "Delhi"})
    acc.cuisines.update({"south indian", "moroccan", "biryani"})
    snap = filter_snapshot_from_full_scan_accumulator(
        acc, normalized_row_count=99, scan_seconds=0.1
    )
    assert snap.cities == ("Delhi", "Pune")
    assert snap.cuisines == ("biryani", "south indian")
    assert "moroccan" not in snap.cuisines
