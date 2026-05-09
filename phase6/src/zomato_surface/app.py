"""FastAPI application (Phase 6)."""

from __future__ import annotations

import traceback
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from zomato_surface import __version__
from zomato_surface.api_schemas import RecommendRequest
from zomato_surface.filter_options import (
    filter_options_response_dict,
    get_filter_options,
)
from zomato_surface.service import recommend
from zomato_surface.ui_options import LLM_CAP_OPTIONS, TOP_K_OPTIONS

_BASE = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(
        title="Zomato-inspired recommendations",
        description="Phase 6: full pipeline (HF -> normalize -> filter -> LLM).",
        version=__version__,
    )
    # Allow the standalone Next.js frontend on port 3000 to call backend APIs.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    templates = Jinja2Templates(directory=str(_BASE / "templates"))
    app.mount("/static", StaticFiles(directory=str(_BASE / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_version": __version__,
                "top_k_options": TOP_K_OPTIONS,
                "llm_cap_options": LLM_CAP_OPTIONS,
            },
        )

    @app.get("/api/filter-options")
    def api_filter_options(
        refresh: bool = Query(
            default=False,
            description="Re-scan full split (drops cache)",
        ),
    ) -> dict:
        snap = get_filter_options(force_refresh=refresh)
        return filter_options_response_dict(snap)

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "version": __version__, "phase": 6}

    @app.post("/api/recommend")
    def api_recommend(body: RecommendRequest) -> JSONResponse:
        try:
            n_match, n_cap, result = recommend(body)
        except Exception as e:  # noqa: BLE001
            return JSONResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "matched_count": 0,
                    "capped_count": 0,
                    "result": None,
                },
                status_code=200,
            )

        if n_match == 0:
            return JSONResponse(
                {
                    "ok": True,
                    "matched_count": 0,
                    "capped_count": 0,
                    "message": "No restaurants matched your filters.",
                    "result": result.model_dump(),
                }
            )

        return JSONResponse(
            {
                "ok": True,
                "matched_count": n_match,
                "capped_count": n_cap,
                "message": None,
                "result": result.model_dump(),
            }
        )

    return app
