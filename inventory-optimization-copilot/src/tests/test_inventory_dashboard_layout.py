"""Automated layout verification for Inventory Dashboard A:V grid."""

from __future__ import annotations

import re
from dataclasses import dataclass

from openpyxl import Workbook, load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter

from src.main import generate_all_data
from src.sheets.dashboard_layout import (
    CHART_AREA_END_COL,
    CHART_AREA_START_COL,
    CHART_MAX_HEIGHT_CM,
    CHART_MAX_WIDTH_CM,
    CHART_MIN_HEIGHT_CM,
    CHART_MIN_WIDTH_CM,
    CHART_TITLES,
    DASHBOARD_CANVAS_COLS,
    DASHBOARD_COLUMN_WIDTHS,
    DASHBOARD_SECTIONS,
    TABLE_AREA_END_COL,
    chart_layout_specs,
)
from src.sheets.inventory_dashboard_sheet import build


@dataclass
class ChartBounds:
    name: str
    anchor_col: int
    anchor_row: int
    end_col: int
    end_row: int


def _anchor_col_row(chart) -> tuple[int, int]:
    anchor = chart.anchor
    if hasattr(anchor, "_from"):
        return anchor._from.col + 1, anchor._from.row + 1
    text = str(anchor)
    col_letter = "".join(ch for ch in text if ch.isalpha())
    row_num = int("".join(ch for ch in text if ch.isdigit()))
    return column_index_from_string(col_letter), row_num


def _chart_bounds(chart) -> ChartBounds:
    col, row = _anchor_col_row(chart)
    width_cm = float(chart.width)
    height_cm = float(chart.height)
    end_col = col + max(1, int(round(width_cm / 2.0)))
    end_row = row + max(1, int(round(height_cm / 0.4)))
    title = chart.title
    if title and title.tx and title.tx.rich and title.tx.rich.paragraphs:
        name = title.tx.rich.paragraphs[0].r[0].t
    else:
        name = str(chart.title)
    return ChartBounds(name, col, row, end_col, end_row)


def _charts_overlap(a: ChartBounds, b: ChartBounds) -> bool:
    if a.end_col < b.anchor_col or b.end_col < a.anchor_col:
        return False
    if a.end_row < b.anchor_row or b.end_row < a.anchor_row:
        return False
    return True


def _build_dashboard_ws():
    wb = Workbook()
    ws = wb.active
    build(ws, {"data": generate_all_data()})
    return ws


def test_dashboard_layout_chart_count_and_specs():
    ws = _build_dashboard_ws()
    specs = chart_layout_specs()
    assert len(ws._charts) == 10
    assert len(specs) == 10

    anchors = []
    for chart in ws._charts:
        col, row = _anchor_col_row(chart)
        anchors.append((col, row))
        assert col >= CHART_AREA_START_COL
        assert col <= CHART_AREA_END_COL
        assert CHART_MIN_WIDTH_CM <= chart.width <= CHART_MAX_WIDTH_CM + 1
        assert CHART_MIN_HEIGHT_CM <= chart.height <= CHART_MAX_HEIGHT_CM + 1

    assert len(set(anchors)) == 10


def test_dashboard_layout_sections_and_columns():
    ws = _build_dashboard_ws()
    specs = chart_layout_specs()

    for section_spec, layout_spec in zip(DASHBOARD_SECTIONS, specs, strict=True):
        assert ws.cell(row=section_spec.start_row, column=1).value == section_spec.title
        header_row = section_spec.start_row + 2
        chart_for_section = [
            c
            for c in ws._charts
            if _anchor_col_row(c)[1] == header_row
            and _anchor_col_row(c)[0] >= CHART_AREA_START_COL
        ]
        assert len(chart_for_section) == 1
        col, row = _anchor_col_row(chart_for_section[0])
        assert layout_spec.anchor_cell == f"{get_column_letter(col)}{row}"

    for col_idx in range(1, DASHBOARD_CANVAS_COLS + 1):
        letter = get_column_letter(col_idx)
        dim = ws.column_dimensions[letter]
        assert dim.hidden is False
        assert (dim.width or 0) > 0

    for letter in "EFGHIJKLMNOP":
        assert (ws.column_dimensions[letter].width or 0) > 0


def test_dashboard_layout_no_chart_table_overlap():
    ws = _build_dashboard_ws()
    title_to_section = {s.chart_title: s for s in DASHBOARD_SECTIONS}
    for chart in ws._charts:
        title = chart.title.tx.rich.paragraphs[0].r[0].t
        section = title_to_section[title]
        col, row = _anchor_col_row(chart)
        assert col >= CHART_AREA_START_COL
        assert col <= CHART_AREA_END_COL
        assert col > TABLE_AREA_END_COL
        assert section.start_row <= row <= section.end_row


def test_dashboard_layout_freeze_and_view():
    ws = _build_dashboard_ws()
    assert ws.freeze_panes == "A9"
    assert ws.sheet_view.showGridLines is False
    assert ws.sheet_view.zoomScale == 85
    assert ws.print_area is not None
    assert "V" in ws.print_area


def test_dashboard_workbook_integrity(tmp_path):
    ws = _build_dashboard_ws()
    path = tmp_path / "dashboard_test.xlsx"
    ws.parent.save(path)
    reloaded = load_workbook(path)
    assert len(reloaded.active._charts) == 10
    reloaded.save(path)


def test_dashboard_column_widths_match_spec():
    ws = _build_dashboard_ws()
    for letter, expected in DASHBOARD_COLUMN_WIDTHS.items():
        assert ws.column_dimensions[letter].width == expected


def test_dashboard_chart_titles_are_business_focused():
    ws = _build_dashboard_ws()
    titles = []
    for chart in ws._charts:
        title = chart.title.tx.rich.paragraphs[0].r[0].t
        titles.append(title)
        assert title not in {"Status", "Aging", "ABC", "Vendor", "Actions", "Summary"}
    assert set(titles) == set(CHART_TITLES.values())


def test_dashboard_chart_layout_spec_registry():
    specs = chart_layout_specs()
    assert len({s.name for s in specs}) == 10
    for spec in specs:
        assert spec.allowed_start_col == CHART_AREA_START_COL
        assert spec.allowed_end_col == CHART_AREA_END_COL
        assert re.fullmatch(r"J\d+", spec.anchor_cell)
