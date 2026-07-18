"""Aged, excess, and risk analysis calculations."""

from __future__ import annotations

import pandas as pd

from src.domain.constants import ANALYST_NOTES, ISSUE_TYPE_MAP, RISK_LEVEL_ORDER

AGED_EXCESS_HEADERS = [
    "SKU",
    "Product Name",
    "Location",
    "Quantity On Hand",
    "Max Stock",
    "Excess Quantity",
    "Age Days",
    "90 Day Demand",
    "Sell Through Rate",
    "Inventory Value",
    "Risk Level",
    "Issue Type",
    "Recommended Action",
    "Analyst Notes",
]


def assign_risk_level(status: str) -> str:
    """Map inventory status to High / Medium / Low risk level."""
    if status in ("Obsolete", "Excess / Aged", "Stockout Risk"):
        return "High"
    if status in ("Excess", "Slow-Moving"):
        return "Medium"
    return "Low"


def build_analysis_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Derive aged/excess analysis rows from master inventory data."""
    if df.empty:
        return pd.DataFrame(columns=AGED_EXCESS_HEADERS)

    working = df.copy()
    working["excess_quantity"] = (
        working["quantity_on_hand"] - working["max_stock"]
    ).clip(lower=0)
    working["inventory_value"] = working["total_value"]
    working["risk_level"] = working["status"].map(assign_risk_level)
    working["issue_type"] = working["status"].map(ISSUE_TYPE_MAP)
    working["analyst_notes"] = working["status"].map(ANALYST_NOTES)

    analysis = working[
        [
            "sku",
            "product_name",
            "location",
            "quantity_on_hand",
            "max_stock",
            "excess_quantity",
            "age_days",
            "demand_90_day",
            "sell_through_rate",
            "inventory_value",
            "risk_level",
            "issue_type",
            "recommended_action",
            "analyst_notes",
        ]
    ].rename(
        columns={
            "sku": "SKU",
            "product_name": "Product Name",
            "location": "Location",
            "quantity_on_hand": "Quantity On Hand",
            "max_stock": "Max Stock",
            "excess_quantity": "Excess Quantity",
            "age_days": "Age Days",
            "demand_90_day": "90 Day Demand",
            "sell_through_rate": "Sell Through Rate",
            "inventory_value": "Inventory Value",
            "risk_level": "Risk Level",
            "issue_type": "Issue Type",
            "recommended_action": "Recommended Action",
            "analyst_notes": "Analyst Notes",
        }
    )

    analysis = analysis[analysis["Risk Level"] != "Low"].copy()
    analysis["_risk_order"] = analysis["Risk Level"].map(RISK_LEVEL_ORDER)
    analysis = analysis.sort_values(
        ["_risk_order", "Inventory Value"],
        ascending=[True, False],
    ).drop(columns="_risk_order")
    return analysis.reset_index(drop=True)
