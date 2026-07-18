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


def _add_percent_of_total(summary: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Append percent_of_total column based on value_col sum."""
    total = float(summary[value_col].sum()) if not summary.empty else 0.0
    if total > 0:
        summary = summary.copy()
        summary["percent_of_total"] = summary[value_col] / total
    else:
        summary = summary.copy()
        summary["percent_of_total"] = 0.0
    return summary


def compute_location_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate inventory value by location."""
    if df.empty:
        return pd.DataFrame(columns=["location", "inventory_value", "percent_of_total"])
    summary = (
        df.groupby("location", as_index=False)["total_value"]
        .sum()
        .rename(columns={"total_value": "inventory_value"})
        .sort_values("inventory_value", ascending=False)
    )
    return _add_percent_of_total(summary, "inventory_value")


def compute_status_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by inventory status."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "inventory_status",
                "sku_location_count",
                "inventory_value",
                "percent_of_total",
            ]
        )
    summary = (
        df.groupby("status", as_index=False)
        .agg(
            sku_location_count=("item_id", "count"),
            inventory_value=("total_value", "sum"),
        )
        .rename(columns={"status": "inventory_status"})
    )
    order = {status: i for i, status in enumerate(INVENTORY_STATUSES)}
    summary["_order"] = summary["inventory_status"].map(order)
    summary = summary.sort_values("_order").drop(columns="_order")
    return _add_percent_of_total(summary, "inventory_value")


def compute_aging_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by aging bucket."""
    rows = []
    for label, low, high in AGING_BUCKETS:
        if df.empty:
            rows.append(
                {
                    "aging_bucket": label,
                    "sku_location_count": 0,
                    "inventory_value": 0.0,
                }
            )
            continue
        mask = (df["age_days"] >= low) & (df["age_days"] <= high)
        subset = df.loc[mask]
        rows.append(
            {
                "aging_bucket": label,
                "sku_location_count": len(subset),
                "inventory_value": subset["total_value"].sum(),
            }
        )
    summary = pd.DataFrame(rows)
    return _add_percent_of_total(summary, "inventory_value")


def compute_action_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate count and value by recommended action."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "recommended_action",
                "record_count",
                "inventory_value",
                "estimated_financial_impact",
            ]
        )
    summary = df.groupby("recommended_action", as_index=False).agg(
        record_count=("item_id", "count"),
        inventory_value=("total_value", "sum"),
    )
    summary["estimated_financial_impact"] = summary["inventory_value"]
    order = {action: i for i, action in enumerate(RECOMMENDED_ACTIONS)}
    summary["_order"] = summary["recommended_action"].map(order)
    return summary.sort_values("_order").drop(columns="_order")


def compute_top_excess(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return top excess items by excess inventory value."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "sku",
                "product_name",
                "location",
                "excess_quantity",
                "excess_value",
            ]
        )
    working = df.copy()
    working["excess_quantity"] = working["quantity_on_hand"] - working["max_stock"]
    working = working[working["excess_quantity"] > 0]
    working["excess_value"] = working["excess_quantity"] * working["unit_cost"]
    top = working.nlargest(limit, "excess_value")
    result = top[
        ["sku", "product_name", "location", "excess_quantity", "excess_value"]
    ].reset_index(drop=True)
    result.insert(0, "rank", range(1, len(result) + 1))
    return result


def compute_abc_usage_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate annual usage value by ABC class."""
    classification = build_classification_dataframe(data)
    if classification.empty:
        return pd.DataFrame(
            columns=[
                "abc_class",
                "sku_count",
                "annual_usage_value",
                "percent_of_annual_usage_value",
            ]
        )
    summary = (
        classification.groupby("ABC Class", as_index=False)
        .agg(
            sku_count=("SKU", "count"),
            annual_usage_value=("Annual Usage Value", "sum"),
        )
        .rename(columns={"ABC Class": "abc_class"})
        .sort_values("abc_class")
    )
    total = float(summary["annual_usage_value"].sum())
    if total > 0:
        summary["percent_of_annual_usage_value"] = summary["annual_usage_value"] / total
    else:
        summary["percent_of_annual_usage_value"] = 0.0
    return summary


def compute_replenishment_status_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate replenishment metrics by status."""
    repl = build_replenishment_dataframe(data)
    if repl.empty:
        return pd.DataFrame(
            columns=[
                "replenishment_status",
                "sku_location_count",
                "recommended_order_quantity",
                "recommended_order_value",
            ]
        )
    working = repl.copy()
    working["order_value"] = working["Recommended Order Qty"] * working["Unit Cost"]
    summary = (
        working.groupby("Replenishment Status", as_index=False)
        .agg(
            sku_location_count=("SKU", "count"),
            recommended_order_quantity=("Recommended Order Qty", "sum"),
            recommended_order_value=("order_value", "sum"),
        )
        .rename(columns={"Replenishment Status": "replenishment_status"})
    )
    return summary.sort_values("recommended_order_value", ascending=False)


def _worst_service_status(statuses: pd.Series) -> str:
    priority = {
        "Below Target": 0,
        "Watch": 1,
        "On Target": 2,
        "No Demand": 3,
    }
    if statuses.empty:
        return "No Demand"
    return str(min(statuses, key=lambda s: priority.get(str(s), 99)))


def compute_fill_rate_by_location(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Average fill rates and service status by location."""
    service = build_service_level_dataframe(data)
    if service.empty:
        return pd.DataFrame(
            columns=[
                "location",
                "unit_fill_rate",
                "line_fill_rate",
                "order_fill_rate",
                "service_status",
            ]
        )
    summary = (
        service.groupby("Location Name", as_index=False)
        .agg(
            unit_fill_rate=("Unit Fill Rate", "mean"),
            line_fill_rate=("Line Fill Rate", "mean"),
            order_fill_rate=("Order Fill Rate", "mean"),
            service_status=("Status", _worst_service_status),
        )
        .rename(columns={"Location Name": "location"})
        .sort_values("unit_fill_rate", ascending=True)
    )
    return summary


def compute_vendor_risk_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Vendor metrics by risk class."""
    vendors = build_vendor_scorecard_dataframe(data)
    if vendors.empty:
        return pd.DataFrame(
            columns=[
                "vendor_risk_class",
                "supplier_count",
                "open_po_value",
                "average_vendor_score",
            ]
        )
    summary = (
        vendors.groupby("Risk Class", as_index=False)
        .agg(
            supplier_count=("Supplier ID", "count"),
            open_po_value=("Open PO Value", "sum"),
            average_vendor_score=("Total Vendor Score", "mean"),
        )
        .rename(columns={"Risk Class": "vendor_risk_class"})
    )
    order = {"Preferred": 0, "Approved": 1, "Watch": 2, "High Risk": 3}
    summary["_order"] = summary["vendor_risk_class"].map(order).fillna(99)
    return summary.sort_values("_order").drop(columns="_order")


def compute_transfer_benefit_summary(
    data: dict[str, pd.DataFrame], limit: int = 10
) -> pd.DataFrame:
    """Top transfer recommendations by net benefit."""
    transfers = build_transfer_dataframe(data)
    if transfers.empty:
        return pd.DataFrame(
            columns=[
                "rank",
                "source_location",
                "destination_location",
                "sku",
                "transfer_quantity",
                "net_benefit",
            ]
        )
    top = transfers.nlargest(limit, "Net Benefit")
    result = top[
        [
            "Source Location",
            "Destination Location",
            "SKU",
            "Transfer Quantity",
            "Net Benefit",
        ]
    ].rename(
        columns={
            "Source Location": "source_location",
            "Destination Location": "destination_location",
            "SKU": "sku",
            "Transfer Quantity": "transfer_quantity",
            "Net Benefit": "net_benefit",
        }
    )
    result = result.reset_index(drop=True)
    result.insert(0, "rank", range(1, len(result) + 1))
    return result


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
