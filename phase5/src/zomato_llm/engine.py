"""OpenAI call, validation, fallback."""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence

from openai import OpenAI
from zomato_canonical.model import RestaurantRecord
from zomato_filter.preferences import UserPreferences

from zomato_llm.config import openai_api_key, openai_base_url, openai_model
from zomato_llm.prompts import SYSTEM_PROMPT, build_user_message, parse_llm_json
from zomato_llm.schema import LlmJsonItem, LlmRankingResult, RankedPick

logger = logging.getLogger(__name__)

GENERIC_FALLBACK = (
    "Matches your filters; ranked by rating. AI explanation unavailable."
)
_DEFAULT_PROMPT_CANDIDATE_LIMIT = 80
_GROQ_PROMPT_CANDIDATE_LIMIT = 24
_GROQ_BACKUP_MODEL = "llama-3.1-8b-instant"


def _branch_label(record: RestaurantRecord) -> str | None:
    """
    Best-effort outlet hint for UI disambiguation.

    Prefer location area; fall back to a short address prefix if area is missing.
    """
    area = (record.location_area or "").strip()
    if area:
        return area
    addr = (record.address or "").strip()
    if not addr:
        return None
    # Keep label short/readable.
    head = addr.split(",", 1)[0].strip()
    return head or None


def _fallback_result(
    candidates: Sequence[RestaurantRecord],
    prefs: UserPreferences,
    top_k: int,
    *,
    reason: str | None = None,
) -> LlmRankingResult:
    picks: list[RankedPick] = []
    for i, r in enumerate(candidates[:top_k]):
        picks.append(
            RankedPick(
                restaurant_id=r.restaurant_id,
                rank=i + 1,
                explanation=_smart_fallback_explanation(r, prefs),
                name=r.name,
                branch=_branch_label(r),
                cuisine=r.cuisines_display,
                rating=r.rating,
                cost_for_two_inr=r.cost_for_two_inr,
            )
        )
    return LlmRankingResult(
        picks=picks,
        summary=None,
        used_llm=False,
        fallback_reason=reason,
        latency_ms=None,
    )


def _smart_fallback_explanation(
    record: RestaurantRecord,
    prefs: UserPreferences,
) -> str:
    """Generate a richer local explanation when live LLM is unavailable."""
    rating = record.rating
    rating_text = (
        f"With a solid {rating:.1f} rating, this place is consistently liked."
        if isinstance(rating, (int, float))
        else "This place aligns well with your current filters."
    )
    price = record.cost_for_two_inr
    if isinstance(price, int):
        price_text = (
            f"Estimated cost for two is around INR {price}, "
            "so it should fit your budget expectations."
        )
    else:
        price_text = "Pricing appears reasonable for the cuisine profile."

    cuisine = (record.cuisines_display or "mixed cuisine").strip()
    pref_hint = (prefs.additional_preferences or "").strip()
    if pref_hint:
        vibe_text = (
            f"It matches your preference for {pref_hint.lower()} "
            f"while staying true to its {cuisine} strengths."
        )
    else:
        vibe_text = (
            f"It stands out as a reliable {cuisine} option "
            "for your selected context."
        )

    return f"{rating_text} {price_text} {vibe_text}"


def _merge_valid_picks(
    parsed_items: list[LlmJsonItem],
    by_id: dict[str, RestaurantRecord],
    top_k: int,
) -> list[RankedPick]:
    seen: set[str] = set()
    out: list[RankedPick] = []
    for row in sorted(parsed_items, key=lambda x: x.rank):
        rid = row.restaurant_id
        if rid not in by_id or rid in seen:
            continue
        rec = by_id[rid]
        out.append(
            RankedPick(
                restaurant_id=rid,
                rank=len(out) + 1,
                explanation=row.explanation.strip(),
                name=rec.name,
                branch=_branch_label(rec),
                cuisine=rec.cuisines_display,
                rating=rec.rating,
                cost_for_two_inr=rec.cost_for_two_inr,
            )
        )
        seen.add(rid)
        if len(out) >= top_k:
            break
    return out


def _maybe_retry_with_backup_groq_model(
    *,
    client: OpenAI,
    base_url: str | None,
    model: str,
    user_msg: str,
) -> str | None:
    """Retry once with a smaller Groq model when primary model is limited."""
    if not (base_url and "groq.com" in base_url):
        return None
    if model == _GROQ_BACKUP_MODEL:
        return None
    try:
        resp = client.chat.completions.create(
            model=_GROQ_BACKUP_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        logger.warning(
            "Primary Groq model limited; succeeded with backup model=%s",
            _GROQ_BACKUP_MODEL,
        )
        return resp.choices[0].message.content or "{}"
    except Exception:
        logger.exception(
            "Backup Groq model retry failed model=%s",
            _GROQ_BACKUP_MODEL,
        )
        return None


def rank_and_explain(
    candidates: Sequence[RestaurantRecord],
    prefs: UserPreferences,
    *,
    top_k: int = 5,
    timeout_seconds: float = 60.0,
) -> LlmRankingResult:
    """
    Ask the LLM for grounded top picks; validate ids; fallback on any failure.

    Requires ``OPENAI_API_KEY`` or ``GROQ_API_KEY`` (Groq uses the OpenAI client \
    with ``https://api.groq.com/openai/v1``) for live calls; otherwise returns \
    deterministic fallback ordering.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    cands = list(candidates)
    if not cands:
        return LlmRankingResult(
            picks=[],
            summary=None,
            used_llm=False,
            fallback_reason="no_candidates",
            latency_ms=None,
        )

    key = openai_api_key()
    if not key:
        return _fallback_result(
            cands,
            prefs,
            top_k,
            reason="missing_openai_api_key",
        )

    by_id = {r.restaurant_id: r for r in cands}
    base_url = openai_base_url()
    prompt_limit = _DEFAULT_PROMPT_CANDIDATE_LIMIT
    if base_url and "groq.com" in base_url:
        prompt_limit = _GROQ_PROMPT_CANDIDATE_LIMIT
    prompt_candidates = cands[:prompt_limit]
    user_msg = build_user_message(
        candidates=prompt_candidates,
        prefs=prefs,
        top_k=top_k,
    )

    client = OpenAI(api_key=key, base_url=base_url, timeout=timeout_seconds)
    model = openai_model()
    logger.info(
        "llm request model=%s provider=%s prompt_candidates=%s total_candidates=%s",
        model,
        "groq" if (base_url and "groq.com" in base_url) else "openai-compatible",
        len(prompt_candidates),
        len(cands),
    )
    t0 = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )
        raw = resp.choices[0].message.content or "{}"
        parsed = parse_llm_json(raw)
        merged = _merge_valid_picks(parsed.items, by_id, top_k)
        if not merged:
            ms = (time.perf_counter() - t0) * 1000
            logger.warning("LLM returned no valid grounded picks; using fallback")
            fb = _fallback_result(
                cands,
                prefs,
                top_k,
                reason="empty_valid_picks_after_parse",
            )
            return fb.model_copy(update={"latency_ms": ms})

        ms = (time.perf_counter() - t0) * 1000
        return LlmRankingResult(
            picks=merged,
            summary=parsed.summary,
            used_llm=True,
            fallback_reason=None,
            latency_ms=ms,
        )
    except Exception:
        raw_retry = _maybe_retry_with_backup_groq_model(
            client=client,
            base_url=base_url,
            model=model,
            user_msg=user_msg,
        )
        if raw_retry is not None:
            try:
                parsed = parse_llm_json(raw_retry)
                merged = _merge_valid_picks(parsed.items, by_id, top_k)
                if merged:
                    ms = (time.perf_counter() - t0) * 1000
                    return LlmRankingResult(
                        picks=merged,
                        summary=parsed.summary,
                        used_llm=True,
                        fallback_reason=None,
                        latency_ms=ms,
                    )
            except Exception:
                logger.exception("Backup Groq response parse/merge failed")
        ms = (time.perf_counter() - t0) * 1000
        logger.exception("LLM ranking failed; using fallback (latency_ms=%s)", ms)
        fb = _fallback_result(cands, prefs, top_k, reason="llm_error")
        return fb.model_copy(update={"latency_ms": ms})
