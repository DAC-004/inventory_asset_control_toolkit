"""Tests for Inventory Dashboard sheet builder."""

from openpyxl import Workbook

from src.data_generation.generate_inventory import generate_inventory_data
from src.main import generate_all_data
from src.sheets.inventory_dashboard_sheet import build


def test_inventory_dashboard_kpi_sections():
    """Dashboard should render four KPI sections."""
    wb = Workbook()
    ws = wb.active
    data = generate_all_data()
    build(ws, {"data": data})

    values = [
        ws.cell(row=r, column=1).value
        for r in range(1, 24)
        if ws.cell(row=r, column=1).value
    ]
    combined = " ".join(str(v) for v in values)
    assert "Inventory Health" in combined
    assert "Classification & Control" in combined
    assert "Planning & Service" in combined
    assert "Procurement & Network" in combined
    assert ws.cell(row=3, column=1).value == "Total Inventory Value"
    assert str(ws.cell(row=4, column=1).value).startswith("=SUM(")


def test_inventory_dashboard_summary_tables_and_charts():
    """Dashboard should include chart data tables and at least ten charts."""
    wb = Workbook()
    ws = wb.active
    data = generate_all_data()
    build(ws, {"data": data})

    values = [
        ws.cell(row=r, column=1).value
        for r in range(1, ws.max_row + 1)
        if ws.cell(row=r, column=1).value
    ]
    combined = " ".join(str(v) for v in values)
    for label in (
        "Inventory Value by Location",
        "ABC Annual Usage Value",
        "Replenishment Status",
        "Fill Rate by Location",
        "Vendor Risk Distribution",
        "Transfer Net Benefit",
        "Recommended Action Summary",
    ):
        assert label in combined
    assert len(ws._charts) >= 10
    table_names = {t.displayName for t in ws.tables.values()}
    assert any(name.startswith("Dashboard") for name in table_names)


def test_inventory_dashboard_readme_link():
    """Dashboard should link back to README."""
    wb = Workbook()
    ws = wb.active
    build(ws, {"data": generate_all_data()})
    link_cell = ws.cell(row=1, column=10)
    assert link_cell.hyperlink is not None
    assert "README" in link_cell.hyperlink.target


def test_inventory_dashboard_gridlines_hidden():
    """Dashboard should hide gridlines for a clean executive layout."""
    wb = Workbook()
    ws = wb.active
    df = generate_inventory_data(row_count=20, seed=42)
    build(ws, {"data": {"inventory": df}})

    assert ws.sheet_view.showGridLines is False
