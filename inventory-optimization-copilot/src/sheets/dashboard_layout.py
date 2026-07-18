"""Deterministic Inventory Dashboard layout specification (canvas A:R)."""

from __future__ import annotations

from dataclasses import dataclass

DASHBOARD_CANVAS_COLS = 18  # A through R
TABLE_AREA_END_COL = 7  # A:G
DIVIDER_COL = 8  # H
CHART_AREA_START_COL = 9  # I
CHART_AREA_END_COL = 18  # R
CHART_ANCHOR_COL = "I"

KPI_START_ROW = 1
KPI_END_ROW = 8
FREEZE_PANE = "A9"
SECTIONS_START_ROW = 10

CHART_WIDTH_CM = 18.0
CHART_HEIGHT_CM = 8.5
CHART_MIN_WIDTH_CM = 17.0
CHART_MAX_WIDTH_CM = 19.0
CHART_MIN_HEIGHT_CM = 8.0
CHART_MAX_HEIGHT_CM = 9.0

DASHBOARD_COLUMN_WIDTHS: dict[str, float] = {
    "A": 18,
    "B": 24,
    "C": 15,
    "D": 15,
    "E": 15,
    "F": 15,
    "G": 15,
    "H": 3,
    "I": 12,
    "J": 12,
    "K": 12,
    "L": 12,
    "M": 12,
    "N": 12,
    "O": 12,
    "P": 12,
    "Q": 12,
    "R": 12,
}

SECTION_TITLE_HEIGHT = 26
TABLE_HEADER_HEIGHT = 24
DATA_ROW_HEIGHT = 20
SPACER_ROW_HEIGHT = 10


@dataclass(frozen=True)
class DashboardSectionSpec:
    """Fixed row block for one table/chart pair."""

    key: str
    title: str
    chart_title: str
    start_row: int
    end_row: int
    chart_type: str  # horizontal_bar | column | clustered_bar | pie | doughnut


@dataclass(frozen=True)
class ChartLayoutSpec:
    """Automated layout test specification for one dashboard chart."""

    name: str
    section: int
    anchor_cell: str
    allowed_start_row: int
    allowed_end_row: int
    allowed_start_col: int
    allowed_end_col: int


DASHBOARD_SECTIONS: tuple[DashboardSectionSpec, ...] = (
    DashboardSectionSpec(
        "location",
        "Inventory Value by Location",
        "Inventory Value by Location",
        10,
        27,
        "horizontal_bar",
    ),
    DashboardSectionSpec(
        "status",
        "Inventory Status",
        "Inventory Status",
        30,
        47,
        "doughnut",
    ),
    DashboardSectionSpec(
        "aging",
        "Aging Buckets",
        "Aging Buckets",
        50,
        67,
        "column",
    ),
    DashboardSectionSpec(
        "top_excess",
        "Top Excess Items",
        "Top Excess Items",
        70,
        87,
        "horizontal_bar",
    ),
    DashboardSectionSpec(
        "abc_usage",
        "ABC Annual Usage Value",
        "ABC Annual Usage Value",
        90,
        107,
        "column",
    ),
    DashboardSectionSpec(
        "replenishment",
        "Replenishment Status",
        "Replenishment Status",
        110,
        127,
        "column",
    ),
    DashboardSectionSpec(
        "fill_rate",
        "Fill Rate by Location",
        "Fill Rate by Location",
        130,
        147,
        "clustered_bar",
    ),
    DashboardSectionSpec(
        "vendor_risk",
        "Vendor Risk",
        "Vendor Risk",
        150,
        167,
        "column",
    ),
    DashboardSectionSpec(
        "transfer_benefit",
        "Transfer Net Benefit",
        "Transfer Net Benefit",
        170,
        187,
        "horizontal_bar",
    ),
    DashboardSectionSpec(
        "action",
        "Recommended Actions",
        "Recommended Actions",
        190,
        207,
        "doughnut",
    ),
)


def chart_layout_specs() -> tuple[ChartLayoutSpec, ...]:
    """Build chart layout specs from the fixed section grid."""
    specs: list[ChartLayoutSpec] = []
    for idx, section in enumerate(DASHBOARD_SECTIONS, start=1):
        anchor_row = section.start_row + 1
        specs.append(
            ChartLayoutSpec(
                name=section.chart_title,
                section=idx,
                anchor_cell=f"{CHART_ANCHOR_COL}{anchor_row}",
                allowed_start_row=section.start_row,
                allowed_end_row=section.end_row,
                allowed_start_col=CHART_AREA_START_COL,
                allowed_end_col=CHART_AREA_END_COL,
            )
        )
    return tuple(specs)
