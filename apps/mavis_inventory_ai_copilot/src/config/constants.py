"""Application constants and business thresholds."""

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = APP_ROOT.parents[1]
TOOLKIT_ROOT = REPO_ROOT / "inventory-it-asset-toolkit"

REQUIRED_COLUMNS = [
    "sku",
    "product_name",
    "category",
    "location",
    "location_type",
    "region",
    "on_hand_qty",
    "min_stock",
    "max_stock",
    "unit_cost",
    "retail_price",
    "inventory_age_days",
    "demand_90_day",
    "avg_weekly_sales",
    "discontinued_flag",
    "transfer_cost_per_unit",
]

COLUMN_ALIASES: dict[str, str] = {
    "quantity_on_hand": "on_hand_qty",
    "selling_price": "retail_price",
    "age_days": "inventory_age_days",
    "90_day_demand": "demand_90_day",
    "item_id": "item_id",
}

EXCEL_SHEET_CANDIDATES = [
    "Master Inventory",
    "Inventory Master",
    "Master_Inventory",
]

AGED_THRESHOLD_DAYS = 180
OBSOLETE_AGE_DAYS = 365
OBSOLETE_DEMAND_AGE_DAYS = 240
SLOW_MOVING_DOS_THRESHOLD = 120
SLOW_MOVING_SELL_THROUGH_THRESHOLD = 0.25
STOCKOUT_DOS_THRESHOLD = 30
DAYS_OF_SUPPLY_CAP = 999

HIGH_VALUE_THRESHOLD = 10_000
MEDIUM_VALUE_THRESHOLD = 5_000

HIGH_NET_BENEFIT_THRESHOLD = 5_000
MEDIUM_NET_BENEFIT_THRESHOLD = 1_000

DEFAULT_TRANSFER_COST_PER_UNIT = 2.50

ISSUE_TYPE_PRIORITY = [
    "Obsolete",
    "Excess/Aged",
    "Stockout Risk",
    "Excess",
    "Slow-Moving",
    "Aged",
    "Healthy",
]

RISK_COLORS = {
    "High": "#DC2626",
    "Medium": "#D97706",
    "Low": "#059669",
    "Neutral": "#2563EB",
}

AGING_BUCKETS = [
    (0, 90, "0-90 days"),
    (91, 180, "91-180 days"),
    (181, 270, "181-270 days"),
    (271, 365, "271-365 days"),
    (366, 10_000, "365+ days"),
]

PAGE_LABELS = [
    "Executive Dashboard",
    "Aged & Excess",
    "Transfer Planner",
    "Markdown Planner",
    "AI Summary",
    "Data Quality",
    "Methodology",
]
