"""Web preview (FastAPI) smoke tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from zomato_recommend.web.app import create_app


def test_api_health() -> None:
    c = TestClient(create_app())
    r = c.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["version"]
    assert len(body["phases"]) == 7


def test_index_html() -> None:
    c = TestClient(create_app())
    r = c.get("/")
    assert r.status_code == 200
    assert "preview" in r.text.lower()


def test_api_restaurants_mocked() -> None:
    fake = [{"name": "Test Cafe", "cuisines": "Italian", "rate": "4.0/5"}]
    with (
        patch("zomato_recommend.web.app._ingest_available", return_value=True),
        patch("zomato_raw_ingest.load_raw_rows", return_value=fake),
    ):
        c = TestClient(create_app())
        r = c.get("/api/restaurants?limit=3")
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["rows"] == fake


def test_api_restaurants_limit_validation() -> None:
    c = TestClient(create_app())
    r = c.get("/api/restaurants?limit=0")
    assert r.status_code == 400
