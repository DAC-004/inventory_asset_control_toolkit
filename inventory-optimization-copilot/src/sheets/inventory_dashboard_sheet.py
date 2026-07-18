"""Inventory Dashboard sheet — leadership KPIs, summaries, and charts."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from config.workbook_config import AS_OF_DATE
from src.domain.constants import MASTER_DATA_START
from src.services.classification_service import compute_dashboard_classification_kpis
from src.services.kpi_dashboard_service import (
    compute_abc_usage_summary,
    compute_action_summary,
    compute_aging_summary,
    compute_fill_rate_by_location,
    compute_location_summary,
    compute_planning_service_kpis,
    compute_procurement_network_kpis,
    compute_replenishment_status_summary,
    compute_status_summary,
    compute_top_excess,
    compute_transfer_benefit_summary,
    compute_vendor_risk_summary,
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
    add_internal_sheet_link,
    autosize_columns,
    create_excel_table,
    format_currency_columns,
    format_integer_columns,
    format_percentage_columns,
    set_column_widths,
    set_landscape_print,
)

TITLE_ROW = 1
TABLES_START_ROW = 24
DASHBOARD_TABLE_PREFIX = "Dashboard"


def _data_end_row(record_count: int) -> int:
    if record_count <= 0:
        return MASTER_DATA_START
    return MASTER_DATA_START + record_count - 1


def _write_title_banner(ws: Worksheet) -> None:
    ws.merge_cells(start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=9)
    cell = ws.cell(
        row=TITLE_ROW,
        column=1,
        value=f"Inventory Dashboard — As of {AS_OF_DATE.strftime('%B %d, %Y')}",
    )
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    cell.fill = sc.HEADER_FILL
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[TITLE_ROW].height = 30
    add_internal_sheet_link(ws, TITLE_ROW, 10, "README", "← README")


def _apply_kpi_value_format(ws: Worksheet, row: int, col: int, fmt: str) -> None:
    cell = ws.cell(row=row, column=col)
    if fmt == "currency":
        cell.number_format = sc.NUMBER_FORMATS["currency_compact"]
    elif fmt == "percentage":
        cell.number_format = sc.NUMBER_FORMATS["percentage"]
    elif fmt == "decimal":
        cell.number_format = "0.00"
    else:
        cell.number_format = sc.NUMBER_FORMATS["integer"]


def _write_kpi_section(
    ws: Worksheet,
    section_row: int,
    title: str,
    cards: list[tuple[str, Any, str]],
    cards_per_row: int = 3,
) -> int:
    """Write a KPI section and return the row after the last KPI value row."""
    apply_section_header_style(ws, section_row, 1, title, span_cols=10)
    card_cols = [1, 4, 7, 10][:cards_per_row]
    title_row = section_row + 1
    value_row = section_row + 2
    for idx, (label, value, fmt) in enumerate(cards):
        row_offset = (idx // cards_per_row) * 2
        col = card_cols[idx % cards_per_row]
        apply_kpi_card_style(
            ws,
            title_row + row_offset,
            col,
            value_row + row_offset,
            col,
            label,
            value,
            span_cols=2,
        )
        _apply_kpi_value_format(ws, value_row + row_offset, col, fmt)
    rows_used = 2 * ((len(cards) + cards_per_row - 1) // cards_per_row)
    return section_row + rows_used + 1


def _write_table_block(
    ws: Worksheet,
    start_row: int,
    section_title: str,
    headers: list[str],
    data_rows: list[list[Any]],
    table_name: str,
) -> tuple[int, int, int]:
    apply_section_header_style(ws, start_row, 1, section_title, span_cols=len(headers))
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
    end_col = chr(ord("A") + len(headers) - 1)
    create_excel_table(
        ws,
        table_name,
        f"A{header_row}:{end_col}{max(last_data_row, header_row)}",
    )
    return header_row, first_data_row, last_data_row


def _write_summary_tables(
    ws: Worksheet,
    df: pd.DataFrame,
    data: dict[str, Any],
    start_row: int,
) -> dict[str, dict[str, int]]:
    meta: dict[str, dict[str, int]] = {}
    row = start_row
    table_idx = 0

    blocks: list[tuple[str, list[str], pd.DataFrame, list[str], int]] = [
        (
            "Inventory Value by Location",
            ["Location", "Inventory Value"],
            compute_location_summary(df),
            ["location", "inventory_value"],
            2,
        ),
        (
            "Inventory Status Breakdown",
            ["Status", "SKU Count", "Inventory Value"],
            compute_status_summary(df),
            ["status", "sku_count", "inventory_value"],
            2,
        ),
        (
            "Aging Bucket Summary",
            ["Aging Bucket", "SKU Count", "Inventory Value"],
            compute_aging_summary(df),
            ["aging_bucket", "sku_count", "inventory_value"],
            3,
        ),
        (
            "Top 10 Excess Inventory Items",
            ["SKU", "Product Name", "Location", "Excess Qty", "Excess Value"],
            compute_top_excess(df),
            ["sku", "product_name", "location", "excess_qty", "excess_value"],
            5,
        ),
        (
            "ABC Annual Usage Value",
            ["ABC Class", "Annual Usage Value"],
            compute_abc_usage_summary(data),
            ["abc_class", "annual_usage_value"],
            2,
        ),
        (
            "Replenishment Status",
            ["Status", "SKU Count"],
            compute_replenishment_status_summary(data),
            ["status", "sku_count"],
            2,
        ),
        (
            "Fill Rate by Location",
            ["Location", "Unit Fill Rate"],
            compute_fill_rate_by_location(data),
            ["location", "unit_fill_rate"],
            2,
        ),
        (
            "Vendor Risk Distribution",
            ["Risk Class", "Vendor Count"],
            compute_vendor_risk_summary(data),
            ["risk_class", "vendor_count"],
            2,
        ),
        (
            "Transfer Net Benefit (Top Lanes)",
            ["Lane", "Net Benefit"],
            compute_transfer_benefit_summary(data),
            ["lane", "net_benefit"],
            2,
        ),
        (
            "Recommended Action Summary",
            ["Recommended Action", "SKU Count", "Inventory Value"],
            compute_action_summary(df),
            ["recommended_action", "sku_count", "inventory_value"],
            2,
        ),
    ]

    key_names = [
        "location",
        "status",
        "aging",
        "top_excess",
        "abc_usage",
        "replenishment",
        "fill_rate",
        "vendor_risk",
        "transfer_benefit",
        "action",
    ]

    for key, (title, headers, summary_df, cols, value_col) in zip(
        key_names, blocks, strict=True
    ):
        table_idx += 1
        rows = summary_df[cols].values.tolist() if not summary_df.empty else []
        _, first, last = _write_table_block(
            ws,
            row,
            title,
            headers,
            rows,
            f"{DASHBOARD_TABLE_PREFIX}{table_idx}Table",
        )
        meta[key] = {
            "header_row": row + 1,
            "first_data_row": first,
            "last_data_row": last,
            "value_col": value_col,
        }
        row = last + 3

    return meta


def _format_summary_tables(ws: Worksheet, meta: dict[str, dict[str, int]]) -> None:
    currency_cols = {
        "location": ["B"],
        "status": ["C"],
        "aging": ["C"],
        "top_excess": ["E"],
        "abc_usage": ["B"],
        "action": ["C"],
        "transfer_benefit": ["B"],
    }
    integer_cols = {
        "status": ["B"],
        "aging": ["B"],
        "top_excess": ["D"],
        "replenishment": ["B"],
        "vendor_risk": ["B"],
        "action": ["B"],
    }
    pct_cols = {"fill_rate": ["B"]}

    for key, cols in currency_cols.items():
        info = meta.get(key)
        if info and info["last_data_row"] >= info["first_data_row"]:
            format_currency_columns(
                ws, cols, info["first_data_row"], info["last_data_row"]
            )
    for key, cols in integer_cols.items():
        info = meta.get(key)
        if info and info["last_data_row"] >= info["first_data_row"]:
            format_integer_columns(
                ws, cols, info["first_data_row"], info["last_data_row"]
            )
    info = meta.get("fill_rate")
    if info and info["last_data_row"] >= info["first_data_row"]:
        format_percentage_columns(
            ws, pct_cols["fill_rate"], info["first_data_row"], info["last_data_row"]
        )


def _add_dashboard_charts(ws: Worksheet, meta: dict[str, dict[str, int]]) -> None:
    pie_keys = {"status", "replenishment", "vendor_risk", "action"}
    chart_specs: list[tuple[str, str, str, int, str | None]] = [
        ("location", "Inventory Value by Location", "F10", 16, "Value ($)"),
        ("status", "Inventory Status", "F26", 14, None),
        ("aging", "Aging Buckets", "F42", 16, "Inventory Value ($)"),
        ("top_excess", "Top Excess Items", "F58", 16, "Excess Value ($)"),
        ("abc_usage", "ABC Annual Usage Value", "L10", 14, "Usage Value ($)"),
        ("replenishment", "Replenishment Status", "L26", 14, None),
        ("fill_rate", "Fill Rate by Location", "L42", 14, "Fill Rate"),
        ("vendor_risk", "Vendor Risk", "L58", 14, None),
        ("transfer_benefit", "Transfer Net Benefit", "F74", 16, "Net Benefit ($)"),
        ("action", "Recommended Actions", "L74", 14, None),
    ]

    for key, title, anchor, width, y_title in chart_specs:
        info = meta.get(key)
        if not info or info["last_data_row"] < info["first_data_row"]:
            continue
        cats = make_category_reference(
            ws, 1, info["first_data_row"], info["last_data_row"]
        )
        value_col = info["value_col"]
        data = make_data_reference(
            ws, value_col, info["header_row"], info["last_data_row"]
        )
        if key in pie_keys:
            pie_data = make_data_reference(
                ws, 2, info["header_row"], info["last_data_row"]
            )
            add_pie_chart(
                ws, title, pie_data, cats, anchor=anchor, width=width, height=10
            )
        else:
            add_bar_chart(
                ws,
                title,
                data,
                cats,
                anchor=anchor,
                width=width,
                height=10,
                y_axis_title=y_title,
            )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Inventory Dashboard from generated workbook data."""
    data = context["data"]
    df: pd.DataFrame = data.get("inventory", pd.DataFrame())
    end_row = _data_end_row(len(df))

    _write_title_banner(ws)

    next_row = _write_kpi_section(
        ws,
        2,
        "Inventory Health",
        [
            (t, f, fmt)
            for t, f, fmt in dashboard_kpi_definitions(MASTER_DATA_START, end_row)
        ],
    )

    class_kpis = compute_dashboard_classification_kpis(data)
    next_row = _write_kpi_section(
        ws,
        next_row,
        "Classification & Control",
        [
            ("Class A SKUs", class_kpis["abc_a_count"], "integer"),
            ("Class B SKUs", class_kpis["abc_b_count"], "integer"),
            ("Class C SKUs", class_kpis["abc_c_count"], "integer"),
            ("Enterprise Turnover", class_kpis["enterprise_turnover"], "decimal"),
            ("Avg Financial DOH", class_kpis["avg_financial_doh"], "decimal"),
            ("Avg Coverage Days", class_kpis["avg_coverage_days"], "decimal"),
            ("Unit Accuracy %", class_kpis["avg_unit_accuracy_pct"], "percentage"),
            ("Overdue Cycle Counts", class_kpis["overdue_count"], "integer"),
        ],
        cards_per_row=4,
    )

    planning = compute_planning_service_kpis(data)
    next_row = _write_kpi_section(
        ws,
        next_row,
        "Planning & Service",
        [
            ("Below Reorder Point", planning["below_reorder_point"], "integer"),
            (
                "Recommended Order Value",
                planning["recommended_order_value"],
                "currency",
            ),
            ("Unit Fill Rate", planning["unit_fill_rate"], "percentage"),
            ("Line Fill Rate", planning["line_fill_rate"], "percentage"),
            ("Order Fill Rate", planning["order_fill_rate"], "percentage"),
            ("Forecast WAPE", planning["forecast_wape"], "percentage"),
            ("Forecast Bias", planning["forecast_bias"], "decimal"),
        ],
        cards_per_row=4,
    )

    procurement = compute_procurement_network_kpis(data)
    _write_kpi_section(
        ws,
        next_row,
        "Procurement & Network",
        [
            ("Open PO Value", procurement["open_po_value"], "currency"),
            ("Late PO Count", procurement["late_po_count"], "integer"),
            ("Vendor OTIF", procurement["vendor_otif"], "percentage"),
            ("High-Risk Vendors", procurement["high_risk_vendors"], "integer"),
            (
                "Recommended Transfer Units",
                procurement["recommended_transfer_units"],
                "integer",
            ),
            ("Transfer Net Benefit", procurement["transfer_net_benefit"], "currency"),
            ("Remaining Shortage", procurement["remaining_shortage"], "integer"),
        ],
        cards_per_row=4,
    )

    table_meta = _write_summary_tables(ws, df, data, TABLES_START_ROW)
    _format_summary_tables(ws, table_meta)
    _add_dashboard_charts(ws, table_meta)

    set_column_widths(ws, {"A": 22, "B": 14, "C": 16, "D": 14, "E": 14, "F": 4})
    autosize_columns(ws, min_width=10, max_width=30)
    ws.sheet_view.showGridLines = False
    set_landscape_print(ws, fit_width=1, repeat_header_rows=f"{TITLE_ROW}:{TITLE_ROW}")
