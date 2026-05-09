"""Environment-driven LLM settings (no secrets in docs)."""

from __future__ import annotations

import os

# Groq OpenAI-compatible endpoint (see https://console.groq.com/docs/openai).
GROQ_OPENAI_BASE_URL = "https://api.groq.com/openai/v1"
# Sensible default when using Groq without OPENAI_MODEL (override in .env).
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def _looks_like_groq_key(value: str) -> bool:
    s = value.strip()
    return s.startswith("gsk_")


def openai_api_key() -> str | None:
    """API key for chat completions (OpenAI or Groq, depending on base URL)."""
    v = os.environ.get("OPENAI_API_KEY")
    if v and v.strip():
        return v.strip()
    v = os.environ.get("GROQ_API_KEY")
    if v and v.strip():
        return v.strip()
    return None


def openai_base_url() -> str | None:
    v = os.environ.get("OPENAI_BASE_URL")
    if v and v.strip():
        return v.strip()
    if os.environ.get("GROQ_API_KEY", "").strip():
        return GROQ_OPENAI_BASE_URL
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key and _looks_like_groq_key(openai_key):
        return GROQ_OPENAI_BASE_URL
    return None


def openai_model() -> str:
    explicit = os.environ.get("OPENAI_MODEL")
    if explicit and explicit.strip():
        return explicit.strip()
    if os.environ.get("GROQ_API_KEY", "").strip():
        return GROQ_DEFAULT_MODEL
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key and _looks_like_groq_key(openai_key):
        return GROQ_DEFAULT_MODEL
    return "gpt-4o-mini"
