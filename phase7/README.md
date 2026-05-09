# Phase 7 - Streamlit deployment surface

This phase adds a Streamlit app that reuses the existing recommendation pipeline.

## Entry point

- `streamlit_app.py` (repo root)

## Local run

From repo root on Windows (venv, phases 2–6, `requirements.txt`, loads `phase6\.env` when present):

```powershell
.\run.ps1 -Streamlit
```

Open **http://127.0.0.1:8501/**.

Manual install (matches Streamlit Cloud):

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

For a dev setup with editable phase packages instead, ensure `streamlit`, `pydantic`, `datasets`, `huggingface_hub`, and `openai` are installed, then run the same `streamlit` command.

The repo includes [`.streamlit/config.toml`](../.streamlit/config.toml) (`gatherUsageStats = false`). On the very first Streamlit run, if you still see an email prompt in the terminal, press Enter once or use `.\run.ps1 -Streamlit` (it pipes a blank line for non-interactive starts).

## Streamlit Community Cloud

The repo includes a root [`requirements.txt`](../requirements.txt) so the cloud builder installs **pydantic**, **datasets**, **openai**, and related packages. Without that file, imports such as `from pydantic import ...` fail at startup.

Set secrets in the app dashboard (for example `OPENAI_API_KEY` or `GROQ_API_KEY`, and optionally `HF_TOKEN`) to match your local `.env` usage.

**Python 3.14 on Community Cloud:** older `datasets` versions crash while hashing cache metadata (pickle API change). The root `requirements.txt` pins `datasets>=4.4.0` to avoid that. You can also pick **Python 3.12** under deploy **Advanced settings** if you prefer.

Open the URL printed by Streamlit (usually `http://localhost:8501`).

## Notes

- The app reuses:
  - `zomato_surface.filter_options.get_filter_options`
  - `zomato_surface.service.recommend`
  - `zomato_surface.api_schemas.RecommendRequest`
- It uses the same LLM/env configuration path (`OPENAI_API_KEY` / `GROQ_API_KEY`).
