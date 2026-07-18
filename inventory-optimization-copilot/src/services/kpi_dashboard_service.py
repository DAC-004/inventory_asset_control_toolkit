"""Dashboard aggregation calculations."""

from __future__ import annotations

import pandas as pd

from config.workbook_config import INVENTORY_STATUSES, RECOMMENDED_ACTIONS
from src.domain.constants import AGING_BUCKETS


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
