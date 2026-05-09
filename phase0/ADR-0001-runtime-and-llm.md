# ADR-0001: Runtime and LLM provider (Phase 0)

## Status

Accepted (Phase 0 charter)

## Context

The product combines a Hugging Face tabular dataset with an LLM for grounded ranking and explanations ([ProblemStatement.md](../Docs/ProblemStatement.md)). Phase 0 must pick a default stack before Phase 1 scaffolding.

## Decision

1. **Application runtime:** **Python 3.11+** for Phases 1–6 (data loading via `datasets`, filtering, and an HTTP service behind the UI).
2. **Primary user input:** a **basic web UI** (built in Phase 6) collects preferences and displays recommendations. The server implements the same preference payload as JSON for programmatic use or tests if needed, but the charter path is **browser-first**.
3. **Primary LLM integration (Phase 5):** **OpenAI-compatible HTTP API** — default provider **OpenAI** (`gpt-4o-mini` or successor for cost/latency), using JSON-mode or strict prompt contract + server-side validation.
4. **Configuration:** API key via environment variable (e.g. `OPENAI_API_KEY`); never commit secrets (Phase 1 `.env.example`).

## Rationale

- Python matches the Hugging Face ecosystem used in Phase 2 and keeps normalization/filtering in one language; a single backend can serve the web UI and optional JSON API.
- Hosted LLM avoids local GPU ops for this assignment; `gpt-4o-mini`-class models are sufficient for structured JSON ranking/explanations over small candidate lists.
- OpenAI-compatible APIs allow swapping to other providers later with minimal code change if base URL + key env vars are abstracted.

## Consequences

- **Positive:** Fast spike scripts, straightforward CI for non-LLM phases, clear vendor docs.
- **Negative:** Ongoing API cost; requires network egress; vendor lock-in unless abstraction is added in Phase 5.

## Alternatives considered

- **Local LLM (Ollama):** Lower cost, heavier setup and hardware variance—deferred.
- **JavaScript/Node only:** Weaker HF tabular ergonomics for early phases—rejected for default path.
