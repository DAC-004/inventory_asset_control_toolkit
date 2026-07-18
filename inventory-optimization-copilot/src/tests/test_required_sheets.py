"""
Tests that verify required sheet names and basic structure.
"""

from config.workbook_config import SHEET_ORDER


def test_sheet_order_count():
    """Inventory v2.0.0 phase 1 includes ten operational tabs."""
    assert len(SHEET_ORDER) == 10


def test_sheet_names_within_excel_limit():
    """Each sheet name must be 31 characters or fewer."""
    for name in SHEET_ORDER:
        assert len(name) <= 31, f"Sheet name too long: {name}"


def test_sheet_order_is_inventory_only():
    """Inventory-only product uses the configured phase-1 tab list."""
    expected = [
        "README",
        "Master Inventory",
        "Inventory Dashboard",
        "Inventory Classification",
        "Aged Excess Analysis",
        "Cycle Count Plan",
        "Replenishment Planning",
        "Markdown Planner",
        "Transfer Planner",
        "Management Summary",
    ]
    assert SHEET_ORDER == expected
