"""Optional pandas path (install phase2 with [pandas])."""

import pytest

from zomato_raw_ingest import load_raw_dataframe


def test_load_raw_dataframe() -> None:
    pytest.importorskip("pandas")
    df = load_raw_dataframe(8)
    assert len(df) == 8
    assert "name" in df.columns
