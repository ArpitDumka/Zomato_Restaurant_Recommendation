#!/usr/bin/env sh
# Railway (Linux): add phase src trees to PYTHONPATH; editable -e ./phase* fails in some builders.
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")"/.. && pwd)"
export PYTHONPATH="${ROOT}/phase2/src:${ROOT}/phase3/src:${ROOT}/phase4/src:${ROOT}/phase5/src:${ROOT}/phase6/src"
exec uvicorn zomato_surface.app:create_app \
  --factory \
  --host 0.0.0.0 \
  --port "${PORT:?PORT must be set by Railway}"
