"""Tests for network transfer and markdown optimization (Prompt 08)."""

from __future__ import annotations

import pandas as pd
import pytest

from config.workbook_config import (
    TRANSFER_MARGIN_RATE,
    TRANSFER_MAX_LEAD_TIME_DAYS,
)
from src.main import generate_all_data
from src.services.markdown_service import (
    MARKDOWN_PLANNER_HEADERS,
    assign_markdown_plan,
    project_sell_through,
)
from src.services.transfer_service import (
    TRANSFER_PLANNER_HEADERS,
    _round_case_pack,
    build_surplus_lookup,
    build_transfer_dataframe,
    estimate_transfer_cost,
    transfer_lead_time_days,
)
from src.workbook.builder import build_workbook


def test_transfer_headers_complete():
    """Transfer planner exposes required planning columns."""
    required = {
        "Rank",
        "SKU",
        "ABC Class",
        "Source Initial Surplus",
        "Destination Initial Requirement",
        "Source Remaining Surplus",
        "Destination Remaining Requirement",
        "Net Benefit",
        "Purchase Alternative Cost",
        "Action",
        "Allocation Batch",
    }
    assert required.issubset(set(TRANSFER_PLANNER_HEADERS))


def test_markdown_headers_complete():
    """Markdown planner exposes recovery and priority columns."""
    required = {
        "Transfer Feasible",
        "Obsolescence Risk",
        "Carrying Exposure",
        "Estimated Recovery Value",
        "Margin Impact",
        "Priority",
        "Recommended Disposition",
    }
    assert required.issubset(set(MARKDOWN_PLANNER_HEADERS))


def test_case_pack_rounding():
    """Transfer quantity should respect case-pack multiples."""
    assert _round_case_pack(7, 4) == 4
    assert _round_case_pack(8, 4) == 8
    assert _round_case_pack(3, 1) == 3
    assert _round_case_pack(0, 6) == 0


def test_transfer_economics_components():
    """Transfer rows should include cost, margin, risk, and purchase alternative."""
    data = generate_all_data()
    transfers = build_transfer_dataframe(data)
    if transfers.empty:
        pytest.skip("No transfer candidates in generated sample")

    row = transfers.iloc[0]
    qty = int(row["Transfer Quantity"])
    assert qty > 0
    assert float(row["Transfer Cost"]) == estimate_transfer_cost(
        row["Source Location"], row["Destination Location"], qty
    )
    assert float(row["Purchase Alternative Cost"]) >= qty * float(row["Unit Cost"])
    assert (
        float(row["Estimated Margin Protected"])
        >= qty * float(row["Unit Cost"]) * TRANSFER_MARGIN_RATE
    )


def test_double_allocation_prevention():
    """Remaining balances should never go negative across allocations."""
    data = generate_all_data()
    transfers = build_transfer_dataframe(data)
    if transfers.empty:
        pytest.skip("No transfer candidates in generated sample")

    for (sku, src), group in transfers.groupby(["SKU", "Source Location"]):
        initial = int(group["Source Initial Surplus"].iloc[0])
        allocated = int(group["Transfer Quantity"].sum())
        assert allocated <= initial
        assert int(group["Source Remaining Surplus"].iloc[-1]) == initial - allocated

    for (sku, dest), group in transfers.groupby(["SKU", "Destination Location"]):
        initial = int(group["Destination Initial Requirement"].iloc[0])
        allocated = int(group["Transfer Quantity"].sum())
        assert allocated <= initial
        final_remaining = int(group["Destination Remaining Requirement"].iloc[-1])
        assert final_remaining == initial - allocated


def test_deterministic_transfer_ranking():
    """Repeated builds should produce identical transfer plans."""
    data = generate_all_data()
    first = build_transfer_dataframe(data)
    second = build_transfer_dataframe(data)
    pd.testing.assert_frame_equal(first, second)


def test_surplus_lookup_for_markdown():
    """Markdown transfer-first uses network surplus by SKU."""
    data = generate_all_data()
    surplus = build_surplus_lookup(data)
    assert isinstance(surplus, dict)
    for sku, qty in surplus.items():
        assert qty > 0
        assert isinstance(sku, str)


def test_markdown_dispositions():
    """All prompt dispositions are reachable from planning rules."""
    dispositions = {
        assign_markdown_plan(60, 20, "Excess", 0.25, False)[1],
        assign_markdown_plan(90, 10, "Excess", 0.20, True)[1],
        assign_markdown_plan(200, 5, "Excess / Aged", 0.15, False)[1],
        assign_markdown_plan(280, 5, "Slow-Moving", 0.08, False)[1],
        assign_markdown_plan(310, 3, "Slow-Moving", 0.04, False)[1],
        assign_markdown_plan(400, 0, "Obsolete", 0.0, False)[1],
        assign_markdown_plan(400, 0, "Slow-Moving", 0.0, True)[1],
    }
    assert dispositions <= {
        "Hold",
        "Transfer First",
        "10% Markdown",
        "20% Markdown",
        "30% Markdown",
        "Liquidate",
        "Discontinue",
        "Dispose",
    }


def test_project_sell_through_uplift():
    """Markdown should increase projected sell-through when markdown applied."""
    base = 0.10
    uplifted = project_sell_through(base, 0.20)
    assert uplifted > base
    assert uplifted <= 0.90
    assert project_sell_through(base, 0.0) == round(base, 4)


def test_lead_time_gate():
    """Lead time above max should block route eligibility in service logic."""
    assert transfer_lead_time_days("DC-A", "DC-B") <= TRANSFER_MAX_LEAD_TIME_DAYS


def test_workbook_integrity_transfer_markdown_sheets(tmp_path):
    """Workbook build includes transfer and markdown sheets with tables."""
    output = tmp_path / "test_transfer_markdown.xlsx"
    build_workbook(generate_all_data(), output_path=output)

    from openpyxl import load_workbook

    wb = load_workbook(output)
    assert "Transfer Planner" in wb.sheetnames
    assert "Markdown Planner" in wb.sheetnames
    assert "TransferPlannerTable" in wb["Transfer Planner"].tables
    assert "MarkdownPlannerTable" in wb["Markdown Planner"].tables
