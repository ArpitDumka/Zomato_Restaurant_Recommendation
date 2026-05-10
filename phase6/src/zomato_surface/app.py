"""FastAPI application (Phase 6)."""

from __future__ import annotations

import asyncio
import logging
import os
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from zomato_surface import __version__
from zomato_surface.api_schemas import RecommendRequest
from zomato_surface.catalog import get_catalog, warm_catalog_at_startup
from zomato_surface.filter_options import (
    filter_options_response_dict,
    get_filter_options,
)
from zomato_surface.service import recommend
from zomato_surface.ui_options import LLM_CAP_OPTIONS, TOP_K_OPTIONS

_BASE = Path(__file__).resolve().parent
_log = logging.getLogger(__name__)


def _cors_allow_origins() -> list[str]:
    """Local Next.js dev plus optional production origins (Railway + Vercel)."""
    base = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    extra = os.environ.get("CORS_ORIGINS", "").strip()
    if not extra:
        return base
    more = [o.strip() for o in extra.split(",") if o.strip()]
    seen: set[str] = set()
    out: list[str] = []
    for o in base + more:
        if o not in seen:
            seen.add(o)
            out.append(o)
    return out


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if warm_catalog_at_startup():
            _log.info("catalog warmup starting")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, get_catalog)
            _log.info("catalog warmup complete")
        yield

    app = FastAPI(
        title="Zomato-inspired recommendations",
        description="Phase 6: full pipeline (HF -> normalize -> filter -> LLM).",
        version=__version__,
        lifespan=lifespan,
    )
    # Next.js on :3000 locally; set CORS_ORIGINS (comma-separated) and optional
    # CORS_ORIGIN_REGEX / CORS_ORIGINS on the API host for Vercel
    # (see Docs/Deployment.md).
    _cors_kw: dict = {
        "allow_origins": _cors_allow_origins(),
        "allow_credentials": False,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    _cors_rx = os.environ.get("CORS_ORIGIN_REGEX", "").strip()
    if _cors_rx:
        _cors_kw["allow_origin_regex"] = _cors_rx
    app.add_middleware(CORSMiddleware, **_cors_kw)
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
    ) -> JSONResponse:
        try:
            snap = get_filter_options(force_refresh=refresh)
            return JSONResponse(filter_options_response_dict(snap))
        except Exception as e:  # noqa: BLE001
            return JSONResponse(
                {
                    "ok": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                status_code=200,
            )

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
