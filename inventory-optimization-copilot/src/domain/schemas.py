"""Column orders and workbook views for generated datasets."""

from __future__ import annotations

INVENTORY_COLUMN_ORDER = [
    "inventory_record_id",
    "item_id",
    "sku",
    "product_name",
    "category",
    "subcategory",
    "location_id",
    "location_name",
    "location_type",
    "region",
    "supplier_id",
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
    "last_movement_date",
    "last_sale_date",
    "age_days",
    "demand_90_day",
    "sell_through_rate",
    "gross_margin_pct",
    "total_value",
    "status",
    "recommended_action",
]

# Phase-1 Master Inventory sheet (subset + legacy location alias)
WORKBOOK_INVENTORY_COLUMN_ORDER = [
    "item_id",
    "sku",
    "product_name",
    "category",
    "subcategory",
    "location",
    "location_type",
    "region",
    "quantity_on_hand",
    "min_stock",
    "max_stock",
    "unit_cost",
    "selling_price",
    "total_value",
    "last_movement_date",
    "last_sale_date",
    "age_days",
    "demand_90_day",
    "sell_through_rate",
    "gross_margin_pct",
    "status",
    "recommended_action",
]

INVENTORY_SNAPSHOT_COLUMN_ORDER = [
    "snapshot_id",
    "snapshot_date",
    "sku",
    "location_id",
    "quantity_on_hand",
    "unit_cost",
    "inventory_value",
]

DEMAND_HISTORY_COLUMN_ORDER = [
    "demand_record_id",
    "week_start_date",
    "sku",
    "location_id",
    "units_sold",
    "units_ordered",
    "units_fulfilled",
    "backorder_units",
    "lost_sales_units",
    "promotion_flag",
    "stockout_flag",
    "unit_cost",
    "selling_price",
]

CUSTOMER_ORDER_COLUMN_ORDER = [
    "order_line_id",
    "order_id",
    "order_date",
    "requested_date",
    "fulfilled_date",
    "customer_segment",
    "sku",
    "location_id",
    "ordered_units",
    "fulfilled_units",
    "backordered_units",
    "line_status",
]

CYCLE_COUNT_COLUMN_ORDER = [
    "count_id",
    "sku",
    "location_id",
    "scheduled_date",
    "count_date",
    "system_quantity",
    "physical_quantity",
    "variance_units",
    "variance_value",
    "count_status",
    "counter_name",
    "review_status",
    "root_cause",
]

SUPPLIER_COLUMN_ORDER = [
    "supplier_id",
    "supplier_name",
    "supplier_category",
    "default_lead_time_days",
    "minimum_order_value",
    "payment_terms",
    "active_status",
    "quality_rating",
    "responsiveness_rating",
    "administrative_compliance_rating",
]

PURCHASE_ORDER_COLUMN_ORDER = [
    "po_line_id",
    "po_number",
    "supplier_id",
    "sku",
    "location_id",
    "buyer",
    "order_date",
    "approval_date",
    "promised_date",
    "expected_date",
    "ordered_quantity",
    "unit_cost",
    "extended_cost",
    "case_pack",
    "minimum_order_quantity",
    "po_status",
]

PURCHASE_ORDER_RECEIPT_COLUMN_ORDER = [
    "receipt_id",
    "po_line_id",
    "receipt_date",
    "received_quantity",
    "accepted_quantity",
    "rejected_quantity",
    "receipt_status",
    "quality_issue",
]

ALL_DATASET_COLUMNS: dict[str, list[str]] = {
    "inventory": INVENTORY_COLUMN_ORDER,
    "inventory_snapshots": INVENTORY_SNAPSHOT_COLUMN_ORDER,
    "demand_history": DEMAND_HISTORY_COLUMN_ORDER,
    "customer_orders": CUSTOMER_ORDER_COLUMN_ORDER,
    "cycle_counts": CYCLE_COUNT_COLUMN_ORDER,
    "suppliers": SUPPLIER_COLUMN_ORDER,
    "purchase_orders": PURCHASE_ORDER_COLUMN_ORDER,
    "purchase_order_receipts": PURCHASE_ORDER_RECEIPT_COLUMN_ORDER,
}

REQUIRED_CSV_FILES = [
    "inventory_data.csv",
    "inventory_snapshots.csv",
    "demand_history.csv",
    "customer_orders.csv",
    "cycle_counts.csv",
    "suppliers.csv",
    "purchase_orders.csv",
    "purchase_order_receipts.csv",
]
