"""CLI entrypoint: health / version (Phase 1) and web server (optional [web])."""

from __future__ import annotations

import argparse
import sys

from zomato_recommend import __version__


def _print_health() -> None:
    print(f"zomato-recommend {__version__} | health: ok")
    print()
    print("Implementation status (see repo README.md):")
    print("  Phase 0 - done: charter, field mapping, dataset spike (folder phase0/)")
    print("  Phase 1 - done: package scaffold, this CLI (folder phase1/)")
    print(
        "  Phase 2 - done: raw HF ingestion (folder phase2/, zomato_raw_ingest)"
    )
    print("  Web UI - http://127.0.0.1:8000 (zomato-recommend serve)")
    print(
        "  Phase 3 - done: canonical records (folder phase3/, zomato_canonical)"
    )
    print("  Phase 4 - done: filters + cap (folder phase4/, zomato_filter)")
    print("  Phase 5 - done: LLM JSON ranking (folder phase5/, zomato_llm)")
    print("  Phase 6 - done: product UI/API (folder phase6/, zomato_surface :8765)")
    print()
    print("Commands:  zomato-recommend serve  |  python -m zomato_surface (phase 6)")


def _run_serve(host: str, port: int) -> int:
    try:
        import uvicorn
    except ImportError:
        print(
            "Missing web dependencies. Install with:\n"
            "  pip install -e ./phase1[web]\n"
            "Also install Phase 2 for live data:\n"
            "  pip install -e ./phase2",
            file=sys.stderr,
        )
        return 1
    from zomato_recommend.web.app import create_app

    print(f"Open http://{host}:{port}/ in your browser (Ctrl+C to stop).")
    uvicorn.run(create_app(), host=host, port=port, log_level="info")
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="zomato-recommend",
        description="Restaurant recommendations (Phase 1 scaffold + web preview).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser(
        "health",
        help="Print version and status (default if no subcommand).",
    )

    p_serve = sub.add_parser(
        "serve",
        help="Start preview web UI (FastAPI + uvicorn).",
    )
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind address")
    p_serve.add_argument("--port", type=int, default=8000, help="Port")

    args = parser.parse_args(argv)

    if args.command == "serve":
        return _run_serve(args.host, args.port)

    _print_health()
    return 0
