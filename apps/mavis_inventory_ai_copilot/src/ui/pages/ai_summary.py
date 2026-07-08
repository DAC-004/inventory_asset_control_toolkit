"""AI Management Summary page."""

from __future__ import annotations

import streamlit as st

from src.services.ai_service import generate_management_summary
from src.services.summary_service import PipelineResult, _top_risks


def render(pipeline: PipelineResult) -> None:
    st.markdown("### AI Management Summary")
    st.caption("Executive-ready narrative generated from calculated KPIs and recommendations.")

    col1, col2 = st.columns([1, 3])
    with col1:
        provider = st.selectbox("AI Provider", ["local", "openai", "anthropic", "gemini"], index=0)
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

    if regenerate or "summary_text" not in st.session_state:
        st.session_state.summary_text = generate_management_summary(
            pipeline.kpis.model_dump(),
            top_risks,
            transfer_summary,
            markdown_summary,
            provider=provider,
        )

    st.markdown(st.session_state.get("summary_text", pipeline.management_summary))

    st.download_button(
        "Download Summary (Markdown)",
        st.session_state.get("summary_text", pipeline.management_summary).encode("utf-8"),
        file_name="management_summary.md",
        mime="text/markdown",
    )

    with st.expander("Summary Inputs (Structured Metrics)"):
        st.json(
            {
                "kpis": pipeline.kpis.model_dump(),
                "top_risks": top_risks[:5],
                "transfer_summary": transfer_summary,
                "markdown_summary": markdown_summary,
            }
        )
