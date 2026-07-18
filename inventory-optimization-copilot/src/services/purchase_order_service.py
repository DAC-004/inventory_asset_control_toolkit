"""Purchase order tracking — receipts, open supply, lateness, and price variance."""

from __future__ import annotations

import math
from datetime import date
from typing import Any

import pandas as pd

from config.workbook_config import AS_OF_DATE

PO_TRACKER_HEADERS = [
    "PO Number",
    "PO Line",
    "Supplier ID",
    "Supplier Name",
    "SKU",
    "Product Name",
    "Location ID",
    "Location Name",
    "Buyer",
    "Order Date",
    "Approval Date",
    "Promised Date",
    "Expected Date",
    "First Receipt Date",
    "Final Receipt Date",
    "Ordered Quantity",
    "Received Quantity",
    "Accepted Quantity",
    "Rejected Quantity",
    "Open Quantity",
    "Unit Cost",
    "Extended Cost",
    "Open PO Value",
    "Baseline Unit Cost",
    "Purchase Price Variance",
    "Purchase Price Variance %",
    "Days Late",
    "PO Status",
    "Receipt Status",
    "Quality Issue",
    "Planner Action",
]

CANCELLED_STATUSES = {"Cancelled"}
NON_SUPPLY_STATUSES = {"Cancelled", "Draft"}


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return default
    result = numerator / denominator
    if not math.isfinite(result):
        return default
    return result


def _finite(value: float, default: float = 0.0) -> float:
    if not math.isfinite(value):
        return default
    return value


def aggregate_receipts(receipts: pd.DataFrame) -> pd.DataFrame:
    """Aggregate receipt metrics by PO line."""
    if receipts.empty:
        return pd.DataFrame(
            columns=[
                "po_line_id",
                "received_quantity",
                "accepted_quantity",
                "rejected_quantity",
                "first_receipt_date",
                "final_receipt_date",
                "receipt_status",
                "quality_issue",
            ]
        )

    grouped = receipts.groupby("po_line_id")
    rows = []
    for po_line_id, grp in grouped:
        if "receipt_date" in grp.columns:
            grp = grp.sort_values("receipt_date")
        last = grp.iloc[-1]
        first_date = (
            grp["receipt_date"].min() if "receipt_date" in grp.columns else None
        )
        final_date = (
            grp["receipt_date"].max() if "receipt_date" in grp.columns else None
        )
        rows.append(
            {
                "po_line_id": po_line_id,
                "received_quantity": int(grp["received_quantity"].sum()),
                "accepted_quantity": int(grp["accepted_quantity"].sum()),
                "rejected_quantity": int(grp["rejected_quantity"].sum()),
                "first_receipt_date": first_date,
                "final_receipt_date": final_date,
                "receipt_status": str(last["receipt_status"]),
                "quality_issue": str(last.get("quality_issue", "") or ""),
            }
        )
    return pd.DataFrame(rows)


def _derive_po_status(
    po_status: str,
    ordered: int,
    accepted: int,
    open_qty: int,
    promised: date | None,
    receipt_status: str,
) -> str:
    if po_status in CANCELLED_STATUSES:
        return "Cancelled"
    if accepted > ordered:
        return "Over-Received"
    if receipt_status == "Quality Hold":
        return "Quality Hold"
    if open_qty > 0 and promised is not None and promised < AS_OF_DATE:
        if po_status not in {"Received", "Closed"}:
            return "Late"
    return po_status


def _days_late(
    promised: date | None,
    final_receipt: date | None,
    derived_status: str,
    open_qty: int,
) -> int:
    if promised is None:
        return 0
    if final_receipt is not None:
        return max(0, (final_receipt - promised).days)
    if open_qty > 0 and derived_status in {
        "Late",
        "Open",
        "Partially Received",
        "Approved",
    }:
        if promised < AS_OF_DATE:
            return max(0, (AS_OF_DATE - promised).days)
    return 0


def _planner_action(derived_status: str, receipt_status: str, days_late: int) -> str:
    if derived_status == "Cancelled":
        return "No Action — Cancelled"
    if derived_status == "Quality Hold":
        return "Quality Review Required"
    if derived_status == "Late" or days_late > 0:
        return "Expedite Delivery"
    if derived_status == "Over-Received":
        return "Review Over-Receipt"
    if derived_status == "Partially Received":
        return "Follow Up on Balance"
    if derived_status in {"Open", "Approved"}:
        return "Monitor In-Transit"
    if derived_status in {"Received", "Closed"}:
        return "Close Line"
    if derived_status == "Draft":
        return "Awaiting Approval"
    return "Monitor"


def _baseline_costs(inventory: pd.DataFrame) -> dict[str, float]:
    if inventory.empty:
        return {}
    raw = inventory.groupby("sku")["unit_cost"].mean()
    return {str(k): float(v) for k, v in raw.items()}


def _int_field(value: Any) -> int:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0
    if pd.isna(value):
        return 0
    return int(value)


def _as_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value).date()
    return parsed if isinstance(parsed, date) else None


def _normalize_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty:
        return inventory
    inv = inventory.copy()
    if "location_name" not in inv.columns:
        inv["location_name"] = inv.get("location", "")
    if "location_id" not in inv.columns:
        inv["location_id"] = inv.get("location", inv.get("location_name", "UNKNOWN"))
    return inv


def build_po_tracker_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build enriched purchase order tracker rows."""
    purchase_orders = data.get("purchase_orders", pd.DataFrame())
    receipts = data.get("purchase_order_receipts", pd.DataFrame())
    suppliers = data.get("suppliers", pd.DataFrame())
    inventory = _normalize_inventory(
        data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    )

    if purchase_orders.empty:
        return pd.DataFrame(columns=PO_TRACKER_HEADERS)

    supplier_names = (
        suppliers.set_index("supplier_id")["supplier_name"].to_dict()
        if not suppliers.empty
        else {}
    )
    product_names = (
        inventory.drop_duplicates("sku").set_index("sku")["product_name"].to_dict()
        if not inventory.empty and "product_name" in inventory.columns
        else {}
    )
    location_names = (
        inventory.drop_duplicates(subset=["sku", "location_id"])
        .set_index(["sku", "location_id"])["location_name"]
        .to_dict()
        if not inventory.empty
        else {}
    )
    baselines = _baseline_costs(inventory)
    receipt_agg = aggregate_receipts(receipts)

    merged = purchase_orders.merge(receipt_agg, on="po_line_id", how="left")
    rows: list[dict[str, Any]] = []

    for _, po in merged.iterrows():
        ordered = int(po["ordered_quantity"])
        received = _int_field(po.get("received_quantity", 0))
        accepted = _int_field(po.get("accepted_quantity", 0))
        rejected = _int_field(po.get("rejected_quantity", 0))
        po_status = str(po["po_status"])
        receipt_status = str(po.get("receipt_status", "") or "")

        if po_status in NON_SUPPLY_STATUSES:
            open_qty = 0
        else:
            open_qty = max(0, ordered - accepted)

        promised = po.get("promised_date")
        promised_date = _as_date(promised)
        first_rcpt = po.get("first_receipt_date")
        final_rcpt = po.get("final_receipt_date")
        first_receipt = _as_date(first_rcpt)
        final_receipt = _as_date(final_rcpt)

        derived_status = _derive_po_status(
            po_status, ordered, accepted, open_qty, promised_date, receipt_status
        )
        days_late = _days_late(promised_date, final_receipt, derived_status, open_qty)

        unit_cost = float(po.get("unit_cost", baselines.get(po["sku"], 0.0)))
        baseline = float(baselines.get(po["sku"], unit_cost))
        ppv = round(unit_cost - baseline, 4)
        ppv_pct = round(_safe_div(ppv, baseline) * 100, 2) if baseline else 0.0
        open_value = round(open_qty * unit_cost, 2)

        sku = str(po["sku"])
        loc_id = str(po["location_id"])
        loc_name = location_names.get((sku, loc_id), loc_id)

        rows.append(
            {
                "PO Number": po.get("po_number", po["po_line_id"]),
                "PO Line": po["po_line_id"],
                "Supplier ID": po.get("supplier_id", ""),
                "Supplier Name": supplier_names.get(
                    po.get("supplier_id", ""), po.get("supplier_id", "")
                ),
                "SKU": sku,
                "Product Name": product_names.get(sku, ""),
                "Location ID": loc_id,
                "Location Name": loc_name,
                "Buyer": po.get("buyer", ""),
                "Order Date": po.get("order_date"),
                "Approval Date": po.get("approval_date"),
                "Promised Date": po.get("promised_date"),
                "Expected Date": po.get("expected_date"),
                "First Receipt Date": first_receipt,
                "Final Receipt Date": final_receipt,
                "Ordered Quantity": ordered,
                "Received Quantity": received,
                "Accepted Quantity": accepted,
                "Rejected Quantity": rejected,
                "Open Quantity": open_qty,
                "Unit Cost": round(unit_cost, 2),
                "Extended Cost": round(
                    float(po.get("extended_cost", ordered * unit_cost)), 2
                ),
                "Open PO Value": open_value,
                "Baseline Unit Cost": round(baseline, 2),
                "Purchase Price Variance": ppv,
                "Purchase Price Variance %": ppv_pct,
                "Days Late": days_late,
                "PO Status": derived_status,
                "Receipt Status": receipt_status or "None",
                "Quality Issue": str(po.get("quality_issue", "") or ""),
                "Planner Action": _planner_action(
                    derived_status, receipt_status, days_late
                ),
            }
        )

    return pd.DataFrame(rows, columns=PO_TRACKER_HEADERS)


def compute_valid_open_supply(
    data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Valid open supply by SKU-location for replenishment.

    Excludes cancelled POs, quality holds, and over-receipts from supply.
    """
    tracker = build_po_tracker_dataframe(data)
    if tracker.empty:
        return pd.DataFrame(
            columns=[
                "sku",
                "location_id",
                "valid_open_quantity",
                "open_po_value",
                "has_late_po",
                "has_quality_hold",
            ]
        )

    valid_rows = tracker[
        (~tracker["PO Status"].isin(list(NON_SUPPLY_STATUSES)))
        & (tracker["Open Quantity"] > 0)
        & (tracker["PO Status"] != "Over-Received")
    ].copy()

    if valid_rows.empty:
        return pd.DataFrame(
            columns=[
                "sku",
                "location_id",
                "valid_open_quantity",
                "open_po_value",
                "has_late_po",
                "has_quality_hold",
            ]
        )

    valid_rows["valid_open_quantity"] = valid_rows.apply(
        lambda r: (
            0
            if r["PO Status"] == "Quality Hold" or r["Receipt Status"] == "Quality Hold"
            else int(r["Open Quantity"])
        ),
        axis=1,
    )
    valid_rows = valid_rows[valid_rows["valid_open_quantity"] > 0]

    if valid_rows.empty:
        return pd.DataFrame(
            columns=[
                "sku",
                "location_id",
                "valid_open_quantity",
                "open_po_value",
                "has_late_po",
                "has_quality_hold",
            ]
        )

    agg = (
        valid_rows.groupby(["SKU", "Location ID"])
        .agg(
            valid_open_quantity=("valid_open_quantity", "sum"),
            open_po_value=("Open PO Value", "sum"),
            has_late_po=("PO Status", lambda s: bool((s == "Late").any())),
            has_quality_hold=(
                "PO Status",
                lambda s: bool((s == "Quality Hold").any()),
            ),
        )
        .reset_index()
        .rename(columns={"SKU": "sku", "Location ID": "location_id"})
    )
    agg["valid_open_quantity"] = agg["valid_open_quantity"].astype(int)
    agg["open_po_value"] = agg["open_po_value"].round(2)
    return agg


def compute_po_tracker_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """KPI summary for PO tracker sheet."""
    if df.empty:
        return {
            "open_lines": 0,
            "open_value": 0.0,
            "late_lines": 0,
            "quality_holds": 0,
        }
    open_lines = df[df["Open Quantity"] > 0]
    return {
        "open_lines": int(len(open_lines)),
        "open_value": round(float(open_lines["Open PO Value"].sum()), 2),
        "late_lines": int((df["PO Status"] == "Late").sum()),
        "quality_holds": int((df["PO Status"] == "Quality Hold").sum()),
    }
