"""Dataset validation with structured error reporting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.domain.schemas import ALL_DATASET_COLUMNS
from src.exceptions import BuildProcessError


@dataclass(frozen=True)
class ValidationErrorDetail:
    dataset: str
    key: str
    field: str
    invalid_value: Any
    expected_rule: str

    def __str__(self) -> str:
        return (
            f"[{self.dataset}] key={self.key!r} field={self.field!r} "
            f"value={self.invalid_value!r} expected={self.expected_rule}"
        )


class DatasetValidationError(BuildProcessError):
    """Raised when one or more dataset validation rules fail."""

    def __init__(self, errors: list[ValidationErrorDetail]) -> None:
        self.errors = errors
        message = "; ".join(str(e) for e in errors[:5])
        if len(errors) > 5:
            message += f"; ... and {len(errors) - 5} more"
        super().__init__(message)


def _err(
    dataset: str,
    key: str,
    field: str,
    value: Any,
    rule: str,
    errors: list[ValidationErrorDetail],
) -> None:
    errors.append(
        ValidationErrorDetail(
            dataset=dataset,
            key=key,
            field=field,
            invalid_value=value,
            expected_rule=rule,
        )
    )


def _require_columns(
    dataset: str, df: pd.DataFrame, errors: list[ValidationErrorDetail]
) -> None:
    expected = ALL_DATASET_COLUMNS[dataset]
    missing = [col for col in expected if col not in df.columns]
    if missing:
        _err(dataset, "*", "columns", missing, f"missing columns {missing}", errors)


def _check_non_negative(
    dataset: str,
    df: pd.DataFrame,
    columns: list[str],
    key_col: str,
    errors: list[ValidationErrorDetail],
) -> None:
    for col in columns:
        if col not in df.columns:
            continue
        bad = df[df[col] < 0]
        for _, row in bad.iterrows():
            _err(
                dataset,
                str(row.get(key_col, "")),
                col,
                row[col],
                "must be >= 0",
                errors,
            )


def validate_suppliers(df: pd.DataFrame, errors: list[ValidationErrorDetail]) -> None:
    _require_columns("suppliers", df, errors)
    if df.empty:
        return
    if not df["supplier_id"].is_unique:
        _err("suppliers", "*", "supplier_id", "duplicate", "must be unique", errors)
    for _, row in df.iterrows():
        key = str(row["supplier_id"])
        for rating in (
            "quality_rating",
            "responsiveness_rating",
            "administrative_compliance_rating",
        ):
            val = float(row[rating])
            if not 1.0 <= val <= 5.0:
                _err("suppliers", key, rating, val, "must be between 1 and 5", errors)


def validate_inventory(
    df: pd.DataFrame,
    supplier_ids: set[str],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("inventory", df, errors)
    if df.empty:
        return
    if not df["inventory_record_id"].is_unique:
        _err(
            "inventory",
            "*",
            "inventory_record_id",
            "duplicate",
            "must be unique",
            errors,
        )
    if df.duplicated(subset=["sku", "location_id"]).any():
        _err(
            "inventory",
            "*",
            "sku+location_id",
            "duplicate",
            "business key must be unique",
            errors,
        )
    _check_non_negative(
        "inventory",
        df,
        [
            "quantity_on_hand",
            "quantity_allocated",
            "backorder_quantity",
            "min_stock",
            "max_stock",
            "target_stock",
            "unit_cost",
            "selling_price",
            "case_pack",
            "minimum_order_quantity",
            "storage_capacity_units",
        ],
        "inventory_record_id",
        errors,
    )
    for _, row in df.iterrows():
        key = str(row["inventory_record_id"])
        if row["supplier_id"] not in supplier_ids:
            _err(
                "inventory",
                key,
                "supplier_id",
                row["supplier_id"],
                "must reference valid supplier",
                errors,
            )
        if row["min_stock"] > row["target_stock"]:
            _err(
                "inventory",
                key,
                "min_stock",
                row["min_stock"],
                "must be <= target_stock",
                errors,
            )
        if row["min_stock"] > row["max_stock"]:
            _err(
                "inventory",
                key,
                "min_stock",
                row["min_stock"],
                "must be <= max_stock",
                errors,
            )
        expected_value = round(
            float(row["quantity_on_hand"]) * float(row["unit_cost"]), 2
        )
        if abs(float(row["total_value"]) - expected_value) > 0.02:
            _err(
                "inventory",
                key,
                "total_value",
                row["total_value"],
                f"must equal quantity_on_hand * unit_cost ({expected_value})",
                errors,
            )
        if float(row["selling_price"]) <= float(row["unit_cost"]):
            _err(
                "inventory",
                key,
                "selling_price",
                row["selling_price"],
                "must exceed unit_cost",
                errors,
            )


def validate_purchase_orders(
    df: pd.DataFrame,
    supplier_ids: set[str],
    inventory_keys: set[tuple[str, str]],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("purchase_orders", df, errors)
    if df.empty:
        return
    if not df["po_line_id"].is_unique:
        _err(
            "purchase_orders", "*", "po_line_id", "duplicate", "must be unique", errors
        )
    for _, row in df.iterrows():
        key = str(row["po_line_id"])
        if row["supplier_id"] not in supplier_ids:
            _err(
                "purchase_orders",
                key,
                "supplier_id",
                row["supplier_id"],
                "must reference valid supplier",
                errors,
            )
        pair = (str(row["sku"]), str(row["location_id"]))
        if pair not in inventory_keys:
            _err(
                "purchase_orders",
                key,
                "sku+location_id",
                pair,
                "must reference inventory record",
                errors,
            )
        expected_ext = round(
            float(row["ordered_quantity"]) * float(row["unit_cost"]), 2
        )
        if abs(float(row["extended_cost"]) - expected_ext) > 0.02:
            _err(
                "purchase_orders",
                key,
                "extended_cost",
                row["extended_cost"],
                f"must equal ordered_quantity * unit_cost ({expected_ext})",
                errors,
            )
        if pd.notna(row["approval_date"]) and row["approval_date"] < row["order_date"]:
            _err(
                "purchase_orders",
                key,
                "approval_date",
                row["approval_date"],
                "must be on or after order_date",
                errors,
            )


def validate_receipts(
    df: pd.DataFrame,
    po_lines: pd.DataFrame,
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("purchase_order_receipts", df, errors)
    if df.empty:
        return
    po_map = po_lines.set_index("po_line_id")
    for _, row in df.iterrows():
        key = str(row["receipt_id"])
        po_line_id = row["po_line_id"]
        if po_line_id not in po_map.index:
            _err(
                "purchase_order_receipts",
                key,
                "po_line_id",
                po_line_id,
                "must reference valid PO line",
                errors,
            )
            continue
        po = po_map.loc[po_line_id]
        if (
            row["received_quantity"]
            != row["accepted_quantity"] + row["rejected_quantity"]
        ):
            _err(
                "purchase_order_receipts",
                key,
                "received_quantity",
                row["received_quantity"],
                "must equal accepted + rejected",
                errors,
            )
        if row["receipt_date"] < po["order_date"]:
            _err(
                "purchase_order_receipts",
                key,
                "receipt_date",
                row["receipt_date"],
                "must be on or after PO order_date",
                errors,
            )


def validate_demand_history(
    df: pd.DataFrame,
    inventory_keys: set[tuple[str, str]],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("demand_history", df, errors)
    if len(df) < 52:
        _err(
            "demand_history",
            "*",
            "row_count",
            len(df),
            "must include at least 52 weekly rows total",
            errors,
        )
    if not df["demand_record_id"].is_unique:
        _err(
            "demand_history",
            "*",
            "demand_record_id",
            "duplicate",
            "must be unique",
            errors,
        )
    for _, row in df.iterrows():
        key = str(row["demand_record_id"])
        pair = (str(row["sku"]), str(row["location_id"]))
        if pair not in inventory_keys:
            _err(
                "demand_history",
                key,
                "sku+location_id",
                pair,
                "must reference inventory record",
                errors,
            )


def validate_snapshots(
    df: pd.DataFrame,
    inventory_keys: set[tuple[str, str]],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("inventory_snapshots", df, errors)
    months = df["snapshot_date"].nunique() if not df.empty else 0
    if months < 12:
        _err(
            "inventory_snapshots",
            "*",
            "snapshot_date",
            months,
            "must include at least 12 monthly snapshots",
            errors,
        )
    for _, row in df.iterrows():
        key = str(row["snapshot_id"])
        pair = (str(row["sku"]), str(row["location_id"]))
        if pair not in inventory_keys:
            _err(
                "inventory_snapshots",
                key,
                "sku+location_id",
                pair,
                "must reference inventory record",
                errors,
            )
        expected = round(float(row["quantity_on_hand"]) * float(row["unit_cost"]), 2)
        if abs(float(row["inventory_value"]) - expected) > 0.02:
            _err(
                "inventory_snapshots",
                key,
                "inventory_value",
                row["inventory_value"],
                f"must equal qty * cost ({expected})",
                errors,
            )


def validate_customer_orders(
    df: pd.DataFrame,
    inventory_keys: set[tuple[str, str]],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("customer_orders", df, errors)
    for _, row in df.iterrows():
        key = str(row["order_line_id"])
        pair = (str(row["sku"]), str(row["location_id"]))
        if pair not in inventory_keys:
            _err(
                "customer_orders",
                key,
                "sku+location_id",
                pair,
                "must reference inventory record",
                errors,
            )
        if row["ordered_units"] != row["fulfilled_units"] + row["backordered_units"]:
            _err(
                "customer_orders",
                key,
                "ordered_units",
                row["ordered_units"],
                "must equal fulfilled + backordered",
                errors,
            )


def validate_cycle_counts(
    df: pd.DataFrame,
    inventory_keys: set[tuple[str, str]],
    errors: list[ValidationErrorDetail],
) -> None:
    _require_columns("cycle_counts", df, errors)
    for _, row in df.iterrows():
        key = str(row["count_id"])
        pair = (str(row["sku"]), str(row["location_id"]))
        if pair not in inventory_keys:
            _err(
                "cycle_counts",
                key,
                "sku+location_id",
                pair,
                "must reference inventory record",
                errors,
            )
        expected_var = int(row["physical_quantity"]) - int(row["system_quantity"])
        if int(row["variance_units"]) != expected_var:
            _err(
                "cycle_counts",
                key,
                "variance_units",
                row["variance_units"],
                f"must equal physical - system ({expected_var})",
                errors,
            )


def validate_all_datasets(datasets: dict[str, pd.DataFrame]) -> None:
    """Validate all generated datasets; raise DatasetValidationError on failure."""
    errors: list[ValidationErrorDetail] = []
    suppliers = datasets.get("suppliers", pd.DataFrame())
    inventory = datasets.get("inventory", pd.DataFrame())
    supplier_ids = (
        set(suppliers["supplier_id"].astype(str)) if not suppliers.empty else set()
    )
    inventory_keys = (
        set(zip(inventory["sku"].astype(str), inventory["location_id"].astype(str)))
        if not inventory.empty
        else set()
    )

    validate_suppliers(suppliers, errors)
    validate_inventory(inventory, supplier_ids, errors)
    validate_purchase_orders(
        datasets.get("purchase_orders", pd.DataFrame()),
        supplier_ids,
        inventory_keys,
        errors,
    )
    validate_receipts(
        datasets.get("purchase_order_receipts", pd.DataFrame()),
        datasets.get("purchase_orders", pd.DataFrame()),
        errors,
    )
    validate_demand_history(
        datasets.get("demand_history", pd.DataFrame()), inventory_keys, errors
    )
    validate_snapshots(
        datasets.get("inventory_snapshots", pd.DataFrame()), inventory_keys, errors
    )
    validate_customer_orders(
        datasets.get("customer_orders", pd.DataFrame()), inventory_keys, errors
    )
    validate_cycle_counts(
        datasets.get("cycle_counts", pd.DataFrame()), inventory_keys, errors
    )

    if errors:
        raise DatasetValidationError(errors)


def quantity_on_order_by_sku_location(
    purchase_orders: pd.DataFrame,
) -> dict[tuple[str, str], int]:
    """Derive open on-order quantity from valid open PO lines."""
    if purchase_orders.empty:
        return {}
    open_statuses = {"Approved", "Open", "Partially Received", "Late"}
    open_lines = purchase_orders[purchase_orders["po_status"].isin(open_statuses)]
    result: dict[tuple[str, str], int] = {}
    for _, row in open_lines.iterrows():
        key = (str(row["sku"]), str(row["location_id"]))
        result[key] = result.get(key, 0) + int(row["ordered_quantity"])
    return result
