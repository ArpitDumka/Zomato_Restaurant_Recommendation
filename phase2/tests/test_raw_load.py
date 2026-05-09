"""Phase 2: raw load smoke tests (requires network + HF Hub on first run)."""

from unittest.mock import patch

from zomato_raw_ingest import DATASET_ID, load_raw_rows
from zomato_raw_ingest.raw import iter_raw_rows, load_materialized_split


def test_dataset_id_matches_phase0_charter() -> None:
    assert DATASET_ID == "ManikaSaini/zomato-restaurant-recommendation"


def test_load_raw_rows_returns_expected_count_and_keys() -> None:
    n = 25
    rows = load_raw_rows(n)
    assert len(rows) == n
    keys = set(rows[0].keys())
    assert "name" in keys
    assert "cuisines" in keys
    assert "listed_in(city)" in keys
    assert "approx_cost(for two people)" in keys
    assert "rate" in keys


def test_load_twice_idempotent_shape() -> None:
    """Same path twice: second call uses HF cache and matches row shape."""
    a = load_raw_rows(12)
    b = load_raw_rows(12)
    assert len(a) == len(b) == 12
    assert set(a[0].keys()) == set(b[0].keys())


def test_iter_raw_rows_first_row_is_dict() -> None:
    it = iter_raw_rows()
    row = next(it)
    assert isinstance(row, dict)
    assert "url" in row


def test_load_materialized_split_uses_non_streaming_dataset() -> None:
    class _FakeDs:
        def to_list(self) -> list[dict]:
            return [{"name": "A", "listed_in(city)": "X"}, {"name": "B"}]

    with patch("zomato_raw_ingest.raw.load_dataset", return_value=_FakeDs()):
        rows = load_materialized_split()
    assert len(rows) == 2
    assert rows[0]["name"] == "A"
