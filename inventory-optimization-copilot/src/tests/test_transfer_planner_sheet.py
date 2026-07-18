"""Tests for Transfer Planner sheet builder."""

from openpyxl import Workbook

from src.data_generation.generate_inventory import generate_inventory_data
from src.domain.constants import TRANSFER_MARGIN_RATE
from src.services.transfer_service import (
    build_transfer_dataframe,
    estimate_transfer_cost,
)
from src.sheets.transfer_planner_sheet import (
    DATA_START_ROW,
    HEADER_ROW,
    HEADERS,
    TABLE_NAME,
    build,
)


def test_estimate_transfer_cost_increases_with_quantity():
    """Transfer cost should scale with quantity moved."""
    low = estimate_transfer_cost("DC-NY", "Store-Bronx", 5)
    high = estimate_transfer_cost("DC-NY", "Store-Bronx", 20)
    assert high > low


def test_build_transfer_dataframe_net_benefit_model():
    """Transfers should use margin protected minus transfer cost with positive net benefit."""
    df = generate_inventory_data(row_count=120, seed=42)
    transfers = build_transfer_dataframe(df)

    assert list(transfers.columns) == HEADERS
    assert not transfers.empty, "Expected category-matched transfer candidates"
    assert (transfers["Net Benefit"] > 0).all()
    assert (transfers["Source Location"] != transfers["Destination Location"]).all()
    assert (transfers["Suggested Transfer Quantity"] > 0).all()

    import numpy as np

    expected_margin = (
        transfers["Suggested Transfer Quantity"]
        * transfers["Unit Cost"]
        * TRANSFER_MARGIN_RATE
    ).round(2)
    expected_net = (expected_margin - transfers["Transfer Cost"]).round(2)
    np.testing.assert_allclose(
        transfers["Estimated Margin Protected"].values,
        expected_margin.values,
        rtol=0,
        atol=0.01,
    )
    np.testing.assert_allclose(
        transfers["Net Benefit"].values,
        expected_net.values,
        rtol=0,
        atol=0.02,
    )


def test_transfer_planner_sheet_structure():
    """Sheet should include table and conditional formatting rules."""
    wb = Workbook()
    ws = wb.active
    df = generate_inventory_data(row_count=120, seed=42)
    build(ws, {"data": {"inventory": df}})

    assert ws.cell(row=HEADER_ROW, column=1).value == "SKU"
    assert TABLE_NAME in ws.tables
    assert len(ws.conditional_formatting) >= 2
    if ws.max_row >= DATA_START_ROW:
        assert ws.cell(row=DATA_START_ROW, column=14).value is not None
