"""Phase 3: normalize raw HF rows into a single canonical record type."""

from zomato_canonical.model import BudgetBand, RestaurantRecord
from zomato_canonical.normalize import (
    RawFilterScanAcc,
    dedupe_restaurant_records,
    merge_raw_row_into_filter_scan,
    merge_record_into_filter_scan,
    normalize_raw_row,
)
from zomato_canonical.parsers import cost_to_budget_band, parse_cost_inr, parse_rating
from zomato_canonical.policy import LOW_MAX_INR, MEDIUM_MAX_INR

__all__ = [
    "BudgetBand",
    "LOW_MAX_INR",
    "MEDIUM_MAX_INR",
    "RawFilterScanAcc",
    "RestaurantRecord",
    "cost_to_budget_band",
    "dedupe_restaurant_records",
    "merge_raw_row_into_filter_scan",
    "merge_record_into_filter_scan",
    "normalize_raw_row",
    "parse_cost_inr",
    "parse_rating",
]
__version__ = "0.1.0"
