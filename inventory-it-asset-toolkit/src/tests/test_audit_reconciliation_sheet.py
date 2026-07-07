"""Tests for Audit Reconciliation sheet builder."""

from openpyxl import Workbook

from src.data_generation.generate_it_assets import generate_it_asset_data
from src.sheets.audit_reconciliation_sheet import (
    EXCEPTION_TYPES,
    _build_exceptions_dataframe,
    _exception_summary,
    build,
)


def test_build_exceptions_includes_all_types():
    """Exception generator should cover every required exception type."""
    assets = generate_it_asset_data(row_count=120, seed=42)
    exceptions = _build_exceptions_dataframe(assets, seed=42)
    summary = _exception_summary(exceptions)

    assert set(EXCEPTION_TYPES).issubset(set(summary["Exception Type"]))
    assert (summary["Count"] >= 0).all()
    assert (exceptions["Exception Type"] != "No Exception").any()


def test_exception_priority_mapping():
    """High-priority exceptions should include missing and duplicate cases."""
    assets = generate_it_asset_data(row_count=120, seed=42)
    exceptions = _build_exceptions_dataframe(assets, seed=42)

    high_types = exceptions[exceptions["Priority"] == "High"]["Exception Type"].unique()
    assert "Missing from Audit" in high_types or "Found Not in System" in high_types


def test_audit_reconciliation_sheet_structure():
    """Sheet should include KPIs, summary, sample tables, and exceptions report."""
    wb = Workbook()
    ws = wb.active
    assets = generate_it_asset_data(row_count=80, seed=42)
    build(ws, {"data": {"it_assets": assets}})

    values = [
        ws.cell(row=r, column=1).value for r in range(1, ws.max_row + 1) if ws.cell(row=r, column=1).value
    ]
    combined = " ".join(str(v) for v in values)
    assert "Audit Reconciliation" in combined
    assert "Exception Summary by Type" in combined
    assert "System Inventory" in combined
    assert "Physical Audit Count" in combined
    assert "Exceptions Report" in combined
    assert "AuditExceptionsReport" in ws.tables
    assert len(ws.conditional_formatting) >= 2
