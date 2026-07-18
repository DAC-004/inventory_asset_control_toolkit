"""Service level analytics — fill rates, backorders, stockouts, and gap analysis."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from config.workbook_config import (
    DEFAULT_SERVICE_LEVEL_TARGET,
    SERVICE_LEVEL_BELOW_TARGET_GAP,
    SERVICE_LEVEL_WATCH_GAP,
)

SERVICE_LEVEL_HEADERS = [
    "Period",
    "Location ID",
    "Location Name",
    "Region",
    "Category",
    "Customer Segment",
    "Order Count",
    "Line Count",
    "Units Ordered",
    "Units Fulfilled Immediately",
    "Unit Fill Rate",
    "Line Fill Rate",
    "Order Fill Rate",
    "Backorder Units",
    "Backorder Rate",
    "Lost Sales Units",
    "Lost Sales Rate",
    "Stockout Weeks",
    "Stockout Frequency",
    "Avg Fulfillment Time (Days)",
    "Service Level Target",
    "Service Gap",
    "Status",
    "Root Cause",
    "Recommendation",
]

ANALYSIS_PERIOD = "Trailing 52 Weeks"


def _finite_rate(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return 0.0
    return _finite_rate(numerator / denominator)


def _service_status(gap: float, has_data: bool) -> str:
    if not has_data:
        return "Data Review Required"
    if gap <= 0:
        return "On Target"
    if gap <= SERVICE_LEVEL_WATCH_GAP:
        return "Watch"
    if gap <= SERVICE_LEVEL_BELOW_TARGET_GAP:
        return "Below Target"
    return "Critical"


def _root_cause_and_recommendation(
    unit_fill: float,
    backorder_rate: float,
    stockout_freq: float,
    target: float,
) -> tuple[str, str]:
    if unit_fill >= target:
        return "Performance meets target", "Continue monitoring"

    if stockout_freq >= 0.10:
        return (
            "Elevated stockout frequency constraining fulfillment",
            "Increase safety stock and review replenishment timing",
        )
    if backorder_rate >= 0.15:
        return (
            "Supply lag driving backorders",
            "Expedite open POs and tighten lead-time monitoring",
        )
    if unit_fill < target - 0.10:
        return (
            "Broad fulfillment shortfall across lines",
            "Review inventory allocation and demand forecast accuracy",
        )
    return (
        "Partial line fulfillment pattern",
        "Investigate pick-pack constraints and segment prioritization",
    )


def _normalize_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty:
        return inventory
    inv = inventory.copy()
    if "location_name" not in inv.columns:
        inv["location_name"] = inv.get("location", "")
    if "location_id" not in inv.columns:
        inv["location_id"] = inv.get("location", inv.get("location_name", "UNKNOWN"))
    if "region" not in inv.columns:
        inv["region"] = ""
    if "category" not in inv.columns:
        inv["category"] = "Unknown"
    return inv


def _inventory_lookup(inventory: pd.DataFrame) -> dict[tuple[str, str], dict[str, str]]:
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    inventory = _normalize_inventory(inventory)
    if inventory.empty:
        return lookup
    for _, row in inventory.drop_duplicates(subset=["sku", "location_id"]).iterrows():
        lookup[(str(row["sku"]), str(row["location_id"]))] = {
            "location_name": str(row.get("location_name", row.get("location", ""))),
            "region": str(row.get("region", "")),
            "category": str(row.get("category", "")),
        }
    return lookup


def _demand_metrics_by_location_category(
    demand: pd.DataFrame, inv_lookup: dict[tuple[str, str], dict[str, str]]
) -> dict[tuple[str, str], dict[str, int | float]]:
    metrics: dict[tuple[str, str], dict[str, int | float]] = {}
    if demand.empty:
        return metrics

    enriched = demand.copy()
    enriched["category"] = enriched.apply(
        lambda r: inv_lookup.get((str(r["sku"]), str(r["location_id"])), {}).get(
            "category", "Unknown"
        ),
        axis=1,
    )
    for (loc_id, category), grp in enriched.groupby(["location_id", "category"]):
        weeks = max(grp["week_start_date"].nunique(), 1)
        metrics[(str(loc_id), str(category))] = {
            "lost_sales_units": int(grp["lost_sales_units"].sum()),
            "stockout_weeks": int((grp["stockout_flag"] == "Yes").sum()),
            "demand_weeks": weeks,
        }
    return metrics


def build_service_level_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build service level analysis by location, category, and segment."""
    orders = data.get("customer_orders", pd.DataFrame())
    demand = data.get("demand_history", pd.DataFrame())
    inventory = _normalize_inventory(
        data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    )

    if orders.empty:
        return pd.DataFrame(columns=SERVICE_LEVEL_HEADERS)

    inv_lookup = _inventory_lookup(inventory)
    demand_metrics = _demand_metrics_by_location_category(demand, inv_lookup)

    orders = orders.copy()
    orders["location_name"] = orders.apply(
        lambda r: inv_lookup.get((str(r["sku"]), str(r["location_id"])), {}).get(
            "location_name", ""
        ),
        axis=1,
    )
    orders["region"] = orders.apply(
        lambda r: inv_lookup.get((str(r["sku"]), str(r["location_id"])), {}).get(
            "region", ""
        ),
        axis=1,
    )
    orders["category"] = orders.apply(
        lambda r: inv_lookup.get((str(r["sku"]), str(r["location_id"])), {}).get(
            "category", "Unknown"
        ),
        axis=1,
    )

    group_cols = [
        "location_id",
        "location_name",
        "region",
        "category",
        "customer_segment",
    ]
    rows: list[dict[str, Any]] = []

    for keys, grp in orders.groupby(group_cols, dropna=False):
        loc_id, loc_name, region, category, segment = keys
        units_ordered = int(grp["ordered_units"].sum())
        units_fulfilled = int(grp["fulfilled_units"].sum())
        backorder_units = int(grp["backordered_units"].sum())
        line_count = len(grp)
        order_count = int(grp["order_id"].nunique())

        line_fill = int((grp["line_status"] == "Fulfilled").sum())
        order_complete = int(
            grp.groupby("order_id")
            .apply(
                lambda g: bool((g["ordered_units"] == g["fulfilled_units"]).all()),
                include_groups=False,
            )
            .sum()
        )

        fulfillment_days: list[float] = []
        for _, line in grp.iterrows():
            if pd.notna(line["fulfilled_date"]) and pd.notna(line["order_date"]):
                delta = (
                    pd.to_datetime(line["fulfilled_date"])
                    - pd.to_datetime(line["order_date"])
                ).days
                if delta >= 0:
                    fulfillment_days.append(float(delta))
        avg_fulfillment = (
            round(sum(fulfillment_days) / len(fulfillment_days), 1)
            if fulfillment_days
            else 0.0
        )

        unit_fill = _safe_div(units_fulfilled, units_ordered)
        line_fill_rate = _safe_div(line_fill, line_count)
        order_fill_rate = _safe_div(order_complete, order_count)
        backorder_rate = _safe_div(backorder_units, units_ordered)

        dmd = demand_metrics.get((str(loc_id), str(category)), {})
        lost_units = int(dmd.get("lost_sales_units", 0))
        stockout_weeks = int(dmd.get("stockout_weeks", 0))
        demand_weeks = int(dmd.get("demand_weeks", 52))

        lost_rate = _safe_div(lost_units, units_ordered + lost_units)
        stockout_freq = _safe_div(stockout_weeks, demand_weeks)

        target = DEFAULT_SERVICE_LEVEL_TARGET
        gap = round(max(0.0, target - unit_fill), 4)
        has_data = units_ordered > 0
        status = _service_status(gap, has_data)
        root, recommendation = _root_cause_and_recommendation(
            unit_fill, backorder_rate, stockout_freq, target
        )

        rows.append(
            {
                "Period": ANALYSIS_PERIOD,
                "Location ID": loc_id,
                "Location Name": loc_name,
                "Region": region,
                "Category": category,
                "Customer Segment": segment,
                "Order Count": order_count,
                "Line Count": line_count,
                "Units Ordered": units_ordered,
                "Units Fulfilled Immediately": units_fulfilled,
                "Unit Fill Rate": round(unit_fill, 4),
                "Line Fill Rate": round(line_fill_rate, 4),
                "Order Fill Rate": round(order_fill_rate, 4),
                "Backorder Units": backorder_units,
                "Backorder Rate": round(backorder_rate, 4),
                "Lost Sales Units": lost_units,
                "Lost Sales Rate": round(lost_rate, 4),
                "Stockout Weeks": stockout_weeks,
                "Stockout Frequency": round(stockout_freq, 4),
                "Avg Fulfillment Time (Days)": avg_fulfillment,
                "Service Level Target": target,
                "Service Gap": gap,
                "Status": status,
                "Root Cause": root,
                "Recommendation": recommendation,
            }
        )

    df = pd.DataFrame(rows, columns=SERVICE_LEVEL_HEADERS)
    if df.empty:
        return df

    return df.sort_values(
        ["Service Gap", "Unit Fill Rate"], ascending=[False, True]
    ).reset_index(drop=True)


def compute_service_level_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Dashboard-style KPIs for the service level sheet."""
    if df.empty:
        return {
            "avg_unit_fill_rate": 0.0,
            "avg_line_fill_rate": 0.0,
            "critical_count": 0,
            "below_target_count": 0,
            "on_target_count": 0,
        }
    return {
        "avg_unit_fill_rate": round(float(df["Unit Fill Rate"].mean()), 4),
        "avg_line_fill_rate": round(float(df["Line Fill Rate"].mean()), 4),
        "critical_count": int((df["Status"] == "Critical").sum()),
        "below_target_count": int((df["Status"] == "Below Target").sum()),
        "on_target_count": int((df["Status"] == "On Target").sum()),
    }
