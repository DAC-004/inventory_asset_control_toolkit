"""
Data validation dropdown lists for editable workbook fields.

Dropdown values are defined in specs.md §13.
"""

from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from config.workbook_config import (
    COMPLIANCE_STATUSES,
    INVENTORY_STATUSES,
    RECOMMENDED_ACTIONS,
)

# Dropdown option strings (comma-separated for Excel list validation)
INVENTORY_STATUS_OPTIONS = ",".join(INVENTORY_STATUSES)
RECOMMENDED_ACTION_OPTIONS = ",".join(RECOMMENDED_ACTIONS)

IT_ASSET_STATUS_OPTIONS = (
    "In Stock,Assigned,In Repair,Returned,Retired,Disposed,Missing"
)
LIFECYCLE_STAGE_OPTIONS = (
    "Received,Tagged,In Stock,Assigned,In Repair,Returned,"
    "Retired,Data Wiped,Disposed"
)
COMPLIANCE_STATUS_OPTIONS = ",".join(COMPLIANCE_STATUSES)
DISPOSAL_STATUS_OPTIONS = (
    "Pending Wipe,Wiped,Pending Vendor Pickup,Disposed,"
    "Certificate Missing,Hold for Review"
)
MOBILE_STATUS_OPTIONS = (
    "Ready,Assigned,Pending Setup,Missing Agreement,Returned,Disabled"
)
YES_NO_OPTIONS = "Yes,No"


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


def add_it_asset_status_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for IT asset status values."""
    return add_list_validation(ws, cell_range, IT_ASSET_STATUS_OPTIONS)


def add_lifecycle_stage_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for IT asset lifecycle stage values."""
    return add_list_validation(ws, cell_range, LIFECYCLE_STAGE_OPTIONS)


def add_compliance_status_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for software compliance status values."""
    return add_list_validation(ws, cell_range, COMPLIANCE_STATUS_OPTIONS)


def add_disposal_status_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for disposal status values."""
    return add_list_validation(ws, cell_range, DISPOSAL_STATUS_OPTIONS)


def add_mobile_status_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add dropdown validation for mobile provisioning status values."""
    return add_list_validation(ws, cell_range, MOBILE_STATUS_OPTIONS)


def add_yes_no_validation(ws: Worksheet, cell_range: str) -> DataValidation:
    """Add Yes/No dropdown validation."""
    return add_list_validation(ws, cell_range, YES_NO_OPTIONS)
