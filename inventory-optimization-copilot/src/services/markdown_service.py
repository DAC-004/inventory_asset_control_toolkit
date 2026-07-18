"""Markdown planning and recovery calculations."""

from __future__ import annotations

import pandas as pd

from config.workbook_config import MARKDOWN_THRESHOLDS
from src.domain.constants import DISPOSITION_SORT_ORDER, MARKDOWN_ELIGIBLE_STATUSES

MARKDOWN_PLANNER_HEADERS = [
    "SKU",
    "Product Name",
    "Location",
    "Quantity On Hand",
    "Unit Cost",
    "Current Selling Price",
    "Current Margin %",
    "Age Days",
    "Demand Trend",
    "Suggested Markdown %",
    "Markdown Price",
    "Projected Sell Through %",
    "Estimated Recovery Value",
    "Margin Impact",
    "Recommended Disposition",
]


def assign_demand_trend(demand_90_day: int, sell_through_rate: float) -> str:
    """Classify demand trend for markdown planning."""
    if demand_90_day == 0:
        return "No Demand"
    if sell_through_rate < 0.10:
        return "Declining"
    if sell_through_rate < 0.20:
        return "Slow"
    return "Moderate"


def assign_markdown_plan(
    age_days: int,
    demand_90_day: int,
    status: str,
) -> tuple[float, str]:
    """Apply markdown rules in priority order."""
    thresholds = MARKDOWN_THRESHOLDS

    if age_days > thresholds["liquidate_age_days"] and demand_90_day == 0:
        return thresholds["liquidate_markdown_pct"], thresholds["liquidate_disposition"]

    if age_days > thresholds["markdown_20_age_days"]:
        return thresholds["markdown_20_pct"], thresholds["markdown_20_disposition"]

    if age_days > thresholds["markdown_10_age_days"]:
        return thresholds["markdown_10_pct"], thresholds["markdown_10_disposition"]

    if status == "Excess":
        return thresholds["hold_markdown_pct"], "Transfer First"

    return thresholds["hold_markdown_pct"], thresholds["hold_disposition"]


def project_sell_through(current_rate: float, markdown_pct: float) -> float:
    """Estimate sell-through improvement after markdown."""
    if markdown_pct == 0:
        return round(current_rate, 4)
    uplift = markdown_pct * 0.45
    return round(min(current_rate + uplift, 0.90), 4)


def build_markdown_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Build markdown planner rows from eligible inventory records."""
    if df.empty:
        return pd.DataFrame(columns=MARKDOWN_PLANNER_HEADERS)

    working = df[df["status"].isin(MARKDOWN_ELIGIBLE_STATUSES)].copy()
    if working.empty:
        return pd.DataFrame(columns=MARKDOWN_PLANNER_HEADERS)

    rows = []
    for _, record in working.iterrows():
        age_days = int(record["age_days"])
        demand = int(record["demand_90_day"])
        status = str(record["status"])
        qty = int(record["quantity_on_hand"])
        unit_cost = float(record["unit_cost"])
        selling_price = float(record["selling_price"])
        sell_through = float(record["sell_through_rate"])
        current_margin = float(record["gross_margin_pct"])

        markdown_pct, disposition = assign_markdown_plan(age_days, demand, status)
        markdown_price = round(selling_price * (1 - markdown_pct), 2)
        projected_str = project_sell_through(sell_through, markdown_pct)
        recovery_value = round(qty * markdown_price * projected_str, 2)

        current_margin_dollars = (selling_price - unit_cost) * qty * sell_through
        projected_margin_dollars = (markdown_price - unit_cost) * qty * projected_str
        margin_impact = round(projected_margin_dollars - current_margin_dollars, 2)

        rows.append(
            {
                "SKU": record["sku"],
                "Product Name": record["product_name"],
                "Location": record["location"],
                "Quantity On Hand": qty,
                "Unit Cost": unit_cost,
                "Current Selling Price": selling_price,
                "Current Margin %": current_margin,
                "Age Days": age_days,
                "Demand Trend": assign_demand_trend(demand, sell_through),
                "Suggested Markdown %": markdown_pct,
                "Markdown Price": markdown_price,
                "Projected Sell Through %": projected_str,
                "Estimated Recovery Value": recovery_value,
                "Margin Impact": margin_impact,
                "Recommended Disposition": disposition,
            }
        )

    result = pd.DataFrame(rows, columns=MARKDOWN_PLANNER_HEADERS)
    result["_sort"] = result["Recommended Disposition"].map(DISPOSITION_SORT_ORDER)
    return (
        result.sort_values(
            ["_sort", "Estimated Recovery Value"], ascending=[True, False]
        )
        .drop(columns="_sort")
        .reset_index(drop=True)
    )
