"""Phase 7 Streamlit deployment surface for recommendations."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
for rel in ("phase2/src", "phase3/src", "phase4/src", "phase5/src", "phase6/src"):
    p = ROOT / rel
    if p.exists():
        sys.path.insert(0, str(p))

from zomato_surface.api_schemas import RecommendRequest
from zomato_surface.filter_options import get_filter_options
from zomato_surface.service import recommend


@st.cache_data(show_spinner=False)
def load_options():
    return get_filter_options()


def main() -> None:
    st.set_page_config(
        page_title="SpiceRoute Select - Streamlit",
        page_icon="🍽️",
        layout="wide",
    )
    st.title("SpiceRoute Select")
    st.caption("Phase 7: Streamlit deployment surface")

    opts = load_options()

    with st.sidebar:
        st.header("Your Preferences")
        city = st.selectbox("City", [""] + list(opts.cities), index=0)
        cuisine = st.selectbox("Cuisine", [""] + list(opts.cuisines), index=0)
        additional_preferences = st.text_input(
            "Additional preferences",
            placeholder="e.g. quiet place, family-friendly, rooftop",
            max_chars=300,
        )
        ratings = [""] + [str(r) for r in opts.min_ratings]
        min_rating_str = st.selectbox("Min rating", ratings, index=0)
        min_rating = float(min_rating_str) if min_rating_str else None
        band_values = [""] + list(opts.budget_bands)
        budget_band = st.selectbox(
            "Budget band",
            band_values,
            index=0,
            help="low / medium / high / unknown",
        )
        top_k = st.slider("Top picks", min_value=1, max_value=5, value=5)
        llm_cap = st.select_slider(
            "Shortlist size sent to model",
            options=[200, 220, 250, 280, 300],
            value=220,
        )
        run = st.button("Get Recommendations", type="primary", use_container_width=True)

    st.info(
        f"Loaded {opts.normalized_row_count:,} normalized rows in {opts.scan_seconds}s "
        "(cached in memory)."
    )

    if not run:
        st.stop()

    req = RecommendRequest(
        city=city or None,
        cuisine_query=cuisine or None,
        additional_preferences=additional_preferences or None,
        min_rating=min_rating,
        budget_band=budget_band or None,
        top_k=top_k,
        llm_candidate_cap=llm_cap,
    )

    with st.spinner("Finding recommendations..."):
        matched_count, capped_count, result = recommend(req)

    col1, col2, col3 = st.columns(3)
    col1.metric("Matched rows", matched_count)
    col2.metric("Sent to model", capped_count)
    col3.metric("LLM used", "Yes" if result.used_llm else "No")

    if not result.used_llm and result.fallback_reason:
        st.warning(f"Using fallback explanations: {result.fallback_reason}")
    if result.summary:
        st.success(result.summary)

    if not result.picks:
        st.info("No picks returned. Try broader filters.")
        st.stop()

    st.subheader("Top Picks")
    for pick in result.picks:
        with st.container(border=True):
            st.markdown(f"**#{pick.rank} {pick.name}**")
            meta = f"Rating: {pick.rating if pick.rating is not None else '—'}"
            meta += f" | Cost for two: INR {pick.cost_for_two_inr if pick.cost_for_two_inr is not None else '—'}"
            meta += f" | Cuisine: {pick.cuisine}"
            if pick.branch:
                meta += f" | Branch: {pick.branch}"
            st.caption(meta)
            st.write(pick.explanation)


if __name__ == "__main__":
    main()

