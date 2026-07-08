"""Inventory Optimization AI Co-Pilot — Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from src.services.summary_service import run_pipeline
from src.ui.components import render_header
from src.ui.layout import init_session_state, render_sidebar
from src.ui.pages import (
    aged_excess,
    ai_summary,
    dashboard,
    data_quality,
    markdown_planner,
    methodology,
    transfer_planner,
)
from src.ui.theme import apply_theme
from src.utils.logging import get_logger

logger = get_logger(__name__)

PAGE_RENDERERS = {
    "Executive Dashboard": dashboard.render,
    "Aged & Excess": aged_excess.render,
    "Transfer Planner": transfer_planner.render,
    "Markdown Planner": markdown_planner.render,
    "AI Summary": ai_summary.render,
    "Data Quality": data_quality.render,
    "Methodology": methodology.render,
}


def load_pipeline():
    if st.session_state.pipeline is None:
        try:
            st.session_state.pipeline = run_pipeline()
        except Exception as exc:
            logger.exception("Pipeline failed")
            st.error(f"Failed to load inventory data: {exc}")
            st.stop()
    return st.session_state.pipeline


def main() -> None:
    st.set_page_config(
        page_title="Inventory Optimization AI Co-Pilot",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    init_session_state()
    render_header()

    pipeline = load_pipeline()
    page = render_sidebar(pipeline)

    renderer = PAGE_RENDERERS.get(page)
    if renderer:
        if page == "Methodology":
            renderer()
        else:
            renderer(pipeline)
    else:
        st.warning(f"Unknown page: {page}")


if __name__ == "__main__":
    main()
