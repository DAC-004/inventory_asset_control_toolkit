"""Column normalization and derived field enrichment."""

from __future__ import annotations

import pandas as pd

from src.config.constants import (
    COLUMN_ALIASES,
    DEFAULT_TRANSFER_COST_PER_UNIT,
    REQUIRED_COLUMNS,
)
from src.models.inventory import InventoryRecord


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names and coerce types."""
    working = df.copy()
    working.columns = [str(c).strip().lower().replace(" ", "_") for c in working.columns]

    rename_map = {k: v for k, v in COLUMN_ALIASES.items() if k in working.columns}
    working = working.rename(columns=rename_map)

    if "discontinued_flag" not in working.columns:
        if "status" in working.columns:
            working["discontinued_flag"] = working["status"].astype(str).str.lower().eq(
                "obsolete"
            )
        else:
            working["discontinued_flag"] = False

    if "avg_weekly_sales" not in working.columns and "demand_90_day" in working.columns:
        working["avg_weekly_sales"] = working["demand_90_day"] / (90 / 7)

    if "transfer_cost_per_unit" not in working.columns:
        working["transfer_cost_per_unit"] = DEFAULT_TRANSFER_COST_PER_UNIT

    for col in REQUIRED_COLUMNS:
        if col not in working.columns:
            continue
        if col == "discontinued_flag":
            working[col] = _coerce_bool(working[col])
        elif col in {"sku", "product_name", "category", "location", "location_type", "region"}:
            working[col] = working[col].astype(str).str.strip()
        elif col == "inventory_age_days":
            working[col] = pd.to_numeric(working[col], errors="coerce").fillna(0).astype(int)
        else:
            working[col] = pd.to_numeric(working[col], errors="coerce").fillna(0)

    return working


def _coerce_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.isin({"true", "1", "yes", "y", "obsolete"})


def to_inventory_records(df: pd.DataFrame) -> list[InventoryRecord]:
    """Convert normalized dataframe rows to InventoryRecord models."""
    records: list[InventoryRecord] = []
    for row in df.to_dict(orient="records"):
        records.append(InventoryRecord.model_validate(row))
    return records


def enrich_discontinued_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Derive discontinued flag when not explicitly provided."""
    working = df.copy()
    if "discontinued_flag" not in working.columns:
        working["discontinued_flag"] = False
    obsolete_from_status = (
        working.get("status", pd.Series([""] * len(working)))
        .astype(str)
        .str.lower()
        .eq("obsolete")
    )
    obsolete_from_age = (working["inventory_age_days"] >= 365) & (
        working["demand_90_day"] == 0
    )
    working["discontinued_flag"] = (
        working["discontinued_flag"].astype(bool) | obsolete_from_status | obsolete_from_age
    )
    return working
