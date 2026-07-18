"""
Tests that verify required sheet names and basic structure.
"""

from config.workbook_config import SHEET_ORDER


def test_sheet_order_count():
    """Inventory v2.0.0 phase 1 includes seven operational tabs."""
    assert len(SHEET_ORDER) == 7


def test_sheet_names_within_excel_limit():
    """Each sheet name must be 31 characters or fewer."""
    for name in SHEET_ORDER:
        assert len(name) <= 31, f"Sheet name too long: {name}"


def test_no_it_sheets_in_order():
    """Inventory-only product must not reference IT tabs."""
    forbidden = {
        "IT Asset Register",
        "Audit Reconciliation",
        "Software Licenses",
        "Mobile Provisioning",
        "Disposal Log",
    }
    assert forbidden.isdisjoint(set(SHEET_ORDER))
