"""Markdown optimization with transfer-first and recovery economics."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config.workbook_config import MARKDOWN_CARRYING_COST_PCT, MARKDOWN_THRESHOLDS
from src.domain.constants import DISPOSITION_SORT_ORDER, MARKDOWN_ELIGIBLE_STATUSES
from src.services.classification_service import build_classification_dataframe
from src.services.forecast_service import build_demand_forecast_dataframe
from src.services.transfer_service import build_surplus_lookup, _normalize_data

MARKDOWN_PLANNER_HEADERS = [
    "SKU",
    "Product Name",
    "Location",
    "ABC Class",
    "Quantity On Hand",
    "Unit Cost",
    "Current Selling Price",
    "Current Margin %",
    "Age Days",
    "Demand Trend",
    "Sell-Through Rate",
    "Transfer Feasible",
    "Obsolescence Risk",
    "Carrying Exposure",
    "Suggested Markdown %",
    "Markdown Price",
    "Projected Sell Through %",
    "Estimated Recovery Value",
    "Margin Impact",
    "Priority",
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


def _obsolescence_risk(
    age_days: int, demand: int, status: str, sell_through: float
) -> str:
    if status == "Obsolete" or (age_days >= 365 and demand == 0):
        return "High"
    if age_days >= 270 and sell_through < 0.10:
        return "High"
    if age_days >= 180:
        return "Medium"
    return "Low"


def _carrying_exposure(qty: int, unit_cost: float, age_days: int) -> float:
    return round(qty * unit_cost * (age_days / 365.0) * MARKDOWN_CARRYING_COST_PCT, 2)


def assign_markdown_plan(
    age_days: int,
    demand_90_day: int,
    status: str,
    sell_through: float,
    transfer_feasible: bool,
) -> tuple[float, str]:
    """Evaluate disposition with transfer-first when economically appropriate."""
    thresholds = MARKDOWN_THRESHOLDS

    if status == "Obsolete" or (age_days >= 365 and demand_90_day == 0):
        if transfer_feasible and status != "Obsolete":
            return 0.0, "Transfer First"
        return 0.30, "Dispose"

    if age_days > thresholds["liquidate_age_days"] and demand_90_day == 0:
        return thresholds["liquidate_markdown_pct"], "Liquidate"

    if transfer_feasible and status in ("Excess", "Excess / Aged", "Slow-Moving"):
        return 0.0, "Transfer First"

    if age_days > 300 and sell_through < 0.10 and demand_90_day > 0:
        return 0.30, "30% Markdown"

    if age_days > thresholds["markdown_20_age_days"]:
        return 0.20, "20% Markdown"

    if age_days > thresholds["markdown_10_age_days"]:
        return 0.10, "10% Markdown"

    if age_days >= 330 and sell_through < 0.05:
        return 0.30, "Discontinue"

    if status == "Excess":
        return thresholds["hold_markdown_pct"], "Transfer First"

    return thresholds["hold_markdown_pct"], thresholds["hold_disposition"]


def project_sell_through(current_rate: float, markdown_pct: float) -> float:
    """Estimate sell-through improvement after markdown."""
    if markdown_pct == 0:
        return round(current_rate, 4)
    uplift = markdown_pct * 0.45
    return round(min(current_rate + uplift, 0.90), 4)


def _priority_score(
    recovery_value: float, obsolescence: str, carrying: float, disposition: str
) -> str:
    score = recovery_value / 100.0 + carrying / 50.0
    if obsolescence == "High":
        score += 50
    elif obsolescence == "Medium":
        score += 20
    if disposition in ("Liquidate", "Dispose", "Discontinue"):
        score += 30
    if score >= 80:
        return "Critical"
    if score >= 40:
        return "High"
    if score >= 15:
        return "Medium"
    return "Low"


def build_markdown_dataframe(
    data: dict[str, pd.DataFrame] | pd.DataFrame,
) -> pd.DataFrame:
    """Build markdown planner rows with transfer-first optimization."""
    ctx = _normalize_data(data)
    df = ctx.get("inventory", ctx.get("inventory_full", pd.DataFrame()))
    if df.empty:
        return pd.DataFrame(columns=MARKDOWN_PLANNER_HEADERS)

    if "location" not in df.columns and "location_name" in df.columns:
        df = df.copy()
        df["location"] = df["location_name"]

    classification = build_classification_dataframe(ctx)
    abc_map = (
        classification.set_index("SKU")["ABC Class"].to_dict()
        if not classification.empty
        else {}
    )

    forecast = build_demand_forecast_dataframe(ctx)
    trend_map: dict[tuple[str, str], str] = {}
    if not forecast.empty:
        for _, row in forecast.iterrows():
            trend_map[(str(row["SKU"]), str(row["Location ID"]))] = str(
                row["Demand Trend"]
            )
            trend_map[(str(row["SKU"]), str(row["Location Name"]))] = str(
                row["Demand Trend"]
            )

    surplus_by_sku = build_surplus_lookup(ctx)

    working = df[df["status"].isin(MARKDOWN_ELIGIBLE_STATUSES)].copy()
    if working.empty:
        return pd.DataFrame(columns=MARKDOWN_PLANNER_HEADERS)

    rows: list[dict[str, Any]] = []
    for _, record in working.iterrows():
        age_days = int(record["age_days"])
        demand = int(record["demand_90_day"])
        status = str(record["status"])
        sku = str(record["sku"])
        loc = str(record.get("location", record.get("location_name", "")))
        qty = int(record["quantity_on_hand"])
        unit_cost = float(record["unit_cost"])
        selling_price = float(record["selling_price"])
        sell_through = float(record["sell_through_rate"])
        current_margin = float(record["gross_margin_pct"])

        network_surplus = surplus_by_sku.get(sku, 0)
        local_excess = qty - int(record.get("max_stock", qty))
        transfer_feasible = network_surplus > 0 and local_excess > 0
        trend = trend_map.get((sku, loc), assign_demand_trend(demand, sell_through))
        obs_risk = _obsolescence_risk(age_days, demand, status, sell_through)
        carrying = _carrying_exposure(qty, unit_cost, age_days)

        markdown_pct, disposition = assign_markdown_plan(
            age_days, demand, status, sell_through, transfer_feasible
        )
        markdown_price = round(selling_price * (1 - markdown_pct), 2)
        projected_str = project_sell_through(sell_through, markdown_pct)
        recovery_value = round(qty * markdown_price * projected_str, 2)

        current_margin_dollars = (selling_price - unit_cost) * qty * sell_through
        projected_margin_dollars = (markdown_price - unit_cost) * qty * projected_str
        margin_impact = round(projected_margin_dollars - current_margin_dollars, 2)
        priority = _priority_score(recovery_value, obs_risk, carrying, disposition)

        rows.append(
            {
                "SKU": sku,
                "Product Name": record["product_name"],
                "Location": loc,
                "ABC Class": abc_map.get(sku, "C"),
                "Quantity On Hand": qty,
                "Unit Cost": unit_cost,
                "Current Selling Price": selling_price,
                "Current Margin %": current_margin,
                "Age Days": age_days,
                "Demand Trend": trend,
                "Sell-Through Rate": round(sell_through, 4),
                "Transfer Feasible": "Yes" if transfer_feasible else "No",
                "Obsolescence Risk": obs_risk,
                "Carrying Exposure": carrying,
                "Suggested Markdown %": markdown_pct,
                "Markdown Price": markdown_price,
                "Projected Sell Through %": projected_str,
                "Estimated Recovery Value": recovery_value,
                "Margin Impact": margin_impact,
                "Priority": priority,
                "Recommended Disposition": disposition,
            }
        )

    result = pd.DataFrame(rows, columns=MARKDOWN_PLANNER_HEADERS)
    result["_sort"] = (
        result["Recommended Disposition"].map(DISPOSITION_SORT_ORDER).fillna(99)
    )
    return (
        result.sort_values(
            ["_sort", "Estimated Recovery Value"], ascending=[True, False]
        )
        .drop(columns="_sort")
        .reset_index(drop=True)
    )
