"""Executive Dashboard page."""

from __future__ import annotations

import streamlit as st

from src.services.summary_service import PipelineResult
from src.ui.components import (
    action_breakdown_chart,
    aging_bucket_chart,
    inventory_value_by_location_chart,
    render_kpi_row,
    status_breakdown_chart,
    top_risks_chart,
)


def render(pipeline: PipelineResult) -> None:
    st.markdown("### Executive Dashboard")
    st.caption("High-level inventory health control tower with portfolio KPIs and risk visualization.")

    render_kpi_row(pipeline.kpis)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            inventory_value_by_location_chart(pipeline.health_records),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            status_breakdown_chart(pipeline.health_records),
            use_container_width=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            aging_bucket_chart(pipeline.health_records),
            use_container_width=True,
        )
    with col4:
        st.plotly_chart(
            action_breakdown_chart(pipeline.health_records),
            use_container_width=True,
        )

    st.plotly_chart(
        top_risks_chart(pipeline.health_records),
        use_container_width=True,
    )
