"""
openpyxl chart builders for dashboard and management summary sheets.
"""

from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.series import SeriesLabel
from openpyxl.worksheet.worksheet import Worksheet


def _apply_chart_title(chart, title: str) -> None:
    chart.title = title
    if chart.title and chart.title.tx:
        chart.title.tx.rich.paragraphs[0].pPr = None


def _apply_plot_layout(chart, *, horizontal: bool) -> None:
    """Reserve right-side space for legend and bottom/left for axis titles."""
    chart.layout = Layout(
        manualLayout=ManualLayout(
            layoutTarget="inner",
            x=0.08,
            y=0.12 if horizontal else 0.14,
            w=0.62 if horizontal else 0.68,
            h=0.72 if horizontal else 0.68,
        )
    )


def _apply_value_only_labels(chart) -> None:
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showVal = True
    chart.dataLabels.showSerName = False
    chart.dataLabels.showCatName = False
    chart.dataLabels.showLegendKey = False
    chart.dataLabels.dLblPos = "outEnd"


def _apply_legend_right(chart, series_name: str | None = None) -> None:
    chart.legend.position = "r"
    chart.legend.overlay = False
    if series_name and chart.series:
        chart.series[0].title = SeriesLabel(v=series_name)


def _configure_axes(
    chart: BarChart,
    *,
    horizontal: bool,
    value_axis_title: str | None,
    category_axis_title: str | None,
    value_axis_min: float | None,
    value_axis_max: float | None,
    reverse_category_order: bool,
) -> None:
    value_axis = chart.x_axis if horizontal else chart.y_axis
    category_axis = chart.y_axis if horizontal else chart.x_axis

    if value_axis_title:
        value_axis.title = value_axis_title
    if category_axis_title:
        category_axis.title = category_axis_title

    if value_axis_min is not None:
        value_axis.scaling.min = value_axis_min
    if value_axis_max is not None:
        value_axis.scaling.max = value_axis_max

    if horizontal and reverse_category_order:
        category_axis.scaling.orientation = "maxMin"

    category_axis.tickLblSkip = 1
    value_axis.majorGridlines = None


def create_bar_chart(
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    grouping: str = "clustered",
    style: int = 10,
    width: float = 15,
    height: float = 10,
    value_axis_title: str | None = None,
    category_axis_title: str | None = None,
    horizontal: bool = False,
    value_axis_min: float | None = None,
    value_axis_max: float | None = None,
    show_data_labels: bool = False,
    reverse_category_order: bool = False,
    series_name: str | None = None,
    *,
    y_axis_title: str | None = None,
    x_axis_title: str | None = None,
    hide_legend: bool | None = None,
) -> BarChart:
    """Build a styled bar/column chart (not yet anchored to a worksheet)."""
    if value_axis_title is None and y_axis_title is not None:
        value_axis_title = y_axis_title
    if category_axis_title is None and x_axis_title is not None:
        category_axis_title = x_axis_title

    chart = BarChart()
    chart.type = "bar" if horizontal else "col"
    chart.grouping = grouping
    chart.style = style
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)
    chart.title.overlay = False

    chart.add_data(data_ref, titles_from_data=series_name is None)
    chart.set_categories(categories_ref)

    _configure_axes(
        chart,
        horizontal=horizontal,
        value_axis_title=value_axis_title,
        category_axis_title=category_axis_title,
        value_axis_min=value_axis_min,
        value_axis_max=value_axis_max,
        reverse_category_order=reverse_category_order,
    )
    _apply_plot_layout(chart, horizontal=horizontal)
    if hide_legend:
        chart.legend = None
    else:
        _apply_legend_right(chart, series_name)

    if show_data_labels:
        _apply_value_only_labels(chart)

    return chart


def create_clustered_bar_chart(
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    style: int = 10,
    width: float = 26,
    height: float = 10,
    horizontal: bool = False,
    value_axis_title: str | None = None,
    category_axis_title: str | None = None,
    value_axis_min: float | None = None,
    value_axis_max: float | None = None,
    reverse_category_order: bool = False,
) -> BarChart:
    """Build a multi-series clustered bar/column chart from one data block."""
    chart = BarChart()
    chart.type = "bar" if horizontal else "col"
    chart.grouping = "clustered"
    chart.style = style
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)
    chart.title.overlay = False

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)

    _configure_axes(
        chart,
        horizontal=horizontal,
        value_axis_title=value_axis_title,
        category_axis_title=category_axis_title,
        value_axis_min=value_axis_min,
        value_axis_max=value_axis_max,
        reverse_category_order=reverse_category_order,
    )
    _apply_plot_layout(chart, horizontal=horizontal)
    chart.legend.position = "r"
    chart.legend.overlay = False
    return chart


def create_pie_chart(
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    style: int = 10,
    width: float = 12,
    height: float = 10,
    show_percent_labels: bool = False,
) -> PieChart:
    chart = PieChart()
    chart.style = style
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)
    chart.title.overlay = False
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)
    chart.legend.position = "r"
    chart.legend.overlay = False
    if show_percent_labels:
        chart.dataLabels = DataLabelList()
        chart.dataLabels.showPercent = True
        chart.dataLabels.showCatName = False
        chart.dataLabels.showVal = False
    return chart


def add_bar_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "J11",
    **kwargs,
) -> BarChart:
    chart = create_bar_chart(title, data_ref, categories_ref, **kwargs)
    ws.add_chart(chart, anchor)
    return chart


def add_clustered_bar_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "J11",
    **kwargs,
) -> BarChart:
    chart = create_clustered_bar_chart(title, data_ref, categories_ref, **kwargs)
    ws.add_chart(chart, anchor)
    return chart


def add_pie_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "J20",
    **kwargs,
) -> PieChart:
    chart = create_pie_chart(title, data_ref, categories_ref, **kwargs)
    ws.add_chart(chart, anchor)
    return chart


def add_line_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "J11",
    width: float = 14,
    height: float = 8,
    y_axis_title: str | None = None,
) -> LineChart:
    chart = LineChart()
    chart.style = 10
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)
    if y_axis_title:
        chart.y_axis.title = y_axis_title
    chart.legend = None
    ws.add_chart(chart, anchor)
    return chart


def make_data_reference(
    ws: Worksheet,
    min_col: int,
    min_row: int,
    max_row: int,
    max_col: int | None = None,
) -> Reference:
    max_col = max_col or min_col
    return Reference(
        ws, min_col=min_col, min_row=min_row, max_col=max_col, max_row=max_row
    )


def make_category_reference(
    ws: Worksheet,
    col: int,
    min_row: int,
    max_row: int,
) -> Reference:
    return Reference(ws, min_col=col, min_row=min_row, max_col=col, max_row=max_row)
