"""
Workbook-level configuration: paths, version, sheet order, and business thresholds.

Centralizes constants so data generators, business rules, and sheet builders
stay consistent. Modify values here rather than scattering magic numbers in code.
"""

from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DATA_GENERATED_DIR = PROJECT_ROOT / "data" / "generated"

# ---------------------------------------------------------------------------
# Workbook metadata
# ---------------------------------------------------------------------------

WORKBOOK_TITLE = "Inventory & IT Asset Control Toolkit"
VERSION = "v1.0.0"
AUTHOR = "Daniel A. Cruz"
OUTPUT_FILENAME = "Inventory_IT_Asset_Control_Toolkit.xlsx"
WORKBOOK_PATH = DIST_DIR / OUTPUT_FILENAME

# Backward-compatible alias used by existing imports
WORKBOOK_FILENAME = OUTPUT_FILENAME

# Fixed demo date for deterministic age and renewal calculations
DEMO_REFERENCE_DATE = date(2026, 7, 1)

# Random seed for reproducible fictional sample data
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Required sheet order (Excel limit: 31 characters per name)
# ---------------------------------------------------------------------------

SHEET_ORDER = [
    "README",
    "Master Inventory",
    "Inventory Dashboard",
    "Aged Excess Analysis",
    "Markdown Planner",
    "Transfer Planner",
    "IT Asset Register",
    "Audit Reconciliation",
    "Software Licenses",
    "Mobile Provisioning",
    "Disposal Log",
    "Management Summary",
]

# ---------------------------------------------------------------------------
# Generated CSV filenames (written to data/generated/)
# ---------------------------------------------------------------------------

CSV_FILES = {
    "inventory": "inventory_data.csv",
    "it_assets": "it_asset_data.csv",
    "software": "software_license_data.csv",
    "mobile": "mobile_data.csv",
    "disposal": "disposal_data.csv",
}

# ---------------------------------------------------------------------------
# Sample data row counts (from PRD §8)
# ---------------------------------------------------------------------------

ROW_COUNTS = {
    "inventory": {"min": 80, "max": 150, "default": 120},
    "it_assets": {"min": 80, "max": 150, "default": 120},
    "software": {"min": 15, "max": 30, "default": 22},
    "mobile": {"min": 30, "max": 60, "default": 45},
    "disposal": {"min": 15, "max": 40, "default": 25},
}

# Backward-compatible aliases
INVENTORY_ROW_MIN = ROW_COUNTS["inventory"]["min"]
INVENTORY_ROW_MAX = ROW_COUNTS["inventory"]["max"]
IT_ASSET_ROW_MIN = ROW_COUNTS["it_assets"]["min"]
IT_ASSET_ROW_MAX = ROW_COUNTS["it_assets"]["max"]
SOFTWARE_ROW_MIN = ROW_COUNTS["software"]["min"]
SOFTWARE_ROW_MAX = ROW_COUNTS["software"]["max"]

# ---------------------------------------------------------------------------
# Inventory status thresholds (specs §7.1)
# Applied in order — first matching rule wins
# ---------------------------------------------------------------------------

INVENTORY_THRESHOLDS = {
    # age_days > this AND demand_90_day == 0 → Obsolete
    "obsolete_age_days": 365,
    # quantity_on_hand > max_stock AND age_days > this → Excess / Aged
    "excess_aged_age_days": 180,
    # age_days > this AND sell_through_rate < slow_moving_rate → Slow-Moving
    "slow_moving_age_days": 180,
    # sell_through_rate below this triggers Slow-Moving (15%)
    "slow_moving_sell_through_rate": 0.15,
    # demand at or below this counts as zero demand for obsolete rule
    "zero_demand": 0,
}

# ---------------------------------------------------------------------------
# Markdown planner thresholds (specs §7.2)
# Applied in order — first matching rule wins
# ---------------------------------------------------------------------------

MARKDOWN_THRESHOLDS = {
    # age_days > this AND demand_90_day == 0 → 30% markdown / Liquidate
    "liquidate_age_days": 365,
    "liquidate_markdown_pct": 0.30,
    "liquidate_disposition": "Liquidate",
    # age_days > this → 20% markdown
    "markdown_20_age_days": 270,
    "markdown_20_pct": 0.20,
    "markdown_20_disposition": "20% Markdown",
    # age_days > this → 10% markdown
    "markdown_10_age_days": 180,
    "markdown_10_pct": 0.10,
    "markdown_10_disposition": "10% Markdown",
    # default when no rule matches
    "hold_markdown_pct": 0.00,
    "hold_disposition": "Hold",
}

# ---------------------------------------------------------------------------
# Transfer planner settings (specs §7.3)
# ---------------------------------------------------------------------------

TRANSFER_SETTINGS = {
    # Extra units added to destination need when sizing a transfer
    "destination_demand_buffer": 5,
}

# ---------------------------------------------------------------------------
# Software license renewal thresholds (specs §7.4)
# Applied in order — first matching rule wins
# ---------------------------------------------------------------------------

SOFTWARE_RENEWAL_THRESHOLDS = {
    # days_until_renewal <= this → Renewal Due Soon
    "renewal_due_soon_days": 30,
    # days_until_renewal <= this → Renewal Watch
    "renewal_watch_days": 90,
}

# ---------------------------------------------------------------------------
# Inventory / action label constants (specs §13)
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

COMPLIANCE_STATUSES = [
    "Compliant",
    "Renewal Watch",
    "Renewal Due Soon",
    "Over-Assigned",
]
