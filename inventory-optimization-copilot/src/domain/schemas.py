"""Inventory record field names and column order."""

from __future__ import annotations

INVENTORY_COLUMN_ORDER = [
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
