"""Management Summary sheet — printable one-page executive overview."""

from typing import Any

from openpyxl.worksheet.worksheet import Worksheet

from src.workbook.styles import apply_title_cell


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build management summary layout."""
    apply_title_cell(ws, 1, 1, "Management Summary")
    ws["A3"] = "Inventory Health Highlights"
    ws["A10"] = "IT Asset Control Highlights"
    ws["A17"] = "Software License Risks"
    ws["A24"] = "30 / 60 / 90 Day Action Plan"
    ws["A26"] = "30 days: Validate records, review exceptions, confirm reporting needs."
    ws["A27"] = "60 days: Standardize audits, improve dashboards, identify recurring issues."
    ws["A28"] = "90 days: Automate reports, build KPI cadence, recommend improvements."
