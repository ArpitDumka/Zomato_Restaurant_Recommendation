"""Parse raw string fields from the HF dataset (unit-test focus)."""

from __future__ import annotations

import re

from zomato_canonical.model import BudgetBand
from zomato_canonical.policy import LOW_MAX_INR, MEDIUM_MAX_INR


def parse_rating(raw: object) -> float | None:
    """
    Parse ``rate`` column values like ``4.1/5``, ``4/5``, or plain ``4.2``.

    Returns ``None`` for missing, empty, or non-numeric tokens (e.g. ``NEW``).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.match(r"^(\d+(?:\.\d+)?)\s*/\s*\d+", s)
    if m:
        return float(m.group(1))
    m2 = re.match(r"^(\d+(?:\.\d+)?)\s*$", s)
    if m2:
        return float(m2.group(1))
    return None


def parse_cost_inr(raw: object) -> int | None:
    """
    Parse ``approx_cost(for two people)`` — digits only, ignores commas/symbols.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    digits = re.sub(r"\D", "", s)
    if not digits:
        return None
    return int(digits)


def cost_to_budget_band(cost_inr: int | None) -> BudgetBand:
    """Map parsed INR (for two) to low / medium / high / unknown."""
    if cost_inr is None:
        return "unknown"
    if cost_inr <= LOW_MAX_INR:
        return "low"
    if cost_inr <= MEDIUM_MAX_INR:
        return "medium"
    return "high"
