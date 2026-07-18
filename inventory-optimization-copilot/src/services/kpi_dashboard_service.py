"""Dashboard aggregation calculations and chart-ready summaries."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config.workbook_config import INVENTORY_STATUSES, RECOMMENDED_ACTIONS
from src.domain.constants import AGING_BUCKETS
from src.services.classification_service import build_classification_dataframe
from src.services.forecast_service import build_demand_forecast_dataframe
from src.services.purchase_order_service import (
    build_po_tracker_dataframe,
    compute_po_tracker_kpis,
)
from src.services.replenishment_service import build_replenishment_dataframe
from src.services.service_level_service import (
    build_service_level_dataframe,
    compute_service_level_kpis,
)
from src.services.transfer_service import build_transfer_dataframe
from src.services.vendor_scorecard_service import (
    build_vendor_scorecard_dataframe,
    compute_vendor_scorecard_kpis,
)


def compute_location_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate inventory value by location."""
    if df.empty:
        return pd.DataFrame(columns=["location", "inventory_value"])
    return (
        df.groupby("location", as_index=False)["total_value"]
        .sum()
        .rename(columns={"total_value": "inventory_value"})
        .sort_values("inventory_value", ascending=False)
    )


def compute_status_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by inventory status."""
    if df.empty:
        return pd.DataFrame(columns=["status", "sku_count", "inventory_value"])
    summary = df.groupby("status", as_index=False).agg(
        sku_count=("item_id", "count"), inventory_value=("total_value", "sum")
    )
    order = {status: i for i, status in enumerate(INVENTORY_STATUSES)}
    summary["_order"] = summary["status"].map(order)
    return summary.sort_values("_order").drop(columns="_order")


def compute_aging_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by aging bucket."""
    rows = []
    for label, low, high in AGING_BUCKETS:
        if df.empty:
            rows.append({"aging_bucket": label, "sku_count": 0, "inventory_value": 0.0})
            continue
        mask = (df["age_days"] >= low) & (df["age_days"] <= high)
        subset = df.loc[mask]
        rows.append(
            {
                "aging_bucket": label,
                "sku_count": len(subset),
                "inventory_value": subset["total_value"].sum(),
            }
        )
    return pd.DataFrame(rows)


def compute_action_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by recommended action."""
    if df.empty:
        return pd.DataFrame(
            columns=["recommended_action", "sku_count", "inventory_value"]
        )
    summary = df.groupby("recommended_action", as_index=False).agg(
        sku_count=("item_id", "count"), inventory_value=("total_value", "sum")
    )
    order = {action: i for i, action in enumerate(RECOMMENDED_ACTIONS)}
    summary["_order"] = summary["recommended_action"].map(order)
    return summary.sort_values("_order").drop(columns="_order")


def compute_top_excess(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top excess items by excess inventory value."""
    if df.empty:
        return pd.DataFrame(
            columns=["sku", "product_name", "location", "excess_qty", "excess_value"]
        )
    working = df.copy()
    working["excess_qty"] = working["quantity_on_hand"] - working["max_stock"]
    working = working[working["excess_qty"] > 0]
    working["excess_value"] = working["excess_qty"] * working["unit_cost"]
    top = working.nlargest(limit, "excess_value")
    return top[
        ["sku", "product_name", "location", "excess_qty", "excess_value"]
    ].reset_index(drop=True)


def compute_abc_usage_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate annual usage value by ABC class."""
    classification = build_classification_dataframe(data)
    if classification.empty:
        return pd.DataFrame(columns=["abc_class", "annual_usage_value"])
    return (
        classification.groupby("ABC Class", as_index=False)["Annual Usage Value"]
        .sum()
        .rename(
            columns={
                "ABC Class": "abc_class",
                "Annual Usage Value": "annual_usage_value",
            }
        )
        .sort_values("abc_class")
    )


def compute_replenishment_status_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Count SKU-locations by replenishment status."""
    repl = build_replenishment_dataframe(data)
    if repl.empty:
        return pd.DataFrame(columns=["status", "sku_count"])
    summary = (
        repl.groupby("Replenishment Status", as_index=False)
        .size()
        .rename(columns={"Replenishment Status": "status", "size": "sku_count"})
    )
    return summary.sort_values("sku_count", ascending=False)


def compute_fill_rate_by_location(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Average unit fill rate by location from service level analysis."""
    service = build_service_level_dataframe(data)
    if service.empty:
        return pd.DataFrame(columns=["location", "unit_fill_rate"])
    return (
        service.groupby("Location Name", as_index=False)["Unit Fill Rate"]
        .mean()
        .rename(
            columns={"Location Name": "location", "Unit Fill Rate": "unit_fill_rate"}
        )
        .sort_values("unit_fill_rate", ascending=True)
    )


def compute_vendor_risk_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Vendor counts by risk class."""
    vendors = build_vendor_scorecard_dataframe(data)
    if vendors.empty:
        return pd.DataFrame(columns=["risk_class", "vendor_count"])
    summary = (
        vendors.groupby("Risk Class", as_index=False)
        .size()
        .rename(columns={"Risk Class": "risk_class", "size": "vendor_count"})
    )
    order = {"Preferred": 0, "Approved": 1, "Watch": 2, "High Risk": 3}
    summary["_order"] = summary["risk_class"].map(order).fillna(99)
    return summary.sort_values("_order").drop(columns="_order")


def compute_transfer_benefit_summary(
    data: dict[str, pd.DataFrame], limit: int = 8
) -> pd.DataFrame:
    """Top transfer lanes by net benefit."""
    transfers = build_transfer_dataframe(data)
    if transfers.empty:
        return pd.DataFrame(columns=["lane", "net_benefit"])
    working = transfers.copy()
    working["lane"] = (
        working["Source Location"] + " → " + working["Destination Location"]
    )
    top = working.nlargest(limit, "Net Benefit")
    return top[["lane", "Net Benefit"]].rename(columns={"Net Benefit": "net_benefit"})


def compute_planning_service_kpis(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Planning and service KPI values for the dashboard."""
    repl = build_replenishment_dataframe(data)
    forecast = build_demand_forecast_dataframe(data)
    service = build_service_level_dataframe(data)
    service_kpis = compute_service_level_kpis(service)

    below_rop = 0
    order_value = 0.0
    if not repl.empty:
        below_rop = int((repl["Projected Available"] < repl["Reorder Point"]).sum())
        order_value = round(
            float((repl["Recommended Order Qty"] * repl["Unit Cost"]).sum()), 2
        )

    avg_wape = 0.0
    avg_bias = 0.0
    if not forecast.empty:
        avg_wape = round(float(forecast["Selected WAPE"].mean()), 4)
        avg_bias = round(float(forecast["Forecast Bias"].mean()), 4)

    order_fill = 0.0
    if not service.empty:
        order_fill = round(float(service["Order Fill Rate"].mean()), 4)

    return {
        "below_reorder_point": below_rop,
        "recommended_order_value": order_value,
        "unit_fill_rate": service_kpis["avg_unit_fill_rate"],
        "line_fill_rate": service_kpis["avg_line_fill_rate"],
        "order_fill_rate": order_fill,
        "forecast_wape": avg_wape,
        "forecast_bias": avg_bias,
    }


def compute_procurement_network_kpis(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Procurement and network KPI values for the dashboard."""
    po_df = build_po_tracker_dataframe(data)
    vendor_df = build_vendor_scorecard_dataframe(data)
    transfers = build_transfer_dataframe(data)
    repl = build_replenishment_dataframe(data)

    po_kpis = compute_po_tracker_kpis(po_df)
    vendor_kpis = compute_vendor_scorecard_kpis(vendor_df)

    transfer_units = 0
    transfer_benefit = 0.0
    if not transfers.empty:
        transfer_units = int(transfers["Transfer Quantity"].sum())
        transfer_benefit = round(float(transfers["Net Benefit"].sum()), 2)

    remaining_shortage = 0
    if not repl.empty:
        remaining_shortage = int(
            repl.loc[repl["Net Requirement"] > 0, "Net Requirement"].sum()
        )
    if not transfers.empty:
        remaining_shortage = int(
            transfers.groupby(["SKU", "Destination Location"])[
                "Destination Remaining Requirement"
            ]
            .last()
            .sum()
        )

    return {
        "open_po_value": po_kpis["open_value"],
        "late_po_count": po_kpis["late_lines"],
        "vendor_otif": vendor_kpis["avg_otif"],
        "high_risk_vendors": vendor_kpis["high_risk_count"],
        "recommended_transfer_units": transfer_units,
        "transfer_net_benefit": transfer_benefit,
        "remaining_shortage": remaining_shortage,
    }
