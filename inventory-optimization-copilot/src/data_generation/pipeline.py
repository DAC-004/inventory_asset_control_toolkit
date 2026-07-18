"""
Deterministic data generation pipeline for inventory planning datasets.

Generates all CSV files under data/generated/ with referential integrity.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from config.workbook_config import (
    AS_OF_DATE,
    CSV_FILES,
    DATA_GENERATED_DIR,
    ROW_COUNTS,
)
from src.domain.catalog import (
    BUYERS,
    COUNTER_NAMES,
    CUSTOMER_SEGMENTS,
    DEMAND_PATTERNS,
    LOCATIONS,
    PAYMENT_TERMS,
    PO_STATUSES,
    PRODUCT_CATALOG,
    STATUS_SCENARIOS,
    SUPPLIER_TEMPLATES,
)
from src.domain.rng import SeededRNG
from src.domain.schemas import (
    CUSTOMER_ORDER_COLUMN_ORDER,
    CYCLE_COUNT_COLUMN_ORDER,
    DEMAND_HISTORY_COLUMN_ORDER,
    INVENTORY_COLUMN_ORDER,
    INVENTORY_SNAPSHOT_COLUMN_ORDER,
    PURCHASE_ORDER_COLUMN_ORDER,
    PURCHASE_ORDER_RECEIPT_COLUMN_ORDER,
    SUPPLIER_COLUMN_ORDER,
)
from src.domain.validation import validate_all_datasets
from src.services.inventory_metrics import (
    assign_status_and_action,
    calc_gross_margin_pct,
    calc_sell_through_rate,
)


def _month_end_dates(reference: date, months: int) -> list[date]:
    """Return month-end dates for the prior ``months`` including reference month."""
    dates: list[date] = []
    year, month = reference.year, reference.month
    for _ in range(months):
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        dates.append(next_month - timedelta(days=1))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(dates))


def _week_starts(reference: date, weeks: int) -> list[date]:
    """Return Monday week-start dates ending at the week containing reference."""
    anchor = reference - timedelta(days=reference.weekday())
    return [anchor - timedelta(weeks=offset) for offset in range(weeks - 1, -1, -1)]


def _sku_for_product_index(index: int, category: str) -> str:
    prefix = "".join(word[0] for word in category.split())[:2].upper()
    return f"{prefix}-{1000 + index:04d}"


def _supplier_for_category(category: str) -> str:
    for supplier_id, _, supplier_cat in SUPPLIER_TEMPLATES:
        if supplier_cat == category:
            return supplier_id
    return "SUP-010"


def generate_suppliers(rng: SeededRNG) -> pd.DataFrame:
    rows = []
    for supplier_id, name, category in SUPPLIER_TEMPLATES:
        base = rng.pattern_index(supplier_id, 7)
        rows.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": name,
                "supplier_category": category,
                "default_lead_time_days": 7 + base * 3,
                "minimum_order_value": round(500 + base * 250, 2),
                "payment_terms": PAYMENT_TERMS[base % len(PAYMENT_TERMS)],
                "active_status": "Active" if base != 6 else "On Watch",
                "quality_rating": round(3.2 + (base % 4) * 0.4, 1),
                "responsiveness_rating": round(3.0 + (base % 5) * 0.35, 1),
                "administrative_compliance_rating": round(3.5 + (base % 3) * 0.5, 1),
            }
        )
    return pd.DataFrame(rows, columns=SUPPLIER_COLUMN_ORDER)


def _build_inventory_record(
    record_index: int,
    product_idx: int,
    location: tuple[str, str, str, str],
    qty: int,
    min_stock: int,
    max_stock: int,
    age_days: int,
    demand_90_day: int,
    reference: date,
    rng: SeededRNG,
) -> dict:
    category, subcategory, product_name, base_cost, supplier_cat = PRODUCT_CATALOG[
        product_idx
    ]
    location_id, location_name, location_type, region = location
    unit_cost = round(base_cost * rng.uniform(0.95, 1.05), 2)
    selling_price = round(unit_cost * rng.uniform(1.35, 1.65), 2)
    target_stock = min_stock + int((max_stock - min_stock) * 0.55)
    case_pack = int(rng.python.choice([1, 2, 4, 6, 12]))
    moq = case_pack * rng.randint(1, 4)
    storage_capacity = max(max_stock * 3, qty + rng.randint(20, 80))
    allocated = min(qty, rng.randint(0, max(1, qty // 4)))
    backorder = max(0, rng.randint(0, 3) - qty // 10) if qty < min_stock else 0
    last_movement = reference - timedelta(days=age_days)
    sale_offset = rng.randint(0, min(14, age_days))
    last_sale = reference - timedelta(days=max(0, age_days - sale_offset))
    sell_through = calc_sell_through_rate(qty, demand_90_day)
    margin = calc_gross_margin_pct(unit_cost, selling_price)
    status, action = assign_status_and_action(
        qty, min_stock, max_stock, age_days, demand_90_day, sell_through
    )
    sku = _sku_for_product_index(product_idx + 1, category)
    record_id = f"INV-{record_index:05d}"
    return {
        "inventory_record_id": record_id,
        "item_id": record_id,
        "sku": sku,
        "product_name": product_name,
        "category": category,
        "subcategory": subcategory,
        "location_id": location_id,
        "location_name": location_name,
        "location_type": location_type,
        "region": region,
        "supplier_id": _supplier_for_category(supplier_cat),
        "quantity_on_hand": qty,
        "quantity_allocated": allocated,
        "backorder_quantity": backorder,
        "min_stock": min_stock,
        "max_stock": max_stock,
        "target_stock": target_stock,
        "unit_cost": unit_cost,
        "selling_price": selling_price,
        "case_pack": case_pack,
        "minimum_order_quantity": moq,
        "storage_capacity_units": storage_capacity,
        "last_movement_date": last_movement,
        "last_sale_date": last_sale,
        "age_days": age_days,
        "demand_90_day": demand_90_day,
        "sell_through_rate": sell_through,
        "gross_margin_pct": margin,
        "total_value": round(qty * unit_cost, 2),
        "status": status,
        "recommended_action": action,
    }


def generate_inventory(rng: SeededRNG, row_count: int | None = None) -> pd.DataFrame:
    row_count = row_count or ROW_COUNTS["inventory"]["default"]
    reference = AS_OF_DATE
    records: list[dict] = []
    used_pairs: set[tuple[int, str]] = set()

    for i, scenario in enumerate(STATUS_SCENARIOS, start=1):
        product_idx = (i - 1) % len(PRODUCT_CATALOG)
        location = LOCATIONS[(i - 1) % len(LOCATIONS)]
        used_pairs.add((product_idx, location[0]))
        records.append(
            _build_inventory_record(
                i,
                product_idx,
                location,
                scenario["quantity_on_hand"],
                scenario["min_stock"],
                scenario["max_stock"],
                scenario["age_days"],
                scenario["demand_90_day"],
                reference,
                rng,
            )
        )

    idx = len(STATUS_SCENARIOS) + 1
    while len(records) < row_count:
        product_idx = rng.randint(0, len(PRODUCT_CATALOG) - 1)
        location = LOCATIONS[rng.randint(0, len(LOCATIONS) - 1)]
        pair = (product_idx, location[0])
        if pair in used_pairs:
            continue
        used_pairs.add(pair)
        min_stock = rng.randint(8, 20)
        max_stock = min_stock + rng.randint(15, 45)
        qty = rng.randint(0, max_stock + 35)
        age_days = rng.randint(5, 420)
        demand_90 = rng.randint(0, 35)
        records.append(
            _build_inventory_record(
                idx,
                product_idx,
                location,
                qty,
                min_stock,
                max_stock,
                age_days,
                demand_90,
                reference,
                rng,
            )
        )
        idx += 1

    df = pd.DataFrame(records, columns=INVENTORY_COLUMN_ORDER)
    for row_idx in df.index:
        row = df.loc[row_idx]
        status, action = assign_status_and_action(
            int(row["quantity_on_hand"]),
            int(row["min_stock"]),
            int(row["max_stock"]),
            int(row["age_days"]),
            int(row["demand_90_day"]),
            float(row["sell_through_rate"]),
        )
        df.at[row_idx, "status"] = status
        df.at[row_idx, "recommended_action"] = action
    df["location"] = df["location_name"]
    return df


def generate_purchase_orders(inventory: pd.DataFrame, rng: SeededRNG) -> pd.DataFrame:
    rows: list[dict] = []
    po_counter = 1000
    line_counter = 1
    status_cycle = PO_STATUSES * 3
    rng.shuffle(status_cycle)

    sample = inventory.sample(n=min(90, len(inventory)), random_state=rng.seed)
    for _, inv in sample.iterrows():
        status = status_cycle[line_counter % len(status_cycle)]
        order_date = AS_OF_DATE - timedelta(days=rng.randint(5, 120))
        approval = (
            order_date + timedelta(days=rng.randint(0, 3))
            if status not in ("Draft",)
            else pd.NaT
        )
        lead = rng.randint(7, 28)
        promised = order_date + timedelta(days=lead)
        expected = promised + timedelta(days=rng.randint(0, 5))
        if status == "Late":
            expected = AS_OF_DATE - timedelta(days=rng.randint(1, 10))
        qty = max(
            int(inv["minimum_order_quantity"]),
            int(inv["case_pack"]) * rng.randint(2, 12),
        )
        unit_cost = float(inv["unit_cost"])
        rows.append(
            {
                "po_line_id": f"POL-{line_counter:05d}",
                "po_number": f"PO-{po_counter:05d}",
                "supplier_id": inv["supplier_id"],
                "sku": inv["sku"],
                "location_id": inv["location_id"],
                "buyer": BUYERS[line_counter % len(BUYERS)],
                "order_date": order_date,
                "approval_date": approval,
                "promised_date": promised,
                "expected_date": expected,
                "ordered_quantity": qty,
                "unit_cost": unit_cost,
                "extended_cost": round(qty * unit_cost, 2),
                "case_pack": int(inv["case_pack"]),
                "minimum_order_quantity": int(inv["minimum_order_quantity"]),
                "po_status": status,
            }
        )
        if line_counter % 3 == 0:
            po_counter += 1
        line_counter += 1

    return pd.DataFrame(rows, columns=PURCHASE_ORDER_COLUMN_ORDER)


def generate_receipts(purchase_orders: pd.DataFrame, rng: SeededRNG) -> pd.DataFrame:
    rows: list[dict] = []
    receipt_counter = 1
    receivable = purchase_orders[
        purchase_orders["po_status"].isin(
            ["Partially Received", "Received", "Late", "Closed"]
        )
    ]

    for _, po in receivable.iterrows():
        if po["po_status"] == "Cancelled":
            continue
        ordered = int(po["ordered_quantity"])
        if po["po_status"] == "Partially Received":
            received = max(1, ordered // 2)
            status = "Partial"
            rejected = rng.randint(0, 2)
            quality = "Minor packaging damage" if rejected else ""
        elif po["po_status"] == "Late":
            received = ordered
            status = "Late"
            rejected = 0
            quality = ""
        elif po["po_status"] == "Received" and receipt_counter % 11 == 0:
            received = ordered
            rejected = rng.randint(1, 4)
            status = "Rejected" if rejected == ordered else "Quality Hold"
            quality = "Failed inspection"
        else:
            received = ordered
            rejected = 0
            status = "Complete"
            quality = ""

        accepted = received - rejected
        lead_days = max(7, (po["promised_date"] - po["order_date"]).days)
        receipt_date = po["order_date"] + timedelta(days=lead_days + rng.randint(0, 5))
        rows.append(
            {
                "receipt_id": f"RCV-{receipt_counter:05d}",
                "po_line_id": po["po_line_id"],
                "receipt_date": receipt_date,
                "received_quantity": received,
                "accepted_quantity": accepted,
                "rejected_quantity": rejected,
                "receipt_status": status,
                "quality_issue": quality,
            }
        )
        receipt_counter += 1

    return pd.DataFrame(rows, columns=PURCHASE_ORDER_RECEIPT_COLUMN_ORDER)


def _weekly_demand_units(
    pattern: str, week_index: int, base: int, rng: SeededRNG
) -> int:
    if pattern == "no_recent_demand":
        return 0 if week_index > 40 else max(0, base // 10)
    if pattern == "stable":
        return max(0, base + rng.randint(-2, 2))
    if pattern == "trending":
        return max(0, base + week_index // 4)
    if pattern == "seasonal":
        seasonal = int(abs((week_index % 26) - 13) * 0.4)
        return max(0, base + seasonal)
    if pattern == "intermittent":
        return base if week_index % 3 == 0 else 0
    if pattern == "promotional":
        return base * 2 if week_index in (20, 21, 44, 45) else max(0, base - 1)
    if pattern == "stockout_constrained":
        return base * 2 if week_index < 10 else max(0, base // 3)
    return max(0, base)


def generate_demand_history(inventory: pd.DataFrame, rng: SeededRNG) -> pd.DataFrame:
    weeks = _week_starts(AS_OF_DATE, 52)
    rows: list[dict] = []
    record_counter = 1
    demand_skus = inventory.head(min(90, len(inventory)))

    for _, inv in demand_skus.iterrows():
        key = f"{inv['sku']}|{inv['location_id']}"
        pattern = DEMAND_PATTERNS[rng.pattern_index(key, len(DEMAND_PATTERNS))]
        base = max(1, int(inv["demand_90_day"]) // 13)
        for week_index, week_start in enumerate(weeks):
            units_sold = _weekly_demand_units(pattern, week_index, base, rng)
            promo = pattern == "promotional" and week_index in (20, 21, 44, 45)
            stockout = pattern == "stockout_constrained" and week_index >= 10
            units_ordered = units_sold + (2 if stockout else 0)
            fulfilled = 0 if stockout else units_sold
            backorder = units_ordered - fulfilled if stockout else 0
            lost = backorder
            rows.append(
                {
                    "demand_record_id": f"DM-{record_counter:06d}",
                    "week_start_date": week_start,
                    "sku": inv["sku"],
                    "location_id": inv["location_id"],
                    "units_sold": units_sold,
                    "units_ordered": units_ordered,
                    "units_fulfilled": fulfilled,
                    "backorder_units": backorder,
                    "lost_sales_units": lost,
                    "promotion_flag": "Yes" if promo else "No",
                    "stockout_flag": "Yes" if stockout else "No",
                    "unit_cost": float(inv["unit_cost"]),
                    "selling_price": float(inv["selling_price"]),
                }
            )
            record_counter += 1

    return pd.DataFrame(rows, columns=DEMAND_HISTORY_COLUMN_ORDER)


def generate_customer_orders(demand: pd.DataFrame, rng: SeededRNG) -> pd.DataFrame:
    rows: list[dict] = []
    line_counter = 1
    order_counter = 5000
    sample = demand[demand["units_ordered"] > 0].sample(
        n=min(220, len(demand)), random_state=rng.seed
    )

    for _, dmd in sample.iterrows():
        ordered = int(dmd["units_ordered"])
        fulfilled = int(dmd["units_fulfilled"])
        backordered = ordered - fulfilled
        order_date = dmd["week_start_date"] + timedelta(days=rng.randint(0, 4))
        requested = order_date + timedelta(days=rng.randint(1, 7))
        fulfilled_date = requested if fulfilled == ordered else pd.NaT
        if backordered > 0:
            line_status = "Partially Fulfilled"
        elif fulfilled == 0:
            line_status = "Backordered"
        else:
            line_status = "Fulfilled"

        rows.append(
            {
                "order_line_id": f"OL-{line_counter:06d}",
                "order_id": f"ORD-{order_counter:05d}",
                "order_date": order_date,
                "requested_date": requested,
                "fulfilled_date": fulfilled_date,
                "customer_segment": CUSTOMER_SEGMENTS[
                    line_counter % len(CUSTOMER_SEGMENTS)
                ],
                "sku": dmd["sku"],
                "location_id": dmd["location_id"],
                "ordered_units": ordered,
                "fulfilled_units": fulfilled,
                "backordered_units": backordered,
                "line_status": line_status,
            }
        )
        if line_counter % 2 == 0:
            order_counter += 1
        line_counter += 1

    return pd.DataFrame(rows, columns=CUSTOMER_ORDER_COLUMN_ORDER)


def generate_inventory_snapshots(inventory: pd.DataFrame) -> pd.DataFrame:
    month_ends = _month_end_dates(AS_OF_DATE, 12)
    rows: list[dict] = []
    snap_counter = 1
    for snap_date in month_ends:
        months_from_asof = (AS_OF_DATE.year - snap_date.year) * 12 + (
            AS_OF_DATE.month - snap_date.month
        )
        drift_factor = 1.0 - (months_from_asof * 0.015)
        for _, inv in inventory.iterrows():
            qty = max(
                0,
                int(round(float(inv["quantity_on_hand"]) * drift_factor)),
            )
            cost = float(inv["unit_cost"])
            rows.append(
                {
                    "snapshot_id": f"SNAP-{snap_counter:06d}",
                    "snapshot_date": snap_date,
                    "sku": inv["sku"],
                    "location_id": inv["location_id"],
                    "quantity_on_hand": qty,
                    "unit_cost": cost,
                    "inventory_value": round(qty * cost, 2),
                }
            )
            snap_counter += 1
    return pd.DataFrame(rows, columns=INVENTORY_SNAPSHOT_COLUMN_ORDER)


def generate_cycle_counts(inventory: pd.DataFrame, rng: SeededRNG) -> pd.DataFrame:
    rows: list[dict] = []
    scenarios = [
        ("exact", 0, "Completed", "Approved", ""),
        ("positive", 3, "Completed", "Approved", "Receiving error"),
        ("negative", -4, "Completed", "Approved", "Shrinkage suspected"),
        ("overdue", 0, "Overdue", "Pending Review", ""),
        ("recount", 2, "Recount Required", "Escalated", "Large variance"),
        ("missed", 0, "Missed", "Rejected", "Counter unavailable"),
    ]
    sample = inventory.sample(n=min(60, len(inventory)), random_state=rng.seed + 1)
    count_counter = 1

    for idx, (_, inv) in enumerate(sample.iterrows()):
        scenario = scenarios[idx % len(scenarios)]
        _, variance_adj, count_status, review_status, root_cause = scenario
        system_qty = int(inv["quantity_on_hand"])
        scheduled = AS_OF_DATE - timedelta(days=rng.randint(5, 45))
        if count_status == "Overdue":
            count_date = pd.NaT
        elif count_status == "Missed":
            count_date = pd.NaT
        else:
            count_date = scheduled + timedelta(days=rng.randint(0, 5))
        physical = system_qty + variance_adj
        variance = physical - system_qty
        rows.append(
            {
                "count_id": f"CC-{count_counter:05d}",
                "sku": inv["sku"],
                "location_id": inv["location_id"],
                "scheduled_date": scheduled,
                "count_date": count_date,
                "system_quantity": system_qty,
                "physical_quantity": physical,
                "variance_units": variance,
                "variance_value": round(variance * float(inv["unit_cost"]), 2),
                "count_status": count_status,
                "counter_name": COUNTER_NAMES[count_counter % len(COUNTER_NAMES)],
                "review_status": review_status,
                "root_cause": root_cause,
            }
        )
        count_counter += 1

    return pd.DataFrame(rows, columns=CYCLE_COUNT_COLUMN_ORDER)


def generate_all_datasets(
    seed: int | None = None,
    row_count: int | None = None,
    validate: bool = True,
) -> dict[str, pd.DataFrame]:
    """Generate all planning datasets with deterministic seeding."""
    rng = SeededRNG.create(seed)
    suppliers = generate_suppliers(rng)
    inventory = generate_inventory(rng, row_count=row_count)
    purchase_orders = generate_purchase_orders(inventory, rng)
    receipts = generate_receipts(purchase_orders, rng)
    demand_history = generate_demand_history(inventory, rng)
    customer_orders = generate_customer_orders(demand_history, rng)
    snapshots = generate_inventory_snapshots(inventory)
    cycle_counts = generate_cycle_counts(inventory, rng)

    datasets = {
        "suppliers": suppliers,
        "inventory": inventory,
        "purchase_orders": purchase_orders,
        "purchase_order_receipts": receipts,
        "demand_history": demand_history,
        "customer_orders": customer_orders,
        "inventory_snapshots": snapshots,
        "cycle_counts": cycle_counts,
    }
    if validate:
        validate_all_datasets(datasets)
    return datasets


def save_all_datasets(
    datasets: dict[str, pd.DataFrame],
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Write all datasets to CSV files."""
    output_dir = output_dir or DATA_GENERATED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    file_map = {
        "inventory": CSV_FILES["inventory"],
        "inventory_snapshots": CSV_FILES["inventory_snapshots"],
        "demand_history": CSV_FILES["demand_history"],
        "customer_orders": CSV_FILES["customer_orders"],
        "cycle_counts": CSV_FILES["cycle_counts"],
        "suppliers": CSV_FILES["suppliers"],
        "purchase_orders": CSV_FILES["purchase_orders"],
        "purchase_order_receipts": CSV_FILES["purchase_order_receipts"],
    }
    paths: dict[str, Path] = {}
    for key, filename in file_map.items():
        path = output_dir / filename
        datasets[key].to_csv(path, index=False, date_format="%Y-%m-%d")
        paths[key] = path
    return paths
