"""Disposal Log sheet — asset retirement and data destruction tracking."""

from typing import Any

import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

from src.workbook.styles import apply_header_row, apply_title_cell, freeze_header


HEADERS = [
    "Asset Tag", "Serial Number", "Device Type", "Assigned User",
    "Return Date", "Condition", "Data Wipe Required", "Data Wipe Completed",
    "Wipe Method", "Disposal Vendor", "Certificate Received", "Disposal Date",
    "Approved By", "Disposal Status",
]


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Write Disposal Log headers and data rows."""
    apply_title_cell(ws, 1, 1, "Disposal Log")
    for col, header in enumerate(HEADERS, start=1):
        ws.cell(row=2, column=col, value=header)
    apply_header_row(ws, row=2, col_count=len(HEADERS))
    freeze_header(ws, row=3)

    df: pd.DataFrame = context["data"].get("disposal", pd.DataFrame())
    for row_idx, row in enumerate(df.itertuples(index=False), start=3):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)
