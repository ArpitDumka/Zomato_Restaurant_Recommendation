"""Prompt construction (candidates + preferences only)."""

from __future__ import annotations

import json
from collections.abc import Sequence

from zomato_canonical.model import RestaurantRecord
from zomato_filter.preferences import UserPreferences

from zomato_llm.schema import LlmJsonPayload

SYSTEM_PROMPT = (
    "You are a food recommendation expert. Rank restaurants for the user.\n\n"
    "Hard rules (grounding):\n"
    "- Only reference restaurants whose restaurant_id appears in the candidates JSON.\n"
    "- Do not invent venues, ratings, prices, or dishes. "
    "Use only facts from the candidate fields.\n\n"
    'Voice for each explanation (the "explanation" string on every item):\n'
    "- Write 2–3 short lines, natural and human-like "
    "(like a friend texting, not bullet points).\n"
    "- Mention vibe: who it suits (date night, friends catch-up, quick work lunch, "
    "etc.) when you can infer it from cuisines, cost, rating, and area.\n"
    "- Say what stands out (atmosphere, value, crowd, cuisine strength) "
    "using only grounded facts.\n"
    '- Tone example (style only; do not copy verbatim): "Perfect for a relaxed dinner, '
    "this cozy Italian spot stands out for its calm vibe and well-balanced flavors "
    'without burning your pocket."\n\n'
    "Output format:\n"
    "- Return one JSON object with keys: items (array), summary (string or null).\n"
    "- Each items[] entry: restaurant_id (string), rank (int starting at 1), "
    "explanation (string as above).\n"
    "- summary: optional one-line wrap-up of the set "
    "(same warm expert tone), or null.\n"
    "- Include at most top_k items. Sort ranks ascending (1 is best)."
)


def candidate_payload(records: Sequence[RestaurantRecord]) -> list[dict]:
    """Compact, factual fields only (grounded list)."""
    out: list[dict] = []
    for r in records:
        out.append(
            {
                "restaurant_id": r.restaurant_id,
                "name": r.name,
                "city_listed": r.city_listed,
                "cuisines": r.cuisines_display,
                "rating": r.rating,
                "cost_for_two_inr": r.cost_for_two_inr,
                "budget_band": r.budget_band,
            }
        )
    return out


def user_prefs_summary(prefs: UserPreferences) -> dict:
    return {
        "city": prefs.city,
        "cuisine_query": prefs.cuisine_query,
        "additional_preferences": prefs.additional_preferences,
        "min_rating": prefs.min_rating,
        "budget_band": prefs.budget_band,
    }


def build_user_message(
    *,
    candidates: Sequence[RestaurantRecord],
    prefs: UserPreferences,
    top_k: int,
) -> str:
    body = {
        "top_k": top_k,
        "user_preferences": user_prefs_summary(prefs),
        "candidates": candidate_payload(candidates),
    }
    return json.dumps(body, ensure_ascii=False)


def parse_llm_json(text: str) -> LlmJsonPayload:
    return LlmJsonPayload.model_validate_json(text)
