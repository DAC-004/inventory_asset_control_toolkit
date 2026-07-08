"""Reusable Streamlit UI components."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config.constants import AGING_BUCKETS, RISK_COLORS
from src.models.inventory import InventoryHealthRecord
from src.models.recommendations import DashboardKPIs
from src.ui.theme import COLORS, PLOTLY_TEMPLATE
from src.utils.formatting import format_currency, format_percent


def render_header() -> None:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%);
            width: 100%;
            box-sizing: border-box;
            padding: 0.65rem 1.5rem;
            border-radius: 8px;
            margin: 0 0 0.75rem 0;
            box-shadow: 0 2px 4px -1px rgba(0,0,0,0.08);
            text-align: center;
        ">
            <h1 style="
                margin: 0;
                font-size: 1.2rem;
                font-weight: 700;
                line-height: 1.3;
                color: #ffffff;
            ">Inventory Optimization AI Co-Pilot</h1>
            <p style="
                margin: 0.2rem 0 0 0;
                font-size: 0.78rem;
                line-height: 1.4;
                color: rgba(255,255,255,0.9);
                max-width: 720px;
                margin-left: auto;
                margin-right: auto;
            ">Enterprise inventory health, transfer optimization, markdown planning,
            and AI-assisted leadership summaries.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, context: str = "", status: str = "neutral") -> None:
    badge_styles = {
        "high": "background:#FEE2E2;color:#991B1B;",
        "medium": "background:#FEF3C7;color:#92400E;",
        "low": "background:#D1FAE5;color:#065F46;",
        "neutral": "background:#DBEAFE;color:#1E40AF;",
    }
    badge_style = badge_styles.get(status, badge_styles["neutral"])

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #E2E8F0;
            border-radius:10px;
            padding:0.9rem 1rem;
            min-height:118px;
            height:100%;
            box-shadow:0 1px 3px rgba(0,0,0,0.05);
            display:flex;
            flex-direction:column;
            box-sizing:border-box;
        ">
            <div style="
                color:#64748B;
                font-size:0.72rem;
                font-weight:600;
                text-transform:uppercase;
                letter-spacing:0.03em;
                line-height:1.3;
                margin-bottom:0.15rem;
            ">{label}</div>
            <div style="
                color:#0F172A;
                font-size:1.35rem;
                font-weight:700;
                margin:0.1rem 0 0.35rem 0;
                line-height:1.2;
            ">{value}</div>
            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:0.5rem;
                margin-top:auto;
                flex-wrap:wrap;
            ">
                <div style="
                    color:#64748B;
                    font-size:0.75rem;
                    line-height:1.3;
                    flex:1;
                    min-width:0;
                ">{context}</div>
                <span style="
                    display:inline-block;
                    padding:0.15rem 0.5rem;
                    border-radius:999px;
                    font-size:0.68rem;
                    font-weight:600;
                    white-space:nowrap;
                    {badge_style}
                ">{status.title()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(kpis: DashboardKPIs) -> None:
    row1 = st.columns(4)
    metrics = [
        ("Total Inventory Value", format_currency(kpis.total_inventory_value), "Portfolio at cost", "neutral"),
        ("Aged Inventory Value", format_currency(kpis.aged_inventory_value), "≥180 days", "high" if kpis.aged_inventory_value > 50000 else "medium"),
        ("Excess Inventory Value", format_currency(kpis.excess_inventory_value), "Above max stock", "high" if kpis.excess_inventory_value > 30000 else "medium"),
        ("Estimated Recovery", format_currency(kpis.estimated_recovery_value), "Markdown potential", "low"),
    ]
    for col, (label, value, ctx, status) in zip(row1, metrics):
        with col:
            render_kpi_card(label, value, ctx, status)

    row2 = st.columns(4)
    metrics2 = [
        ("Slow-Moving SKUs", str(kpis.slow_moving_sku_count), "Unique SKUs", "medium"),
        ("Obsolete SKUs", str(kpis.obsolete_sku_count), "Exit candidates", "high"),
        ("Transfer Candidates", str(kpis.transfer_candidate_count), "Net benefit > 0", "low"),
        ("Stockout Risk", str(kpis.stockout_risk_count), "Below min stock", "high" if kpis.stockout_risk_count > 5 else "medium"),
    ]
    for col, (label, value, ctx, status) in zip(row2, metrics2):
        with col:
            render_kpi_card(label, value, ctx, status)

    row3 = st.columns(4)
    metrics3 = [
        ("Avg Gross Margin", format_percent(kpis.average_gross_margin_percent), "Portfolio average", "low"),
        ("Inventory Turnover", f"{kpis.inventory_turnover:.2f}x", "Annualized approx.", "neutral"),
        ("GMROI", f"{kpis.gmroi:.2f}", "Gross margin ROI", "neutral"),
        ("Avg Days of Supply", f"{kpis.average_days_of_supply:.0f}", "Network average", "medium"),
    ]
    for col, (label, value, ctx, status) in zip(row3, metrics3):
        with col:
            render_kpi_card(label, value, ctx, status)


def _horizontal_bar_layout(fig: go.Figure, *, height: int, left_margin: int = 140) -> go.Figure:
    fig.update_layout(
        margin=dict(l=left_margin, r=24, t=48, b=24),
        height=height,
        yaxis=dict(automargin=True, tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11)),
        title=dict(font=dict(size=14), x=0, xanchor="left"),
    )
    return fig


def inventory_value_by_location_chart(records: list[InventoryHealthRecord]) -> go.Figure:
    df = pd.DataFrame([r.model_dump() for r in records])
    agg = df.groupby("location", as_index=False)["inventory_value"].sum().sort_values(
        "inventory_value", ascending=True
    )
    fig = px.bar(
        agg,
        x="inventory_value",
        y="location",
        orientation="h",
        title="Inventory Value by Location",
        color_discrete_sequence=[COLORS["secondary"]],
        template=PLOTLY_TEMPLATE,
    )
    height = max(380, len(agg) * 26 + 80)
    fig.update_xaxes(title="Inventory Value ($)")
    return _horizontal_bar_layout(fig, height=height, left_margin=120)


def status_breakdown_chart(records: list[InventoryHealthRecord]) -> go.Figure:
    df = pd.DataFrame([r.model_dump() for r in records])
    counts = df["issue_type"].value_counts().reset_index()
    counts.columns = ["issue_type", "count"]
    fig = px.pie(
        counts,
        names="issue_type",
        values="count",
        title="Inventory Status Breakdown",
        hole=0.45,
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=48, b=20),
        height=400,
        title=dict(font=dict(size=14), x=0, xanchor="left"),
        legend=dict(font=dict(size=11)),
    )
    return fig


def aging_bucket_chart(records: list[InventoryHealthRecord]) -> go.Figure:
    df = pd.DataFrame([r.model_dump() for r in records])

    def bucket(age: int) -> str:
        for low, high, label in AGING_BUCKETS:
            if low <= age <= high:
                return label
        return "365+ days"

    df["aging_bucket"] = df["inventory_age_days"].apply(bucket)
    agg = df.groupby("aging_bucket", as_index=False)["inventory_value"].sum()
    order = [b[2] for b in AGING_BUCKETS]
    agg["aging_bucket"] = pd.Categorical(agg["aging_bucket"], categories=order, ordered=True)
    agg = agg.sort_values("aging_bucket")
    fig = px.bar(
        agg,
        x="aging_bucket",
        y="inventory_value",
        title="Aging Bucket Summary",
        color_discrete_sequence=[COLORS["accent"]],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=48, b=40),
        height=360,
        title=dict(font=dict(size=14), x=0, xanchor="left"),
    )
    fig.update_xaxes(title="Age Bucket", tickfont=dict(size=11))
    fig.update_yaxes(title="Inventory Value ($)", tickfont=dict(size=11))
    return fig


def action_breakdown_chart(records: list[InventoryHealthRecord]) -> go.Figure:
    df = pd.DataFrame([r.model_dump() for r in records])
    counts = df["recommended_action"].value_counts().reset_index()
    counts.columns = ["action", "count"]
    counts = counts.sort_values("count", ascending=True)
    fig = px.bar(
        counts,
        x="count",
        y="action",
        orientation="h",
        title="Recommended Action Breakdown",
        color="count",
        color_continuous_scale="Blues",
        template=PLOTLY_TEMPLATE,
    )
    height = max(320, len(counts) * 34 + 80)
    fig.update_layout(
        margin=dict(l=20, r=20, t=48, b=24),
        height=height,
        showlegend=False,
        title=dict(font=dict(size=14), x=0, xanchor="left"),
        yaxis=dict(automargin=True, tickfont=dict(size=11)),
        xaxis=dict(title="Count", tickfont=dict(size=11)),
    )
    return fig


def top_risks_chart(records: list[InventoryHealthRecord], limit: int = 10) -> go.Figure:
    df = pd.DataFrame([r.model_dump() for r in records])
    df = df[df["issue_type"] != "Healthy"].copy()
    df["label"] = df["sku"] + " @ " + df["location"]
    top = df.nlargest(limit, "inventory_value")
    fig = px.bar(
        top,
        x="inventory_value",
        y="label",
        orientation="h",
        title="Top Inventory Risks by Dollar Exposure",
        color="risk_level",
        color_discrete_map=RISK_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    height = max(420, len(top) * 30 + 80)
    return _horizontal_bar_layout(fig, height=height, left_margin=180)


def transfer_benefit_chart(transfers_df: pd.DataFrame) -> go.Figure:
    if transfers_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Net Benefit by Transfer Recommendation", template=PLOTLY_TEMPLATE)
        return fig
    top = transfers_df.nlargest(10, "net_benefit").copy()
    top["label"] = top["sku"] + ": " + top["source_location"] + " → " + top["destination_location"]
    fig = px.bar(
        top,
        x="net_benefit",
        y="label",
        orientation="h",
        title="Net Benefit by Transfer Recommendation",
        color_discrete_sequence=[COLORS["success"]],
        template=PLOTLY_TEMPLATE,
    )
    height = max(420, len(top) * 30 + 80)
    return _horizontal_bar_layout(fig, height=height, left_margin=200)


def markdown_recovery_chart(markdowns_df: pd.DataFrame) -> go.Figure:
    if markdowns_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Estimated Recovery by Markdown", template=PLOTLY_TEMPLATE)
        return fig
    top = markdowns_df.nlargest(10, "estimated_recovery_value").copy()
    top["label"] = top["sku"] + " @ " + top["location"]
    fig = px.bar(
        top,
        x="estimated_recovery_value",
        y="label",
        orientation="h",
        title="Estimated Recovery by Markdown Recommendation",
        color_discrete_sequence=[COLORS["warning"]],
        template=PLOTLY_TEMPLATE,
    )
    height = max(420, len(top) * 30 + 80)
    return _horizontal_bar_layout(fig, height=height, left_margin=160)


def render_explanation_panel(title: str, text: str) -> None:
    st.markdown(f"#### {title}")
    st.info(text)


def styled_health_dataframe(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No records match the current filters.")
        return

    display = df.copy()

    def highlight_risk(row: pd.Series) -> list[str]:
        if row.get("risk_level") == "High":
            return ["background-color: #FEE2E2"] * len(row)
        if row.get("risk_level") == "Medium":
            return ["background-color: #FEF3C7"] * len(row)
        return [""] * len(row)

    if "risk_level" in display.columns:
        st.dataframe(display.style.apply(highlight_risk, axis=1), use_container_width=True, hide_index=True)
    else:
        st.dataframe(display, use_container_width=True, hide_index=True)
