"""Dashboard chart quality and presentation tests."""

from __future__ import annotations

from openpyxl import Workbook

from src.main import generate_all_data
from src.sheets.dashboard_layout import CHART_TITLES, DASHBOARD_SECTIONS
from src.sheets.inventory_dashboard_sheet import build


def _dashboard():
    wb = Workbook()
    ws = wb.active
    build(ws, {"data": generate_all_data()})
    return ws


def _chart_titles(ws):
    titles = []
    for chart in ws._charts:
        titles.append(chart.title.tx.rich.paragraphs[0].r[0].t)
    return titles


def test_all_charts_have_unique_approved_titles():
    ws = _dashboard()
    titles = _chart_titles(ws)
    assert len(titles) == 10
    assert len(set(titles)) == 10
    assert set(titles) == set(CHART_TITLES.values())


def test_no_doughnut_charts_used():
    ws = _dashboard()
    from openpyxl.chart import DoughnutChart, PieChart

    for chart in ws._charts:
        assert not isinstance(chart, (DoughnutChart, PieChart))


def test_charts_are_bar_types():
    ws = _dashboard()
    from openpyxl.chart import BarChart

    for chart in ws._charts:
        assert isinstance(chart, BarChart)


def test_chart_dimensions_executive_size():
    ws = _dashboard()
    for chart in ws._charts:
        assert 24 <= chart.width <= 28.5
        assert 9 <= chart.height <= 11.5


def test_top_excess_has_at_most_ten_rows():
    ws = _dashboard()
    section = next(s for s in DASHBOARD_SECTIONS if s.key == "top_excess")
    header = section.start_row + 2
    rows = 0
    r = header + 1
    while ws.cell(r, 1).value is not None and r < section.end_row:
        rows += 1
        r += 1
    assert rows <= 10


def test_no_default_series_names_in_chart_xml():
    ws = _dashboard()
    for chart in ws._charts:
        title = chart.title.tx.rich.paragraphs[0].r[0].t
        assert "Series1" not in title
        assert "Column1" not in title
