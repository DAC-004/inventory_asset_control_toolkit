"""Inventory data validation rules."""

from __future__ import annotations

import pandas as pd

from src.config.constants import REQUIRED_COLUMNS
from src.models.recommendations import ValidationResult


def validate_inventory_data(df: pd.DataFrame) -> ValidationResult:
    """Validate inventory dataframe and return errors and warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    if df["sku"].isna().any() or (df["sku"].astype(str).str.strip() == "").any():
        errors.append("Null or empty SKU values detected.")

    numeric_cols = [
        "on_hand_qty",
        "min_stock",
        "max_stock",
        "unit_cost",
        "retail_price",
        "inventory_age_days",
        "demand_90_day",
        "avg_weekly_sales",
        "transfer_cost_per_unit",
    ]
    for col in numeric_cols:
        if (df[col] < 0).any():
            errors.append(f"Negative values found in {col}.")

    dupes = df.duplicated(subset=["sku", "location"], keep=False)
    if dupes.any():
        warnings.append(
            f"Duplicate SKU-location pairs detected ({dupes.sum()} rows)."
        )

    below_cost = df["retail_price"] < df["unit_cost"]
    if below_cost.any():
        warnings.append(
            f"Retail price below unit cost on {below_cost.sum()} row(s)."
        )

    max_below_min = df["max_stock"] < df["min_stock"]
    if max_below_min.any():
        warnings.append(
            f"Max stock below min stock on {max_below_min.sum()} row(s)."
        )

    inconsistent_demand = (df["avg_weekly_sales"] == 0) & (df["demand_90_day"] > 0)
    if inconsistent_demand.any():
        warnings.append(
            "Average weekly sales is zero while 90-day demand is positive "
            f"on {inconsistent_demand.sum()} row(s)."
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
