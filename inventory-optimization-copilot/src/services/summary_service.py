"""Management summary business calculations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.services.classification_service import compute_dashboard_classification_kpis
from src.services.forecast_service import build_demand_forecast_dataframe
from src.services.inventory_health_service import build_analysis_dataframe
from src.services.kpi_dashboard_service import (
    compute_planning_service_kpis,
    compute_procurement_network_kpis,
)
from src.services.markdown_service import build_markdown_dataframe
from src.services.purchase_order_service import build_po_tracker_dataframe
from src.services.replenishment_service import build_replenishment_dataframe
from src.services.service_level_service import build_service_level_dataframe
from src.services.transfer_service import build_transfer_dataframe
from src.services.vendor_scorecard_service import build_vendor_scorecard_dataframe


def recommended_action_summary(inventory: pd.DataFrame) -> list[tuple[str, int]]:
    """Return recommended action counts for executive summary."""
    if inventory.empty:
        return []
    counts = inventory["recommended_action"].value_counts()
    return [(str(action), int(count)) for action, count in counts.items()]


def top_inventory_risks(
    inventory: pd.DataFrame, limit: int = 5
) -> list[dict[str, Any]]:
    """Return top inventory risk rows for management summary."""
    analysis = build_analysis_dataframe(inventory)
    if analysis.empty:
        return []
    rows: list[dict[str, Any]] = []
    for _, row in analysis.head(limit).iterrows():
        rows.append(
            {
                "SKU": row["SKU"],
                "Location": row["Location"],
                "Issue": row["Issue Type"],
                "Value": row["Inventory Value"],
            }
        )
    return rows


def build_management_summary_context(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Aggregate executive metrics across inventory planning modules."""
    inventory = data.get("inventory", pd.DataFrame())
    class_kpis = compute_dashboard_classification_kpis(data)
    planning = compute_planning_service_kpis(data)
    procurement = compute_procurement_network_kpis(data)

    repl = build_replenishment_dataframe(data)
    order_required = (
        int((repl["Replenishment Status"] == "Order Required").sum())
        if not repl.empty
        else 0
    )

    markdown = build_markdown_dataframe(data)
    markdown_candidates = len(markdown)
    transfer_actions = len(build_transfer_dataframe(data))

    service = build_service_level_dataframe(data)
    critical_service = (
        int((service["Status"] == "Critical").sum()) if not service.empty else 0
    )

    forecast = build_demand_forecast_dataframe(data)
    forecast_reviews = (
        int((forecast["Review Status"] != "Approved").sum())
        if not forecast.empty
        else 0
    )

    vendors = build_vendor_scorecard_dataframe(data)
    watch_vendors = (
        int((vendors["Risk Class"] == "Watch").sum()) if not vendors.empty else 0
    )

    po = build_po_tracker_dataframe(data)
    open_po_lines = int((po["Open Quantity"] > 0).sum()) if not po.empty else 0

    total_value = (
        round(float(inventory["total_value"].sum()), 2) if not inventory.empty else 0.0
    )
    aged_value = (
        round(
            float(inventory.loc[inventory["age_days"] > 180, "total_value"].sum()),
            2,
        )
        if not inventory.empty
        else 0.0
    )
    excess_count = (
        int(inventory["status"].isin(["Excess", "Excess / Aged"]).sum())
        if not inventory.empty
        else 0
    )
    stockout_count = (
        int((inventory["status"] == "Stockout Risk").sum())
        if not inventory.empty
        else 0
    )

    return {
        "total_value": total_value,
        "aged_value": aged_value,
        "excess_count": excess_count,
        "stockout_count": stockout_count,
        "recovery_value": (
            round(float(markdown["Estimated Recovery Value"].sum()), 2)
            if not markdown.empty
            else 0.0
        ),
        "class_kpis": class_kpis,
        "planning": planning,
        "procurement": procurement,
        "order_required": order_required,
        "markdown_candidates": markdown_candidates,
        "transfer_actions": transfer_actions,
        "critical_service": critical_service,
        "forecast_reviews": forecast_reviews,
        "watch_vendors": watch_vendors,
        "open_po_lines": open_po_lines,
        "action_summary": recommended_action_summary(inventory),
        "top_risks": top_inventory_risks(inventory),
    }
