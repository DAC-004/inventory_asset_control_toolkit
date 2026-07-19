"""Dashboard chart quality and presentation tests."""

from __future__ import annotations

import re

from openpyxl import Workbook
from openpyxl.chart import BarChart

from src.main import generate_all_data
from src.services.kpi_dashboard_service import (
    compute_top_excess,
    compute_transfer_benefit_summary,
)
from src.sheets.dashboard_layout import CHART_TITLES
from src.sheets.inventory_dashboard_sheet import build


def _dashboard():
    wb = Workbook()
    ws = wb.active
    ctx: dict = {"data": generate_all_data()}
    build(ws, ctx)
    return ws, ctx


def _chart_by_title(ws, title: str) -> BarChart:
    for chart in ws._charts:
        if chart.title.tx.rich.paragraphs[0].r[0].t == title:
            return chart
    raise AssertionError(f"Chart not found: {title}")


def _anchor_row(chart) -> int:
    anchor = chart.anchor
    if hasattr(anchor, "_from"):
        return int(anchor._from.row + 1)
    match = re.search(r"\d+", str(anchor))
    assert match is not None
    return int(match.group())


def _chart_titles(ws):
    titles = []
    for chart in ws._charts:
        titles.append(chart.title.tx.rich.paragraphs[0].r[0].t)
    return titles


def test_all_charts_have_unique_approved_titles():
    ws, _ = _dashboard()
    titles = _chart_titles(ws)
    assert len(titles) == 10
    assert len(set(titles)) == 10
    assert set(titles) == set(CHART_TITLES.values())


def test_no_doughnut_charts_used():
    ws, _ = _dashboard()
    from openpyxl.chart import DoughnutChart, PieChart

    for chart in ws._charts:
        assert not isinstance(chart, (DoughnutChart, PieChart))


def test_charts_are_bar_types():
    ws, _ = _dashboard()
    for chart in ws._charts:
        assert isinstance(chart, BarChart)


def test_chart_dimensions_fit_sections():
    ws, ctx = _dashboard()
    layouts = {s.key: s for s in ctx["_dashboard_section_layouts"]}
    title_to_key = {v: k for k, v in CHART_TITLES.items()}
    for chart in ws._charts:
        title = chart.title.tx.rich.paragraphs[0].r[0].t
        section = layouts[title_to_key[title]]
        row = _anchor_row(chart)
        end_row = row + max(1, int(round(float(chart.height) / 0.4)))
        assert 8.0 <= chart.height <= 12.5
        assert 22 <= chart.width <= 28.5
        assert section.start_row <= row <= section.end_row
        assert end_row <= section.end_row - 2


def test_dashboard_charts_have_no_legends():
    ws, _ = _dashboard()
    for chart in ws._charts:
        assert chart.legend is None


def test_data_labels_applied_to_each_series():
    ws, _ = _dashboard()
    for chart in ws._charts:
        assert chart.dataLabels is not None
        assert chart.dataLabels.showVal is True
        for series in chart.series:
            assert series.dLbls is not None
            assert series.dLbls.showVal is True
            assert series.dLbls.showSerName is False


def test_ranked_horizontal_bars_reverse_category_order():
    ws, _ = _dashboard()
    for key in ("top_excess", "transfer_benefit"):
        chart = _chart_by_title(ws, CHART_TITLES[key])
        assert chart.type == "bar"
        assert chart.y_axis.scaling.orientation == "maxMin"
        assert chart.x_axis.axPos == "b"
        assert chart.y_axis.axPos == "l"


def test_fill_rate_chart_uses_compact_inside_labels():
    ws, _ = _dashboard()
    chart = _chart_by_title(ws, CHART_TITLES["fill_rate"])
    assert len(chart.series) == 3
    for series in chart.series:
        assert series.dLbls.dLblPos == "ctr"


def test_horizontal_bars_use_left_categories_bottom_values():
    ws, _ = _dashboard()
    chart = _chart_by_title(ws, CHART_TITLES["location"])
    assert chart.x_axis.scaling.orientation == "minMax"
    assert chart.x_axis.axPos == "b"
    assert chart.y_axis.axPos == "l"


def test_section_spacer_is_two_rows():
    ws, ctx = _dashboard()
    layouts = ctx["_dashboard_section_layouts"]
    for prev, nxt in zip(layouts, layouts[1:], strict=False):
        gap = nxt.start_row - prev.end_row - 1
        assert gap == 2


def test_chart_label_column_hidden():
    ws, _ = _dashboard()
    assert ws.column_dimensions["H"].hidden is True


def test_top_excess_table_chart_category_alignment():
    data = generate_all_data()
    df = data["inventory"]
    ws, ctx = _dashboard()
    meta = ctx["_dashboard_section_meta"]["top_excess"]
    expected = compute_top_excess(df)

    labels = [
        ws.cell(row=r, column=meta["chart_label_col"]).value
        for r in range(meta["first_data_row"], meta["last_data_row"] + 1)
    ]
    values = [
        ws.cell(row=r, column=6).value
        for r in range(meta["first_data_row"], meta["last_data_row"] + 1)
    ]
    assert labels == expected["chart_label"].tolist()
    assert values == expected["excess_value"].tolist()


def test_transfer_benefit_table_chart_alignment():
    data = generate_all_data()
    ws, ctx = _dashboard()
    meta = ctx["_dashboard_section_meta"]["transfer_benefit"]
    expected = compute_transfer_benefit_summary(data)

    labels = [
        ws.cell(row=r, column=meta["chart_label_col"]).value
        for r in range(meta["first_data_row"], meta["last_data_row"] + 1)
    ]
    values = [
        ws.cell(row=r, column=6).value
        for r in range(meta["first_data_row"], meta["last_data_row"] + 1)
    ]
    assert labels == expected["chart_label"].tolist()
    assert values == expected["net_benefit"].tolist()
