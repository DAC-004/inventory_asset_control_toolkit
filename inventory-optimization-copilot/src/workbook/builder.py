"""
Workbook builder: orchestrates data loading and sheet creation.

Creates Inventory_Optimization_Copilot.xlsx in dist/.
"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook

from config.workbook_config import (
    AUTHOR,
    SHEET_ORDER,
    WORKBOOK_PATH,
    WORKBOOK_TITLE,
)
from src.sheets import (
    aged_excess_sheet,
    cycle_count_plan_sheet,
    demand_forecast_sheet,
    inventory_classification_sheet,
    inventory_dashboard_sheet,
    management_summary_sheet,
    markdown_planner_sheet,
    master_inventory_sheet,
    readme_sheet,
    replenishment_planning_sheet,
    purchase_order_tracker_sheet,
    service_level_analysis_sheet,
    transfer_planner_sheet,
    vendor_scorecards_sheet,
)

logger = logging.getLogger(__name__)

SHEET_BUILDERS = {
    "README": readme_sheet.build,
    "Master Inventory": master_inventory_sheet.build,
    "Inventory Dashboard": inventory_dashboard_sheet.build,
    "Inventory Classification": inventory_classification_sheet.build,
    "Aged Excess Analysis": aged_excess_sheet.build,
    "Cycle Count Plan": cycle_count_plan_sheet.build,
    "Replenishment Planning": replenishment_planning_sheet.build,
    "Demand Forecast": demand_forecast_sheet.build,
    "Service Level Analysis": service_level_analysis_sheet.build,
    "Purchase Order Tracker": purchase_order_tracker_sheet.build,
    "Vendor Scorecards": vendor_scorecards_sheet.build,
    "Markdown Planner": markdown_planner_sheet.build,
    "Transfer Planner": transfer_planner_sheet.build,
    "Management Summary": management_summary_sheet.build,
}


def create_workbook() -> Workbook:
    """
    Create a new openpyxl Workbook with the default sheet removed.

    Returns:
        Empty Workbook ready for sheet builders.
    """
    wb = Workbook()
    default_ws = wb.active
    if default_ws is not None:
        wb.remove(default_ws)
    wb.properties.title = WORKBOOK_TITLE
    wb.properties.creator = AUTHOR
    wb.properties.subject = "Inventory Optimization"
    wb.calculation.fullCalcOnLoad = True
    return wb


def build_workbook(
    data: dict[str, pd.DataFrame], output_path: Path | None = None
) -> Path:
    """
    Assemble the full workbook from generated DataFrames.

    Args:
        data: Dict with key ``inventory`` containing the master inventory DataFrame.
        output_path: Override default dist/ output path.

    Returns:
        Path to the saved .xlsx file.
    """
    output_path = output_path or WORKBOOK_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wb = create_workbook()
    context: dict[str, Any] = {"data": data, "workbook": wb}

    for sheet_name in SHEET_ORDER:
        builder = SHEET_BUILDERS[sheet_name]
        ws = wb.create_sheet(title=sheet_name)
        logger.debug("Building sheet: %s", sheet_name)
        builder(ws, context)

    wb.save(output_path)
    logger.info("Workbook saved: %s", output_path)
    return output_path
