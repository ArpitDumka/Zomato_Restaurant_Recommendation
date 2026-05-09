"""Static dropdown options for fields that are not dataset-driven (Phase 6 UI)."""

from __future__ import annotations

TOP_K_OPTIONS: tuple[int, ...] = tuple(range(1, 6))

# Shortlist sent to the LLM after user filters (full split is ~52k rows).
LLM_CAP_OPTIONS: tuple[int, ...] = (200, 220, 250, 280, 300)
