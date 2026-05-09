"""End-to-end: in-memory full catalog -> filter -> shortlist -> LLM top picks."""

from __future__ import annotations

import logging

from zomato_canonical import RestaurantRecord
from zomato_filter import (
    UserPreferences,
    rank_by_rating_cap,
    record_matches_preferences,
)
from zomato_llm import rank_and_explain
from zomato_llm.schema import LlmRankingResult

from zomato_surface.api_schemas import RecommendRequest
from zomato_surface.catalog import all_records

logger = logging.getLogger(__name__)

# Keep LLM payload fast/safe even when shortlist is set higher in UI.
_MAX_LLM_PROMPT_CANDIDATES = 80


def recommend(req: RecommendRequest) -> tuple[int, int, LlmRankingResult]:
    """
    Filter the materialized split (~52k rows), shortlist 200–300 by rating, LLM top_k.

    The catalog is loaded once on first use (full Hub download into memory + normalize).

    Returns:
        matched_count, capped_count, ranking_result
    """
    prefs = UserPreferences(
        city=req.city,
        cuisine_query=req.cuisine_query,
        additional_preferences=req.additional_preferences,
        min_rating=req.min_rating,
        budget_band=req.budget_band,
    )

    matched: list[RestaurantRecord] = [
        r for r in all_records() if record_matches_preferences(r, prefs)
    ]
    capped = rank_by_rating_cap(matched, max_candidates=req.llm_candidate_cap)
    prompt_ready = capped[:_MAX_LLM_PROMPT_CANDIDATES]
    logger.info(
        "recommend pipeline matched_rows=%s capped=%s prompt_ready=%s top_k=%s",
        len(matched),
        len(capped),
        len(prompt_ready),
        req.top_k,
    )
    result = rank_and_explain(prompt_ready, prefs, top_k=req.top_k)
    return len(matched), len(prompt_ready), result
