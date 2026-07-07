"""
Tests that verify required sheet names and basic structure.
"""

from config.workbook_config import SHEET_ORDER


def test_sheet_order_count():
    """Workbook spec requires exactly 12 tabs."""
    assert len(SHEET_ORDER) == 12


def test_sheet_names_within_excel_limit():
    """Each sheet name must be 31 characters or fewer."""
    for name in SHEET_ORDER:
        assert len(name) <= 31, f"Sheet name too long: {name}"
