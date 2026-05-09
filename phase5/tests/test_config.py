"""LLM config resolution (Groq vs OpenAI)."""

from __future__ import annotations

import zomato_llm.config as cfg


def test_groq_key_sets_base_url_and_default_model(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_example")
    assert cfg.openai_api_key() == "gsk_test_example"
    assert cfg.openai_base_url() == cfg.GROQ_OPENAI_BASE_URL
    assert cfg.openai_model() == cfg.GROQ_DEFAULT_MODEL


def test_openai_key_gsk_prefix_uses_groq_host(monkeypatch) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "gsk_from_openai_slot")
    assert cfg.openai_base_url() == cfg.GROQ_OPENAI_BASE_URL
    assert cfg.openai_model() == cfg.GROQ_DEFAULT_MODEL


def test_explicit_openai_model_overrides_groq_default(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "gsk_x")
    monkeypatch.setenv("OPENAI_MODEL", "mixtral-8x7b-32768")
    assert cfg.openai_model() == "mixtral-8x7b-32768"
