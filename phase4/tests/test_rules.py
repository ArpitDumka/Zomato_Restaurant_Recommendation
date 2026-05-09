"""Filter rules (fixtures only, no Hub)."""

from zomato_canonical.model import RestaurantRecord

from zomato_filter.preferences import UserPreferences
from zomato_filter.rules import filter_restaurant_records, record_matches_preferences


def test_city_case_insensitive(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(city="BANASHANKARI")
    out = filter_restaurant_records(sample_records, prefs)
    names = {r.name for r in out}
    assert names == {"Alpha", "Beta", "Delta"}


def test_cuisine_substring(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(cuisine_query="italian")
    out = filter_restaurant_records(sample_records, prefs)
    assert [r.name for r in out] == ["Beta"]


def test_min_rating_excludes_null(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(min_rating=3.0)
    out = filter_restaurant_records(sample_records, prefs)
    assert "Gamma" not in {r.name for r in out}


def test_budget_band_strict(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(budget_band="low")
    out = filter_restaurant_records(sample_records, prefs)
    assert [r.name for r in out] == ["Beta"]


def test_combined_filters(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(
        city="Banashankari",
        cuisine_query="indian",
        min_rating=4.0,
        budget_band="medium",
    )
    out = filter_restaurant_records(sample_records, prefs)
    assert [r.name for r in out] == ["Alpha"]


def test_empty_prefs_passes_all(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences()
    assert len(filter_restaurant_records(sample_records, prefs)) == len(sample_records)


def test_min_rating_boundary(
    sample_records: list[RestaurantRecord],
) -> None:
    alpha = sample_records[0]
    assert record_matches_preferences(alpha, UserPreferences(min_rating=4.2))
    assert not record_matches_preferences(alpha, UserPreferences(min_rating=4.3))
