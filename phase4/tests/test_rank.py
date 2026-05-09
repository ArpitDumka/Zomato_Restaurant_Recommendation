"""Ranking and cap."""

import pytest
from zomato_canonical.model import RestaurantRecord

from zomato_filter.rank import rank_by_rating_cap, stub_explanation


def test_stub_explanation() -> None:
    assert stub_explanation() == "Ranked by rating."


def test_rank_by_rating_desc_then_name(sample_records: list[RestaurantRecord]) -> None:
    out = rank_by_rating_cap(sample_records, max_candidates=10)
    # Alpha and Delta both 4.2; Alpha before Delta alphabetically
    assert [r.name for r in out[:2]] == ["Alpha", "Delta"]
    assert out[-1].name == "Gamma"  # no rating last


def test_cap_limits_length(sample_records: list[RestaurantRecord]) -> None:
    out = rank_by_rating_cap(sample_records, max_candidates=2)
    assert len(out) == 2


def test_cap_invalid() -> None:
    with pytest.raises(ValueError):
        rank_by_rating_cap([], max_candidates=0)
