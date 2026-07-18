"""
Workbook utility helpers: column sizing, tables, filters, formats, and print layout.
"""

from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font

from config import style_config as sc

# ---------------------------------------------------------------------------
# Navigation links
# ---------------------------------------------------------------------------


def add_internal_sheet_link(
    ws: Worksheet,
    row: int,
    col: int,
    target_sheet: str,
    display: str | None = None,
) -> None:
    """Add an in-workbook hyperlink to another sheet."""
    label = display or target_sheet
    cell = ws.cell(row=row, column=col, value=label)
    cell.hyperlink = f"#'{target_sheet}'!A1"
    cell.font = Font(
        name=sc.FONTS["default_name"],
        color=sc.COLORS["dark_blue"],
        underline="single",
        size=sc.FONTS["body_size"],
    )
    cell.alignment = sc.LEFT_ALIGN


# ---------------------------------------------------------------------------
# Column sizing
# ---------------------------------------------------------------------------


def autosize_columns(
    ws: Worksheet,
    min_width: float = 10,
    max_width: float = 45,
    padding: int = 2,
) -> None:
    """Approximate auto-fit column widths based on cell content length."""
    for column_cells in ws.columns:
        col_letter = get_column_letter(column_cells[0].column)
        length = max(len(str(cell.value or "")) for cell in column_cells)
        adjusted = min(max(length + padding, min_width), max_width)
        ws.column_dimensions[col_letter].width = adjusted


def auto_width_columns(
    ws: Worksheet,
    min_width: int = 10,
    max_width: int = 45,
) -> None:
    """Alias for autosize_columns (backward compatible)."""
    autosize_columns(ws, min_width=min_width, max_width=max_width)


def set_column_widths(ws: Worksheet, widths: dict[str, float]) -> None:
    """Set explicit column widths from a dict of column letter → width."""
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width


# ---------------------------------------------------------------------------
# Excel tables and filters
# ---------------------------------------------------------------------------


def create_excel_table(
    ws: Worksheet,
    table_name: str,
    ref: str,
    style: str = "TableStyleMedium2",
    show_row_stripes: bool = True,
) -> Table:
    """
    Create a filterable Excel table over the given range.

    Returns:
        The Table object (also registered on the worksheet).
    """
    table = Table(displayName=table_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name=style,
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=show_row_stripes,
        showColumnStripes=False,
    )
    ws.add_table(table)
    return table


def add_excel_table(
    ws: Worksheet,
    table_name: str,
    ref: str,
    style: str = "TableStyleMedium2",
) -> Table:
    """Alias for create_excel_table (backward compatible)."""
    return create_excel_table(ws, table_name, ref, style=style)


def apply_auto_filter(
    ws: Worksheet,
    ref: str,
) -> None:
    """Enable auto-filter dropdowns on a header + data range."""
    ws.auto_filter.ref = ref


# ---------------------------------------------------------------------------
# Number formatting
# ---------------------------------------------------------------------------


def _col_indices(col_letters: list[str]) -> list[int]:
    """Convert column letters to 1-based column indices."""
    return [column_index_from_string(letter) for letter in col_letters]


def format_currency_columns(
    ws: Worksheet,
    col_letters: list[str],
    start_row: int,
    end_row: int,
    number_format: str | None = None,
) -> None:
    """Apply currency number format to specified columns across a row range."""
    fmt = number_format or sc.NUMBER_FORMATS["currency"]
    for col_idx in _col_indices(col_letters):
        for row in range(start_row, end_row + 1):
            ws.cell(row=row, column=col_idx).number_format = fmt


def format_percentage_columns(
    ws: Worksheet,
    col_letters: list[str],
    start_row: int,
    end_row: int,
    number_format: str | None = None,
) -> None:
    """Apply percentage number format to specified columns across a row range."""
    fmt = number_format or sc.NUMBER_FORMATS["percentage"]
    for col_idx in _col_indices(col_letters):
        for row in range(start_row, end_row + 1):
            ws.cell(row=row, column=col_idx).number_format = fmt


def format_date_columns(
    ws: Worksheet,
    col_letters: list[str],
    start_row: int,
    end_row: int,
    number_format: str | None = None,
) -> None:
    """Apply date number format to specified columns across a row range."""
    fmt = number_format or sc.NUMBER_FORMATS["date"]
    for col_idx in _col_indices(col_letters):
        for row in range(start_row, end_row + 1):
            ws.cell(row=row, column=col_idx).number_format = fmt


def format_integer_columns(
    ws: Worksheet,
    col_letters: list[str],
    start_row: int,
    end_row: int,
    number_format: str | None = None,
) -> None:
    """Apply integer number format to specified columns across a row range."""
    fmt = number_format or sc.NUMBER_FORMATS["integer"]
    for col_idx in _col_indices(col_letters):
        for row in range(start_row, end_row + 1):
            ws.cell(row=row, column=col_idx).number_format = fmt


# ---------------------------------------------------------------------------
# Print layout
# ---------------------------------------------------------------------------


def set_print_layout(
    ws: Worksheet,
    orientation: str = "portrait",
    paper_size: int | None = None,
    fit_width: int = 1,
    fit_height: int = 0,
    center_horizontal: bool = True,
    repeat_header_rows: str | None = None,
) -> None:
    """
    Configure worksheet print settings for professional output.

    Args:
        ws: Target worksheet.
        orientation: "portrait" or "landscape".
        paper_size: openpyxl paper size constant (default: letter).
        fit_width: Pages wide (0 = no scaling).
        fit_height: Pages tall (0 = no limit).
        center_horizontal: Center sheet horizontally on page.
        repeat_header_rows: Rows to repeat, e.g. "1:2" for title + header.
    """
    if orientation == "landscape":
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    else:
        ws.page_setup.orientation = ws.ORIENTATION_PORTRAIT

    if paper_size is not None:
        ws.page_setup.paperSize = paper_size

    ws.page_setup.fitToWidth = fit_width
    ws.page_setup.fitToHeight = fit_height
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = center_horizontal

    if repeat_header_rows:
        ws.print_title_rows = repeat_header_rows


def set_landscape_print(
    ws: Worksheet,
    fit_width: int = 1,
    repeat_header_rows: str = "1:2",
) -> None:
    """Shortcut for landscape dashboard-style print layout."""
    set_print_layout(
        ws,
        orientation="landscape",
        fit_width=fit_width,
        fit_height=0,
        repeat_header_rows=repeat_header_rows,
    )


def set_portrait_print(
    ws: Worksheet,
    fit_width: int = 1,
    fit_height: int = 1,
    repeat_header_rows: str | None = "1:2",
) -> None:
    """Shortcut for one-page portrait summary print layout."""
    set_print_layout(
        ws,
        orientation="portrait",
        fit_width=fit_width,
        fit_height=fit_height,
        repeat_header_rows=repeat_header_rows,
    )
