"""Markdown Planner sheet — markdown modeling for aged and excess inventory."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from src.services.markdown_service import (
    MARKDOWN_PLANNER_HEADERS,
    build_markdown_dataframe,
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
    format_percentage_columns,
    set_landscape_print,
)

HEADERS = MARKDOWN_PLANNER_HEADERS

TITLE_ROW = 1
HEADER_ROW = 2
DATA_START_ROW = 3
COL_COUNT = len(HEADERS)
TABLE_NAME = "MarkdownPlannerTable"

COL_INTEGER = ["D", "H"]
COL_CURRENCY = ["E", "F", "K", "M", "N"]
COL_PERCENTAGE = ["G", "J", "L"]
COL_DISPOSITION = "O"

DISPOSITION_CF_MAP = {
    "Liquidate": "critical",
    "20% Markdown": "slow_moving",
    "10% Markdown": "watch",
    "Transfer First": "watch",
    "Hold": "healthy",
}


def _write_title(ws: Worksheet, record_count: int) -> None:
    """Render sheet title."""
    ws.merge_cells(
        start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=COL_COUNT
    )
    cell = ws.cell(
        row=TITLE_ROW,
        column=1,
        value=f"Markdown Planner — {record_count:,} Candidate Items",
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


def _write_data_rows(ws: Worksheet, planner: pd.DataFrame) -> int:
    """Write planner rows and return last row."""
    if planner.empty:
        return HEADER_ROW

    for row_offset, (_, row) in enumerate(planner.iterrows()):
        excel_row = DATA_START_ROW + row_offset
        for col_idx, header in enumerate(HEADERS, start=1):
            value = row[header]
            if pd.isna(value):
                value = None
            ws.cell(row=excel_row, column=col_idx, value=value)
    return DATA_START_ROW + len(planner) - 1


def _apply_column_formats(ws: Worksheet, last_row: int) -> None:
    """Apply currency, percentage, and integer formats."""
    if last_row < DATA_START_ROW:
        return
    format_integer_columns(ws, COL_INTEGER, DATA_START_ROW, last_row)
    format_currency_columns(ws, COL_CURRENCY, DATA_START_ROW, last_row)
    format_percentage_columns(ws, COL_PERCENTAGE, DATA_START_ROW, last_row)


def _create_planner_table(ws: Worksheet, last_row: int) -> None:
    """Create filterable Excel table."""
    end_col = get_column_letter(COL_COUNT)
    if last_row < DATA_START_ROW:
        last_row = DATA_START_ROW
    create_excel_table(ws, TABLE_NAME, f"A{HEADER_ROW}:{end_col}{last_row}")


def _apply_disposition_formatting(ws: Worksheet, last_row: int) -> None:
    """Apply conditional formatting to Recommended Disposition."""
    if last_row < DATA_START_ROW:
        return
    disposition_range = f"{COL_DISPOSITION}{DATA_START_ROW}:{COL_DISPOSITION}{last_row}"
    apply_risk_conditional_formatting(
        ws,
        disposition_range,
        COL_DISPOSITION,
        DATA_START_ROW,
        DISPOSITION_CF_MAP,
    )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Markdown Planner sheet from inventory data."""
    df: pd.DataFrame = context["data"].get("inventory", pd.DataFrame())
    planner = build_markdown_dataframe(df)

    _write_title(ws, len(planner))
    _write_headers(ws)
    last_row = _write_data_rows(ws, planner)

    _apply_column_formats(ws, last_row)
    _create_planner_table(ws, last_row)
    _apply_disposition_formatting(ws, last_row)

    freeze_panes(ws, row=DATA_START_ROW, col=1)
    autosize_columns(ws, min_width=10, max_width=38)
    ws.column_dimensions["B"].width = min(ws.column_dimensions["B"].width, 32)

    ws.sheet_view.showGridLines = False
    set_landscape_print(
        ws, fit_width=1, repeat_header_rows=f"{HEADER_ROW}:{HEADER_ROW}"
    )
