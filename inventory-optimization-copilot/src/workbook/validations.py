"""
Data validation dropdown lists for editable workbook fields.
"""

from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from config.workbook_config import INVENTORY_STATUSES, RECOMMENDED_ACTIONS

INVENTORY_STATUS_OPTIONS = ",".join(INVENTORY_STATUSES)
RECOMMENDED_ACTION_OPTIONS = ",".join(RECOMMENDED_ACTIONS)


def add_list_validation(
    ws: Worksheet,
    cell_range: str,
    options: str,
    allow_blank: bool = True,
    show_error_message: bool = True,
    error_title: str = "Invalid Entry",
    error_message: str = "Please select a value from the dropdown list.",
) -> DataValidation:
    """
    Attach a dropdown list validation to a cell range.

    Returns:
        The DataValidation object (also registered on the worksheet).
    """
    dv = DataValidation(
        type="list",
        formula1=f'"{options}"',
        allow_blank=allow_blank,
        showErrorMessage=show_error_message,
        errorTitle=error_title,
        error=error_message,
    )
    ws.add_data_validation(dv)
    dv.add(cell_range)
    return dv


def add_inventory_status_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for inventory status values."""
    return add_list_validation(ws, cell_range, INVENTORY_STATUS_OPTIONS)


def add_recommended_action_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for recommended action values."""
    return add_list_validation(ws, cell_range, RECOMMENDED_ACTION_OPTIONS)
