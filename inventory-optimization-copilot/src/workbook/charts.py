"""
openpyxl chart builders for dashboard and management summary sheets.
"""

from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.worksheet.worksheet import Worksheet


def _apply_chart_title(chart, title: str) -> None:
    """Set chart title with consistent font styling."""
    chart.title = title
    if chart.title and chart.title.tx:
        chart.title.tx.rich.paragraphs[0].pPr = None  # use default


def create_bar_chart(
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    grouping: str = "clustered",
    style: int = 10,
    width: float = 15,
    height: float = 10,
    y_axis_title: str | None = None,
) -> BarChart:
    """
    Build a styled bar chart (not yet anchored to a worksheet).

    Args:
        title: Chart title text.
        data_ref: openpyxl Reference for series values.
        categories_ref: openpyxl Reference for category labels.
        grouping: Bar grouping mode ("clustered", "stacked", "percentStacked").
        style: Built-in chart style index.
        width: Chart width in cm.
        height: Chart height in cm.
        y_axis_title: Optional Y-axis label.

    Returns:
        Configured BarChart instance.
    """
    chart = BarChart()
    chart.type = "col"
    chart.grouping = grouping
    chart.style = style
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)

    if y_axis_title:
        chart.y_axis.title = y_axis_title

    chart.legend.position = "b"
    return chart


def create_pie_chart(
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    style: int = 10,
    width: float = 12,
    height: float = 10,
    show_percent_labels: bool = True,
) -> PieChart:
    """
    Build a styled pie chart (not yet anchored to a worksheet).

    Args:
        title: Chart title text.
        data_ref: openpyxl Reference for series values.
        categories_ref: openpyxl Reference for slice labels.
        style: Built-in chart style index.
        width: Chart width in cm.
        height: Chart height in cm.
        show_percent_labels: Show percentage labels on slices.

    Returns:
        Configured PieChart instance.
    """
    chart = PieChart()
    chart.style = style
    chart.width = width
    chart.height = height
    _apply_chart_title(chart, title)

    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories_ref)

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
    anchor: str = "E5",
    **kwargs,
) -> BarChart:
    """Create a bar chart and anchor it on the worksheet."""
    chart = create_bar_chart(title, data_ref, categories_ref, **kwargs)
    ws.add_chart(chart, anchor)
    return chart


def add_pie_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "E20",
    **kwargs,
) -> PieChart:
    """Create a pie chart and anchor it on the worksheet."""
    chart = create_pie_chart(title, data_ref, categories_ref, **kwargs)
    ws.add_chart(chart, anchor)
    return chart


def add_line_chart(
    ws: Worksheet,
    title: str,
    data_ref: Reference,
    categories_ref: Reference,
    anchor: str = "E5",
    width: float = 14,
    height: float = 8,
    y_axis_title: str | None = None,
) -> LineChart:
    """Create a line chart and anchor it on the worksheet."""
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
    """Build a Reference for chart data on the given worksheet."""
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
    """Build a Reference for chart category labels on the given worksheet."""
    return Reference(ws, min_col=col, min_row=min_row, max_col=col, max_row=max_row)
