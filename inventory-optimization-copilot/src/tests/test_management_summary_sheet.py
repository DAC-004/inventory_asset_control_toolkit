"""Tests for Management Summary sheet builder."""

from openpyxl import Workbook

from src.data_generation.generate_inventory import generate_inventory_data
from src.main import generate_all_data
from src.services.summary_service import (
    build_management_summary_context,
    top_inventory_risks,
)
from src.sheets.management_summary_sheet import (
    KPI1_VALUE_ROW,
    RISK_DATA_START_ROW,
    SECTION1_ROW,
    SECTION8_ROW,
    build,
)


def test_top_inventory_risk_helper_returns_rows():
    inventory = generate_inventory_data(row_count=120, seed=42)
    inv_risks = top_inventory_risks(inventory)
    assert 1 <= len(inv_risks) <= 5
    assert "SKU" in inv_risks[0]


def test_management_summary_context():
    """Executive context should aggregate cross-module metrics."""
    ctx = build_management_summary_context(generate_all_data())
    assert ctx["total_value"] >= 0
    assert "planning" in ctx
    assert "procurement" in ctx
    assert isinstance(ctx["action_summary"], list)


def test_management_summary_sheet_structure():
    """Sheet should include executive sections and print settings."""
    wb = Workbook()
    ws = wb.active
    data = generate_all_data()
    build(ws, {"data": data})

    assert "Inventory Health" in str(ws.cell(row=SECTION1_ROW, column=1).value)
    assert "Transfer & Markdown" in str(ws.cell(row=SECTION1_ROW + 16, column=1).value)
    assert "30 / 60 / 90" in str(ws.cell(row=SECTION8_ROW, column=1).value)
    assert ws.cell(row=KPI1_VALUE_ROW, column=1).value is not None
    assert ws.cell(row=RISK_DATA_START_ROW, column=1).value
    assert ws.sheet_view.showGridLines is False
    assert ws.page_setup.orientation == ws.ORIENTATION_LANDSCAPE
    assert ws.cell(row=1, column=10).hyperlink is not None
