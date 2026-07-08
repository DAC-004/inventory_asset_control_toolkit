"""Markdown Planner page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.summary_service import PipelineResult
from src.ui.components import markdown_recovery_chart, render_explanation_panel, styled_health_dataframe


def render(pipeline: PipelineResult) -> None:
    st.markdown("### Markdown Planner")
    st.caption("Margin-aware exit strategies for aged, excess, and slow-moving inventory.")

    markdowns = pipeline.markdowns
    if not markdowns:
        st.info("No markdown candidates identified for the current dataset.")
        return

    df = pd.DataFrame([m.model_dump() for m in markdowns])

    dispositions = st.multiselect(
        "Disposition",
        sorted(df["recommended_disposition"].unique()),
        default=sorted(df["recommended_disposition"].unique()),
    )
    min_recovery = st.slider(
        "Minimum Recovery Value ($)",
        0,
        int(df["estimated_recovery_value"].max()) + 1,
        0,
    )

    filtered = df[
        df["recommended_disposition"].isin(dispositions)
        & (df["estimated_recovery_value"] >= min_recovery)
    ].sort_values("estimated_recovery_value", ascending=False)

    st.plotly_chart(markdown_recovery_chart(filtered), use_container_width=True)

    display_cols = [
        "sku", "product_name", "location", "inventory_age_days",
        "current_retail_price", "unit_cost", "current_margin",
        "suggested_markdown_pct", "markdown_price", "projected_sell_through_pct",
        "estimated_recovery_value", "margin_impact", "recommended_disposition",
        "explanation",
    ]
    display = filtered[display_cols].copy()
    display["suggested_markdown_pct"] = display["suggested_markdown_pct"].map(lambda x: f"{x:.0%}")
    display["projected_sell_through_pct"] = display["projected_sell_through_pct"].map(lambda x: f"{x:.0%}")

    styled_health_dataframe(display)

    st.download_button(
        "Download Markdown Plan (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="markdown_recommendations.csv",
        mime="text/csv",
    )

    if not filtered.empty:
        idx = st.selectbox(
            "Markdown detail",
            filtered.index,
            format_func=lambda i: (
                f"{filtered.loc[i, 'sku']} @ {filtered.loc[i, 'location']} — "
                f"{filtered.loc[i, 'recommended_disposition']}"
            ),
        )
        render_explanation_panel("Markdown Rationale", filtered.loc[idx, "explanation"])
