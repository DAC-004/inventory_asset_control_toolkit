"""IT Asset Register sheet — lifecycle asset tracking."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pandas as pd
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from config.workbook_config import DEMO_REFERENCE_DATE
from src.data_generation.generate_it_assets import COLUMN_ORDER
from src.workbook.styles import (
    apply_it_asset_status_formatting,
    apply_risk_conditional_formatting,
    apply_table_header_style,
    freeze_panes,
)
from src.workbook.utils import (
    autosize_columns,
    create_excel_table,
    format_date_columns,
    set_landscape_print,
)
from src.workbook.validations import add_it_asset_status_validation, add_lifecycle_stage_validation

HEADERS = [
    "Asset Tag",
    "Serial Number",
    "Device Type",
    "Make",
    "Model",
    "Assigned User",
    "Department",
    "Location",
    "Borough",
    "Purchase Date",
    "Warranty Expiration",
    "Status",
    "Condition",
    "Last Audit Date",
    "Lifecycle Stage",
    "Notes",
]

TITLE_ROW = 1
HEADER_ROW = 2
DATA_START_ROW = 3
COL_COUNT = len(HEADERS)
TABLE_NAME = "ITAssetRegisterTable"

COL_DATES = ["J", "K", "N"]
COL_STATUS = "L"
COL_LIFECYCLE = "O"
COL_WARRANTY = "K"
WARRANTY_WATCH_DAYS = 90

LIFECYCLE_STAGE_CF_MAP = {
    "Received": "neutral",
    "Tagged": "neutral",
    "In Stock": "healthy",
    "Assigned": "healthy",
    "In Repair": "watch",
    "Returned": "neutral",
    "Retired": "watch",
    "Data Wiped": "watch",
    "Disposed": "neutral",
}


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
    """Render sheet title."""
    ws.merge_cells(start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=COL_COUNT)
    cell = ws.cell(
        row=TITLE_ROW,
        column=1,
        value=f"IT Asset Register — {record_count:,} Assets Under Management",
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


def _write_data_rows(ws: Worksheet, df: pd.DataFrame) -> int:
    """Write IT asset rows and return last row."""
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
    """Apply date formatting to date columns."""
    if last_row < DATA_START_ROW:
        return
    format_date_columns(ws, COL_DATES, DATA_START_ROW, last_row)


def _create_register_table(ws: Worksheet, last_row: int) -> None:
    """Create filterable Excel table."""
    end_col = get_column_letter(COL_COUNT)
    if last_row < DATA_START_ROW:
        last_row = DATA_START_ROW
    create_excel_table(ws, TABLE_NAME, f"A{HEADER_ROW}:{end_col}{last_row}")


def _apply_status_and_lifecycle_formatting(ws: Worksheet, last_row: int) -> None:
    """Apply conditional formatting to Status and Lifecycle Stage."""
    if last_row < DATA_START_ROW:
        return

    status_range = f"{COL_STATUS}{DATA_START_ROW}:{COL_STATUS}{last_row}"
    lifecycle_range = f"{COL_LIFECYCLE}{DATA_START_ROW}:{COL_LIFECYCLE}{last_row}"

    apply_it_asset_status_formatting(ws, status_range, COL_STATUS, DATA_START_ROW)
    apply_risk_conditional_formatting(
        ws,
        lifecycle_range,
        COL_LIFECYCLE,
        DATA_START_ROW,
        LIFECYCLE_STAGE_CF_MAP,
    )


def _apply_missing_asset_highlight(ws: Worksheet, last_row: int) -> None:
    """Highlight entire rows red when asset status is Missing."""
    if last_row < DATA_START_ROW:
        return

    end_col = get_column_letter(COL_COUNT)
    row_range = f"A{DATA_START_ROW}:{end_col}{last_row}"
    red_fill = PatternFill(start_color=sc.COLORS["red"], end_color=sc.COLORS["red"], fill_type="solid")
    white_font_rule = FormulaRule(
        formula=[f'${COL_STATUS}{DATA_START_ROW}="Missing"'],
        fill=red_fill,
    )
    ws.conditional_formatting.add(row_range, white_font_rule)


def _apply_warranty_expiration_highlight(ws: Worksheet, last_row: int) -> None:
    """Highlight warranty expirations within 90 days of the demo reference date."""
    if last_row < DATA_START_ROW:
        return

    reference = DEMO_REFERENCE_DATE
    deadline = reference + timedelta(days=WARRANTY_WATCH_DAYS)
    warranty_range = f"{COL_WARRANTY}{DATA_START_ROW}:{COL_WARRANTY}{last_row}"
    anchor = f"${COL_WARRANTY}{DATA_START_ROW}"

    yellow_fill = PatternFill(
        start_color=sc.COLORS["yellow"],
        end_color=sc.COLORS["yellow"],
        fill_type="solid",
    )
    formula = (
        f"AND({anchor}>=DATE({reference.year},{reference.month},{reference.day}),"
        f"{anchor}<=DATE({deadline.year},{deadline.month},{deadline.day}))"
    )
    ws.conditional_formatting.add(warranty_range, FormulaRule(formula=[formula], fill=yellow_fill))


def _apply_validations(ws: Worksheet, last_row: int) -> None:
    """Add dropdown validations for Status and Lifecycle Stage."""
    if last_row < DATA_START_ROW:
        return

    add_it_asset_status_validation(
        ws, f"{COL_STATUS}{DATA_START_ROW}:{COL_STATUS}{last_row}"
    )
    add_lifecycle_stage_validation(
        ws, f"{COL_LIFECYCLE}{DATA_START_ROW}:{COL_LIFECYCLE}{last_row}"
    )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the IT Asset Register from IT asset data."""
    df: pd.DataFrame = context["data"].get("it_assets", pd.DataFrame())

    _write_title(ws, len(df))
    _write_headers(ws)
    last_row = _write_data_rows(ws, df)

    _apply_column_formats(ws, last_row)
    _create_register_table(ws, last_row)
    _apply_status_and_lifecycle_formatting(ws, last_row)
    _apply_missing_asset_highlight(ws, last_row)
    _apply_warranty_expiration_highlight(ws, last_row)
    _apply_validations(ws, last_row)

    freeze_panes(ws, row=DATA_START_ROW, col=1)
    autosize_columns(ws, min_width=10, max_width=40)
    ws.column_dimensions["F"].width = min(ws.column_dimensions["F"].width, 22)
    ws.column_dimensions["P"].width = min(max(ws.column_dimensions["P"].width, 28), 48)

    ws.sheet_view.showGridLines = False
    set_landscape_print(ws, fit_width=1, repeat_header_rows=f"{HEADER_ROW}:{HEADER_ROW}")
