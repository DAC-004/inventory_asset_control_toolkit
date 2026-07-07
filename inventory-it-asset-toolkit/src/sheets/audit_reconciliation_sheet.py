"""Audit Reconciliation sheet — system vs. physical audit exceptions."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from config import style_config as sc
from config.workbook_config import RANDOM_SEED
from src.workbook.styles import (
    apply_kpi_card_style,
    apply_risk_conditional_formatting,
    apply_section_header_style,
    apply_table_header_style,
    freeze_panes,
)
from src.workbook.utils import (
    autosize_columns,
    create_excel_table,
    set_column_widths,
    set_landscape_print,
)

EXCEPTION_TYPES = [
    "Missing from Audit",
    "Found Not in System",
    "Wrong Location",
    "Wrong User",
    "Duplicate Serial Number",
    "Missing Asset Tag",
    "Retired but Active",
    "No Exception",
]

EXCEPTION_HEADERS = [
    "Asset Tag",
    "Serial Number",
    "Expected Location",
    "Actual Location",
    "Expected User",
    "Actual User",
    "Exception Type",
    "Priority",
    "Follow-Up Owner",
    "Resolution Status",
]

SYSTEM_HEADERS = [
    "Asset Tag",
    "Serial Number",
    "Device Type",
    "Location",
    "Assigned User",
    "Status",
]

PHYSICAL_HEADERS = [
    "Asset Tag",
    "Serial Number",
    "Location",
    "Assigned User",
    "Physical Status",
]

SUMMARY_HEADERS = ["Exception Type", "Count"]

FOLLOW_UP_OWNERS = [
    "Daniel A. Cruz",
    "Patricia Nguyen",
    "Robert Kim",
    "IT Service Desk",
    "Field Support Lead",
]

ALT_LOCATIONS = [
    "Store-Brooklyn",
    "Store-Queens",
    "Store-Manhattan",
    "HQ-Queens",
    "DC-NY",
]

TITLE_ROW = 1
KPI_TITLE_ROW = 3
KPI_VALUE_ROW = 4

PRIORITY_BY_EXCEPTION = {
    "Missing from Audit": "High",
    "Found Not in System": "High",
    "Wrong Location": "Medium",
    "Wrong User": "Medium",
    "Duplicate Serial Number": "High",
    "Missing Asset Tag": "Medium",
    "Retired but Active": "High",
    "No Exception": "Low",
}

PRIORITY_CF_MAP = {
    "High": "critical",
    "Medium": "slow_moving",
    "Low": "healthy",
}

EXCEPTION_TYPE_CF_MAP = {
    "No Exception": "healthy",
    "Missing from Audit": "critical",
    "Found Not in System": "critical",
    "Wrong Location": "slow_moving",
    "Wrong User": "slow_moving",
    "Duplicate Serial Number": "critical",
    "Missing Asset Tag": "slow_moving",
    "Retired but Active": "critical",
}


def _resolution_for_exception(exception_type: str, rng: np.random.Generator) -> str:
    """Assign resolution status based on exception severity."""
    if exception_type == "No Exception":
        return "Resolved"
    if exception_type in ("Missing from Audit", "Found Not in System", "Retired but Active"):
        return "Open"
    options = ["Open", "In Progress", "Resolved"]
    weights = [0.5, 0.35, 0.15] if exception_type != "No Exception" else [0, 0, 1]
    return options[int(rng.choice(len(options), p=weights))]


def _build_exceptions_dataframe(
    assets: pd.DataFrame,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate audit exception records from IT asset system data.

    Simulates physical audit variances and ensures all exception types appear.
    """
    if assets.empty:
        return pd.DataFrame(columns=EXCEPTION_HEADERS)

    rng = np.random.default_rng(seed + 10)
    active = assets[~assets["status"].isin(["Disposed"])].copy()
    records: list[dict[str, Any]] = []

    for _, row in active.iterrows():
        expected_loc = str(row["location"])
        expected_user = str(row["assigned_user"]) if row["assigned_user"] else "Unassigned"
        actual_loc = expected_loc
        actual_user = expected_user
        exception_type = "No Exception"

        if row["status"] == "Missing":
            exception_type = "Missing from Audit"
            actual_loc = ""
            actual_user = ""
        elif row["status"] == "Retired" and rng.random() < 0.35:
            exception_type = "Retired but Active"
            actual_user = "Active User Detected"
        elif row["status"] == "Assigned" and rng.random() < 0.06:
            exception_type = "Wrong Location"
            actual_loc = ALT_LOCATIONS[int(rng.integers(0, len(ALT_LOCATIONS)))]
        elif row["status"] == "Assigned" and rng.random() < 0.05:
            exception_type = "Wrong User"
            actual_user = "Different User Listed"
        elif rng.random() < 0.02:
            exception_type = "Missing Asset Tag"

        priority = PRIORITY_BY_EXCEPTION[exception_type]
        owner = "" if exception_type == "No Exception" else FOLLOW_UP_OWNERS[
            int(rng.integers(0, len(FOLLOW_UP_OWNERS)))
        ]

        records.append(
            {
                "Asset Tag": "" if exception_type == "Missing Asset Tag" else row["asset_tag"],
                "Serial Number": row["serial_number"],
                "Expected Location": expected_loc,
                "Actual Location": actual_loc,
                "Expected User": expected_user,
                "Actual User": actual_user,
                "Exception Type": exception_type,
                "Priority": priority,
                "Follow-Up Owner": owner,
                "Resolution Status": _resolution_for_exception(exception_type, rng),
            }
        )

    # Guaranteed curated scenarios for under-represented exception types
    if len(active) >= 3:
        base = active.iloc[2]
        records.append(
            {
                "Asset Tag": "UNKNOWN-001",
                "Serial Number": f"PHY{int(rng.integers(10000000, 99999999))}",
                "Expected Location": "",
                "Actual Location": "Store-Bronx",
                "Expected User": "",
                "Actual User": "Walk-In Asset",
                "Exception Type": "Found Not in System",
                "Priority": "High",
                "Follow-Up Owner": "Daniel A. Cruz",
                "Resolution Status": "Open",
            }
        )
        dup_serial = str(base["serial_number"])
        records.append(
            {
                "Asset Tag": "LAP-DUP-01",
                "Serial Number": dup_serial,
                "Expected Location": str(base["location"]),
                "Actual Location": str(base["location"]),
                "Expected User": "Unassigned",
                "Actual User": "Unassigned",
                "Exception Type": "Duplicate Serial Number",
                "Priority": "High",
                "Follow-Up Owner": "Patricia Nguyen",
                "Resolution Status": "In Progress",
            }
        )

    result = pd.DataFrame(records, columns=EXCEPTION_HEADERS)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    result["_order"] = result["Priority"].map(priority_order)
    return (
        result.sort_values(["_order", "Exception Type"])
        .drop(columns="_order")
        .reset_index(drop=True)
    )


def _build_system_sample(assets: pd.DataFrame, sample_size: int = 18) -> pd.DataFrame:
    """Build a sample system inventory table from active assets."""
    if assets.empty:
        return pd.DataFrame(columns=SYSTEM_HEADERS)

    active = assets[~assets["status"].isin(["Disposed"])].copy()
    sample = active.head(sample_size)
    return pd.DataFrame(
        {
            "Asset Tag": sample["asset_tag"],
            "Serial Number": sample["serial_number"],
            "Device Type": sample["device_type"],
            "Location": sample["location"],
            "Assigned User": sample["assigned_user"].replace("", "Unassigned"),
            "Status": sample["status"],
        }
    )


def _build_physical_sample(
    exceptions: pd.DataFrame,
    assets: pd.DataFrame,
    sample_size: int = 18,
) -> pd.DataFrame:
    """Build a sample physical audit table aligned to system records."""
    if assets.empty:
        return pd.DataFrame(columns=PHYSICAL_HEADERS)

    active = assets[~assets["status"].isin(["Disposed"])].copy().head(sample_size)
    physical_status = []
    for _, row in active.iterrows():
        if row["status"] == "Missing":
            physical_status.append("Not Found")
        else:
            physical_status.append("Present")

    physical = pd.DataFrame(
        {
            "Asset Tag": active["asset_tag"],
            "Serial Number": active["serial_number"],
            "Location": active["location"],
            "Assigned User": active["assigned_user"].replace("", "Unassigned"),
            "Physical Status": physical_status,
        }
    )

    # Append physical-only find
    found_not_in_system = exceptions[exceptions["Exception Type"] == "Found Not in System"]
    if not found_not_in_system.empty:
        extra = found_not_in_system.iloc[0]
        physical = pd.concat(
            [
                physical,
                pd.DataFrame(
                    [
                        {
                            "Asset Tag": extra["Asset Tag"],
                            "Serial Number": extra["Serial Number"],
                            "Location": extra["Actual Location"],
                            "Assigned User": extra["Actual User"],
                            "Physical Status": "Present",
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return physical


def _exception_summary(exceptions: pd.DataFrame) -> pd.DataFrame:
    """Count exceptions by type; include zero counts for missing types."""
    if exceptions.empty:
        return pd.DataFrame({"Exception Type": EXCEPTION_TYPES, "Count": [0] * len(EXCEPTION_TYPES)})

    counts = exceptions["Exception Type"].value_counts()
    rows = [{"Exception Type": et, "Count": int(counts.get(et, 0))} for et in EXCEPTION_TYPES]
    return pd.DataFrame(rows)


def _write_title(ws: Worksheet) -> None:
    """Render sheet title."""
    ws.merge_cells(start_row=TITLE_ROW, start_column=1, end_row=TITLE_ROW, end_column=10)
    cell = ws.cell(row=TITLE_ROW, column=1, value="Audit Reconciliation")
    cell.font = Font(
        name=sc.FONTS["default_name"],
        bold=True,
        color=sc.COLORS["white"],
        size=sc.FONTS["title_size"],
    )
    cell.fill = sc.HEADER_FILL
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[TITLE_ROW].height = 28


def _write_kpi_section(ws: Worksheet, exceptions: pd.DataFrame, start_col: int = 1) -> int:
    """Write KPI cards and return the next available row."""
    total_audited = len(exceptions)
    exception_rows = exceptions[exceptions["Exception Type"] != "No Exception"]
    exception_count = len(exception_rows)
    exception_rate = exception_count / total_audited if total_audited else 0
    high_priority = len(exception_rows[exception_rows["Priority"] == "High"])
    open_items = len(exception_rows[exception_rows["Resolution Status"] == "Open"])

    kpis = [
        ("Total Assets Audited", total_audited, sc.NUMBER_FORMATS["integer"]),
        ("Exception Count", exception_count, sc.NUMBER_FORMATS["integer"]),
        ("Exception Rate", exception_rate, sc.NUMBER_FORMATS["percentage"]),
        ("High Priority Exceptions", high_priority, sc.NUMBER_FORMATS["integer"]),
        ("Open Exceptions", open_items, sc.NUMBER_FORMATS["integer"]),
    ]

    card_cols = [1, 3, 5, 7, 9]
    for idx, (title, value, fmt) in enumerate(kpis):
        col = card_cols[idx]
        apply_kpi_card_style(ws, KPI_TITLE_ROW, col, KPI_VALUE_ROW, col, title, value, span_cols=2)
        ws.cell(row=KPI_VALUE_ROW, column=col).number_format = fmt

    return KPI_VALUE_ROW + 2


def _write_table_section(
    ws: Worksheet,
    start_row: int,
    section_title: str,
    headers: list[str],
    data: pd.DataFrame,
    table_name: str,
) -> int:
    """Write a titled table section and return the row after the table."""
    apply_section_header_style(ws, start_row, 1, section_title, span_cols=len(headers))
    header_row = start_row + 1
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=header_row, column=col_idx, value=header)
    apply_table_header_style(ws, header_row, len(headers))

    first_data_row = header_row + 1
    last_data_row = header_row
    for offset, (_, row) in enumerate(data.iterrows()):
        excel_row = first_data_row + offset
        for col_idx, header in enumerate(headers, start=1):
            value = row[header]
            ws.cell(row=excel_row, column=col_idx, value="" if pd.isna(value) else value)
        last_data_row = excel_row

    if last_data_row < first_data_row:
        last_data_row = first_data_row

    end_col = get_column_letter(len(headers))
    create_excel_table(ws, table_name, f"A{header_row}:{end_col}{last_data_row}")
    return last_data_row + 2


def _apply_exception_formatting(ws: Worksheet, header_row: int, last_row: int) -> None:
    """Apply conditional formatting to Priority and Exception Type columns."""
    if last_row <= header_row:
        return

    data_start = header_row + 1
    priority_col = get_column_letter(EXCEPTION_HEADERS.index("Priority") + 1)
    type_col = get_column_letter(EXCEPTION_HEADERS.index("Exception Type") + 1)

    apply_risk_conditional_formatting(
        ws,
        f"{priority_col}{data_start}:{priority_col}{last_row}",
        priority_col,
        data_start,
        PRIORITY_CF_MAP,
    )
    apply_risk_conditional_formatting(
        ws,
        f"{type_col}{data_start}:{type_col}{last_row}",
        type_col,
        data_start,
        EXCEPTION_TYPE_CF_MAP,
    )


def build(ws: Worksheet, context: dict[str, Any]) -> None:
    """Build the Audit Reconciliation sheet from IT asset data."""
    assets: pd.DataFrame = context["data"].get("it_assets", pd.DataFrame())
    exceptions = _build_exceptions_dataframe(assets)
    system_sample = _build_system_sample(assets)
    physical_sample = _build_physical_sample(exceptions, assets)
    summary = _exception_summary(exceptions)

    _write_title(ws)
    next_row = _write_kpi_section(ws, exceptions)

    next_row = _write_table_section(
        ws,
        next_row,
        "Exception Summary by Type",
        SUMMARY_HEADERS,
        summary,
        "AuditExceptionSummary",
    )

    next_row = _write_table_section(
        ws,
        next_row,
        "System Inventory (Sample)",
        SYSTEM_HEADERS,
        system_sample,
        "AuditSystemInventory",
    )

    next_row = _write_table_section(
        ws,
        next_row,
        "Physical Audit Count (Sample)",
        PHYSICAL_HEADERS,
        physical_sample,
        "AuditPhysicalCount",
    )

    apply_section_header_style(ws, next_row, 1, "Exceptions Report", span_cols=len(EXCEPTION_HEADERS))
    header_row = next_row + 1
    for col_idx, header in enumerate(EXCEPTION_HEADERS, start=1):
        ws.cell(row=header_row, column=col_idx, value=header)
    apply_table_header_style(ws, header_row, len(EXCEPTION_HEADERS))

    first_data_row = header_row + 1
    last_row = header_row
    for offset, (_, row) in enumerate(exceptions.iterrows()):
        excel_row = first_data_row + offset
        for col_idx, header in enumerate(EXCEPTION_HEADERS, start=1):
            value = row[header]
            ws.cell(row=excel_row, column=col_idx, value="" if pd.isna(value) else value)
        last_row = excel_row

    if last_row >= first_data_row:
        end_col = get_column_letter(len(EXCEPTION_HEADERS))
        create_excel_table(ws, "AuditExceptionsReport", f"A{header_row}:{end_col}{last_row}")
        _apply_exception_formatting(ws, header_row, last_row)

    freeze_panes(ws, row=first_data_row, col=1)
    set_column_widths(ws, {"A": 14, "B": 14, "C": 16, "D": 16, "E": 16, "F": 16, "G": 22, "H": 10, "I": 18, "J": 16})
    autosize_columns(ws, min_width=10, max_width=28)
    ws.sheet_view.showGridLines = False
    set_landscape_print(ws, fit_width=1, repeat_header_rows=f"{TITLE_ROW}:{TITLE_ROW}")
