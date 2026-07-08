"""AI Management Summary page."""

from __future__ import annotations

import streamlit as st

from src.config.settings import get_settings
from src.services.ai_service import AISummaryError, generate_management_summary
from src.services.summary_service import PipelineResult, _top_risks

PROVIDERS = ["openai", "local"]


def _resolve_openai_api_key(settings_api_key: str) -> str:
    if settings_api_key.strip():
        return settings_api_key.strip()
    if st.session_state.get("openai_api_key"):
        return st.session_state.openai_api_key.strip()
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
        if secret_key:
            return str(secret_key).strip()
    except Exception:
        pass
    return ""


def render(pipeline: PipelineResult) -> None:
    st.markdown("### AI Management Summary")
    st.caption("Executive-ready narrative generated from calculated KPIs and recommendations.")

    settings = get_settings()
    default_index = PROVIDERS.index(settings.ai_provider) if settings.ai_provider in PROVIDERS else 0

    col1, col2 = st.columns([1, 3])
    with col1:
        provider = st.selectbox("AI Provider", PROVIDERS, index=default_index)
        openai_api_key = _resolve_openai_api_key(settings.openai_api_key)
        if provider == "openai" and not openai_api_key:
            entered_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="Stored in this browser session only. Or set OPENAI_API_KEY in .env.",
            )
            if entered_key:
                st.session_state.openai_api_key = entered_key.strip()
                openai_api_key = entered_key.strip()
        regenerate = st.button("Generate Summary", type="primary", use_container_width=True)

    top_risks = _top_risks(pipeline.health_records)
    transfer_summary = {
        "recommended_count": len([t for t in pipeline.transfers if t.recommendation == "Transfer Recommended"]),
        "total_net_benefit": sum(t.net_benefit for t in pipeline.transfers),
    }
    markdown_summary = {
        "candidate_count": len(pipeline.markdowns),
        "total_recovery": sum(m.estimated_recovery_value for m in pipeline.markdowns),
    }

    summary_inputs = {
        "kpis": pipeline.kpis.model_dump(),
        "top_risks": top_risks,
        "transfer_summary": transfer_summary,
        "markdown_summary": markdown_summary,
    }

    should_generate = regenerate or (
        provider == "local"
        and "summary_text" not in st.session_state
    )

    if should_generate:
        try:
            with st.spinner(
                "Calling OpenAI..." if provider == "openai" else "Generating local summary..."
            ):
                st.session_state.summary_text = generate_management_summary(
                    summary_inputs["kpis"],
                    summary_inputs["top_risks"],
                    summary_inputs["transfer_summary"],
                    summary_inputs["markdown_summary"],
                    provider=provider,
                    openai_api_key=openai_api_key if provider == "openai" else None,
                )
            st.session_state.summary_provider = provider
            st.session_state.summary_error = None
        except AISummaryError as exc:
            st.session_state.summary_error = str(exc)
            st.session_state.summary_provider = provider

    if st.session_state.get("summary_error") and st.session_state.get("summary_provider") == provider:
        st.error(st.session_state.summary_error)

    if provider == "openai" and not should_generate and "summary_text" not in st.session_state:
        st.info("Enter your OpenAI API key and click **Generate Summary** to create an LLM narrative.")

    if st.session_state.get("summary_text") and st.session_state.get("summary_provider") == provider:
        if provider == "openai":
            st.caption(f"Generated with OpenAI ({settings.openai_model}).")
        else:
            st.caption("Generated with local template (offline).")
        st.markdown(st.session_state.summary_text)

        st.download_button(
            "Download Summary (Markdown)",
            st.session_state.summary_text.encode("utf-8"),
            file_name="management_summary.md",
            mime="text/markdown",
        )

    with st.expander("Summary Inputs (Structured Metrics)"):
        st.json(
            {
                "kpis": summary_inputs["kpis"],
                "top_risks": summary_inputs["top_risks"][:5],
                "transfer_summary": summary_inputs["transfer_summary"],
                "markdown_summary": summary_inputs["markdown_summary"],
            }
        )
