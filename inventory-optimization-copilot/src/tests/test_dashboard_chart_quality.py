"""Dashboard chart quality and presentation tests."""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.chart import BarChart

from src.main import generate_all_data
from src.services.kpi_dashboard_service import (
    compute_top_excess,
    compute_transfer_benefit_summary,
)
from src.sheets.dashboard_layout import CHART_SERIES_NAMES, CHART_TITLES
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


def test_chart_dimensions_executive_size():
    ws, _ = _dashboard()
    for chart in ws._charts:
        assert 24 <= chart.width <= 28.5
        assert 9 <= chart.height <= 11.5


def test_top_excess_has_at_most_ten_rows():
    ws, ctx = _dashboard()
    meta = ctx["_dashboard_section_meta"]["top_excess"]
    rows = meta["last_data_row"] - meta["first_data_row"] + 1
    assert rows <= 10


def test_no_default_series_names_in_chart_xml():
    ws, _ = _dashboard()
    for chart in ws._charts:
        title = chart.title.tx.rich.paragraphs[0].r[0].t
        assert "Series1" not in title
        assert "Column1" not in title


def test_legends_on_right_without_overlay():
    ws, _ = _dashboard()
    for chart in ws._charts:
        if chart.legend is None:
            continue
        assert chart.legend.position == "r"
        assert chart.legend.overlay is False


def test_data_labels_show_values_only():
    ws, _ = _dashboard()
    for chart in ws._charts:
        labels = chart.dataLabels
        if labels is None:
            continue
        assert labels.showVal is True
        assert labels.showSerName is False
        assert labels.showCatName is False
        assert labels.showLegendKey is False


def test_ranked_horizontal_bars_reverse_category_order():
    ws, _ = _dashboard()
    for key in ("top_excess", "transfer_benefit"):
        chart = _chart_by_title(ws, CHART_TITLES[key])
        assert chart.type == "bar"
        assert chart.y_axis.scaling.orientation == "maxMin"


def test_single_series_use_approved_legend_names():
    ws, _ = _dashboard()
    for key, expected in CHART_SERIES_NAMES.items():
        chart = _chart_by_title(ws, CHART_TITLES[key])
        if key == "fill_rate":
            continue
        assert chart.series[0].title is not None
        assert chart.series[0].title.v == expected


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
    ranks = [
        ws.cell(row=r, column=1).value
        for r in range(meta["first_data_row"], meta["last_data_row"] + 1)
    ]
    assert ranks == list(range(1, len(ranks) + 1))


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
