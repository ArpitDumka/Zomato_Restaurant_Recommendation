"""Phase 4: preference filters + rating-ranked cap (no LLM)."""

from zomato_filter.pipeline import filter_rank_cap
from zomato_filter.preferences import UserPreferences
from zomato_filter.rank import rank_by_rating_cap, stub_explanation
from zomato_filter.rules import filter_restaurant_records, record_matches_preferences

__all__ = [
    "UserPreferences",
    "filter_rank_cap",
    "filter_restaurant_records",
    "rank_by_rating_cap",
    "record_matches_preferences",
    "stub_explanation",
]
__version__ = "0.1.0"
