"""Inter-location transfer recommendation calculations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config.workbook_config import TRANSFER_SETTINGS
from src.domain.constants import (
    TRANSFER_MARGIN_RATE,
    TRANSFER_STRONG_DEMAND_THRESHOLD,
)

TRANSFER_PLANNER_HEADERS = [
    "SKU",
    "Product Name",
    "Source Location",
    "Destination Location",
    "Source Quantity",
    "Destination Quantity",
    "Destination Min Stock",
    "Destination Demand",
    "Suggested Transfer Quantity",
    "Unit Cost",
    "Transfer Cost",
    "Estimated Margin Protected",
    "Net Benefit",
    "Recommendation",
]


def estimate_transfer_cost(
    source_location: str, destination_location: str, quantity: int
) -> float:
    """Estimate transfer cost using a lane-based model."""
    source_is_dc = source_location.startswith("DC")
    dest_is_dc = destination_location.startswith("DC")

    if source_is_dc and not dest_is_dc:
        base_cost, per_unit = 52.0, 2.50
    elif not source_is_dc and not dest_is_dc:
        base_cost, per_unit = 28.0, 3.85
    elif not source_is_dc and dest_is_dc:
        base_cost, per_unit = 48.0, 2.95
    else:
        base_cost, per_unit = 40.0, 2.20

    return round(base_cost + quantity * per_unit, 2)


def destination_needs_stock(dest: pd.Series) -> bool:
    """Return True when destination qualifies for inbound transfer."""
    below_min = dest["quantity_on_hand"] < dest["min_stock"]
    strong_demand = dest["demand_90_day"] >= TRANSFER_STRONG_DEMAND_THRESHOLD
    return bool((below_min and dest["demand_90_day"] > 0) or strong_demand)


def suggested_transfer_quantity(
    source: pd.Series,
    dest: pd.Series,
    demand_buffer: int,
) -> int:
    """Calculate suggested transfer quantity."""
    source_excess = int(source["quantity_on_hand"] - source["max_stock"])
    shortage = max(int(dest["min_stock"] - dest["quantity_on_hand"]), 0)
    demand_need = (
        max(int(dest["demand_90_day"] // 4), 0)
        if dest["demand_90_day"] >= TRANSFER_STRONG_DEMAND_THRESHOLD
        else 0
    )
    destination_need = shortage + demand_buffer + demand_need
    return max(min(source_excess, destination_need), 0)


def build_transfer_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Identify transfer opportunities with positive net benefit."""
    if df.empty:
        return pd.DataFrame(columns=TRANSFER_PLANNER_HEADERS)

    demand_buffer = TRANSFER_SETTINGS["destination_demand_buffer"]
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()

    sources = df[df["quantity_on_hand"] > df["max_stock"]]
    if sources.empty:
        return pd.DataFrame(columns=TRANSFER_PLANNER_HEADERS)

    for _, source in sources.iterrows():
        sku_matches = df[
            (df["sku"] == source["sku"]) & (df["location"] != source["location"])
        ]
        category_matches = df[
            (df["category"] == source["category"])
            & (df["subcategory"] == source["subcategory"])
            & (df["location"] != source["location"])
            & (df["sku"] != source["sku"])
        ]
        destinations = pd.concat([sku_matches, category_matches]).drop_duplicates(
            subset=["item_id"]
        )

        for _, dest in destinations.iterrows():
            if not destination_needs_stock(dest):
                continue

            suggested_qty = suggested_transfer_quantity(source, dest, demand_buffer)
            if suggested_qty <= 0:
                continue

            pair_key = (
                str(source["sku"]),
                str(source["location"]),
                str(dest["location"]),
                str(dest["sku"]),
            )
            if pair_key in seen:
                continue
            seen.add(pair_key)

            unit_cost = float(source["unit_cost"])
            transfer_cost = estimate_transfer_cost(
                str(source["location"]),
                str(dest["location"]),
                suggested_qty,
            )
            margin_protected = round(
                suggested_qty * unit_cost * TRANSFER_MARGIN_RATE, 2
            )
            net_benefit = round(margin_protected - transfer_cost, 2)

            if net_benefit <= 0:
                continue

            recommendation = (
                "Transfer Recommended" if net_benefit >= 25 else "Review Transfer"
            )

            candidates.append(
                {
                    "SKU": source["sku"],
                    "Product Name": source["product_name"],
                    "Source Location": source["location"],
                    "Destination Location": dest["location"],
                    "Source Quantity": int(source["quantity_on_hand"]),
                    "Destination Quantity": int(dest["quantity_on_hand"]),
                    "Destination Min Stock": int(dest["min_stock"]),
                    "Destination Demand": int(dest["demand_90_day"]),
                    "Suggested Transfer Quantity": suggested_qty,
                    "Unit Cost": unit_cost,
                    "Transfer Cost": transfer_cost,
                    "Estimated Margin Protected": margin_protected,
                    "Net Benefit": net_benefit,
                    "Recommendation": recommendation,
                }
            )

    if not candidates:
        return pd.DataFrame(columns=TRANSFER_PLANNER_HEADERS)

    result = pd.DataFrame(candidates, columns=TRANSFER_PLANNER_HEADERS)
    return result.sort_values("Net Benefit", ascending=False).reset_index(drop=True)
