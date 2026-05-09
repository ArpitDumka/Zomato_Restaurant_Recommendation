"""Build :class:`RestaurantRecord` from raw HF-shaped dicts."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from typing import Any

from zomato_canonical.model import RestaurantRecord
from zomato_canonical.parsers import cost_to_budget_band, parse_cost_inr, parse_rating

# Raw column names from ManikaSaini/zomato-restaurant-recommendation
COL_NAME = "name"
COL_CITY = "listed_in(city)"
COL_LOCATION = "location"
COL_CUISINES = "cuisines"
COL_RATE = "rate"
COL_COST = "approx_cost(for two people)"
COL_URL = "url"
COL_ADDRESS = "address"
COL_VOTES = "votes"
COL_REST_TYPE = "rest_type"
COL_ONLINE = "online_order"
COL_BOOK = "book_table"


def _clean_str(raw: object | None) -> str:
    if raw is None:
        return ""
    return re.sub(r"\s+", " ", str(raw).strip())


def _optional_str(raw: object | None) -> str | None:
    s = _clean_str(raw)
    return s if s else None


def _parse_votes(raw: object | None) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def stable_restaurant_id(
    *,
    url: str | None,
    name: str,
    address: str,
    city_listed: str,
) -> str:
    """Prefer ``url``; else deterministic short hash (FieldMapping fallback)."""
    u = _optional_str(url)
    if u:
        return u
    payload = f"{name}\n{address}\n{city_listed}".encode("utf-8")
    return "h:" + hashlib.sha256(payload).hexdigest()[:24]


def cuisines_tokens_from_display(display: str) -> tuple[str, ...]:
    parts = [p.strip().lower() for p in display.split(",")]
    return tuple(p for p in parts if p)


def normalize_raw_row(row: Mapping[str, Any]) -> RestaurantRecord | None:
    """
    Convert one raw dataset dict into a :class:`RestaurantRecord`.

    Returns ``None`` if ``name`` is missing or empty (undisplayable row).
    """
    name = _clean_str(row.get(COL_NAME))
    if not name:
        return None

    city_listed = _clean_str(row.get(COL_CITY))
    address = _clean_str(row.get(COL_ADDRESS))
    cuisines_display = _clean_str(row.get(COL_CUISINES))
    cost_inr = parse_cost_inr(row.get(COL_COST))
    rating = parse_rating(row.get(COL_RATE))

    rid = stable_restaurant_id(
        url=_optional_str(row.get(COL_URL)),
        name=name,
        address=address,
        city_listed=city_listed,
    )

    return RestaurantRecord(
        restaurant_id=rid,
        name=name,
        city_listed=city_listed,
        location_area=_optional_str(row.get(COL_LOCATION)),
        cuisines_display=cuisines_display,
        cuisines_tokens=cuisines_tokens_from_display(cuisines_display),
        rating=rating,
        cost_for_two_inr=cost_inr,
        budget_band=cost_to_budget_band(cost_inr),
        url=_optional_str(row.get(COL_URL)),
        address=address,
        votes=_parse_votes(row.get(COL_VOTES)),
        rest_type=_optional_str(row.get(COL_REST_TYPE)),
        online_order=_optional_str(row.get(COL_ONLINE)),
        book_table=_optional_str(row.get(COL_BOOK)),
    )


def dedupe_restaurant_records(
    records: Iterable[RestaurantRecord],
) -> list[RestaurantRecord]:
    """Keep first occurrence per ``restaurant_id`` (stable order)."""
    seen: set[str] = set()
    out: list[RestaurantRecord] = []
    for r in records:
        if r.restaurant_id in seen:
            continue
        seen.add(r.restaurant_id)
        out.append(r)
    return out
