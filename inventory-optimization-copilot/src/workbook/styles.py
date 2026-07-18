"""
Reusable openpyxl style helpers.

Wraps constants from config/style_config.py for application to cells and ranges.
"""

from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc

# ---------------------------------------------------------------------------
# Title and section headers
# ---------------------------------------------------------------------------


def apply_title_style(ws: Worksheet, row: int, col: int, title: str) -> None:
    """Apply workbook title styling to a single cell."""
    cell = ws.cell(row=row, column=col, value=title)
    cell.font = sc.TITLE_FONT
    cell.alignment = sc.LEFT_ALIGN


def apply_title_cell(ws: Worksheet, row: int, col: int, title: str) -> None:
    """Alias for apply_title_style (backward compatible)."""
    apply_title_style(ws, row, col, title)


def apply_section_header_style(
    ws: Worksheet,
    row: int,
    col: int,
    text: str,
    span_cols: int = 1,
) -> None:
    """Apply dark-blue section header styling, optionally merged across columns."""
    cell = ws.cell(row=row, column=col, value=text)
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["body_size"],
    )
    cell.fill = PatternFill(
        start_color=sc.COLORS["dark_blue"],
        end_color=sc.COLORS["dark_blue"],
        fill_type="solid",
    )
    cell.alignment = sc.LEFT_ALIGN
    cell.border = sc.THIN_GRAY_BORDER
    if span_cols > 1:
        ws.merge_cells(
            start_row=row,
            start_column=col,
            end_row=row,
            end_column=col + span_cols - 1,
        )


# ---------------------------------------------------------------------------
# Table headers
# ---------------------------------------------------------------------------


def apply_table_header_style(ws: Worksheet, row: int, col_count: int) -> None:
    """Apply navy table header styling across col_count columns in a row."""
    for col in range(1, col_count + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = sc.HEADER_FILL
        cell.font = sc.HEADER_FONT
        cell.alignment = sc.CENTER_ALIGN
        cell.border = sc.THIN_GRAY_BORDER


def apply_header_row(ws: Worksheet, row: int, col_count: int) -> None:
    """Alias for apply_table_header_style (backward compatible)."""
    apply_table_header_style(ws, row, col_count)


def apply_table_header_range(
    ws: Worksheet,
    start_row: int,
    start_col: int,
    end_col: int,
) -> None:
    """Apply table header styling to a specific column range on one row."""
    for col in range(start_col, end_col + 1):
        cell = ws.cell(row=start_row, column=col)
        cell.fill = sc.HEADER_FILL
        cell.font = sc.HEADER_FONT
        cell.alignment = sc.CENTER_ALIGN
        cell.border = sc.THIN_GRAY_BORDER


# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------


def apply_kpi_card_style(
    ws: Worksheet,
    title_row: int,
    title_col: int,
    value_row: int,
    value_col: int,
    title: str,
    value,
    span_cols: int = 2,
) -> None:
    """
    Render a KPI card with title and value cells over a merged block.

    Merges title_row and value_row each across span_cols columns.
    """
    end_col = title_col + span_cols - 1

    ws.merge_cells(
        start_row=title_row,
        start_column=title_col,
        end_row=title_row,
        end_column=end_col,
    )
    ws.merge_cells(
        start_row=value_row,
        start_column=title_col,
        end_row=value_row,
        end_column=end_col,
    )

    title_cell = ws.cell(row=title_row, column=title_col, value=title)
    title_cell.font = sc.KPI_TITLE_FONT
    title_cell.fill = sc.KPI_CARD_FILL
    title_cell.alignment = sc.KPI_CARD_STYLE["alignment"]
    title_cell.border = sc.NAVY_BORDER

    value_cell = ws.cell(row=value_row, column=title_col, value=value)
    value_cell.font = sc.KPI_VALUE_FONT
    value_cell.fill = sc.KPI_CARD_FILL
    value_cell.alignment = sc.KPI_CARD_STYLE["alignment"]
    value_cell.border = sc.NAVY_BORDER

    for row in (title_row, value_row):
        for col in range(title_col, end_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.fill = sc.KPI_CARD_FILL
            cell.border = sc.NAVY_BORDER


# ---------------------------------------------------------------------------
# Borders and alignment
# ---------------------------------------------------------------------------


def apply_border_to_range(
    ws: Worksheet,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
    border: Border | None = None,
) -> None:
    """Apply a uniform border to every cell in a rectangular range."""
    border = border or sc.THIN_GRAY_BORDER
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            ws.cell(row=row, column=col).border = border


def apply_alignment_to_range(
    ws: Worksheet,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
    alignment: Alignment | None = None,
) -> None:
    """Apply uniform alignment to every cell in a rectangular range."""
    alignment = alignment or sc.CENTER_ALIGN
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            ws.cell(row=row, column=col).alignment = alignment


def apply_body_style_to_range(
    ws: Worksheet,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
) -> None:
    """Apply default body font and left alignment to a data range."""
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = sc.BODY_FONT
            cell.alignment = sc.LEFT_ALIGN


# ---------------------------------------------------------------------------
# Freeze panes
# ---------------------------------------------------------------------------


def freeze_panes(ws: Worksheet, row: int = 2, col: int = 1) -> None:
    """Freeze panes below row and to the right of col."""
    ws.freeze_panes = ws.cell(row=row, column=col)


def freeze_header(ws: Worksheet, row: int = 2) -> None:
    """Alias for freeze_panes with default first-column freeze (backward compatible)."""
    freeze_panes(ws, row=row, col=1)


# ---------------------------------------------------------------------------
# Risk conditional formatting
# ---------------------------------------------------------------------------


def _risk_fill_for_level(risk_level: str) -> PatternFill:
    """Build a PatternFill from a risk level key."""
    color = sc.RISK_LEVEL_COLORS.get(risk_level, sc.COLORS["gray"])
    return PatternFill(start_color=color, end_color=color, fill_type="solid")


def apply_risk_conditional_formatting(
    ws: Worksheet,
    target_range: str,
    status_column_letter: str,
    first_data_row: int,
    status_risk_map: dict[str, str],
) -> None:
    """
    Apply status-based risk coloring to a column range using conditional formatting.

    Args:
        ws: Target worksheet.
        target_range: Excel range to format (e.g. "U3:U122").
        status_column_letter: Column letter containing status values.
        first_data_row: First data row used as the relative anchor in formulas.
        status_risk_map: Maps status label → risk level key (see style_config).
    """
    anchor = f"${status_column_letter}{first_data_row}"
    for status, risk_level in status_risk_map.items():
        fill = _risk_fill_for_level(risk_level)
        rule = FormulaRule(
            formula=[f'{anchor}="{status}"'],
            fill=fill,
        )
        ws.conditional_formatting.add(target_range, rule)


def apply_inventory_status_formatting(
    ws: Worksheet,
    target_range: str,
    status_column_letter: str,
    first_data_row: int,
) -> None:
    """Apply inventory status risk colors to a range."""
    apply_risk_conditional_formatting(
        ws,
        target_range,
        status_column_letter,
        first_data_row,
        sc.INVENTORY_STATUS_RISK,
    )


def apply_compliance_status_formatting(
    ws: Worksheet,
    target_range: str,
    status_column_letter: str,
    first_data_row: int,
) -> None:
    """Apply software compliance status risk colors to a range."""
    apply_risk_conditional_formatting(
        ws,
        target_range,
        status_column_letter,
        first_data_row,
        sc.COMPLIANCE_STATUS_RISK,
    )


def apply_it_asset_status_formatting(
    ws: Worksheet,
    target_range: str,
    status_column_letter: str,
    first_data_row: int,
) -> None:
    """Apply IT asset status risk colors to a range."""
    apply_risk_conditional_formatting(
        ws,
        target_range,
        status_column_letter,
        first_data_row,
        sc.IT_ASSET_STATUS_RISK,
    )


def apply_disposal_status_formatting(
    ws: Worksheet,
    target_range: str,
    status_column_letter: str,
    first_data_row: int,
) -> None:
    """Apply disposal status risk colors to a range."""
    apply_risk_conditional_formatting(
        ws,
        target_range,
        status_column_letter,
        first_data_row,
        sc.DISPOSAL_STATUS_RISK,
    )


def apply_row_risk_fill(
    ws: Worksheet,
    row: int,
    start_col: int,
    end_col: int,
    status: str,
    status_risk_map: dict[str, str],
) -> None:
    """Directly fill a row with a risk color based on status (no conditional rule)."""
    risk_level = status_risk_map.get(status, "neutral")
    fill = _risk_fill_for_level(risk_level)
    for col in range(start_col, end_col + 1):
        ws.cell(row=row, column=col).fill = fill
