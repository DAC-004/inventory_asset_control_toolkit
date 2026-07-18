"""Excel formula KPI definitions for dashboard and management summary."""

from __future__ import annotations

from config.workbook_config import INVENTORY_THRESHOLDS
from src.domain.constants import (
    COL_AGE_DAYS,
    COL_RECOMMENDED_ACTION,
    COL_STATUS,
    COL_TOTAL_VALUE,
    MARKDOWN_ACTIONS,
    MASTER_DATA_START,
    MASTER_SHEET,
    TRANSFER_ACTIONS,
)
from src.workbook.formulas import (
    count_if_range,
    sum_if_numeric,
    sum_if_range,
    sum_range,
)


def recovery_value_formula(start: int, end: int) -> str:
    """Estimated recovery from markdown / liquidation candidate inventory."""
    parts = [
        sum_if_range(
            MASTER_SHEET, COL_RECOMMENDED_ACTION, action, COL_TOTAL_VALUE, start, end
        )
        for action in MARKDOWN_ACTIONS
    ]
    return "=" + "+".join(part.lstrip("=") for part in parts)


def dashboard_kpi_definitions(start: int, end: int) -> list[tuple[str, str, str]]:
    """
    Return KPI card definitions: (title, formula, format_type).

    format_type: currency | integer | percentage
    """
    aged_threshold = INVENTORY_THRESHOLDS["excess_aged_age_days"]
    return [
        (
            "Total Inventory Value",
            sum_range(MASTER_SHEET, COL_TOTAL_VALUE, start, end),
            "currency",
        ),
        (
            "Aged Inventory Value",
            sum_if_numeric(
                MASTER_SHEET,
                COL_AGE_DAYS,
                f">{aged_threshold}",
                COL_TOTAL_VALUE,
                start,
                end,
            ),
            "currency",
        ),
        (
            "Excess Inventory Value",
            "="
            + "+".join(
                sum_if_range(
                    MASTER_SHEET, COL_STATUS, status, COL_TOTAL_VALUE, start, end
                ).lstrip("=")
                for status in ("Excess", "Excess / Aged")
            ),
            "currency",
        ),
        (
            "Obsolete SKU Count",
            count_if_range(MASTER_SHEET, COL_STATUS, start, end, "Obsolete"),
            "integer",
        ),
        (
            "Stockout Risk SKU Count",
            count_if_range(MASTER_SHEET, COL_STATUS, start, end, "Stockout Risk"),
            "integer",
        ),
        ("Estimated Recovery Value", recovery_value_formula(start, end), "currency"),
    ]


def management_summary_kpis(inv_end: int) -> list[tuple[str, str, str]]:
    """KPI definitions for the printable management summary."""
    start = MASTER_DATA_START
    aged_threshold = INVENTORY_THRESHOLDS["excess_aged_age_days"]
    excess_formula = "=" + "+".join(
        sum_if_range(
            MASTER_SHEET, COL_STATUS, status, COL_TOTAL_VALUE, start, inv_end
        ).lstrip("=")
        for status in ("Excess", "Excess / Aged")
    )
    transfer_formula = "=" + "+".join(
        count_if_range(
            MASTER_SHEET, COL_RECOMMENDED_ACTION, start, inv_end, action
        ).lstrip("=")
        for action in TRANSFER_ACTIONS
    )
    markdown_formula = "=" + "+".join(
        count_if_range(
            MASTER_SHEET, COL_RECOMMENDED_ACTION, start, inv_end, action
        ).lstrip("=")
        for action in MARKDOWN_ACTIONS
    )
    return [
        (
            "Total Inventory Value",
            sum_range(MASTER_SHEET, COL_TOTAL_VALUE, start, inv_end),
            "currency",
        ),
        (
            "Aged Inventory Value",
            sum_if_numeric(
                MASTER_SHEET,
                COL_AGE_DAYS,
                f">{aged_threshold}",
                COL_TOTAL_VALUE,
                start,
                inv_end,
            ),
            "currency",
        ),
        ("Excess Inventory Value", excess_formula, "currency"),
        ("Transfer Candidates", transfer_formula, "integer"),
        ("Markdown Candidates", markdown_formula, "integer"),
    ]
