"""
Workbook-level configuration: paths, version, sheet order, and business thresholds.

Centralizes constants so data generators, business rules, and sheet builders
stay consistent. Modify values here rather than scattering magic numbers in code.
"""

from datetime import date
from pathlib import Path
from typing import TypedDict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DATA_GENERATED_DIR = PROJECT_ROOT / "data" / "generated"

# ---------------------------------------------------------------------------
# Workbook metadata
# ---------------------------------------------------------------------------

WORKBOOK_TITLE = "Inventory Optimization Copilot"
VERSION = "v2.0.0"
AUTHOR = "Daniel A. Cruz"
OUTPUT_FILENAME = "Inventory_Optimization_Copilot.xlsx"
WORKBOOK_PATH = DIST_DIR / OUTPUT_FILENAME

# Backward-compatible alias used by existing imports
WORKBOOK_FILENAME = OUTPUT_FILENAME

# Fixed as-of date for deterministic age and planning calculations
AS_OF_DATE = date(2026, 7, 1)
DEMO_REFERENCE_DATE = AS_OF_DATE

# Random seed for reproducible fictional sample data
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# ABC classification thresholds (Prompt 04)
# Cumulative usage value %: A <= ABC_A, B <= ABC_B, else C.
# Boundary: SKU at exactly threshold pct receives that class (inclusive upper bound).
# ---------------------------------------------------------------------------

ABC_A_THRESHOLD = 0.80
ABC_B_THRESHOLD = 0.95

CYCLE_COUNT_FREQUENCY = {
    "A": "Monthly",
    "B": "Quarterly",
    "C": "Semiannually",
}

# ---------------------------------------------------------------------------
# Service level targets and Z-scores (Prompt 05)
# ---------------------------------------------------------------------------

SERVICE_LEVEL_TARGETS = {
    "A": 0.99,
    "B": 0.95,
    "C": 0.90,
}

SERVICE_LEVEL_Z_SCORES = {
    "A": 2.326,
    "B": 1.645,
    "C": 1.282,
}

GLOBAL_LEAD_TIME_FALLBACK_DAYS = 14
ORDERING_COST = 75.0
HOLDING_COST_PCT = 0.25
MIN_LEAD_TIME_SAMPLES_ADVANCED = 5
MIN_WEEKS_FOR_ADVANCED_SAFETY_STOCK = 8

OPEN_PO_STATUSES = [
    "Approved",
    "Open",
    "Partially Received",
    "Late",
]

# ---------------------------------------------------------------------------
# Demand forecast parameters (Prompt 06)
# Primary method selection metric: lowest WAPE on holdout window.
# ---------------------------------------------------------------------------

FORECAST_HOLDOUT_WEEKS = 8
FORECAST_PRIMARY_METRIC = "WAPE"
FORECAST_SES_ALPHA = 0.30
FORECAST_WMA_WEIGHTS = [0.40, 0.30, 0.20, 0.10]
FORECAST_MA_WINDOW = 4
FORECAST_BLEND_FORECAST_WEIGHT = 0.60
FORECAST_DEMO_CHART_SKU_COUNT = 3

DEFAULT_SERVICE_LEVEL_TARGET = 0.95
SERVICE_LEVEL_WATCH_GAP = 0.02
SERVICE_LEVEL_BELOW_TARGET_GAP = 0.05

# ---------------------------------------------------------------------------
# Vendor scorecard weights (Prompt 07) — must sum to 100%
# ---------------------------------------------------------------------------

VENDOR_SCORE_WEIGHTS = {
    "otif": 0.35,
    "quality": 0.20,
    "lead_time_consistency": 0.15,
    "price_performance": 0.15,
    "responsiveness": 0.10,
    "administrative_compliance": 0.05,
}

MIN_VENDOR_PO_SAMPLES = 3
VENDOR_RISK_PREFERRED_MIN = 90
VENDOR_RISK_APPROVED_MIN = 75
VENDOR_RISK_WATCH_MIN = 60

PO_OPEN_SUPPLY_STATUSES = [
    "Approved",
    "Open",
    "Partially Received",
    "Late",
    "Quality Hold",
]

# ---------------------------------------------------------------------------
# Required sheet order (Excel limit: 31 characters per name)
# Prompts 04–09 will add: Inventory Classification, Cycle Count Plan,
# Replenishment Planning, Demand Forecast, Service Level Analysis,
# Purchase Order Tracker, Vendor Scorecards (between Transfer and Summary).
# ---------------------------------------------------------------------------

SHEET_ORDER = [
    "README",
    "Master Inventory",
    "Inventory Dashboard",
    "Inventory Classification",
    "Aged Excess Analysis",
    "Cycle Count Plan",
    "Replenishment Planning",
    "Demand Forecast",
    "Service Level Analysis",
    "Purchase Order Tracker",
    "Vendor Scorecards",
    "Markdown Planner",
    "Transfer Planner",
    "Management Summary",
]

# ---------------------------------------------------------------------------
# Generated CSV filenames (written to data/generated/)
# ---------------------------------------------------------------------------

CSV_FILES = {
    "inventory": "inventory_data.csv",
    "inventory_snapshots": "inventory_snapshots.csv",
    "demand_history": "demand_history.csv",
    "customer_orders": "customer_orders.csv",
    "cycle_counts": "cycle_counts.csv",
    "suppliers": "suppliers.csv",
    "purchase_orders": "purchase_orders.csv",
    "purchase_order_receipts": "purchase_order_receipts.csv",
}

# ---------------------------------------------------------------------------
# Sample data row counts
# ---------------------------------------------------------------------------

ROW_COUNTS = {
    "inventory": {"min": 80, "max": 150, "default": 120},
}

# Backward-compatible aliases
INVENTORY_ROW_MIN = ROW_COUNTS["inventory"]["min"]
INVENTORY_ROW_MAX = ROW_COUNTS["inventory"]["max"]

# ---------------------------------------------------------------------------
# Inventory status thresholds (specs §7.1)
# Applied in order — first matching rule wins
# ---------------------------------------------------------------------------

INVENTORY_THRESHOLDS = {
    "obsolete_age_days": 365,
    "excess_aged_age_days": 180,
    "slow_moving_age_days": 180,
    "slow_moving_sell_through_rate": 0.15,
    "zero_demand": 0,
}

# ---------------------------------------------------------------------------
# Markdown planner thresholds (specs §7.2)
# ---------------------------------------------------------------------------


class MarkdownThresholds(TypedDict):
    liquidate_age_days: int
    liquidate_markdown_pct: float
    liquidate_disposition: str
    markdown_20_age_days: int
    markdown_20_pct: float
    markdown_20_disposition: str
    markdown_10_age_days: int
    markdown_10_pct: float
    markdown_10_disposition: str
    hold_markdown_pct: float
    hold_disposition: str


MARKDOWN_THRESHOLDS: MarkdownThresholds = {
    "liquidate_age_days": 365,
    "liquidate_markdown_pct": 0.30,
    "liquidate_disposition": "Liquidate",
    "markdown_20_age_days": 270,
    "markdown_20_pct": 0.20,
    "markdown_20_disposition": "20% Markdown",
    "markdown_10_age_days": 180,
    "markdown_10_pct": 0.10,
    "markdown_10_disposition": "10% Markdown",
    "hold_markdown_pct": 0.00,
    "hold_disposition": "Hold",
}

# ---------------------------------------------------------------------------
# Transfer planner settings (specs §7.3)
# ---------------------------------------------------------------------------

TRANSFER_SETTINGS = {
    "destination_demand_buffer": 5,
}

# ---------------------------------------------------------------------------
# Network transfer settings (Prompt 08)
# ---------------------------------------------------------------------------

TRANSFER_MAX_LEAD_TIME_DAYS = 7
TRANSFER_SOURCE_RISK_RATE = 0.05
TRANSFER_PURCHASE_MARKUP = 0.05
TRANSFER_ORDERING_COST = 75.0
TRANSFER_MIN_NET_BENEFIT = 0.0
TRANSFER_MARGIN_RATE = 0.35
TRANSFER_EMERGENCY_BACKORDER_OVERRIDE = True

MARKDOWN_CARRYING_COST_PCT = 0.25

# ---------------------------------------------------------------------------
# Inventory / action label constants
# ---------------------------------------------------------------------------

INVENTORY_STATUSES = [
    "Healthy",
    "Stockout Risk",
    "Excess",
    "Slow-Moving",
    "Excess / Aged",
    "Obsolete",
]

RECOMMENDED_ACTIONS = [
    "Monitor",
    "Replenish",
    "Review Transfer",
    "Transfer or Markdown",
    "Markdown Review",
    "Liquidate",
]
