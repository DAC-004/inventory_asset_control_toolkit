"""Multi-warehouse transfer optimization with deterministic allocation."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from config.workbook_config import (
    ORDERING_COST,
    TRANSFER_EMERGENCY_BACKORDER_OVERRIDE,
    TRANSFER_MARGIN_RATE,
    TRANSFER_MAX_LEAD_TIME_DAYS,
    TRANSFER_MIN_NET_BENEFIT,
    TRANSFER_PURCHASE_MARKUP,
    TRANSFER_SOURCE_RISK_RATE,
)
from src.services.classification_service import build_classification_dataframe
from src.services.purchase_order_service import compute_valid_open_supply
from src.services.replenishment_service import build_replenishment_dataframe

TRANSFER_PLANNER_HEADERS = [
    "Rank",
    "SKU",
    "Product Name",
    "ABC Class",
    "Source Location",
    "Destination Location",
    "Source Projected Available",
    "Destination Projected Available",
    "Source Protected Level",
    "Destination Protected Level",
    "Source Initial Surplus",
    "Destination Initial Requirement",
    "Source Remaining Surplus",
    "Destination Remaining Requirement",
    "Source Backorder Qty",
    "Destination Backorder Qty",
    "Service Gap",
    "Transfer Lead Time (Days)",
    "Transfer Quantity",
    "Unit Cost",
    "Transfer Cost",
    "Estimated Margin Protected",
    "Expected Source Risk Cost",
    "Net Benefit",
    "Purchase Alternative Cost",
    "Action",
    "Priority",
    "Reason",
    "Allocation Batch",
]


def _normalize_data(
    data: dict[str, pd.DataFrame] | pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    if isinstance(data, pd.DataFrame):
        inv = data.copy()
        if "location_name" not in inv.columns and "location" in inv.columns:
            inv["location_name"] = inv["location"]
        if "location_id" not in inv.columns:
            inv["location_id"] = inv["location_name"]
        return {"inventory": inv, "inventory_full": inv}
    return data


def _location_label(row: pd.Series) -> str:
    return str(row.get("location_name", row.get("location", "")))


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


def transfer_lead_time_days(source_location: str, destination_location: str) -> int:
    """Documented lane lead times between location types."""
    source_is_dc = source_location.startswith("DC")
    dest_is_dc = destination_location.startswith("DC")
    if source_is_dc and not dest_is_dc:
        return 2
    if not source_is_dc and dest_is_dc:
        return 3
    if not source_is_dc and not dest_is_dc:
        return 4
    return 5


def is_allowed_route(source_location: str, destination_location: str) -> bool:
    """Cross-location routes are allowed when locations differ."""
    if not source_location or not destination_location:
        return False
    if source_location == destination_location:
        return False
    return True


def _round_case_pack(quantity: int, case_pack: int) -> int:
    if quantity <= 0:
        return 0
    if case_pack <= 1:
        return quantity
    return int(math.floor(quantity / case_pack) * case_pack)


def _build_position_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Inventory positions with surplus and requirement by SKU-location."""
    repl = build_replenishment_dataframe(data)
    if repl.empty:
        return pd.DataFrame()

    inventory = data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    inv_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    if not inventory.empty:
        inv = inventory.copy()
        if "location_name" not in inv.columns:
            inv["location_name"] = inv.get("location", "")
        if "location_id" not in inv.columns:
            inv["location_id"] = inv.get("location", inv["location_name"])
        for _, row in inv.iterrows():
            key = (str(row["sku"]), str(row.get("location_id", row["location_name"])))
            inv_lookup[key] = {
                "product_name": row.get("product_name", ""),
                "region": row.get("region", ""),
                "case_pack": int(row.get("case_pack", 1)),
                "storage_capacity_units": int(row.get("storage_capacity_units", 9999)),
                "selling_price": float(
                    row.get("selling_price", row.get("unit_cost", 0))
                ),
                "location_name": str(row.get("location_name", row.get("location", ""))),
            }

    classification = build_classification_dataframe(data)
    abc_map = (
        classification.set_index("SKU")["ABC Class"].to_dict()
        if not classification.empty
        else {}
    )

    rows: list[dict[str, Any]] = []
    for _, row in repl.iterrows():
        sku = str(row["SKU"])
        loc_id = str(row["Location ID"])
        loc_name = str(row["Location Name"])
        target = int(row["Target Stock"])
        rop = int(row["Reorder Point"])
        protected = max(target, rop)
        projected = int(row["Projected Available"])
        surplus = max(projected - protected, 0)
        requirement = max(target - projected, 0)
        meta = inv_lookup.get((sku, loc_id), inv_lookup.get((sku, loc_name), {}))

        rows.append(
            {
                "sku": sku,
                "location_id": loc_id,
                "location_name": loc_name,
                "product_name": meta.get("product_name", row.get("Product Name", "")),
                "abc_class": abc_map.get(sku, "C"),
                "region": meta.get("region", ""),
                "projected_available": projected,
                "protected_level": protected,
                "target_stock": target,
                "transferable_surplus": surplus,
                "destination_requirement": requirement,
                "backorder_qty": int(row["Backorder Quantity"]),
                "unit_cost": float(row["Unit Cost"]),
                "selling_price": float(meta.get("selling_price", row["Unit Cost"])),
                "case_pack": int(meta.get("case_pack", 1)),
                "storage_capacity": int(meta.get("storage_capacity_units", 9999)),
                "service_gap": max(0, requirement) / max(target, 1),
            }
        )

    return pd.DataFrame(rows)


def _purchase_alternative_cost(quantity: int, unit_cost: float) -> float:
    return round(
        quantity * unit_cost * (1 + TRANSFER_PURCHASE_MARKUP) + ORDERING_COST, 2
    )


def _determine_action(
    qty: int,
    net_benefit: float,
    transfer_cost: float,
    purchase_cost: float,
    dest_backorder: int,
    has_late_po: bool,
    emergency: bool,
) -> tuple[str, str, str]:
    if qty <= 0:
        return "No Action", "Low", "No transferable quantity after allocation rules"

    if emergency and net_benefit <= TRANSFER_MIN_NET_BENEFIT:
        return (
            "Transfer",
            "Critical",
            "Emergency override — destination backorder requires inbound stock",
        )

    if net_benefit < TRANSFER_MIN_NET_BENEFIT:
        return "Monitor", "Low", "Net benefit below threshold"

    if has_late_po and dest_backorder > 0:
        return (
            "Expedite Existing PO",
            "High",
            "Late open PO exists; expedite before transfer",
        )

    if transfer_cost < purchase_cost and net_benefit >= TRANSFER_MIN_NET_BENEFIT:
        if qty > 0 and purchase_cost < transfer_cost * 1.5:
            return "Transfer", "High", "Transfer lower cost than purchase alternative"
        return "Transfer", "Medium", "Positive net benefit vs purchase alternative"

    if purchase_cost <= transfer_cost:
        if net_benefit > 0:
            return (
                "Transfer Then Purchase",
                "Medium",
                "Partial transfer; remainder via purchase",
            )
        return "Purchase", "Medium", "Purchase alternative more economical"

    return "Data Review Required", "Low", "Economics inconclusive — manual review"


def _assert_transfer_invariants(
    allocated: int,
    remaining_surplus: int,
    remaining_requirement: int,
    source_loc: str,
    dest_loc: str,
) -> None:
    assert source_loc != dest_loc
    assert allocated > 0
    assert allocated <= remaining_surplus
    assert allocated <= remaining_requirement


def build_transfer_dataframe(
    data: dict[str, pd.DataFrame] | pd.DataFrame,
) -> pd.DataFrame:
    """Build ranked transfer plan with deterministic double-allocation prevention."""
    ctx = _normalize_data(data)
    positions = _build_position_table(ctx)
    if positions.empty:
        return pd.DataFrame(columns=TRANSFER_PLANNER_HEADERS)

    open_supply = compute_valid_open_supply(ctx)
    late_po_skus: set[tuple[str, str]] = set()
    if not open_supply.empty:
        late_rows = open_supply[open_supply["has_late_po"]]
        for _, r in late_rows.iterrows():
            late_po_skus.add((str(r["sku"]), str(r["location_id"])))

    remaining_surplus: dict[tuple[str, str], int] = {}
    remaining_requirement: dict[tuple[str, str], int] = {}
    initial_surplus: dict[tuple[str, str], int] = {}
    initial_requirement: dict[tuple[str, str], int] = {}

    for _, pos in positions.iterrows():
        key = (str(pos["sku"]), str(pos["location_name"]))
        remaining_surplus[key] = int(pos["transferable_surplus"])
        remaining_requirement[key] = int(pos["destination_requirement"])
        initial_surplus[key] = int(pos["transferable_surplus"])
        initial_requirement[key] = int(pos["destination_requirement"])

    candidates: list[dict[str, Any]] = []
    skus = sorted(positions["sku"].unique())

    for sku in skus:
        sku_rows = positions[positions["sku"] == sku]
        sources = sku_rows[sku_rows["transferable_surplus"] > 0].sort_values(
            ["transferable_surplus", "location_name"], ascending=[False, True]
        )
        destinations = sku_rows[sku_rows["destination_requirement"] > 0].sort_values(
            ["destination_requirement", "backorder_qty", "location_name"],
            ascending=[False, False, True],
        )

        for _, src in sources.iterrows():
            for _, dest in destinations.iterrows():
                src_loc = str(src["location_name"])
                dest_loc = str(dest["location_name"])
                if src_loc == dest_loc:
                    continue
                if not is_allowed_route(src_loc, dest_loc):
                    continue

                lead_time = transfer_lead_time_days(src_loc, dest_loc)
                if lead_time > TRANSFER_MAX_LEAD_TIME_DAYS:
                    continue

                src_key = (sku, src_loc)
                dest_key = (sku, dest_loc)
                avail_surplus = remaining_surplus.get(src_key, 0)
                avail_req = remaining_requirement.get(dest_key, 0)
                if avail_surplus <= 0 or avail_req <= 0:
                    continue

                dest_capacity = int(dest["storage_capacity"]) - int(
                    dest["projected_available"]
                )
                if dest_capacity <= 0:
                    continue

                case_pack = int(src["case_pack"])
                raw_qty = min(avail_surplus, avail_req, dest_capacity)
                qty = _round_case_pack(raw_qty, case_pack)
                if qty <= 0:
                    continue

                unit_cost = float(src["unit_cost"])
                selling = float(src["selling_price"])
                transfer_cost = estimate_transfer_cost(src_loc, dest_loc, qty)
                margin_protected = round(
                    qty * max(selling - unit_cost, unit_cost * TRANSFER_MARGIN_RATE), 2
                )
                post_transfer_surplus = avail_surplus - qty
                risk_factor = (
                    1.0 if post_transfer_surplus < src["protected_level"] * 0.1 else 0.5
                )
                source_risk = round(
                    qty * unit_cost * TRANSFER_SOURCE_RISK_RATE * risk_factor, 2
                )
                net_benefit = round(margin_protected - transfer_cost - source_risk, 2)
                purchase_alt = _purchase_alternative_cost(qty, unit_cost)

                dest_backorder = int(dest["backorder_qty"])
                emergency = TRANSFER_EMERGENCY_BACKORDER_OVERRIDE and dest_backorder > 0
                has_late = (sku, str(dest["location_id"])) in late_po_skus

                if net_benefit <= TRANSFER_MIN_NET_BENEFIT and not emergency:
                    continue

                candidates.append(
                    {
                        "sku": sku,
                        "product_name": src["product_name"],
                        "abc_class": src["abc_class"],
                        "source_loc": src_loc,
                        "dest_loc": dest_loc,
                        "src_projected": int(src["projected_available"]),
                        "dest_projected": int(dest["projected_available"]),
                        "src_protected": int(src["protected_level"]),
                        "dest_protected": int(dest["protected_level"]),
                        "src_initial_surplus": initial_surplus[src_key],
                        "dest_initial_req": initial_requirement[dest_key],
                        "src_backorder": int(src["backorder_qty"]),
                        "dest_backorder": dest_backorder,
                        "service_gap": round(float(dest["service_gap"]), 4),
                        "lead_time": lead_time,
                        "qty": qty,
                        "unit_cost": unit_cost,
                        "selling_price": selling,
                        "transfer_cost": transfer_cost,
                        "margin_protected": margin_protected,
                        "source_risk": source_risk,
                        "net_benefit": net_benefit,
                        "purchase_alt": purchase_alt,
                        "has_late_po": has_late,
                        "emergency": emergency,
                        "src_key": src_key,
                        "dest_key": dest_key,
                    }
                )

    candidates.sort(
        key=lambda c: (
            -c["net_benefit"],
            -c["dest_backorder"],
            c["sku"],
            c["source_loc"],
            c["dest_loc"],
        )
    )

    allocations: list[dict[str, Any]] = []
    batch_id = 1

    for cand in candidates:
        src_key = cand["src_key"]
        dest_key = cand["dest_key"]
        avail_surplus = remaining_surplus.get(src_key, 0)
        avail_req = remaining_requirement.get(dest_key, 0)
        if avail_surplus <= 0 or avail_req <= 0:
            continue

        qty = min(cand["qty"], avail_surplus, avail_req)
        src_pos = positions[
            (positions["sku"] == cand["sku"])
            & (positions["location_name"] == cand["source_loc"])
        ]
        case_pack = int(src_pos.iloc[0]["case_pack"]) if not src_pos.empty else 1
        qty = _round_case_pack(qty, case_pack)
        if qty <= 0 or qty > avail_surplus or qty > avail_req:
            continue

        _assert_transfer_invariants(
            qty,
            avail_surplus,
            avail_req,
            cand["source_loc"],
            cand["dest_loc"],
        )

        remaining_surplus[src_key] = avail_surplus - qty
        remaining_requirement[dest_key] = avail_req - qty

        transfer_cost = estimate_transfer_cost(
            cand["source_loc"], cand["dest_loc"], qty
        )
        selling = float(cand["selling_price"])
        unit_cost = float(cand["unit_cost"])
        margin_protected = round(
            qty * max(selling - unit_cost, unit_cost * TRANSFER_MARGIN_RATE),
            2,
        )
        post_transfer_surplus = remaining_surplus[src_key]
        risk_factor = (
            1.0 if post_transfer_surplus < cand["src_protected"] * 0.1 else 0.5
        )
        source_risk = round(
            qty * unit_cost * TRANSFER_SOURCE_RISK_RATE * risk_factor, 2
        )
        net_benefit = round(margin_protected - transfer_cost - source_risk, 2)
        purchase_alt = _purchase_alternative_cost(qty, unit_cost)

        action, priority, reason = _determine_action(
            qty,
            net_benefit,
            transfer_cost,
            purchase_alt,
            cand["dest_backorder"],
            cand["has_late_po"],
            cand["emergency"],
        )

        if action in {"No Action", "Monitor"} and not cand["emergency"]:
            continue

        allocations.append(
            {
                "Rank": len(allocations) + 1,
                "SKU": cand["sku"],
                "Product Name": cand["product_name"],
                "ABC Class": cand["abc_class"],
                "Source Location": cand["source_loc"],
                "Destination Location": cand["dest_loc"],
                "Source Projected Available": cand["src_projected"],
                "Destination Projected Available": cand["dest_projected"],
                "Source Protected Level": cand["src_protected"],
                "Destination Protected Level": cand["dest_protected"],
                "Source Initial Surplus": cand["src_initial_surplus"],
                "Destination Initial Requirement": cand["dest_initial_req"],
                "Source Remaining Surplus": remaining_surplus[src_key],
                "Destination Remaining Requirement": remaining_requirement[dest_key],
                "Source Backorder Qty": cand["src_backorder"],
                "Destination Backorder Qty": cand["dest_backorder"],
                "Service Gap": cand["service_gap"],
                "Transfer Lead Time (Days)": cand["lead_time"],
                "Transfer Quantity": qty,
                "Unit Cost": cand["unit_cost"],
                "Transfer Cost": transfer_cost,
                "Estimated Margin Protected": margin_protected,
                "Expected Source Risk Cost": source_risk,
                "Net Benefit": net_benefit,
                "Purchase Alternative Cost": purchase_alt,
                "Action": action,
                "Priority": priority,
                "Reason": reason,
                "Allocation Batch": batch_id,
            }
        )
        batch_id += 1

    if not allocations:
        return pd.DataFrame(columns=TRANSFER_PLANNER_HEADERS)

    return pd.DataFrame(allocations, columns=TRANSFER_PLANNER_HEADERS)


def build_surplus_lookup(
    data: dict[str, pd.DataFrame] | pd.DataFrame,
) -> dict[str, int]:
    """Total transferable surplus by SKU for markdown transfer-first logic."""
    positions = _build_position_table(_normalize_data(data))
    if positions.empty:
        return {}
    agg = positions.groupby("sku")["transferable_surplus"].sum()
    return {str(k): int(v) for k, v in agg.items() if v > 0}
