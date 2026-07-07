"""
Shared Excel formula builders for KPI and summary calculations.

Returns formula strings ready to assign to openpyxl cells.
"""

from openpyxl.utils import get_column_letter


def _quote_sheet(sheet_name: str) -> str:
    """Wrap sheet name in single quotes for formula references."""
    return f"'{sheet_name}'"


def cell_ref(sheet_name: str, col_letter: str, row: int) -> str:
    """Return a cross-sheet cell reference string (without leading =)."""
    return f"{_quote_sheet(sheet_name)}!{col_letter}{row}"


def sum_range(
    sheet_name: str,
    col_letter: str,
    start_row: int,
    end_row: int,
) -> str:
    """Return a SUM formula referencing another sheet column range."""
    ref = f"{_quote_sheet(sheet_name)}!{col_letter}{start_row}:{col_letter}{end_row}"
    return f"=SUM({ref})"


def average_range(
    sheet_name: str,
    col_letter: str,
    start_row: int,
    end_row: int,
) -> str:
    """Return an AVERAGE formula referencing another sheet column range."""
    ref = f"{_quote_sheet(sheet_name)}!{col_letter}{start_row}:{col_letter}{end_row}"
    return f"=AVERAGE({ref})"


def count_range(
    sheet_name: str,
    col_letter: str,
    start_row: int,
    end_row: int,
) -> str:
    """Return a COUNT formula for numeric cells in a range."""
    ref = f"{_quote_sheet(sheet_name)}!{col_letter}{start_row}:{col_letter}{end_row}"
    return f"=COUNT({ref})"


def count_if_range(
    sheet_name: str,
    status_col: str,
    start_row: int,
    end_row: int,
    criteria: str,
) -> str:
    """Return a COUNTIF formula for status-based KPI counts."""
    ref = f"{_quote_sheet(sheet_name)}!{status_col}{start_row}:{status_col}{end_row}"
    return f'=COUNTIF({ref},"{criteria}")'


def count_if_not(
    sheet_name: str,
    col_letter: str,
    start_row: int,
    end_row: int,
    criteria: str,
) -> str:
    """Return a COUNTIF formula counting cells not equal to criteria."""
    ref = f"{_quote_sheet(sheet_name)}!{col_letter}{start_row}:{col_letter}{end_row}"
    return f'=COUNTIF({ref},"<>{criteria}")'


def sum_if_range(
    sheet_name: str,
    criteria_col: str,
    criteria: str,
    sum_col: str,
    start_row: int,
    end_row: int,
) -> str:
    """Return a SUMIF formula summing sum_col where criteria_col matches."""
    criteria_range = (
        f"{_quote_sheet(sheet_name)}!{criteria_col}{start_row}:{criteria_col}{end_row}"
    )
    sum_range_ref = f"{_quote_sheet(sheet_name)}!{sum_col}{start_row}:{sum_col}{end_row}"
    return f'=SUMIF({criteria_range},"{criteria}",{sum_range_ref})'


def sum_if_numeric(
    sheet_name: str,
    criteria_col: str,
    criteria: str,
    sum_col: str,
    start_row: int,
    end_row: int,
) -> str:
    """Return a SUMIFS-style formula with a numeric criteria (e.g. age > 180)."""
    # For simple greater-than, use SUMIF with expression criteria
    criteria_range = (
        f"{_quote_sheet(sheet_name)}!{criteria_col}{start_row}:{criteria_col}{end_row}"
    )
    sum_range_ref = f"{_quote_sheet(sheet_name)}!{sum_col}{start_row}:{sum_col}{end_row}"
    return f"=SUMIF({criteria_range},{criteria},{sum_range_ref})"


def if_formula(condition: str, value_if_true: str, value_if_false: str) -> str:
    """Return an IF formula string."""
    return f"=IF({condition},{value_if_true},{value_if_false})"


def multiply_cells(sheet_name: str, col_a: str, col_b: str, row: int) -> str:
    """Return a formula multiplying two cells on the same row."""
    a = cell_ref(sheet_name, col_a, row)
    b = cell_ref(sheet_name, col_b, row)
    return f"={a}*{b}"


def margin_pct_formula(
    sheet_name: str,
    selling_price_col: str,
    unit_cost_col: str,
    row: int,
) -> str:
    """Return gross margin % formula: (Selling Price - Unit Cost) / Selling Price."""
    sp = cell_ref(sheet_name, selling_price_col, row)
    uc = cell_ref(sheet_name, unit_cost_col, row)
    return f"=IF({sp}=0,0,({sp}-{uc})/{sp})"


def col_sum_formula(col_index: int, start_row: int, end_row: int) -> str:
    """Return a SUM formula for a column on the current sheet."""
    col_letter = get_column_letter(col_index)
    return f"=SUM({col_letter}{start_row}:{col_letter}{end_row})"
