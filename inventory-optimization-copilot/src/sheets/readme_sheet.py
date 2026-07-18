"""README sheet — toolkit guide for interviewers and reviewers."""

from __future__ import annotations

from typing import Any

from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from config.workbook_config import (
    AS_OF_DATE,
    AUTHOR,
    SHEET_ORDER,
    VERSION,
    WORKBOOK_TITLE,
)
from src.workbook.styles import apply_section_header_style
from src.workbook.utils import (
    add_internal_sheet_link,
    set_column_widths,
    set_portrait_print,
)

CONTENT_START_COL = 1
CONTENT_END_COL = 4
SPAN_COLS = CONTENT_END_COL - CONTENT_START_COL + 1


def _merge_and_write(
    ws: Worksheet,
    row: int,
    text: str,
    *,
    font: Font | None = None,
    fill: PatternFill | None = None,
    alignment: Alignment | None = None,
    row_height: float | None = None,
) -> None:
    ws.merge_cells(
        start_row=row,
        start_column=CONTENT_START_COL,
        end_row=row,
        end_column=CONTENT_END_COL,
    )
    cell = ws.cell(row=row, column=CONTENT_START_COL, value=text)
    cell.font = font or sc.BODY_FONT
    cell.alignment = alignment or Alignment(
        horizontal="left", vertical="top", wrap_text=True
    )
    if fill:
        cell.fill = fill
    if row_height:
        ws.row_dimensions[row].height = row_height


def _apply_title_banner(ws: Worksheet, row: int, title: str) -> None:
    ws.merge_cells(
        start_row=row,
        start_column=CONTENT_START_COL,
        end_row=row,
        end_column=CONTENT_END_COL,
    )
    cell = ws.cell(row=row, column=CONTENT_START_COL, value=title)
    cell.font = Font(
        name=sc.FONTS["default_name"], bold=True, color=sc.COLORS["white"], size=18
    )
    cell.fill = PatternFill(
        start_color=sc.COLORS["navy"], end_color=sc.COLORS["navy"], fill_type="solid"
    )
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 36


def _apply_subtitle_bar(ws: Worksheet, row: int, text: str) -> None:
    ws.merge_cells(
        start_row=row,
        start_column=CONTENT_START_COL,
        end_row=row,
        end_column=CONTENT_END_COL,
    )
    cell = ws.cell(row=row, column=CONTENT_START_COL, value=text)
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["dark_blue"],
        size=sc.FONTS["body_size"],
    )
    cell.fill = sc.KPI_CARD_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 22


def _apply_disclaimer(ws: Worksheet, row: int, text: str) -> None:
    ws.merge_cells(
        start_row=row,
        start_column=CONTENT_START_COL,
        end_row=row,
        end_column=CONTENT_END_COL,
    )
    cell = ws.cell(row=row, column=CONTENT_START_COL, value=text)
    cell.font = Font(
        name=sc.FONTS["default_name"],
        italic=True,
        color=sc.COLORS["dark_blue"],
        size=sc.FONTS["body_size"],
    )
    cell.fill = PatternFill(
        start_color=sc.COLORS["gray"], end_color=sc.COLORS["gray"], fill_type="solid"
    )
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 28


def _write_section(ws: Worksheet, row: int, title: str) -> int:
    apply_section_header_style(ws, row, CONTENT_START_COL, title, span_cols=SPAN_COLS)
    ws.row_dimensions[row].height = 22
    return row + 1


def _write_body(ws: Worksheet, row: int, text: str, row_height: float = 48) -> int:
    _merge_and_write(ws, row, text, row_height=row_height)
    return row + 1


def _write_spacer(ws: Worksheet, row: int, height: float = 8) -> int:
    ws.row_dimensions[row].height = height
    return row + 1


def _write_navigation_links(ws: Worksheet, start_row: int) -> int:
    row = start_row
    sheets = [name for name in SHEET_ORDER if name != "README"]
    for idx, sheet_name in enumerate(sheets):
        link_row = row + idx // 2
        link_col = 1 if idx % 2 == 0 else 3
        add_internal_sheet_link(ws, link_row, link_col, sheet_name)
    return row + (len(sheets) + 1) // 2


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Populate the README tab with inventory optimization overview and demo guidance."""
    row = 1
    _apply_title_banner(ws, row, WORKBOOK_TITLE)
    row += 1
    _apply_subtitle_bar(
        ws,
        row,
        f"Version: {VERSION}    |    Author: {AUTHOR}    |    "
        f"As-of Date: {AS_OF_DATE.strftime('%B %d, %Y')}",
    )
    row += 1
    _apply_disclaimer(
        ws,
        row,
        "Disclaimer: All data in this workbook is fictional sample data created for "
        "demonstration and interview purposes. No live systems or real company records "
        "are represented.",
    )
    row += 1
    row = _write_spacer(ws, row)

    row = _write_section(ws, row, "Purpose of This Workbook")
    row = _write_body(
        ws,
        row,
        "Inventory Optimization Copilot is a decision-support workbook for supply chain, "
        "procurement, and distribution teams. It highlights aged and excess inventory, "
        "replenishment priorities, transfer and markdown economics, service performance, "
        "and vendor risk — generated entirely from reproducible Python source code.",
        row_height=56,
    )
    row = _write_spacer(ws, row)

    row = _write_section(ws, row, "Recommended Demo Path")
    row = _write_body(
        ws,
        row,
        "Suggested flow (10 minutes):\n"
        "1. Inventory Dashboard — health, classification, planning, and procurement KPIs\n"
        "2. Inventory Classification & Cycle Count Plan — ABC, turnover, accuracy\n"
        "3. Aged Excess Analysis — exception review\n"
        "4. Replenishment Planning — ROP, safety stock, order recommendations\n"
        "5. Transfer Planner — network surplus allocation and net benefit\n"
        "6. Markdown Planner — transfer-first vs. markdown dispositions\n"
        "7. Demand Forecast & Service Level Analysis — WAPE, fill rates\n"
        "8. Purchase Order Tracker & Vendor Scorecards — open supply and OTIF\n"
        "9. Management Summary — printable executive overview\n\n"
        "Narrative: "
        '"This workbook focuses on inventory optimization. The dashboard quantifies value, '
        "aged exposure, and service gaps. I drill into replenishment and transfer economics, "
        'evaluate markdown recovery, and close with a leadership-ready summary."',
        row_height=140,
    )
    row = _write_spacer(ws, row)

    row = _write_section(ws, row, "Workbook Navigation")
    row = _write_navigation_links(ws, row)
    row += 2

    row = _write_section(ws, row, "KPI Notes")
    row = _write_body(
        ws,
        row,
        "• Total / aged / excess values derive from Master Inventory status and age rules\n"
        "• Recovery value sums markdown-eligible estimated recovery from the Markdown Planner\n"
        "• Fill rates and service gaps use trailing 52-week customer order history\n"
        "• Forecast WAPE selects the lowest-error statistical method per SKU-location\n"
        "• Transfer net benefit = margin protected − transfer cost − source risk cost\n"
        "• Vendor OTIF and risk scores weight delivery, quality, lead time, and compliance",
        row_height=88,
    )
    row = _write_spacer(ws, row)

    row = _write_section(ws, row, "Assumptions & Limitations")
    row = _write_body(
        ws,
        row,
        "Assumptions: deterministic fictional data (seed 42), fixed as-of date, static lead "
        "times, lane-based transfer costs, and simplified markdown sell-through uplift.\n\n"
        "Limitations: not a live ERP integration; forecasts and scorecards reflect sample "
        "history only; transfer capacity uses storage headroom estimates; executive summary "
        "is illustrative and requires business validation before operational use.",
        row_height=88,
    )
    row = _write_spacer(ws, row)

    row = _write_section(ws, row, "Build Instructions")
    row = _write_body(
        ws,
        row,
        "From the inventory-optimization-copilot project root:\n"
        "  pip install -r requirements.txt\n"
        "  python src/main.py\n\n"
        "Outputs:\n"
        "  dist/Inventory_Optimization_Copilot.xlsx (14 tabs)\n"
        "  data/generated/*.csv (8 inventory planning datasets)",
        row_height=72,
    )

    set_column_widths(ws, {"A": 24, "B": 24, "C": 24, "D": 24})
    ws.sheet_view.showGridLines = False
    set_portrait_print(ws, fit_width=1, fit_height=0, repeat_header_rows="1:3")
