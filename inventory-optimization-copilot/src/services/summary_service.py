"""Management summary business calculations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.services.inventory_health_service import build_analysis_dataframe


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
