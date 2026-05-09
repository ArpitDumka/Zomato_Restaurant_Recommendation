"""LLM engine tests (mocked OpenAI)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from zomato_canonical.model import RestaurantRecord
from zomato_filter.preferences import UserPreferences

from zomato_llm.engine import rank_and_explain


def _rec(rid: str, name: str = "N") -> RestaurantRecord:
    return RestaurantRecord(
        restaurant_id=rid,
        name=name,
        city_listed="C",
        location_area=None,
        cuisines_display="Italian",
        cuisines_tokens=("italian",),
        rating=4.0,
        cost_for_two_inr=500,
        budget_band="low",
        url=None,
        address="a",
        votes=1,
        rest_type=None,
        online_order=None,
        book_table=None,
    )


def test_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    prefs = UserPreferences()
    out = rank_and_explain([_rec("x")], prefs, top_k=2)
    assert out.used_llm is False
    assert len(out.picks) == 1
    assert out.picks[0].restaurant_id == "x"


def test_llm_happy_path(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    prefs = UserPreferences(city="C")
    cands = [_rec("id1", "A"), _rec("id2", "B")]
    payload = {
        "items": [
            {"restaurant_id": "id2", "rank": 1, "explanation": "Closer match."},
            {"restaurant_id": "id1", "rank": 2, "explanation": "Also good."},
        ],
        "summary": "Two picks.",
    }
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=json.dumps(payload)))]

    with patch("zomato_llm.engine.OpenAI") as m_client:
        m_inst = MagicMock()
        m_client.return_value = m_inst
        m_inst.chat.completions.create.return_value = mock_resp
        out = rank_and_explain(cands, prefs, top_k=2)

    assert out.used_llm is True
    assert out.summary == "Two picks."
    assert [p.restaurant_id for p in out.picks] == ["id2", "id1"]
    assert out.picks[0].name == "B"


def test_llm_invalid_json_falls_back(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    prefs = UserPreferences()
    cands = [_rec("only")]
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="not-json"))]

    with patch("zomato_llm.engine.OpenAI") as m_client:
        m_inst = MagicMock()
        m_client.return_value = m_inst
        m_inst.chat.completions.create.return_value = mock_resp
        out = rank_and_explain(cands, prefs, top_k=1)

    assert out.used_llm is False
    assert out.fallback_reason == "llm_error"
