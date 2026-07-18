"""Inventory Dashboard sheet — leadership KPIs, summaries, and charts."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from src.domain.constants import MASTER_DATA_START
from src.services.classification_service import compute_dashboard_classification_kpis
from src.services.kpi_dashboard_service import (
    compute_action_summary,
    compute_aging_summary,
    compute_location_summary,
    compute_status_summary,
    compute_top_excess,
)
from src.services.kpi_service import dashboard_kpi_definitions
from src.workbook.charts import (
    add_bar_chart,
    add_pie_chart,
    make_category_reference,
    make_data_reference,
)
from src.workbook.styles import (
    apply_kpi_card_style,
    apply_section_header_style,
    apply_table_header_style,
)
from src.workbook.utils import (
    autosize_columns,
    format_currency_columns,
    format_integer_columns,
    set_column_widths,
    set_landscape_print,
)

TITLE_ROW = 1
KPI_ROW_1_TITLE = 3
KPI_ROW_1_VALUE = 4
KPI_ROW_2_TITLE = 6
KPI_ROW_2_VALUE = 7
CLASS_SECTION_ROW = 8
CLASS_KPI_ROW_1_TITLE = 9
CLASS_KPI_ROW_1_VALUE = 10
CLASS_KPI_ROW_2_TITLE = 11
CLASS_KPI_ROW_2_VALUE = 12
SUMMARY_START_ROW = 14


def _data_end_row(record_count: int) -> int:
    """Last data row on Master Inventory for the given record count."""
    if record_count <= 0:
        return MASTER_DATA_START
    return MASTER_DATA_START + record_count - 1


def _write_title_banner(ws: Worksheet) -> None:
    """Render dashboard title."""
    ws.merge_cells(
        start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=10
    )
    cell = ws.cell(row=TITLE_ROW, column=1, value="Inventory Dashboard")
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    cell.fill = sc.HEADER_FILL
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[TITLE_ROW].height = 30


def _write_kpi_cards(ws: Worksheet, start: int, end: int) -> None:
    """Render 10 KPI cards in a 5×2 grid."""
    kpis = dashboard_kpi_definitions(start, end)
    card_cols = [1, 3, 5, 7, 9]

    for idx, (title, formula, fmt) in enumerate(kpis):
        row_pair = 0 if idx < 5 else 1
        col = card_cols[idx % 5]
        title_row = KPI_ROW_1_TITLE if row_pair == 0 else KPI_ROW_2_TITLE
        value_row = KPI_ROW_1_VALUE if row_pair == 0 else KPI_ROW_2_VALUE

        apply_kpi_card_style(
            ws, title_row, col, value_row, col, title, formula, span_cols=2
        )

        value_cell = ws.cell(row=value_row, column=col)
        if fmt == "currency":
            value_cell.number_format = sc.NUMBER_FORMATS["currency_compact"]
        elif fmt == "percentage":
            value_cell.number_format = sc.NUMBER_FORMATS["percentage"]
        else:
            value_cell.number_format = sc.NUMBER_FORMATS["integer"]


def _write_classification_kpi_cards(ws: Worksheet, data: dict[str, Any]) -> None:
    """Render ABC, turnover, DOH, coverage, accuracy, and overdue KPIs."""
    apply_section_header_style(
        ws, CLASS_SECTION_ROW, 1, "Classification & Cycle Count KPIs", span_cols=10
    )
    kpis = compute_dashboard_classification_kpis(data)
    cards = [
        ("Class A SKUs", kpis["abc_a_count"], "integer"),
        ("Class B SKUs", kpis["abc_b_count"], "integer"),
        ("Class C SKUs", kpis["abc_c_count"], "integer"),
        ("Enterprise Turnover", kpis["enterprise_turnover"], "decimal"),
        ("Avg Financial DOH", kpis["avg_financial_doh"], "decimal"),
        ("Avg Coverage Days", kpis["avg_coverage_days"], "decimal"),
        ("Unit Accuracy %", kpis["avg_unit_accuracy_pct"], "percentage"),
        ("Overdue Counts", kpis["overdue_count"], "integer"),
    ]
    card_cols = [1, 3, 5, 7, 9]
    for idx, (title, value, fmt) in enumerate(cards):
        row_pair = 0 if idx < 5 else 1
        col = card_cols[idx % 5]
        title_row = CLASS_KPI_ROW_1_TITLE if row_pair == 0 else CLASS_KPI_ROW_2_TITLE
        value_row = CLASS_KPI_ROW_1_VALUE if row_pair == 0 else CLASS_KPI_ROW_2_VALUE
        apply_kpi_card_style(
            ws, title_row, col, value_row, col, title, value, span_cols=2
        )
        value_cell = ws.cell(row=value_row, column=col)
        if fmt == "percentage":
            value_cell.number_format = sc.NUMBER_FORMATS["percentage"]
        elif fmt == "integer":
            value_cell.number_format = sc.NUMBER_FORMATS["integer"]
        else:
            value_cell.number_format = "0.00"


def _write_table_block(
    ws: Worksheet,
    start_row: int,
    section_title: str,
    headers: list[str],
    data_rows: list[list[Any]],
) -> tuple[int, int, int]:
    """
    Write a summary table block.

    Returns:
        (header_row, first_data_row, last_data_row)
    """
    apply_section_header_style(ws, start_row, 1, section_title, span_cols=4)
    header_row = start_row + 1
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=header_row, column=col_idx, value=header)
    apply_table_header_style(ws, header_row, len(headers))

    first_data_row = header_row + 1
    for row_offset, row_values in enumerate(data_rows):
        excel_row = first_data_row + row_offset
        for col_idx, value in enumerate(row_values, start=1):
            ws.cell(row=excel_row, column=col_idx, value=value)

    last_data_row = first_data_row + len(data_rows) - 1 if data_rows else header_row
    return header_row, first_data_row, last_data_row


def _write_summary_tables(
    ws: Worksheet,
    df: pd.DataFrame,
    start_row: int,
) -> dict[str, dict[str, int]]:
    """
    Write all summary tables and return row metadata for chart references.

    Keys: location, status, aging, action, top_excess
    Values: dict with header_row, first_data_row, last_data_row, value_col
    """
    meta: dict[str, dict[str, int]] = {}
    row = start_row

    loc_df = compute_location_summary(df)
    _, first, last = _write_table_block(
        ws,
        row,
        "Inventory Value by Location",
        ["Location", "Inventory Value"],
        loc_df[["location", "inventory_value"]].values.tolist(),
    )
    meta["location"] = {
        "header_row": row + 1,
        "first_data_row": first,
        "last_data_row": last,
        "value_col": 2,
    }
    row = last + 3

    status_df = compute_status_summary(df)
    _, first, last = _write_table_block(
        ws,
        row,
        "Inventory Status Breakdown",
        ["Status", "SKU Count", "Inventory Value"],
        status_df.values.tolist(),
    )
    meta["status"] = {
        "header_row": row + 1,
        "first_data_row": first,
        "last_data_row": last,
        "value_col": 2,
    }
    row = last + 3

    aging_df = compute_aging_summary(df)
    _, first, last = _write_table_block(
        ws,
        row,
        "Aging Bucket Summary",
        ["Aging Bucket", "SKU Count", "Inventory Value"],
        aging_df.values.tolist(),
    )
    meta["aging"] = {
        "header_row": row + 1,
        "first_data_row": first,
        "last_data_row": last,
        "value_col": 2,
    }
    row = last + 3

    action_df = compute_action_summary(df)
    _, first, last = _write_table_block(
        ws,
        row,
        "Recommended Action Summary",
        ["Recommended Action", "SKU Count", "Inventory Value"],
        action_df.values.tolist(),
    )
    meta["action"] = {
        "header_row": row + 1,
        "first_data_row": first,
        "last_data_row": last,
        "value_col": 2,
    }
    row = last + 3

    excess_df = compute_top_excess(df)
    _, first, last = _write_table_block(
        ws,
        row,
        "Top 10 Excess Inventory Items",
        ["SKU", "Product Name", "Location", "Excess Qty", "Excess Value"],
        excess_df.values.tolist(),
    )
    meta["top_excess"] = {
        "header_row": row + 1,
        "first_data_row": first,
        "last_data_row": last,
        "value_col": 5,
    }
    return meta


def _format_summary_tables(ws: Worksheet, meta: dict[str, dict[str, int]]) -> None:
    """Apply number formats to summary table value columns."""
    loc = meta["location"]
    if loc["last_data_row"] >= loc["first_data_row"]:
        format_currency_columns(ws, ["B"], loc["first_data_row"], loc["last_data_row"])

    status_info = meta["status"]
    if status_info["last_data_row"] >= status_info["first_data_row"]:
        format_integer_columns(
            ws, ["B"], status_info["first_data_row"], status_info["last_data_row"]
        )
        format_currency_columns(
            ws, ["C"], status_info["first_data_row"], status_info["last_data_row"]
        )

    aging = meta["aging"]
    if aging["last_data_row"] >= aging["first_data_row"]:
        format_integer_columns(
            ws, ["B"], aging["first_data_row"], aging["last_data_row"]
        )
        format_currency_columns(
            ws, ["C"], aging["first_data_row"], aging["last_data_row"]
        )

    action = meta["action"]
    if action["last_data_row"] >= action["first_data_row"]:
        format_integer_columns(
            ws, ["B"], action["first_data_row"], action["last_data_row"]
        )
        format_currency_columns(
            ws, ["C"], action["first_data_row"], action["last_data_row"]
        )

    excess = meta["top_excess"]
    if excess["last_data_row"] >= excess["first_data_row"]:
        format_integer_columns(
            ws, ["D"], excess["first_data_row"], excess["last_data_row"]
        )
        format_currency_columns(
            ws, ["E"], excess["first_data_row"], excess["last_data_row"]
        )


def _add_dashboard_charts(ws: Worksheet, meta: dict[str, dict[str, int]]) -> None:
    """Create bar and pie charts referencing summary tables."""
    loc = meta["location"]
    if loc["last_data_row"] >= loc["first_data_row"]:
        cats = make_category_reference(
            ws, 1, loc["first_data_row"], loc["last_data_row"]
        )
        data = make_data_reference(ws, 2, loc["header_row"], loc["last_data_row"])
        add_bar_chart(
            ws,
            "Inventory Value by Location",
            data,
            cats,
            anchor="F10",
            width=16,
            height=10,
            y_axis_title="Value ($)",
        )

    status = meta["status"]
    if status["last_data_row"] >= status["first_data_row"]:
        cats = make_category_reference(
            ws, 1, status["first_data_row"], status["last_data_row"]
        )
        data = make_data_reference(ws, 2, status["header_row"], status["last_data_row"])
        add_pie_chart(
            ws,
            "Inventory Status Breakdown",
            data,
            cats,
            anchor="F26",
            width=14,
            height=10,
        )

    aging = meta["aging"]
    if aging["last_data_row"] >= aging["first_data_row"]:
        cats = make_category_reference(
            ws, 1, aging["first_data_row"], aging["last_data_row"]
        )
        data = make_data_reference(ws, 3, aging["header_row"], aging["last_data_row"])
        add_bar_chart(
            ws,
            "Aging Bucket Summary",
            data,
            cats,
            anchor="F42",
            width=16,
            height=10,
            y_axis_title="Inventory Value ($)",
        )

    excess = meta["top_excess"]
    if excess["last_data_row"] >= excess["first_data_row"]:
        cats = make_category_reference(
            ws, 1, excess["first_data_row"], excess["last_data_row"]
        )
        data = make_data_reference(ws, 5, excess["header_row"], excess["last_data_row"])
        add_bar_chart(
            ws,
            "Top 10 Excess Inventory Items",
            data,
            cats,
            anchor="F58",
            width=16,
            height=10,
            y_axis_title="Excess Value ($)",
        )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Inventory Dashboard from the inventory DataFrame."""
    data = context["data"]
    df: pd.DataFrame = data.get("inventory", pd.DataFrame())
    end_row = _data_end_row(len(df))

    _write_title_banner(ws)
    apply_section_header_style(ws, 2, 1, "Key Performance Indicators", span_cols=10)
    _write_kpi_cards(ws, MASTER_DATA_START, end_row)
    _write_classification_kpi_cards(ws, data)

    table_meta = _write_summary_tables(ws, df, SUMMARY_START_ROW)
    _format_summary_tables(ws, table_meta)
    _add_dashboard_charts(ws, table_meta)

    set_column_widths(ws, {"A": 22, "B": 14, "C": 16, "D": 14, "E": 14, "F": 4})
    autosize_columns(ws, min_width=10, max_width=28)
    ws.sheet_view.showGridLines = False
    set_landscape_print(ws, fit_width=1, repeat_header_rows="1:1")
