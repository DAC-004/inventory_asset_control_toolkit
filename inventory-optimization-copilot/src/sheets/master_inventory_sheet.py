"""Master Inventory sheet — operational inventory dataset."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from src.services.workbook_inventory import COLUMN_ORDER
from src.workbook.styles import (
    apply_inventory_status_formatting,
    apply_risk_conditional_formatting,
    apply_table_header_style,
    freeze_panes,
)
from src.workbook.utils import (
    add_internal_sheet_link,
    autosize_columns,
    create_excel_table,
    format_currency_columns,
    format_date_columns,
    format_integer_columns,
    format_percentage_columns,
    set_landscape_print,
)
from src.workbook.validations import (
    add_inventory_status_validation,
    add_recommended_action_validation,
)

# Display headers aligned to COLUMN_ORDER in generate_inventory.py
HEADERS = [
    "Item ID",
    "SKU",
    "Product Name",
    "Category",
    "Subcategory",
    "Location",
    "Location Type",
    "Region",
    "Quantity On Hand",
    "Min Stock",
    "Max Stock",
    "Unit Cost",
    "Selling Price",
    "Total Value",
    "Last Movement Date",
    "Last Sale Date",
    "Age Days",
    "90 Day Demand",
    "Sell Through Rate",
    "Gross Margin %",
    "Status",
    "Recommended Action",
]

TITLE_ROW = 1
HEADER_ROW = 2
DATA_START_ROW = 3
COL_COUNT = len(HEADERS)

# Column letters for formatting and validation
COL_CURRENCY = ["L", "M", "N"]
COL_DATES = ["O", "P"]
COL_INTEGER = ["I", "J", "K", "Q", "R"]
COL_PERCENTAGE = ["S", "T"]
COL_STATUS = "U"
COL_RECOMMENDED_ACTION = "V"

RECOMMENDED_ACTION_RISK = {
    "Monitor": "healthy",
    "Replenish": "critical",
    "Review Transfer": "watch",
    "Transfer or Markdown": "slow_moving",
    "Markdown Review": "slow_moving",
    "Liquidate": "obsolete",
}

TABLE_NAME = "MasterInventoryTable"


def _coerce_cell_value(value: Any) -> Any:
    """Normalize pandas/numpy values for openpyxl."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date()
    return value


def _write_title(ws: Worksheet, record_count: int) -> None:
    """Render sheet title and record-count subtitle."""
    ws.merge_cells(
        start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=COL_COUNT - 1
    )
    title_cell = ws.cell(
        row=TITLE_ROW,
        column=1,
        value=f"Master Inventory — {record_count:,} SKU-Location Records",
    )
    title_cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    title_cell.fill = sc.HEADER_FILL
    title_cell.alignment = Alignment(
        horizontal="left", vertical="center", wrap_text=True
    )
    ws.row_dimensions[TITLE_ROW].height = 28
    add_internal_sheet_link(ws, TITLE_ROW, COL_COUNT, "README", "← README")


def _write_headers(ws: Worksheet) -> None:
    """Write and style the table header row."""
    for col_idx, header in enumerate(HEADERS, start=1):
        ws.cell(row=HEADER_ROW, column=col_idx, value=header)
    apply_table_header_style(ws, HEADER_ROW, COL_COUNT)
    ws.row_dimensions[HEADER_ROW].height = 22


def _write_data_rows(ws: Worksheet, df: pd.DataFrame) -> int:
    """
    Write inventory data rows from the DataFrame.

    Returns:
        Last populated row number.
    """
    if df.empty:
        return HEADER_ROW

    for row_offset, (_, row) in enumerate(df.iterrows()):
        excel_row = DATA_START_ROW + row_offset
        for col_idx, col_name in enumerate(COLUMN_ORDER, start=1):
            ws.cell(
                row=excel_row,
                column=col_idx,
                value=_coerce_cell_value(row.get(col_name)),
            )
    return DATA_START_ROW + len(df) - 1


def _apply_column_formats(ws: Worksheet, last_row: int) -> None:
    """Apply number formats to currency, date, integer, and percentage columns."""
    if last_row < DATA_START_ROW:
        return

    format_currency_columns(ws, COL_CURRENCY, DATA_START_ROW, last_row)
    format_date_columns(ws, COL_DATES, DATA_START_ROW, last_row)
    format_integer_columns(ws, COL_INTEGER, DATA_START_ROW, last_row)
    format_percentage_columns(ws, COL_PERCENTAGE, DATA_START_ROW, last_row)


def _apply_status_formatting(ws: Worksheet, last_row: int) -> None:
    """Apply conditional formatting to Status and Recommended Action columns."""
    if last_row < DATA_START_ROW:
        return

    status_range = f"{COL_STATUS}{DATA_START_ROW}:{COL_STATUS}{last_row}"
    action_range = (
        f"{COL_RECOMMENDED_ACTION}{DATA_START_ROW}:{COL_RECOMMENDED_ACTION}{last_row}"
    )

    apply_inventory_status_formatting(ws, status_range, COL_STATUS, DATA_START_ROW)
    apply_risk_conditional_formatting(
        ws,
        action_range,
        COL_RECOMMENDED_ACTION,
        DATA_START_ROW,
        RECOMMENDED_ACTION_RISK,
    )


def _apply_validations(ws: Worksheet, last_row: int) -> None:
    """Add dropdown validations for Status and Recommended Action."""
    if last_row < DATA_START_ROW:
        return

    add_inventory_status_validation(
        ws, f"{COL_STATUS}{DATA_START_ROW}:{COL_STATUS}{last_row}"
    )
    add_recommended_action_validation(
        ws,
        f"{COL_RECOMMENDED_ACTION}{DATA_START_ROW}:{COL_RECOMMENDED_ACTION}{last_row}",
    )


def _create_inventory_table(ws: Worksheet, last_row: int) -> None:
    """Create a filterable Excel table over the header and data range."""
    end_col = get_column_letter(COL_COUNT)
    table_ref = f"A{HEADER_ROW}:{end_col}{last_row}"
    create_excel_table(
        ws,
        TABLE_NAME,
        table_ref,
        style="TableStyleMedium2",
        show_row_stripes=True,
    )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Master Inventory sheet from the inventory DataFrame."""
    df: pd.DataFrame = context["data"].get("inventory", pd.DataFrame())

    _write_title(ws, len(df))
    _write_headers(ws)
    last_row = _write_data_rows(ws, df)

    # Ensure at least one data row for table creation when empty
    if last_row < DATA_START_ROW:
        last_row = DATA_START_ROW

    _apply_column_formats(ws, last_row)
    _create_inventory_table(ws, last_row)
    _apply_status_formatting(ws, last_row)
    _apply_validations(ws, last_row)

    freeze_panes(ws, row=DATA_START_ROW, col=1)
    autosize_columns(ws, min_width=10, max_width=42)
    ws.column_dimensions["C"].width = min(ws.column_dimensions["C"].width, 36)

    ws.sheet_view.showGridLines = False
    set_landscape_print(
        ws, fit_width=1, repeat_header_rows=f"{HEADER_ROW}:{HEADER_ROW}"
    )
