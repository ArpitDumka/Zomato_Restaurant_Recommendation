"""Validated API bodies (Phase 6)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Budget = Literal["low", "medium", "high", "unknown"]


class RecommendRequest(BaseModel):
    city: str | None = Field(default=None, max_length=120)
    cuisine_query: str | None = Field(default=None, max_length=120)
    additional_preferences: str | None = Field(default=None, max_length=300)
    min_rating: float | None = Field(default=None, ge=0.0, le=5.0)
    budget_band: Budget | None = None
    top_k: int = Field(default=5, ge=1, le=5)
    llm_candidate_cap: int = Field(
        default=250,
        ge=200,
        le=300,
        description="Max restaurants sent to the LLM after filters (shortlist).",
    )

    @field_validator("city", "cuisine_query", "additional_preferences", mode="before")
    @classmethod
    def _empty_to_none(cls, v: object) -> object:
        if v == "":
            return None
        return v
