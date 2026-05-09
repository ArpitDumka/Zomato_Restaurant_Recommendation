"""filter + rank + cap."""

from zomato_canonical.model import RestaurantRecord

from zomato_filter.pipeline import filter_rank_cap
from zomato_filter.preferences import UserPreferences


def test_filter_rank_cap(sample_records: list[RestaurantRecord]) -> None:
    prefs = UserPreferences(city="Banashankari", min_rating=4.0)
    out = filter_rank_cap(sample_records, prefs, max_candidates=1)
    assert len(out) == 1
    assert out[0].name == "Alpha"
