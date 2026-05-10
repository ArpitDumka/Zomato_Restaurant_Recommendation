"""Phase 6 API smoke tests (service mocked)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from zomato_llm.schema import LlmRankingResult, RankedPick

from zomato_surface.app import create_app
from zomato_surface.filter_options import FilterOptionsSnapshot


def test_health() -> None:
    c = TestClient(create_app())
    r = c.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_cors_allow_all_on_railway_without_cors_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RAILWAY_SERVICE_ID", "srv")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.delenv("CORS_ORIGIN_REGEX", raising=False)
    monkeypatch.delenv("ZOMATO_STRICT_CORS", raising=False)
    c = TestClient(create_app())
    r = c.get("/api/health", headers={"Origin": "https://app.vercel.app"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "*"


def test_cors_strict_disables_allow_all_on_railway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RAILWAY_SERVICE_ID", "srv")
    monkeypatch.setenv("ZOMATO_STRICT_CORS", "1")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.delenv("CORS_ORIGIN_REGEX", raising=False)
    c = TestClient(create_app())
    r = c.get("/api/health", headers={"Origin": "https://app.vercel.app"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") != "*"


def test_filter_options_mocked() -> None:
    snap = FilterOptionsSnapshot(
        cities=("Banashankari", "BTM"),
        cuisines=("italian", "north indian"),
        min_ratings=(3.5, 4.0),
        budget_bands=("low", "medium"),
        cost_for_two_inr_min=200,
        cost_for_two_inr_max=1800,
        normalized_row_count=120,
        scan_seconds=1.25,
    )
    with patch("zomato_surface.app.get_filter_options", return_value=snap):
        c = TestClient(create_app())
        r = c.get("/api/filter-options")
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["cities"] == ["Banashankari", "BTM"]
    assert j["cuisines"] == ["italian", "north indian"]
    assert j["min_ratings"] == [3.5, 4.0]
    assert j["normalized_row_count"] == 120
    assert len(j["budget_options"]) == 2
    assert j["budget_options"][0]["value"] == "low"


def test_recommend_mocked() -> None:
    result = LlmRankingResult(
        picks=[
            RankedPick(
                restaurant_id="id1",
                rank=1,
                explanation="Nice fit.",
                name="Cafe",
                cuisine="Italian",
                rating=4.2,
                cost_for_two_inr=500,
            )
        ],
        summary="One pick.",
        used_llm=True,
        fallback_reason=None,
        latency_ms=12.0,
    )
    with patch(
        "zomato_surface.app.recommend",
        return_value=(3, 1, result),
    ):
        c = TestClient(create_app())
        r = c.post(
            "/api/recommend",
            json={"city": "X", "top_k": 5, "llm_candidate_cap": 250},
        )
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["matched_count"] == 3
    assert j["result"]["picks"][0]["name"] == "Cafe"
