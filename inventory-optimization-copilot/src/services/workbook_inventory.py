"""Map full inventory model to phase-1 workbook sheet columns."""

from __future__ import annotations

import pandas as pd

from src.domain.schemas import WORKBOOK_INVENTORY_COLUMN_ORDER


def inventory_for_workbook(df: pd.DataFrame) -> pd.DataFrame:
    """
    Project the full inventory dataset to Master Inventory sheet columns.

    Adds legacy ``location`` alias from ``location_name``.
    """
    if df.empty:
        return pd.DataFrame(columns=WORKBOOK_INVENTORY_COLUMN_ORDER)

    view = df.copy()
    view["location"] = view["location_name"]
    if "item_id" not in view.columns and "inventory_record_id" in view.columns:
        view["item_id"] = view["inventory_record_id"]

    return view[WORKBOOK_INVENTORY_COLUMN_ORDER].copy()


# Backward-compatible alias for sheet imports
COLUMN_ORDER = WORKBOOK_INVENTORY_COLUMN_ORDER
