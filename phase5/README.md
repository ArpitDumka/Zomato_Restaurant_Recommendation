# Phase 5 — LLM ranking and explanations

Implements **Phase 5** from [PhaseWiseArchitecture.md](../Docs/PhaseWiseArchitecture.md): **grounded** JSON from an OpenAI-compatible chat model, **validation** of `restaurant_id`, and **fallback** to Phase 4 ordering on errors or missing API key.

## Install (after Phases 3–4)

```powershell
pip install -e ../phase3
pip install -e ../phase4
cd phase5
pip install -e ".[dev]"
```

LLM keys are read from the **process environment** (`OPENAI_API_KEY` or `GROQ_API_KEY`; see `zomato_llm.config`). Without a key, `rank_and_explain` returns **fallback** picks.

For the Phase 6 UI, put keys in **`phase6/.env`** (recommended). `run.ps1 -Surface` loads `phase5/.env` first, then **`phase6/.env`** (same variable name in both files: **phase6 wins**).

## API (`zomato_llm`)

```python
from zomato_llm import rank_and_explain
from zomato_filter.preferences import UserPreferences

result = rank_and_explain(capped_candidates, UserPreferences(city="Banashankari"), top_k=5)
print(result.model_dump())
```

`result.picks` include **name, cuisine, rating, cost**, and **explanation**. `used_llm` indicates whether the model path succeeded.

## Tests

```powershell
pytest
ruff check src tests
```

LLM calls are **mocked** in tests.

Next: **Phase 6** surface app ([`phase6/`](../phase6/README.md)).
