"""Parser and budget-band boundary tests (Phase 3)."""

import pytest

from zomato_canonical.parsers import cost_to_budget_band, parse_cost_inr, parse_rating
from zomato_canonical.policy import LOW_MAX_INR, MEDIUM_MAX_INR


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("4.1/5", 4.1),
        ("4/5", 4.0),
        ("  3.25/5  ", 3.25),
        ("5", 5.0),
        ("", None),
        (None, None),
        ("NEW", None),
        ("-", None),
    ],
)
def test_parse_rating(raw: object, expected: float | None) -> None:
    assert parse_rating(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("800", 800),
        ("1,200", 1200),
        ("₹500", 500),
        ("", None),
        (None, None),
        ("abc", None),
    ],
)
def test_parse_cost_inr(raw: object, expected: int | None) -> None:
    assert parse_cost_inr(raw) == expected


def test_budget_band_boundaries() -> None:
    assert cost_to_budget_band(None) == "unknown"
    assert cost_to_budget_band(LOW_MAX_INR) == "low"
    assert cost_to_budget_band(LOW_MAX_INR + 1) == "medium"
    assert cost_to_budget_band(MEDIUM_MAX_INR) == "medium"
    assert cost_to_budget_band(MEDIUM_MAX_INR + 1) == "high"
