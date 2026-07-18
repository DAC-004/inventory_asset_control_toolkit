"""Replenishment planning — lead time, safety stock, ROP, EOQ, and order recommendations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import pandas as pd

from config.workbook_config import (
    AS_OF_DATE,
    GLOBAL_LEAD_TIME_FALLBACK_DAYS,
    HOLDING_COST_PCT,
    MIN_LEAD_TIME_SAMPLES_ADVANCED,
    MIN_WEEKS_FOR_ADVANCED_SAFETY_STOCK,
    ORDERING_COST,
    SERVICE_LEVEL_TARGETS,
    SERVICE_LEVEL_Z_SCORES,
)
from src.services.classification_service import build_classification_dataframe
from src.services.forecast_service import build_forecast_lookup, resolve_planning_demand
from src.services.purchase_order_service import compute_valid_open_supply
from src.services.vendor_scorecard_service import build_vendor_risk_lookup

REPLENISHMENT_HEADERS = [
    "SKU",
    "Location ID",
    "Location Name",
    "Product Name",
    "Category",
    "Supplier ID",
    "Supplier Risk Class",
    "ABC Class",
    "Quantity On Hand",
    "Quantity Allocated",
    "Backorder Quantity",
    "Open PO Quantity",
    "Projected Available",
    "Min Stock",
    "Max Stock",
    "Target Stock",
    "Storage Capacity Units",
    "Unit Cost",
    "Annual Demand",
    "Avg Daily Demand",
    "Planning Avg Daily Demand",
    "Demand Source",
    "Avg Weekly Demand",
    "Demand Std Dev",
    "Coefficient of Variation",
    "Demand Pattern",
    "Service Level Target",
    "Z-Score",
    "Planning Lead Time Days",
    "Lead Time Source",
    "Lead Time Average",
    "Lead Time Median",
    "Lead Time Minimum",
    "Lead Time Maximum",
    "Lead Time Std Dev",
    "Lead Time Late Rate",
    "Avg Days Late",
    "Lead Time Sample Count",
    "Expected Lead-Time Demand",
    "Safety Stock Method",
    "Safety Stock",
    "Reorder Point",
    "Net Requirement",
    "EOQ",
    "MOQ",
    "Case Pack",
    "Recommended Order Qty",
    "Order By Date",
    "Replenishment Status",
    "Notes",
]


@dataclass(frozen=True)
class LeadTimeStats:
    average: float
    median: float
    minimum: float
    maximum: float
    std_dev: float
    late_rate: float
    avg_days_late: float
    sample_count: int


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0 or not math.isfinite(denominator):
        return default
    result = numerator / denominator
    if not math.isfinite(result):
        return default
    return result


def _normalize_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    if inventory.empty:
        return inventory
    inv = inventory.copy()
    if "location_name" not in inv.columns:
        inv["location_name"] = inv.get("location", "")
    if "location_id" not in inv.columns:
        inv["location_id"] = inv.get("location", inv.get("location_name", "UNKNOWN"))
    for col, default in (
        ("quantity_allocated", 0),
        ("backorder_quantity", 0),
        ("case_pack", 1),
        ("minimum_order_quantity", 1),
        ("storage_capacity_units", 9999),
        ("target_stock", 0),
    ):
        if col not in inv.columns:
            inv[col] = default
    return inv


def _build_lead_time_records(
    purchase_orders: pd.DataFrame, receipts: pd.DataFrame
) -> pd.DataFrame:
    """Actual lead time = final receipt date - PO approval date."""
    if purchase_orders.empty:
        return pd.DataFrame(
            columns=[
                "po_line_id",
                "sku",
                "supplier_id",
                "actual_lead_time_days",
                "days_late",
                "is_late",
            ]
        )

    final_receipts = (
        receipts.groupby("po_line_id")["receipt_date"].max().reset_index()
        if not receipts.empty
        else pd.DataFrame(columns=["po_line_id", "receipt_date"])
    )
    final_receipts = final_receipts.rename(
        columns={"receipt_date": "final_receipt_date"}
    )

    merged = purchase_orders.merge(final_receipts, on="po_line_id", how="inner")
    merged = merged[
        merged["approval_date"].notna() & merged["final_receipt_date"].notna()
    ]
    if merged.empty:
        return pd.DataFrame(
            columns=[
                "po_line_id",
                "sku",
                "supplier_id",
                "actual_lead_time_days",
                "days_late",
                "is_late",
            ]
        )

    approval = pd.to_datetime(merged["approval_date"])
    receipt = pd.to_datetime(merged["final_receipt_date"])
    promised = pd.to_datetime(merged["promised_date"])
    merged = merged.copy()
    merged["actual_lead_time_days"] = (receipt - approval).dt.days
    merged["days_late"] = (receipt - promised).dt.days.clip(lower=0)
    merged["is_late"] = merged["days_late"] > 0
    return merged[
        [
            "po_line_id",
            "sku",
            "supplier_id",
            "actual_lead_time_days",
            "days_late",
            "is_late",
        ]
    ]


def compute_lead_time_stats(records: pd.DataFrame) -> LeadTimeStats:
    """Aggregate lead-time metrics for a history slice."""
    if records.empty:
        return LeadTimeStats(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)

    days = records["actual_lead_time_days"].astype(float)
    late = records[records["is_late"]]
    return LeadTimeStats(
        average=round(float(days.mean()), 2),
        median=round(float(days.median()), 2),
        minimum=round(float(days.min()), 2),
        maximum=round(float(days.max()), 2),
        std_dev=round(float(days.std(ddof=0)) if len(days) > 1 else 0.0, 2),
        late_rate=round(float(records["is_late"].mean()), 4),
        avg_days_late=(
            round(float(late["days_late"].mean()), 2) if not late.empty else 0.0
        ),
        sample_count=int(len(records)),
    )


def resolve_planning_lead_time(
    sku: str,
    supplier_id: str,
    sku_supplier_stats: LeadTimeStats,
    supplier_stats: LeadTimeStats,
    supplier_default: float,
) -> tuple[float, str, LeadTimeStats]:
    """Fallback: SKU+Supplier → Supplier → Supplier default → Global."""
    if sku_supplier_stats.sample_count > 0:
        return sku_supplier_stats.average, "SKU + Supplier history", sku_supplier_stats
    if supplier_stats.sample_count > 0:
        return supplier_stats.average, "Supplier history", supplier_stats
    if supplier_default > 0:
        default_stats = LeadTimeStats(
            supplier_default,
            supplier_default,
            supplier_default,
            supplier_default,
            0.0,
            0.0,
            0.0,
            0,
        )
        return supplier_default, "Supplier default", default_stats
    fallback = float(GLOBAL_LEAD_TIME_FALLBACK_DAYS)
    default_stats = LeadTimeStats(
        fallback, fallback, fallback, fallback, 0.0, 0.0, 0.0, 0
    )
    return fallback, "Global fallback", default_stats


def _demand_stats(demand: pd.DataFrame, sku: str, location_id: str) -> dict[str, Any]:
    """Trailing 52-week demand statistics at SKU-location."""
    empty = {
        "annual_demand": 0,
        "avg_daily_demand": 0.0,
        "avg_weekly_demand": 0.0,
        "demand_std_dev": 0.0,
        "coefficient_of_variation": 0.0,
        "demand_pattern": "no_recent_demand",
        "weekly_values": [],
    }
    if demand.empty:
        return empty

    subset = demand[(demand["sku"] == sku) & (demand["location_id"] == location_id)]
    if subset.empty:
        return empty

    weekly = subset.sort_values("week_start_date")["units_sold"].astype(float).tolist()
    annual = int(round(sum(weekly)))
    weeks = max(len(weekly), 1)
    avg_weekly = sum(weekly) / weeks
    avg_daily = avg_weekly / 7.0
    if len(weekly) > 1:
        mean_w = avg_weekly
        var_w = sum((w - mean_w) ** 2 for w in weekly) / len(weekly)
        weekly_std = math.sqrt(var_w)
        demand_std = weekly_std / math.sqrt(7.0)
    else:
        demand_std = 0.0

    cv = _safe_div(demand_std, avg_daily, 0.0) if avg_daily > 0 else 0.0
    pattern = _classify_demand_pattern(weekly, avg_daily, cv)

    return {
        "annual_demand": annual,
        "avg_daily_demand": round(avg_daily, 4),
        "avg_weekly_demand": round(avg_weekly, 4),
        "demand_std_dev": round(demand_std, 4),
        "coefficient_of_variation": round(cv, 4),
        "demand_pattern": pattern,
        "weekly_values": weekly,
    }


def _classify_demand_pattern(weekly: list[float], avg_daily: float, cv: float) -> str:
    if avg_daily <= 0:
        return "no_recent_demand"
    recent = weekly[-13:] if len(weekly) >= 13 else weekly
    if sum(recent) == 0:
        return "no_recent_demand"
    if cv >= 1.0:
        return "intermittent"
    if cv >= 0.5:
        return "seasonal"
    if len(weekly) >= 26:
        first = sum(weekly[:26]) / 26
        second = sum(weekly[26:]) / max(len(weekly[26:]), 1)
        if second > first * 1.15:
            return "trending"
        if second < first * 0.85:
            return "declining"
    if max(weekly) >= avg_daily * 7 * 2.5:
        return "promotional"
    return "stable"


def _service_level_for_abc(abc_class: str) -> tuple[float, float]:
    target = SERVICE_LEVEL_TARGETS.get(abc_class, SERVICE_LEVEL_TARGETS["C"])
    z_score = SERVICE_LEVEL_Z_SCORES.get(abc_class, SERVICE_LEVEL_Z_SCORES["C"])
    return target, z_score


def _safety_stock(
    z_score: float,
    avg_daily_demand: float,
    demand_std_dev: float,
    planning_lead_time: float,
    lead_time_std_dev: float,
    lead_time_sample_count: int,
    weekly_count: int,
) -> tuple[int, str]:
    if avg_daily_demand <= 0 or planning_lead_time <= 0:
        return 0, "No Demand"

    use_advanced = (
        lead_time_sample_count >= MIN_LEAD_TIME_SAMPLES_ADVANCED
        and weekly_count >= MIN_WEEKS_FOR_ADVANCED_SAFETY_STOCK
        and demand_std_dev > 0
        and lead_time_std_dev > 0
    )

    if use_advanced:
        demand_variance = demand_std_dev**2
        lead_time_variance = lead_time_std_dev**2
        inner = (planning_lead_time * demand_variance) + (
            (avg_daily_demand**2) * lead_time_variance
        )
        stock = z_score * math.sqrt(max(inner, 0.0))
        method = "Advanced (Lead Time & Demand Variance)"
    else:
        stock = z_score * demand_std_dev * math.sqrt(planning_lead_time)
        method = "Basic (Demand Std Dev × √Lead Time)"

    return max(0, int(round(stock))), method


def _compute_eoq(annual_demand: float, unit_cost: float) -> int:
    if annual_demand <= 0 or unit_cost <= 0:
        return 0
    holding = unit_cost * HOLDING_COST_PCT
    if holding <= 0:
        return 0
    eoq = math.sqrt(2 * annual_demand * ORDERING_COST / holding)
    if not math.isfinite(eoq):
        return 0
    return max(0, int(round(eoq)))


def _round_to_case_pack(quantity: float, case_pack: int) -> int:
    if case_pack <= 1:
        return max(0, int(round(quantity)))
    if quantity <= 0:
        return 0
    return int(math.ceil(quantity / case_pack) * case_pack)


def _determine_status_and_quantity(
    *,
    projected_available: float,
    reorder_point: int,
    max_stock: int,
    min_stock: int,
    avg_daily_demand: float,
    net_requirement: int,
    eoq: int,
    moq: int,
    case_pack: int,
    storage_capacity: int,
    open_po_qty: int,
    has_late_po: bool,
    has_quality_hold: bool,
    supplier_risk: str,
    unit_cost: float,
    supplier_mov: float,
) -> tuple[int, str, str]:
    notes: list[str] = []

    if avg_daily_demand <= 0:
        return 0, "No Recent Demand", "No trailing demand in 52-week history"

    if unit_cost <= 0:
        return 0, "Data Review Required", "Missing or invalid unit cost"

    if projected_available > max_stock:
        return 0, "Overstocked", "Projected available exceeds max stock"

    if has_quality_hold:
        notes.append("Open PO on quality hold excluded from valid supply")

    if supplier_risk in {"High Risk", "Watch"}:
        notes.append(f"Supplier risk class: {supplier_risk}")

    if supplier_risk == "High Risk" and projected_available <= reorder_point:
        return (
            0,
            "Supplier Constraint",
            f"High-risk supplier ({supplier_risk}); review before ordering",
        )

    if has_late_po and projected_available <= reorder_point:
        return (
            0,
            "Expedite Existing PO",
            "Open PO is late; expedite before placing new order",
        )

    if projected_available > reorder_point:
        if projected_available < min_stock:
            return 0, "Monitor", "Above reorder point but below minimum stock"
        return 0, "Sufficient", "Projected available covers reorder point"

    raw_qty = max(net_requirement, eoq, moq)
    raw_qty = _round_to_case_pack(raw_qty, case_pack)

    capacity_room = max(0, storage_capacity - int(projected_available))
    if raw_qty > capacity_room:
        capped = _round_to_case_pack(capacity_room, case_pack)
        if capped <= 0:
            return (
                0,
                "Capacity Constraint",
                "Storage capacity prevents additional orders",
            )
        notes.append("Quantity capped by storage capacity")
        raw_qty = capped

    order_value = raw_qty * unit_cost
    if supplier_mov > 0 and order_value < supplier_mov and raw_qty > 0:
        mov_qty = _round_to_case_pack(
            _safe_div(supplier_mov, unit_cost, moq), case_pack
        )
        if mov_qty > capacity_room:
            return (
                0,
                "Supplier Constraint",
                "Cannot meet supplier minimum order value within capacity",
            )
        raw_qty = max(raw_qty, mov_qty)
        notes.append("Quantity raised to supplier minimum order value")

    if open_po_qty > 0:
        notes.append(
            f"{open_po_qty} units already on open POs included in projected available"
        )

    note_text = (
        "; ".join(notes)
        if notes
        else "Order recommended to restore target service level"
    )
    return raw_qty, "Order Required", note_text


def _order_by_date(
    projected_available: float, reorder_point: int, avg_daily_demand: float
) -> date | None:
    if avg_daily_demand <= 0:
        return None
    if projected_available <= reorder_point:
        return AS_OF_DATE
    days_until = (projected_available - reorder_point) / avg_daily_demand
    return AS_OF_DATE + timedelta(days=max(0, int(math.floor(days_until))))


def build_replenishment_dataframe(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build SKU-location replenishment planning table."""
    inventory = _normalize_inventory(
        data.get("inventory_full", data.get("inventory", pd.DataFrame()))
    )
    demand = data.get("demand_history", pd.DataFrame())
    purchase_orders = data.get("purchase_orders", pd.DataFrame())
    receipts = data.get("purchase_order_receipts", pd.DataFrame())
    suppliers = data.get("suppliers", pd.DataFrame())

    if inventory.empty:
        return pd.DataFrame(columns=REPLENISHMENT_HEADERS)

    classification = build_classification_dataframe(data)
    abc_map = (
        classification.set_index(["SKU"])["ABC Class"].to_dict()
        if not classification.empty
        else {}
    )

    lead_records = _build_lead_time_records(purchase_orders, receipts)
    supplier_defaults = (
        suppliers.set_index("supplier_id")["default_lead_time_days"].to_dict()
        if not suppliers.empty
        else {}
    )
    supplier_mov = (
        suppliers.set_index("supplier_id")["minimum_order_value"].to_dict()
        if not suppliers.empty
        else {}
    )
    open_po = compute_valid_open_supply(data)
    vendor_risk = build_vendor_risk_lookup(data)
    open_po_map: dict[tuple[str, str], dict[str, Any]] = {}
    if not open_po.empty:
        for _, row in open_po.iterrows():
            open_po_map[(str(row["sku"]), str(row["location_id"]))] = {
                "open_po_quantity": int(row["valid_open_quantity"]),
                "has_late_po": bool(row["has_late_po"]),
                "has_quality_hold": bool(row["has_quality_hold"]),
            }

    forecast_lookup = build_forecast_lookup(data)

    rows: list[dict[str, Any]] = []
    for _, inv in inventory.iterrows():
        sku = inv["sku"]
        loc_id = inv["location_id"]
        supplier_id = str(inv.get("supplier_id", ""))
        abc_class = abc_map.get(sku, "C")
        service_target, z_score = _service_level_for_abc(abc_class)

        sku_supplier_records = lead_records[
            (lead_records["sku"] == sku) & (lead_records["supplier_id"] == supplier_id)
        ]
        supplier_records = lead_records[lead_records["supplier_id"] == supplier_id]
        sku_supplier_stats = compute_lead_time_stats(sku_supplier_records)
        supplier_stats = compute_lead_time_stats(supplier_records)
        supplier_default = float(supplier_defaults.get(supplier_id, 0))

        planning_lt, lt_source, lt_stats = resolve_planning_lead_time(
            sku,
            supplier_id,
            sku_supplier_stats,
            supplier_stats,
            supplier_default,
        )

        dmd = _demand_stats(demand, sku, loc_id)
        fc = forecast_lookup.get((str(sku), str(loc_id)), {})
        planning_daily, demand_source = resolve_planning_demand(
            dmd["avg_daily_demand"],
            float(fc.get("weekly_level", 0.0)),
            float(fc.get("selected_wape", 1.0)),
            float(fc.get("historical_wape", 1.0)),
        )
        qoh = int(inv["quantity_on_hand"])
        allocated = int(inv["quantity_allocated"])
        backorder = int(inv["backorder_quantity"])
        open_info = open_po_map.get((sku, loc_id), {})
        open_po_qty = int(open_info.get("open_po_quantity", 0))
        has_late_po = bool(open_info.get("has_late_po", False))
        has_quality_hold = bool(open_info.get("has_quality_hold", False))
        supplier_risk = vendor_risk.get(supplier_id, "Data Insufficient")

        projected = qoh + open_po_qty - allocated - backorder
        expected_ltd = round(planning_daily * planning_lt, 2)
        safety_stock, ss_method = _safety_stock(
            z_score,
            planning_daily,
            dmd["demand_std_dev"],
            planning_lt,
            lt_stats.std_dev,
            lt_stats.sample_count,
            len(dmd["weekly_values"]),
        )
        reorder_point = max(0, int(round(expected_ltd + safety_stock)))
        net_requirement = max(0, reorder_point - int(projected))

        unit_cost = float(inv["unit_cost"])
        eoq = _compute_eoq(float(dmd["annual_demand"]), unit_cost)
        moq = int(inv["minimum_order_quantity"])
        case_pack = max(1, int(inv["case_pack"]))
        storage_capacity = int(inv["storage_capacity_units"])
        max_stock = int(inv["max_stock"])
        min_stock = int(inv["min_stock"])
        target_stock = int(inv.get("target_stock", min_stock))

        rec_qty, status, notes = _determine_status_and_quantity(
            projected_available=projected,
            reorder_point=reorder_point,
            max_stock=max_stock,
            min_stock=min_stock,
            avg_daily_demand=planning_daily,
            net_requirement=net_requirement,
            eoq=eoq,
            moq=moq,
            case_pack=case_pack,
            storage_capacity=storage_capacity,
            open_po_qty=open_po_qty,
            has_late_po=has_late_po,
            has_quality_hold=has_quality_hold,
            supplier_risk=supplier_risk,
            unit_cost=unit_cost,
            supplier_mov=float(supplier_mov.get(supplier_id, 0)),
        )
        if demand_source != "Historical Average":
            notes = f"Demand source: {demand_source}. {notes}"
        order_by = _order_by_date(projected, reorder_point, planning_daily)

        rows.append(
            {
                "SKU": sku,
                "Location ID": loc_id,
                "Location Name": inv["location_name"],
                "Product Name": inv["product_name"],
                "Category": inv["category"],
                "Supplier ID": supplier_id,
                "Supplier Risk Class": supplier_risk,
                "ABC Class": abc_class,
                "Quantity On Hand": qoh,
                "Quantity Allocated": allocated,
                "Backorder Quantity": backorder,
                "Open PO Quantity": open_po_qty,
                "Projected Available": projected,
                "Min Stock": min_stock,
                "Max Stock": max_stock,
                "Target Stock": target_stock,
                "Storage Capacity Units": storage_capacity,
                "Unit Cost": round(unit_cost, 2),
                "Annual Demand": dmd["annual_demand"],
                "Avg Daily Demand": dmd["avg_daily_demand"],
                "Planning Avg Daily Demand": planning_daily,
                "Demand Source": demand_source,
                "Avg Weekly Demand": dmd["avg_weekly_demand"],
                "Demand Std Dev": dmd["demand_std_dev"],
                "Coefficient of Variation": dmd["coefficient_of_variation"],
                "Demand Pattern": dmd["demand_pattern"],
                "Service Level Target": service_target,
                "Z-Score": z_score,
                "Planning Lead Time Days": round(planning_lt, 2),
                "Lead Time Source": lt_source,
                "Lead Time Average": lt_stats.average,
                "Lead Time Median": lt_stats.median,
                "Lead Time Minimum": lt_stats.minimum,
                "Lead Time Maximum": lt_stats.maximum,
                "Lead Time Std Dev": lt_stats.std_dev,
                "Lead Time Late Rate": lt_stats.late_rate,
                "Avg Days Late": lt_stats.avg_days_late,
                "Lead Time Sample Count": lt_stats.sample_count,
                "Expected Lead-Time Demand": expected_ltd,
                "Safety Stock Method": ss_method,
                "Safety Stock": safety_stock,
                "Reorder Point": reorder_point,
                "Net Requirement": net_requirement,
                "EOQ": eoq,
                "MOQ": moq,
                "Case Pack": case_pack,
                "Recommended Order Qty": rec_qty,
                "Order By Date": order_by,
                "Replenishment Status": status,
                "Notes": notes,
            }
        )

    return pd.DataFrame(rows, columns=REPLENISHMENT_HEADERS)


def compute_replenishment_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Summary KPIs for the replenishment planning sheet."""
    if df.empty:
        return {
            "order_required_count": 0,
            "expedite_count": 0,
            "sufficient_count": 0,
            "avg_safety_stock": 0.0,
            "avg_reorder_point": 0.0,
            "total_recommended_qty": 0,
        }
    status = df["Replenishment Status"]
    return {
        "order_required_count": int((status == "Order Required").sum()),
        "expedite_count": int((status == "Expedite Existing PO").sum()),
        "sufficient_count": int((status == "Sufficient").sum()),
        "avg_safety_stock": round(float(df["Safety Stock"].mean()), 1),
        "avg_reorder_point": round(float(df["Reorder Point"].mean()), 1),
        "total_recommended_qty": int(df["Recommended Order Qty"].sum()),
    }
