"""Application layout and sidebar navigation."""

from __future__ import annotations

import streamlit as st

from src.config.constants import PAGE_LABELS
from src.config.settings import get_settings
from src.services.summary_service import PipelineResult
from src.ui.theme import apply_sidebar_theme


def init_session_state() -> None:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = PAGE_LABELS[0]


def _navigate_to(page: str) -> None:
    if st.session_state.current_page != page:
        st.session_state.current_page = page
        st.rerun()


def render_sidebar(pipeline: PipelineResult | None) -> str:
    with st.sidebar:
        apply_sidebar_theme()
        st.markdown('<p class="nav-section-title">Navigation</p>', unsafe_allow_html=True)

        for label in PAGE_LABELS:
            is_active = st.session_state.current_page == label
            if st.button(
                label,
                key=f"nav_{label}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                _navigate_to(label)

        st.divider()
        st.markdown("#### Data Source")
        if pipeline:
            st.markdown(
                f"""
                <div class="sidebar-section">
                    <span class="sidebar-metric">Source: {pipeline.source_path.name}</span>
                    <span class="sidebar-metric">Loaded: {pipeline.loaded_at.strftime("%Y-%m-%d %H:%M")}</span>
                    <span class="sidebar-metric">Rows: {pipeline.kpis.total_sku_locations:,}</span>
                    <span class="sidebar-metric">Exceptions: {pipeline.kpis.exception_count:,}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<p class="sidebar-metric">No data loaded</p>', unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Mode")
        settings = get_settings()
        if settings.ai_provider == "openai" and settings.openai_api_key:
            st.info(f"OpenAI ({settings.openai_model})")
        elif settings.ai_provider == "openai":
            st.warning("OpenAI selected — add API key on AI Summary page")
        elif settings.ai_provider == "local":
            st.success("Demo Mode (Local AI)")
        else:
            st.warning(f"{settings.ai_provider.title()} (not configured)")

        if st.button("Refresh Data", key="refresh_data", use_container_width=True):
            st.session_state.pipeline = None
            st.rerun()

    return st.session_state.current_page
