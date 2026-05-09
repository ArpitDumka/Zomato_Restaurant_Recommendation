"""FastAPI app: dashboard and JSON APIs for current project state."""

from __future__ import annotations

import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from zomato_recommend import __version__

_BASE = Path(__file__).resolve().parent


def _ingest_available() -> bool:
    try:
        import zomato_raw_ingest  # noqa: F401
    except ImportError:
        return False
    return True


def create_app() -> FastAPI:
    app = FastAPI(
        title="Zomato-inspired recommendations",
        description=(
            "Preview UI: phases 0-3 (raw sample; normalization in phase3 package)."
        ),
        version=__version__,
    )

    templates = Jinja2Templates(directory=str(_BASE / "templates"))
    app.mount(
        "/static",
        StaticFiles(directory=str(_BASE / "static")),
        name="static",
    )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_version": __version__,
            },
        )

    @app.get("/api/health")
    def api_health() -> dict:
        return {
            "ok": True,
            "version": __version__,
            "ingestion_installed": _ingest_available(),
            "phases": [
                {"id": 0, "name": "Charter & dataset spike", "done": True},
                {"id": 1, "name": "Scaffold & web preview", "done": True},
                {"id": 2, "name": "Raw HF ingestion", "done": True},
                {"id": 3, "name": "Normalization", "done": True},
                {"id": 4, "name": "Filtering", "done": True},
                {"id": 5, "name": "LLM layer", "done": True},
                {"id": 6, "name": "Full product UI", "done": True},
            ],
        }

    @app.get("/api/restaurants")
    def api_restaurants(limit: int = 15) -> JSONResponse:
        if limit < 1 or limit > 200:
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 200",
            )
        if not _ingest_available():
            return JSONResponse(
                {
                    "ok": False,
                    "error": (
                        "Package zomato_raw_ingest not installed. "
                        "Run: pip install -e ./phase2"
                    ),
                    "rows": [],
                }
            )
        try:
            from zomato_raw_ingest import load_raw_rows

            rows = load_raw_rows(limit)
        except Exception as e:  # noqa: BLE001 — surface HF/network errors to UI
            return JSONResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "rows": [],
                },
                status_code=200,
            )
        serializable: list[dict] = []
        for r in rows:
            serializable.append({k: _json_safe(v) for k, v in r.items()})
        return JSONResponse({"ok": True, "error": None, "rows": serializable})

    return app


def _json_safe(v: object) -> object:
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    return str(v)
