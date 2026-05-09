"""CLI: run uvicorn for Phase 6."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    p = argparse.ArgumentParser(prog="zomato-surface")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args(argv)
    try:
        import uvicorn
    except ImportError:
        print("Install: pip install -e ./phase6", file=sys.stderr)
        return 1
    from zomato_surface.app import create_app

    print(f"Phase 6 UI: http://{args.host}:{args.port}/")
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="info")
    return 0
