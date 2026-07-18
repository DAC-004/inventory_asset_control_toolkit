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
