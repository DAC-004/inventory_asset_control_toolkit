"""Aged & Excess Inventory page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.services.inventory_health_service import get_exception_records
from src.services.summary_service import PipelineResult
from src.ui.components import render_explanation_panel, styled_health_dataframe


def render(pipeline: PipelineResult) -> None:
    st.markdown("### Aged & Excess Inventory")
    st.caption("Exception inventory prioritized by financial exposure and operational risk.")

    exceptions = get_exception_records(pipeline.health_records)
    df = pd.DataFrame([r.model_dump() for r in exceptions])

    if df.empty:
        st.success("No exception inventory detected.")
        return

    col1, col2, col3, col4 = st.columns(4)
    locations = sorted(df["location"].unique())
    categories = sorted(df["category"].unique())
    issue_types = sorted(df["issue_type"].unique())
    risk_levels = sorted(df["risk_level"].unique())
    actions = sorted(df["recommended_action"].unique())

    with col1:
        sel_loc = st.multiselect("Location", locations, default=locations)
    with col2:
        sel_cat = st.multiselect("Category", categories, default=categories)
    with col3:
        sel_issue = st.multiselect("Issue Type", issue_types, default=issue_types)
    with col4:
        sel_risk = st.multiselect("Risk Level", risk_levels, default=risk_levels)

    sel_action = st.multiselect("Recommended Action", actions, default=actions)

    filtered = df[
        df["location"].isin(sel_loc)
        & df["category"].isin(sel_cat)
        & df["issue_type"].isin(sel_issue)
        & df["risk_level"].isin(sel_risk)
        & df["recommended_action"].isin(sel_action)
    ].sort_values("inventory_value", ascending=False)

    display_cols = [
        "sku", "product_name", "category", "location", "region",
        "on_hand_qty", "min_stock", "max_stock", "excess_qty",
        "inventory_age_days", "demand_90_day", "avg_weekly_sales",
        "sell_through_rate", "days_of_supply", "inventory_value",
        "gross_margin", "risk_level", "issue_type", "recommended_action",
        "recommendation_reason",
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    styled_health_dataframe(filtered[display_cols])

    st.download_button(
        "Download Filtered Exceptions (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="aged_excess_exceptions.csv",
        mime="text/csv",
    )

    if not filtered.empty:
        selected = st.selectbox(
            "View recommendation detail",
            filtered.index,
            format_func=lambda i: f"{filtered.loc[i, 'sku']} @ {filtered.loc[i, 'location']} — {filtered.loc[i, 'issue_type']}",
        )
        row = filtered.loc[selected]
        render_explanation_panel(
            "Recommendation Explanation",
            row["recommendation_reason"],
        )
