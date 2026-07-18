"""Inventory Dashboard sheet — fixed A:R table/chart section grid."""

from __future__ import annotations

from typing import Any

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
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
from src.sheets.dashboard_layout import (
    CHART_ANCHOR_COL,
    CHART_HEIGHT_CM,
    CHART_WIDTH_CM,
    DASHBOARD_CANVAS_COLS,
    DASHBOARD_COLUMN_WIDTHS,
    DASHBOARD_SECTIONS,
    DATA_ROW_HEIGHT,
    FREEZE_PANE,
    SECTION_TITLE_HEIGHT,
    TABLE_AREA_END_COL,
    TABLE_HEADER_HEIGHT,
)
from src.workbook.charts import (
    add_bar_chart,
    add_clustered_bar_chart,
    add_doughnut_chart,
    make_category_reference,
    make_data_reference,
)
from src.workbook.styles import apply_kpi_card_style, apply_table_header_style
from src.workbook.utils import (
    add_internal_sheet_link,
    create_excel_table,
    format_currency_columns,
    format_integer_columns,
    format_percentage_columns,
    set_column_widths,
    set_landscape_print,
)

DASHBOARD_TABLE_PREFIX = "Dashboard"
MAX_TABLE_DATA_ROWS = 15
DOUGHNUT_MAX_CATEGORIES = 5

# Backward-compatible exports for tests
LAYOUT_COLS = DASHBOARD_CANVAS_COLS
CHART_BAR_WIDTH_CM = CHART_WIDTH_CM
CHART_MAX_HEIGHT_CM = CHART_HEIGHT_CM


def _data_end_row(record_count: int) -> int:
    if record_count <= 0:
        return MASTER_DATA_START
    return MASTER_DATA_START + record_count - 1


def _clear_dashboard_charts(ws: Worksheet) -> int:
    """Remove all chart objects before rebuilding layout."""
    count = len(ws._charts)
    ws._charts.clear()
    return count


def _apply_canvas_columns(ws: Worksheet) -> None:
    """Explicit column visibility and widths for dashboard canvas A:R."""
    set_column_widths(ws, DASHBOARD_COLUMN_WIDTHS)
    for col_idx in range(1, DASHBOARD_CANVAS_COLS + 1):
        letter = get_column_letter(col_idx)
        dim = ws.column_dimensions[letter]
        dim.hidden = False
        if dim.width is None or dim.width <= 0:
            dim.width = DASHBOARD_COLUMN_WIDTHS.get(letter, 12)


def _write_header_and_kpis(ws: Worksheet, end_row: int, data: dict[str, Any]) -> None:
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=17)
    title_cell = ws.cell(
        row=1,
        column=1,
        value=f"Inventory Dashboard — As of {AS_OF_DATE.strftime('%B %d, %Y')}",
    )
    title_cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    title_cell.fill = sc.HEADER_FILL
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    add_internal_sheet_link(ws, 1, 18, "README", "← README")

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=18)
    desc = ws.cell(
        row=2,
        column=1,
        value=(
            "Executive snapshot of inventory health, classification, planning, "
            "service, procurement, and network optimization."
        ),
    )
    desc.font = Font(name=sc.FONTS["default_name"], size=sc.FONTS["body_size"])
    desc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[2].height = 22

    kpi_cards: list[tuple[str, Any, str]] = []
    kpi_cards.extend(
        (title, formula, fmt)
        for title, formula, fmt in dashboard_kpi_definitions(MASTER_DATA_START, end_row)
    )
    class_kpis = compute_dashboard_classification_kpis(data)
    kpi_cards.extend(
        [
            ("Class A SKUs", class_kpis["abc_a_count"], "integer"),
            ("Class B SKUs", class_kpis["abc_b_count"], "integer"),
            ("Class C SKUs", class_kpis["abc_c_count"], "integer"),
            ("Enterprise Turnover", class_kpis["enterprise_turnover"], "decimal"),
            ("Avg Financial DOH", class_kpis["avg_financial_doh"], "decimal"),
            ("Avg Coverage Days", class_kpis["avg_coverage_days"], "decimal"),
            ("Unit Accuracy %", class_kpis["avg_unit_accuracy_pct"], "percentage"),
            ("Overdue Cycle Counts", class_kpis["overdue_count"], "integer"),
        ]
    )
    planning = compute_planning_service_kpis(data)
    kpi_cards.extend(
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
        ]
    )
    procurement = compute_procurement_network_kpis(data)
    kpi_cards.extend(
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
        ]
    )

    cards_per_row = 7
    span_cols = 2
    start_row = 3
    for idx, (label, value, fmt) in enumerate(kpi_cards):
        band = idx // cards_per_row
        col = 1 + (idx % cards_per_row) * span_cols
        title_row = start_row + band * 2
        value_row = title_row + 1
        apply_kpi_card_style(
            ws, title_row, col, value_row, col, label, value, span_cols=span_cols
        )
        value_cell = ws.cell(row=value_row, column=col)
        if fmt == "currency":
            value_cell.number_format = sc.NUMBER_FORMATS["currency_compact"]
        elif fmt == "percentage":
            value_cell.number_format = sc.NUMBER_FORMATS["percentage"]
        elif fmt == "decimal":
            value_cell.number_format = "0.00"
        else:
            value_cell.number_format = sc.NUMBER_FORMATS["integer"]
        ws.row_dimensions[title_row].height = 18
        ws.row_dimensions[value_row].height = 22


def _section_border() -> Border:
    side = Side(style="thin", color=sc.COLORS["border_gray"])
    return Border(left=side, right=side, top=side, bottom=side)


def _write_section_title(ws: Worksheet, section_row: int, title: str) -> None:
    ws.merge_cells(
        start_row=section_row,
        start_column=1,
        end_row=section_row,
        end_column=DASHBOARD_CANVAS_COLS,
    )
    cell = ws.cell(row=section_row, column=1, value=title)
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["body_size"],
    )
    cell.fill = PatternFill(
        start_color=sc.COLORS["navy"],
        end_color=sc.COLORS["navy"],
        fill_type="solid",
    )
    cell.alignment = Alignment(horizontal="left", vertical="center")
    cell.border = _section_border()
    ws.row_dimensions[section_row].height = SECTION_TITLE_HEIGHT


def _apply_section_frame(
    ws: Worksheet, start_row: int, end_row: int, last_data_row: int
) -> None:
    """Light border and subtle background around the section block."""
    fill = PatternFill(
        start_color=sc.COLORS["gray"],
        end_color=sc.COLORS["gray"],
        fill_type="solid",
    )
    border = _section_border()
    content_end = max(last_data_row, start_row + 1)
    for row in range(start_row + 1, min(end_row, content_end) + 1):
        for col in range(1, DASHBOARD_CANVAS_COLS + 1):
            cell = ws.cell(row=row, column=col)
            if col <= TABLE_AREA_END_COL:
                cell.fill = fill
            cell.border = border


def _write_section_table(
    ws: Worksheet,
    section: Any,
    headers: list[str],
    rows: list[list[Any]],
    table_name: str,
) -> dict[str, int]:
    _write_section_title(ws, section.start_row, section.title)
    header_row = section.start_row + 1
    trimmed = rows[:MAX_TABLE_DATA_ROWS]

    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=header_row, column=col_idx, value=header)
    apply_table_header_style(ws, header_row, len(headers))
    ws.row_dimensions[header_row].height = TABLE_HEADER_HEIGHT

    first_data_row = header_row + 1
    wrap = Alignment(horizontal="left", vertical="center", wrap_text=True)
    for row_offset, row_values in enumerate(trimmed):
        excel_row = first_data_row + row_offset
        ws.row_dimensions[excel_row].height = DATA_ROW_HEIGHT
        for col_idx, value in enumerate(row_values, start=1):
            cell = ws.cell(row=excel_row, column=col_idx, value=value)
            cell.alignment = wrap

    last_data_row = first_data_row + len(trimmed) - 1 if trimmed else header_row
    table_end_col = get_column_letter(min(len(headers), TABLE_AREA_END_COL))
    create_excel_table(
        ws,
        table_name,
        f"A{header_row}:{table_end_col}{max(last_data_row, header_row)}",
    )
    _apply_section_frame(ws, section.start_row, section.end_row, last_data_row)
    return {
        "header_row": header_row,
        "first_data_row": first_data_row,
        "last_data_row": last_data_row,
        "table_cols": len(headers),
    }


def _section_dataframes(
    df: pd.DataFrame, data: dict[str, Any]
) -> dict[str, tuple[list[str], pd.DataFrame, list[str]]]:
    return {
        "location": (
            ["Location", "Inventory Value", "Percent of Total"],
            compute_location_summary(df),
            ["location", "inventory_value", "percent_of_total"],
        ),
        "status": (
            [
                "Inventory Status",
                "SKU-Location Count",
                "Inventory Value",
                "Percent of Total",
            ],
            compute_status_summary(df),
            [
                "inventory_status",
                "sku_location_count",
                "inventory_value",
                "percent_of_total",
            ],
        ),
        "aging": (
            [
                "Aging Bucket",
                "SKU-Location Count",
                "Inventory Value",
                "Percent of Total",
            ],
            compute_aging_summary(df),
            [
                "aging_bucket",
                "sku_location_count",
                "inventory_value",
                "percent_of_total",
            ],
        ),
        "top_excess": (
            [
                "Rank",
                "SKU",
                "Product Name",
                "Location",
                "Excess Quantity",
                "Excess Value",
            ],
            compute_top_excess(df),
            [
                "rank",
                "sku",
                "product_name",
                "location",
                "excess_quantity",
                "excess_value",
            ],
        ),
        "abc_usage": (
            [
                "ABC Class",
                "SKU Count",
                "Annual Usage Value",
                "Percent of Annual Usage Value",
            ],
            compute_abc_usage_summary(data),
            [
                "abc_class",
                "sku_count",
                "annual_usage_value",
                "percent_of_annual_usage_value",
            ],
        ),
        "replenishment": (
            [
                "Replenishment Status",
                "SKU-Location Count",
                "Recommended Order Quantity",
                "Recommended Order Value",
            ],
            compute_replenishment_status_summary(data),
            [
                "replenishment_status",
                "sku_location_count",
                "recommended_order_quantity",
                "recommended_order_value",
            ],
        ),
        "fill_rate": (
            [
                "Location",
                "Unit Fill Rate",
                "Line Fill Rate",
                "Order Fill Rate",
                "Service Status",
            ],
            compute_fill_rate_by_location(data),
            [
                "location",
                "unit_fill_rate",
                "line_fill_rate",
                "order_fill_rate",
                "service_status",
            ],
        ),
        "vendor_risk": (
            [
                "Vendor Risk Class",
                "Supplier Count",
                "Open PO Value",
                "Average Vendor Score",
            ],
            compute_vendor_risk_summary(data),
            [
                "vendor_risk_class",
                "supplier_count",
                "open_po_value",
                "average_vendor_score",
            ],
        ),
        "transfer_benefit": (
            [
                "Rank",
                "Source Location",
                "Destination Location",
                "SKU",
                "Transfer Quantity",
                "Net Benefit",
            ],
            compute_transfer_benefit_summary(data),
            [
                "rank",
                "source_location",
                "destination_location",
                "sku",
                "transfer_quantity",
                "net_benefit",
            ],
        ),
        "action": (
            [
                "Recommended Action",
                "Record Count",
                "Inventory Value",
                "Estimated Financial Impact",
            ],
            compute_action_summary(df),
            [
                "recommended_action",
                "record_count",
                "inventory_value",
                "estimated_financial_impact",
            ],
        ),
    }


def _format_section_table(ws: Worksheet, key: str, meta: dict[str, int]) -> None:
    first = meta["first_data_row"]
    last = meta["last_data_row"]
    if last < first:
        return

    currency_map = {
        "location": ["B"],
        "status": ["C"],
        "aging": ["C"],
        "top_excess": ["F"],
        "abc_usage": ["C"],
        "replenishment": ["D"],
        "vendor_risk": ["C"],
        "transfer_benefit": ["F"],
        "action": ["C", "D"],
    }
    integer_map = {
        "status": ["B"],
        "aging": ["B"],
        "top_excess": ["A", "E"],
        "abc_usage": ["B"],
        "replenishment": ["B", "C"],
        "vendor_risk": ["B"],
        "transfer_benefit": ["A", "E"],
        "action": ["B"],
    }
    pct_map = {
        "location": ["C"],
        "status": ["D"],
        "aging": ["D"],
        "abc_usage": ["D"],
        "fill_rate": ["B", "C", "D"],
    }

    if key in currency_map:
        format_currency_columns(ws, currency_map[key], first, last)
    if key in integer_map:
        format_integer_columns(ws, integer_map[key], first, last)
    if key in pct_map:
        format_percentage_columns(ws, pct_map[key], first, last)
    if key == "vendor_risk":
        for row in range(first, last + 1):
            ws.cell(row=row, column=4).number_format = "0.0"


def _category_count(meta: dict[str, int]) -> int:
    if meta["last_data_row"] < meta["first_data_row"]:
        return 0
    return meta["last_data_row"] - meta["first_data_row"] + 1


def _add_section_chart(
    ws: Worksheet,
    section: Any,
    meta: dict[str, int],
) -> None:
    if meta["last_data_row"] < meta["first_data_row"]:
        return

    anchor = f"{CHART_ANCHOR_COL}{meta['header_row']}"
    cats = make_category_reference(ws, 1, meta["first_data_row"], meta["last_data_row"])
    count = _category_count(meta)
    w, h = CHART_WIDTH_CM, CHART_HEIGHT_CM

    if section.key == "location":
        data = make_data_reference(ws, 2, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            horizontal=True,
            y_axis_title="Value ($)",
            hide_legend=True,
            tick_label_skip=1 if count <= 8 else 2,
        )
    elif section.key == "status":
        data = make_data_reference(ws, 2, meta["header_row"], meta["last_data_row"])
        if count <= DOUGHNUT_MAX_CATEGORIES:
            add_doughnut_chart(
                ws,
                section.chart_title,
                data,
                cats,
                anchor=anchor,
                width=w,
                height=h,
                legend_position="r",
            )
        else:
            add_bar_chart(
                ws,
                section.chart_title,
                data,
                cats,
                anchor=anchor,
                width=w,
                height=h,
                hide_legend=True,
            )
    elif section.key == "aging":
        data = make_data_reference(ws, 3, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            y_axis_title="Inventory Value ($)",
            hide_legend=True,
        )
    elif section.key == "top_excess":
        data = make_data_reference(ws, 6, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            horizontal=True,
            y_axis_title="Excess Value ($)",
            hide_legend=True,
        )
    elif section.key == "abc_usage":
        data = make_data_reference(ws, 3, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            y_axis_title="Usage Value ($)",
            hide_legend=True,
        )
    elif section.key == "replenishment":
        data = make_data_reference(ws, 2, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            hide_legend=True,
        )
    elif section.key == "fill_rate":
        refs = [
            make_data_reference(ws, col, meta["header_row"], meta["last_data_row"])
            for col in (2, 3, 4)
        ]
        add_clustered_bar_chart(
            ws,
            section.chart_title,
            refs,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            horizontal=True,
            y_axis_title="Fill Rate",
        )
    elif section.key == "vendor_risk":
        data = make_data_reference(ws, 2, meta["header_row"], meta["last_data_row"])
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            cats,
            anchor=anchor,
            width=w,
            height=h,
            hide_legend=True,
        )
    elif section.key == "transfer_benefit":
        data = make_data_reference(ws, 6, meta["header_row"], meta["last_data_row"])
        rank_cats = make_category_reference(
            ws, 1, meta["first_data_row"], meta["last_data_row"]
        )
        add_bar_chart(
            ws,
            section.chart_title,
            data,
            rank_cats,
            anchor=anchor,
            width=w,
            height=h,
            horizontal=True,
            y_axis_title="Net Benefit ($)",
            hide_legend=True,
        )
    elif section.key == "action":
        data = make_data_reference(ws, 2, meta["header_row"], meta["last_data_row"])
        if count <= DOUGHNUT_MAX_CATEGORIES:
            add_doughnut_chart(
                ws,
                section.chart_title,
                data,
                cats,
                anchor=anchor,
                width=w,
                height=h,
                legend_position="r",
            )
        else:
            add_bar_chart(
                ws,
                section.chart_title,
                data,
                cats,
                anchor=anchor,
                width=w,
                height=h,
                hide_legend=True,
            )


def _apply_view_settings(ws: Worksheet, last_row: int) -> None:
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    ws.freeze_panes = FREEZE_PANE
    ws.sheet_view.selection[0].activeCell = "A1"
    ws.sheet_view.selection[0].sqref = "A1"
    ws.print_area = f"A1:R{last_row}"


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Inventory Dashboard from generated workbook data."""
    data = context["data"]
    df: pd.DataFrame = data.get("inventory", pd.DataFrame())
    end_row = _data_end_row(len(df))

    charts_before = _clear_dashboard_charts(ws)
    context["_dashboard_charts_before_cleanup"] = charts_before

    _apply_canvas_columns(ws)
    _write_header_and_kpis(ws, end_row, data)

    section_meta: dict[str, dict[str, int]] = {}
    datasets = _section_dataframes(df, data)

    for idx, section in enumerate(DASHBOARD_SECTIONS, start=1):
        headers, summary_df, cols = datasets[section.key]
        rows = summary_df[cols].values.tolist() if not summary_df.empty else []
        meta = _write_section_table(
            ws,
            section,
            headers,
            rows,
            f"{DASHBOARD_TABLE_PREFIX}{idx}Table",
        )
        section_meta[section.key] = meta
        _format_section_table(ws, section.key, meta)
        _add_section_chart(ws, section, meta)

    last_row = DASHBOARD_SECTIONS[-1].end_row
    _apply_view_settings(ws, last_row)
    set_landscape_print(ws, fit_width=1, repeat_header_rows="1:2")

    context["_dashboard_section_meta"] = section_meta
