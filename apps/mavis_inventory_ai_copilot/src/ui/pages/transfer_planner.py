"""Transfer Planner page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.summary_service import PipelineResult
from src.ui.components import render_explanation_panel, styled_health_dataframe, transfer_benefit_chart


def render(pipeline: PipelineResult) -> None:
    st.markdown("### Transfer Planner")
    st.caption("Network balancing recommendations ranked by net financial benefit.")

    transfers = pipeline.transfers
    if not transfers:
        st.info("No transfer recommendations meet the net benefit threshold.")
        return

    df = pd.DataFrame([t.model_dump() for t in transfers])

    min_benefit = st.slider("Minimum Net Benefit ($)", 0, int(df["net_benefit"].max()) + 1, 0)
    confidence = st.multiselect(
        "Confidence Level",
        sorted(df["confidence_level"].unique()),
        default=sorted(df["confidence_level"].unique()),
    )

    filtered = df[
        (df["net_benefit"] >= min_benefit) & (df["confidence_level"].isin(confidence))
    ].sort_values("net_benefit", ascending=False)

    st.plotly_chart(transfer_benefit_chart(filtered), use_container_width=True)

    display_cols = [
        "sku", "product_name", "source_location", "destination_location",
        "source_excess_qty", "destination_need_qty", "suggested_transfer_qty",
        "transfer_cost_per_unit", "total_transfer_cost", "estimated_margin_protected",
        "net_benefit", "recommendation", "confidence_level", "explanation",
    ]
    styled_health_dataframe(filtered[display_cols])

    st.download_button(
        "Download Transfer Plan (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="transfer_recommendations.csv",
        mime="text/csv",
    )

    if not filtered.empty:
        idx = st.selectbox(
            "Transfer detail",
            filtered.index,
            format_func=lambda i: (
                f"{filtered.loc[i, 'sku']}: {filtered.loc[i, 'source_location']} → "
                f"{filtered.loc[i, 'destination_location']} (${filtered.loc[i, 'net_benefit']:,.0f})"
            ),
        )
        render_explanation_panel("Transfer Rationale", filtered.loc[idx, "explanation"])
