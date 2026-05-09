"""Canonical record and dedupe tests."""

from zomato_canonical.normalize import (
    dedupe_restaurant_records,
    normalize_raw_row,
    stable_restaurant_id,
)


def _minimal_raw(**overrides: object) -> dict:
    base = {
        "name": "Cafe Test",
        "listed_in(city)": "Banashankari",
        "location": "Main Road",
        "cuisines": "Italian, Cafe",
        "rate": "4.2/5",
        "approx_cost(for two people)": "600",
        "url": "https://zomato.com/x",
        "address": "1 St",
        "votes": 100,
        "rest_type": "Casual Dining",
        "online_order": "Yes",
        "book_table": "No",
    }
    base.update(overrides)
    return base


def test_normalize_raw_row_basic() -> None:
    r = normalize_raw_row(_minimal_raw())
    assert r is not None
    assert r.name == "Cafe Test"
    assert r.restaurant_id == "https://zomato.com/x"
    assert r.rating == 4.2
    assert r.cost_for_two_inr == 600
    assert r.budget_band == "medium"
    assert r.cuisines_tokens == ("italian", "cafe")
    assert r.votes == 100


def test_normalize_drops_empty_name() -> None:
    assert normalize_raw_row(_minimal_raw(name="  ")) is None
    assert normalize_raw_row(_minimal_raw(name="")) is None


def test_stable_id_hash_without_url() -> None:
    r = normalize_raw_row(_minimal_raw(url=""))
    assert r is not None
    assert r.restaurant_id.startswith("h:")
    assert len(r.restaurant_id) == 2 + 24


def test_stable_restaurant_id_deterministic() -> None:
    a = stable_restaurant_id(url=None, name="N", address="A", city_listed="C")
    b = stable_restaurant_id(url=None, name="N", address="A", city_listed="C")
    assert a == b
    assert a.startswith("h:")


def test_dedupe_keeps_first() -> None:
    r1 = normalize_raw_row(_minimal_raw(name="A", url="https://a"))
    r2 = normalize_raw_row(_minimal_raw(name="B", url="https://a"))
    assert r1 and r2
    out = dedupe_restaurant_records([r1, r2])
    assert len(out) == 1
    assert out[0].name == "A"


def test_votes_coerce_string() -> None:
    r = normalize_raw_row(_minimal_raw(votes="42"))
    assert r is not None
    assert r.votes == 42
