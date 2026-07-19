"""Deterministic Inventory Dashboard layout specification (canvas A:V)."""

from __future__ import annotations

from dataclasses import dataclass

DASHBOARD_CANVAS_COLS = 22  # A through V
TABLE_AREA_END_COL = 8  # A:H
DIVIDER_COL = 9  # I spacer
CHART_AREA_START_COL = 10  # J
CHART_AREA_END_COL = 22  # V
CHART_ANCHOR_COL = "J"
CHART_LABEL_COL = 8  # column H — optional chart category helper (outside table)

KPI_START_ROW = 1
KPI_END_ROW = 8
FREEZE_PANE = "A9"
SECTIONS_START_ROW = 10

CHART_WIDTH_CM = 26.0
CHART_HEIGHT_CM = 10.0
CHART_MIN_WIDTH_CM = 24.0
CHART_MAX_WIDTH_CM = 28.0
CHART_MIN_HEIGHT_CM = 9.0
CHART_MAX_HEIGHT_CM = 11.0

AS_OF_CONTEXT = "As of July 1, 2026"

DASHBOARD_COLUMN_WIDTHS: dict[str, float] = {
    "A": 16,
    "B": 22,
    "C": 16,
    "D": 16,
    "E": 16,
    "F": 16,
    "G": 16,
    "H": 16,
    "I": 3,
    "J": 12,
    "K": 12,
    "L": 12,
    "M": 12,
    "N": 12,
    "O": 12,
    "P": 12,
    "Q": 12,
    "R": 12,
    "S": 12,
    "T": 12,
    "U": 12,
    "V": 12,
}

SECTION_TITLE_HEIGHT = 26
TABLE_HEADER_HEIGHT = 24
DATA_ROW_HEIGHT = 20

# Approved chart titles (business-focused)
CHART_TITLES: dict[str, str] = {
    "location": "Inventory Value by Location",
    "status": "Inventory Exposure by Status",
    "aging": "Inventory Value by Aging Bucket",
    "top_excess": "Top 10 Excess Inventory Items",
    "abc_usage": "Annual Usage Value by ABC Class",
    "replenishment": "Replenishment Requirements by Status",
    "fill_rate": "Fill Rate by Location",
    "vendor_risk": "Supplier Exposure by Risk Class",
    "transfer_benefit": "Top Transfer Opportunities by Net Benefit",
    "action": "Inventory Value by Recommended Action",
}


@dataclass(frozen=True)
class DashboardSectionSpec:
    """Fixed row block for one table/chart pair."""

    key: str
    title: str
    chart_title: str
    start_row: int
    end_row: int
    chart_type: str
    context: str = AS_OF_CONTEXT


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
    chart_type: str


def _section(start: int, key: str, title: str, chart_type: str) -> DashboardSectionSpec:
    return DashboardSectionSpec(
        key=key,
        title=title,
        chart_title=CHART_TITLES[key],
        start_row=start,
        end_row=start + 19,
        chart_type=chart_type,
    )


# Two blank rows between each 20-row section block.
DASHBOARD_SECTIONS: tuple[DashboardSectionSpec, ...] = (
    _section(10, "location", "Inventory Value by Location", "horizontal_bar"),
    _section(32, "status", "Inventory Exposure by Status", "horizontal_bar"),
    _section(54, "aging", "Inventory Value by Aging Bucket", "column"),
    _section(76, "top_excess", "Top 10 Excess Inventory Items", "horizontal_bar"),
    _section(98, "abc_usage", "Annual Usage Value by ABC Class", "column"),
    _section(
        120, "replenishment", "Replenishment Requirements by Status", "horizontal_bar"
    ),
    _section(142, "fill_rate", "Fill Rate by Location", "clustered_bar"),
    _section(164, "vendor_risk", "Supplier Exposure by Risk Class", "column"),
    _section(
        186,
        "transfer_benefit",
        "Top Transfer Opportunities by Net Benefit",
        "horizontal_bar",
    ),
    _section(208, "action", "Inventory Value by Recommended Action", "horizontal_bar"),
)


def chart_layout_specs() -> tuple[ChartLayoutSpec, ...]:
    """Build chart layout specs from the fixed section grid."""
    specs: list[ChartLayoutSpec] = []
    for idx, section in enumerate(DASHBOARD_SECTIONS, start=1):
        anchor_row = section.start_row + 2
        specs.append(
            ChartLayoutSpec(
                name=section.chart_title,
                section=idx,
                anchor_cell=f"{CHART_ANCHOR_COL}{anchor_row}",
                allowed_start_row=section.start_row,
                allowed_end_row=section.end_row,
                allowed_start_col=CHART_AREA_START_COL,
                allowed_end_col=CHART_AREA_END_COL,
                chart_type=section.chart_type,
            )
        )
    return tuple(specs)
