"""Management Summary sheet — printable one-page executive overview (inventory only)."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from config.workbook_config import (
    AS_OF_DATE,
    INVENTORY_THRESHOLDS,
    ROW_COUNTS,
    VERSION,
)
from src.sheets.aged_excess_sheet import _build_analysis_dataframe
from src.workbook.formulas import (
    count_if_range,
    sum_if_numeric,
    sum_if_range,
    sum_range,
)
from src.workbook.styles import (
    apply_kpi_card_style,
    apply_section_header_style,
    apply_table_header_range,
)
from src.workbook.utils import (
    format_currency_columns,
    set_column_widths,
    set_print_layout,
)

MASTER_SHEET = "Master Inventory"
MASTER_DATA_START = 3

COL_TOTAL_VALUE = "N"
COL_AGE_DAYS = "Q"
COL_STATUS = "U"
COL_RECOMMENDED_ACTION = "V"

MARKDOWN_ACTIONS = ("Markdown Review", "Transfer or Markdown", "Liquidate")
TRANSFER_ACTIONS = ("Review Transfer", "Transfer or Markdown")

INVENTORY_RISK_HEADERS = ["SKU", "Location", "Issue", "Value"]

TITLE_ROW = 1
SUBTITLE_ROW = 2
SECTION1_ROW = 3
KPI1_TITLE_ROW = 4
KPI1_VALUE_ROW = 5
SECTION2_ROW = 7
SUMMARY_HEADER_ROW = 8
SUMMARY_DATA_START_ROW = 9
SECTION3_ROW = 14
RISK_HEADER_ROW = 15
RISK_DATA_START_ROW = 16
SECTION4_ROW = 22
PLAN_HEADER_ROW = 23
PLAN_DATA_START_ROW = 24

ACTION_PLAN = {
    "30 Days": [
        "Validate inventory records and exception flags",
        "Review top aged and excess SKU-locations",
        "Confirm transfer vs. markdown priorities",
    ],
    "60 Days": [
        "Execute approved network transfers",
        "Apply markdown tiers by category margin guardrails",
        "Replenish stockout-risk locations",
    ],
    "90 Days": [
        "Measure inventory turnover and recovery impact",
        "Automate weekly KPI review cadence",
        "Recommend process improvements to leadership",
    ],
}


def _data_end(start_row: int, record_count: int) -> int:
    if record_count <= 0:
        return start_row
    return start_row + record_count - 1


def _inventory_kpis(inv_end: int) -> list[tuple[str, str, str]]:
    start = MASTER_DATA_START
    aged_threshold = INVENTORY_THRESHOLDS["excess_aged_age_days"]
    excess_formula = "=" + "+".join(
        sum_if_range(
            MASTER_SHEET, COL_STATUS, status, COL_TOTAL_VALUE, start, inv_end
        ).lstrip("=")
        for status in ("Excess", "Excess / Aged")
    )
    transfer_formula = "=" + "+".join(
        count_if_range(
            MASTER_SHEET, COL_RECOMMENDED_ACTION, start, inv_end, action
        ).lstrip("=")
        for action in TRANSFER_ACTIONS
    )
    markdown_formula = "=" + "+".join(
        count_if_range(
            MASTER_SHEET, COL_RECOMMENDED_ACTION, start, inv_end, action
        ).lstrip("=")
        for action in MARKDOWN_ACTIONS
    )
    return [
        (
            "Total Inventory Value",
            sum_range(MASTER_SHEET, COL_TOTAL_VALUE, start, inv_end),
            "currency",
        ),
        (
            "Aged Inventory Value",
            sum_if_numeric(
                MASTER_SHEET,
                COL_AGE_DAYS,
                f">{aged_threshold}",
                COL_TOTAL_VALUE,
                start,
                inv_end,
            ),
            "currency",
        ),
        ("Excess Inventory Value", excess_formula, "currency"),
        ("Transfer Candidates", transfer_formula, "integer"),
        ("Markdown Candidates", markdown_formula, "integer"),
    ]


def _recommended_action_summary(inventory: pd.DataFrame) -> list[tuple[str, int]]:
    if inventory.empty:
        return []
    counts = inventory["recommended_action"].value_counts()
    return [(str(action), int(count)) for action, count in counts.items()]


def _top_inventory_risks(
    inventory: pd.DataFrame, limit: int = 5
) -> list[dict[str, Any]]:
    analysis = _build_analysis_dataframe(inventory)
    if analysis.empty:
        return []
    rows: list[dict[str, Any]] = []
    for _, row in analysis.head(limit).iterrows():
        rows.append(
            {
                "SKU": row["SKU"],
                "Location": row["Location"],
                "Issue": row["Issue Type"],
                "Value": row["Inventory Value"],
            }
        )
    return rows


def _write_title_banner(ws: Worksheet) -> None:
    ws.merge_cells(start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=8)
    cell = ws.cell(row=TITLE_ROW, column=1, value="Management Summary")
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    cell.fill = sc.HEADER_FILL
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[TITLE_ROW].height = 30

    ws.merge_cells(
        start_row=SUBTITLE_ROW, start_column=1, end_row=SUBTITLE_ROW, end_column=8
    )
    subtitle = ws.cell(
        row=SUBTITLE_ROW,
        column=1,
        value=f"{VERSION} | Executive Overview | As-of Date: {AS_OF_DATE.strftime('%B %d, %Y')}",
    )
    subtitle.font = Font(
        name=sc.FONTS["default_name"],
        italic=True,
        color=sc.COLORS["dark_blue"],
        size=sc.FONTS["body_size"],
    )
    subtitle.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[SUBTITLE_ROW].height = 18


def _write_kpi_cards(
    ws: Worksheet,
    title_row: int,
    value_row: int,
    kpis: list[tuple[str, str, str]],
) -> None:
    card_cols = [1, 3, 5, 7, 9]
    format_map = {
        "currency": sc.NUMBER_FORMATS["currency_compact"],
        "integer": sc.NUMBER_FORMATS["integer"],
    }
    for idx, (title, value, fmt_key) in enumerate(kpis):
        col = card_cols[idx]
        apply_kpi_card_style(
            ws, title_row, col, value_row, col, title, value, span_cols=2
        )
        ws.cell(row=value_row, column=col).number_format = format_map[fmt_key]


def _write_action_summary(ws: Worksheet, action_rows: list[tuple[str, int]]) -> None:
    apply_section_header_style(
        ws, SECTION2_ROW, 1, "2. Recommended Action Summary", span_cols=8
    )
    apply_table_header_range(ws, SUMMARY_HEADER_ROW, 1, 2)
    ws.cell(row=SUMMARY_HEADER_ROW, column=1, value="Action")
    ws.cell(row=SUMMARY_HEADER_ROW, column=2, value="Count")
    for offset, (label, count) in enumerate(action_rows[:8]):
        excel_row = SUMMARY_DATA_START_ROW + offset
        ws.cell(row=excel_row, column=1, value=label)
        count_cell = ws.cell(row=excel_row, column=2, value=count)
        count_cell.number_format = sc.NUMBER_FORMATS["integer"]


def _write_risk_table(ws: Worksheet, inventory_risks: list[dict[str, Any]]) -> None:
    apply_section_header_style(
        ws, SECTION3_ROW, 1, "3. Top Inventory Risks", span_cols=8
    )
    apply_table_header_range(ws, RISK_HEADER_ROW, 1, 4)
    for col_idx, header in enumerate(INVENTORY_RISK_HEADERS, start=1):
        ws.cell(row=RISK_HEADER_ROW, column=col_idx, value=header)
    for offset in range(5):
        excel_row = RISK_DATA_START_ROW + offset
        if offset < len(inventory_risks):
            risk = inventory_risks[offset]
            ws.cell(row=excel_row, column=1, value=risk["SKU"])
            ws.cell(row=excel_row, column=2, value=risk["Location"])
            ws.cell(row=excel_row, column=3, value=risk["Issue"])
            value_cell = ws.cell(row=excel_row, column=4, value=risk["Value"])
            value_cell.number_format = sc.NUMBER_FORMATS["currency_compact"]


def _write_action_plan(ws: Worksheet) -> None:
    apply_section_header_style(
        ws, SECTION4_ROW, 1, "4. 30 / 60 / 90 Day Action Plan", span_cols=8
    )
    plan_cols = [1, 4, 7]
    for idx, horizon in enumerate(["30 Days", "60 Days", "90 Days"]):
        col = plan_cols[idx]
        ws.merge_cells(
            start_row=PLAN_HEADER_ROW,
            start_column=col,
            end_row=PLAN_HEADER_ROW,
            end_column=col + 2,
        )
        header = ws.cell(row=PLAN_HEADER_ROW, column=col, value=horizon)
        header.font = sc.KPI_TITLE_FONT
        header.fill = sc.KPI_CARD_FILL
        header.alignment = sc.KPI_CARD_STYLE["alignment"]
        header.border = sc.NAVY_BORDER
        for bullet_idx, bullet in enumerate(ACTION_PLAN[horizon]):
            row = PLAN_DATA_START_ROW + bullet_idx
            ws.merge_cells(
                start_row=row, start_column=col, end_row=row, end_column=col + 2
            )
            cell = ws.cell(row=row, column=col, value=f"• {bullet}")
            cell.font = sc.BODY_FONT
            cell.alignment = Alignment(
                horizontal="left", vertical="top", wrap_text=True
            )
            cell.border = sc.THIN_GRAY_BORDER
            ws.row_dimensions[row].height = 28


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the printable Management Summary one-pager."""
    inventory = context["data"].get("inventory", pd.DataFrame())
    inv_count = len(inventory) or ROW_COUNTS["inventory"]["default"]
    inv_end = _data_end(MASTER_DATA_START, inv_count)
    inventory_risks = _top_inventory_risks(inventory)

    _write_title_banner(ws)
    apply_section_header_style(
        ws, SECTION1_ROW, 1, "1. Inventory Health Highlights", span_cols=8
    )
    _write_kpi_cards(ws, KPI1_TITLE_ROW, KPI1_VALUE_ROW, _inventory_kpis(inv_end))
    _write_action_summary(ws, _recommended_action_summary(inventory))
    _write_risk_table(ws, inventory_risks)
    _write_action_plan(ws)

    format_currency_columns(ws, ["D"], RISK_DATA_START_ROW, RISK_DATA_START_ROW + 4)
    set_column_widths(
        ws, {"A": 16, "B": 18, "C": 22, "D": 14, "E": 2, "F": 14, "G": 16, "H": 18}
    )
    ws.sheet_view.showGridLines = False
    set_print_layout(
        ws,
        orientation="landscape",
        fit_width=1,
        fit_height=1,
        repeat_header_rows=f"{TITLE_ROW}:{SUBTITLE_ROW}",
    )
