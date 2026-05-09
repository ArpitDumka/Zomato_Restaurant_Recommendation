"""Structured LLM output and API-facing result objects."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LlmJsonItem(BaseModel):
    """Expected shape inside the model JSON payload."""

    restaurant_id: str = Field(min_length=1)
    rank: int = Field(ge=1)
    explanation: str = Field(min_length=1, max_length=2000)


class LlmJsonPayload(BaseModel):
    items: list[LlmJsonItem] = Field(default_factory=list)
    summary: str | None = Field(default=None, max_length=2000)


class RankedPick(BaseModel):
    """One grounded recommendation after validation / merge."""

    restaurant_id: str
    rank: int
    explanation: str
    name: str
    branch: str | None = None
    cuisine: str
    rating: float | None
    cost_for_two_inr: int | None


class LlmRankingResult(BaseModel):
    picks: list[RankedPick]
    summary: str | None
    used_llm: bool
    fallback_reason: str | None = None
    latency_ms: float | None = None
