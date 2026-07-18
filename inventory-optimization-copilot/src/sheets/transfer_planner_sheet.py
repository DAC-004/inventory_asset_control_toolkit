"""Transfer Planner sheet — inter-location transfer recommendations."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from src.services.transfer_service import (
    TRANSFER_PLANNER_HEADERS,
    build_transfer_dataframe,
)
from src.workbook.styles import (
    apply_risk_conditional_formatting,
    apply_table_header_style,
    freeze_panes,
)
from src.workbook.utils import (
    autosize_columns,
    create_excel_table,
    format_currency_columns,
    format_integer_columns,
    set_landscape_print,
)

HEADERS = TRANSFER_PLANNER_HEADERS

TITLE_ROW = 1
HEADER_ROW = 2
DATA_START_ROW = 3
COL_COUNT = len(HEADERS)
TABLE_NAME = "TransferPlannerTable"

COL_INTEGER = ["E", "F", "G", "H", "I"]
COL_CURRENCY = ["J", "K", "L", "M"]
COL_NET_BENEFIT = "M"
COL_RECOMMENDATION = "N"

RECOMMENDATION_CF_MAP = {
    "Transfer Recommended": "healthy",
    "Review Transfer": "watch",
    "Do Not Transfer": "critical",
}


def _write_title(ws: Worksheet, record_count: int) -> None:
    """Render sheet title."""
    ws.merge_cells(
        start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=COL_COUNT
    )
    cell = ws.cell(
        row=TITLE_ROW,
        column=1,
        value=f"Transfer Planner — {record_count:,} Recommended Transfers",
    )
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    cell.fill = sc.HEADER_FILL
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[TITLE_ROW].height = 28


def _write_headers(ws: Worksheet) -> None:
    """Write and style table headers."""
    for col_idx, header in enumerate(HEADERS, start=1):
        ws.cell(row=HEADER_ROW, column=col_idx, value=header)
    apply_table_header_style(ws, HEADER_ROW, COL_COUNT)
    ws.row_dimensions[HEADER_ROW].height = 22


def _write_data_rows(ws: Worksheet, transfers: pd.DataFrame) -> int:
    """Write transfer rows and return last row."""
    if transfers.empty:
        return HEADER_ROW

    for row_offset, (_, row) in enumerate(transfers.iterrows()):
        excel_row = DATA_START_ROW + row_offset
        for col_idx, header in enumerate(HEADERS, start=1):
            value = row[header]
            if pd.isna(value):
                value = None
            ws.cell(row=excel_row, column=col_idx, value=value)
    return DATA_START_ROW + len(transfers) - 1


def _apply_column_formats(ws: Worksheet, last_row: int) -> None:
    """Apply currency and integer formats."""
    if last_row < DATA_START_ROW:
        return
    format_integer_columns(ws, COL_INTEGER, DATA_START_ROW, last_row)
    format_currency_columns(ws, COL_CURRENCY, DATA_START_ROW, last_row)


def _create_transfer_table(ws: Worksheet, last_row: int) -> None:
    """Create filterable Excel table."""
    end_col = get_column_letter(COL_COUNT)
    if last_row < DATA_START_ROW:
        last_row = DATA_START_ROW
    create_excel_table(ws, TABLE_NAME, f"A{HEADER_ROW}:{end_col}{last_row}")


def _apply_net_benefit_formatting(ws: Worksheet, last_row: int) -> None:
    """Green for positive net benefit; red for zero or negative."""
    if last_row < DATA_START_ROW:
        return

    benefit_range = f"{COL_NET_BENEFIT}{DATA_START_ROW}:{COL_NET_BENEFIT}{last_row}"
    green_fill = PatternFill(
        start_color=sc.COLORS["green"], end_color=sc.COLORS["green"], fill_type="solid"
    )
    red_fill = PatternFill(
        start_color=sc.COLORS["red"], end_color=sc.COLORS["red"], fill_type="solid"
    )

    ws.conditional_formatting.add(
        benefit_range,
        CellIsRule(operator="greaterThan", formula=["0"], fill=green_fill),
    )
    ws.conditional_formatting.add(
        benefit_range,
        CellIsRule(operator="lessThanOrEqual", formula=["0"], fill=red_fill),
    )


def _apply_recommendation_formatting(ws: Worksheet, last_row: int) -> None:
    """Apply disposition-style formatting to Recommendation column."""
    if last_row < DATA_START_ROW:
        return

    recommendation_range = (
        f"{COL_RECOMMENDATION}{DATA_START_ROW}:{COL_RECOMMENDATION}{last_row}"
    )
    apply_risk_conditional_formatting(
        ws,
        recommendation_range,
        COL_RECOMMENDATION,
        DATA_START_ROW,
        RECOMMENDATION_CF_MAP,
    )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Transfer Planner sheet from inventory data."""
    df: pd.DataFrame = context["data"].get("inventory", pd.DataFrame())
    transfers = build_transfer_dataframe(df)

    _write_title(ws, len(transfers))
    _write_headers(ws)
    last_row = _write_data_rows(ws, transfers)

    _apply_column_formats(ws, last_row)
    _create_transfer_table(ws, last_row)
    _apply_net_benefit_formatting(ws, last_row)
    _apply_recommendation_formatting(ws, last_row)

    freeze_panes(ws, row=DATA_START_ROW, col=1)
    autosize_columns(ws, min_width=10, max_width=36)
    ws.column_dimensions["B"].width = min(ws.column_dimensions["B"].width, 30)

    ws.sheet_view.showGridLines = False
    set_landscape_print(
        ws, fit_width=1, repeat_header_rows=f"{HEADER_ROW}:{HEADER_ROW}"
    )
