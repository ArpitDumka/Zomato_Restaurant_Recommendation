# Phase 7 - Streamlit deployment surface

This phase adds a Streamlit app that reuses the existing recommendation pipeline.

## Entry point

- `streamlit_app.py` (repo root)

## Local run

From repo root (recommended after existing editable installs from earlier phases):

```powershell
pip install streamlit
streamlit run streamlit_app.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501`).

## Notes

- The app reuses:
  - `zomato_surface.filter_options.get_filter_options`
  - `zomato_surface.service.recommend`
  - `zomato_surface.api_schemas.RecommendRequest`
- It uses the same LLM/env configuration path (`OPENAI_API_KEY` / `GROQ_API_KEY`).
